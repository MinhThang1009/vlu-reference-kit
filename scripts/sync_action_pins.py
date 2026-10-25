#!/usr/bin/env python3
"""Synchronize reviewed workflow action pins to each action's latest release."""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from urllib.parse import quote
from urllib.request import HTTPRedirectHandler, Request, build_opener


GITHUB_API_URL = "https://api.github.com"
MAX_RESPONSE_BYTES = 8 * 1024 * 1024
MAX_ACTION_TAG_PAGES = 20
MAX_ANNOTATED_TAG_DEPTH = 10
YAML_TAG_PATTERN = r"!(?:<[^>\r\n]+>|[^\s\[\]{},#&*|>@]*)"
YAML_NODE_PROPERTIES_PATTERN = rf"(?:(?:&[A-Za-z0-9_-]+|{YAML_TAG_PATTERN})\s+)*"
YAML_ANCHOR_PROPERTIES_PATTERN = (
    rf"(?:(?:{YAML_TAG_PATTERN})\s+)*&(?P<anchor>[A-Za-z0-9_-]+)\s+"
    rf"(?:(?:{YAML_TAG_PATTERN})\s+)*"
)
YAML_ANCHORED_VALUE_PREFIX_PATTERN = (
    rf"\s*(?:(?:-\s*)?[^#\r\n]+:\s*|-\s*){YAML_ANCHOR_PROPERTIES_PATTERN}"
)
YAML_DOUBLE_QUOTED_LINE_CONTINUATION_PATTERN = r"(?:\\\r?\n[ \t]*)*"
YAML_DOUBLE_QUOTED_CONTINUATION_PATTERN = r"\\\r?\n[ \t]*"
YAML_DOUBLE_QUOTED_ESCAPE_PATTERN = (
    r'\\(?:[0abtnvfre "/\\N_LP]|x[0-9a-fA-F]{2}|u[0-9a-fA-F]{4}|U[0-9a-fA-F]{8})'
)
YAML_ACTION_COMPONENT_PATTERN = (
    rf"(?:[A-Za-z0-9_.-]|{YAML_DOUBLE_QUOTED_ESCAPE_PATTERN})+"
)
YAML_ACTION_PATH_SEPARATOR_PATTERN = rf"(?:/|{YAML_DOUBLE_QUOTED_ESCAPE_PATTERN})"
YAML_ACTION_REVISION_SEPARATOR_PATTERN = r"(?:@|\\(?:x40|u0040|U00000040))"
YAML_ACTION_SHA_PATTERN = rf"(?:[0-9a-fA-F]|{YAML_DOUBLE_QUOTED_ESCAPE_PATTERN})+"
YAML_CONTINUED_ACTION_COMPONENT_PATTERN = (
    rf"(?:[A-Za-z0-9_.-]|{YAML_DOUBLE_QUOTED_ESCAPE_PATTERN}|"
    rf"{YAML_DOUBLE_QUOTED_CONTINUATION_PATTERN})+"
)
YAML_ACTION_REFERENCE_PATTERN = (
    rf"{YAML_ACTION_COMPONENT_PATTERN}{YAML_ACTION_PATH_SEPARATOR_PATTERN}"
    rf"{YAML_ACTION_COMPONENT_PATTERN}(?:{YAML_ACTION_PATH_SEPARATOR_PATTERN}"
    rf"{YAML_ACTION_COMPONENT_PATTERN})*"
)
YAML_DOUBLE_QUOTED_USES_KEY_PATTERN = (
    rf'"{YAML_DOUBLE_QUOTED_LINE_CONTINUATION_PATTERN}(?:u|\\x75|\\u0075|\\U00000075)'
    rf"{YAML_DOUBLE_QUOTED_LINE_CONTINUATION_PATTERN}(?:s|\\x73|\\u0073|\\U00000073)"
    rf"{YAML_DOUBLE_QUOTED_LINE_CONTINUATION_PATTERN}(?:e|\\x65|\\u0065|\\U00000065)"
    rf"{YAML_DOUBLE_QUOTED_LINE_CONTINUATION_PATTERN}(?:s|\\x73|\\u0073|\\U00000073)"
    rf'{YAML_DOUBLE_QUOTED_LINE_CONTINUATION_PATTERN}"'
)
YAML_USES_KEY_PATTERN = rf"{YAML_NODE_PROPERTIES_PATTERN}(?:uses|'uses'|{YAML_DOUBLE_QUOTED_USES_KEY_PATTERN})"
YAML_BLOCK_SCALAR_STRIP_PATTERN = r"[>|](?:[0-9]*-|-[0-9]*)"
FLOW_MAPPING_CONTENT_PATTERN = r"""(?:[^{}'"]|'[^']*'|"(?:[^"\\]|\\.)*"|\{(?:[^{}'"]|'[^']*'|"(?:[^"\\]|\\.)*")*\}|\{\{[^{}]*\}\})*"""
ACTION_PIN_PATTERN = re.compile(
    rf"(?m)^(?P<prefix>\s*(?:-\s*)?{YAML_USES_KEY_PATTERN}:\s*{YAML_NODE_PROPERTIES_PATTERN})(?P<quote>['\"]?)(?P<action>{YAML_ACTION_REFERENCE_PATTERN}){YAML_ACTION_REVISION_SEPARATOR_PATTERN}(?P<sha>{YAML_ACTION_SHA_PATTERN})(?P=quote)(?P<comment>[ \t]*(?:#[^\r\n]*)?)(?=\r?$)"
)
CONTINUED_DOUBLE_QUOTED_ACTION_PIN_PATTERN = re.compile(
    rf'(?m)^(?P<prefix>\s*(?:-\s*)?{YAML_USES_KEY_PATTERN}:\s*{YAML_NODE_PROPERTIES_PATTERN})(?P<quote>")(?=(?:[^"\r\n]|{YAML_DOUBLE_QUOTED_CONTINUATION_PATTERN})*{YAML_DOUBLE_QUOTED_CONTINUATION_PATTERN})(?P<action>{YAML_CONTINUED_ACTION_COMPONENT_PATTERN}{YAML_ACTION_PATH_SEPARATOR_PATTERN}{YAML_CONTINUED_ACTION_COMPONENT_PATTERN}(?:{YAML_ACTION_PATH_SEPARATOR_PATTERN}{YAML_CONTINUED_ACTION_COMPONENT_PATTERN})*){YAML_ACTION_REVISION_SEPARATOR_PATTERN}(?P<sha>(?:[0-9a-fA-F]|{YAML_DOUBLE_QUOTED_ESCAPE_PATTERN}|{YAML_DOUBLE_QUOTED_CONTINUATION_PATTERN})+)(?P=quote)(?P<comment>[ \t]*(?:#[^\r\n]*)?)(?=\r?$)'
)
USES_PATTERN = re.compile(
    rf"(?m)^\s*(?:-\s*)?{YAML_USES_KEY_PATTERN}:\s*{YAML_NODE_PROPERTIES_PATTERN}(?P<quote>['\"]?)(?P<reference>\S+?)(?P=quote)(?:[ \t]*(?:#[^\r\n]*)?)?(?=\r?$)"
)
CONTINUED_DOUBLE_QUOTED_USES_PATTERN = re.compile(
    rf'(?m)^\s*(?:-\s*)?{YAML_USES_KEY_PATTERN}:\s*{YAML_NODE_PROPERTIES_PATTERN}(?P<quote>")(?P<reference>[^"\r\n]*(?:{YAML_DOUBLE_QUOTED_CONTINUATION_PATTERN}[^"\r\n]*)+)(?P=quote)(?:[ \t]*(?:#[^\r\n]*)?)?(?=\r?$)'
)
CONTINUED_ANCHORED_ACTION_REFERENCE_PATTERN = re.compile(
    rf'(?m)^(?P<prefix>{YAML_ANCHORED_VALUE_PREFIX_PATTERN})(?P<quote>")(?P<reference>[^"\r\n]*(?:{YAML_DOUBLE_QUOTED_CONTINUATION_PATTERN}[^"\r\n]*)+)(?P=quote)(?:[ \t]*(?:#[^\r\n]*)?)?(?=\r?$)'
)
EXPLICIT_USES_PATTERN = re.compile(
    rf"(?m)^(?P<prefix>\s*(?:-\s*)?\?\s*{YAML_USES_KEY_PATTERN}\s*\r?\n\s*:\s*{YAML_NODE_PROPERTIES_PATTERN})(?P<quote>['\"]?)(?P<reference>\S+?)(?P=quote)(?:[ \t]*(?:#[^\r\n]*)?)?(?=\r?$)"
)
EXPLICIT_ACTION_PIN_PATTERN = re.compile(
    rf"(?m)^(?P<prefix>\s*(?:-\s*)?\?\s*{YAML_USES_KEY_PATTERN}\s*\r?\n\s*:\s*{YAML_NODE_PROPERTIES_PATTERN})(?P<explicit>)(?P<quote>['\"]?)(?P<action>{YAML_ACTION_REFERENCE_PATTERN}){YAML_ACTION_REVISION_SEPARATOR_PATTERN}(?P<sha>{YAML_ACTION_SHA_PATTERN})(?P=quote)(?P<comment>[ \t]*(?:#[^\r\n]*)?)(?=\r?$)"
)
EXPLICIT_BLOCK_USES_PATTERN = re.compile(
    rf"(?m)^(?P<prefix>\s*(?:-\s*)?\?\s*{YAML_NODE_PROPERTIES_PATTERN}{YAML_BLOCK_SCALAR_STRIP_PATTERN}[ \t]*(?:#[^\r\n]*)?\r?\n[ \t]*uses[ \t]*\r?\n\s*:\s*{YAML_NODE_PROPERTIES_PATTERN})(?P<quote>['\"]?)(?P<reference>\S+?)(?P=quote)(?:[ \t]*(?:#[^\r\n]*)?)?(?=\r?$)"
)
EXPLICIT_BLOCK_ACTION_PIN_PATTERN = re.compile(
    rf"(?m)^(?P<prefix>\s*(?:-\s*)?\?\s*{YAML_NODE_PROPERTIES_PATTERN}{YAML_BLOCK_SCALAR_STRIP_PATTERN}[ \t]*(?:#[^\r\n]*)?\r?\n[ \t]*uses[ \t]*\r?\n\s*:\s*{YAML_NODE_PROPERTIES_PATTERN})(?P<explicit>)(?P<quote>['\"]?)(?P<action>{YAML_ACTION_REFERENCE_PATTERN}){YAML_ACTION_REVISION_SEPARATOR_PATTERN}(?P<sha>{YAML_ACTION_SHA_PATTERN})(?P=quote)(?P<comment>[ \t]*(?:#[^\r\n]*)?)(?=\r?$)"
)
BLOCK_SCALAR_USES_PATTERN = re.compile(
    rf"(?m)^\s*(?:-\s*)?{YAML_USES_KEY_PATTERN}:\s*{YAML_NODE_PROPERTIES_PATTERN}[>|][0-9+-]*[ \t]*(?:#[^\r\n]*)?\r?\n[ \t]*(?P<reference>\S+?)(?:[ \t]*(?:#[^\r\n]*)?)?(?=\r?$)"
)
BLOCK_SCALAR_ACTION_PIN_PATTERN = re.compile(
    rf"(?m)^(?P<prefix>\s*(?:-\s*)?{YAML_USES_KEY_PATTERN}:\s*{YAML_NODE_PROPERTIES_PATTERN}[>|][0-9+-]*[ \t]*(?:#[^\r\n]*)?\r?\n[ \t]*)(?P<quote>)(?P<action>{YAML_ACTION_REFERENCE_PATTERN}){YAML_ACTION_REVISION_SEPARATOR_PATTERN}(?P<sha>{YAML_ACTION_SHA_PATTERN})(?P<comment>[ \t]*)(?=\r?$)"
)
FLOW_USES_PATTERN = re.compile(
    rf"(?m)^\s*(?:-\s*)?\{{{FLOW_MAPPING_CONTENT_PATTERN}?(?:\?\s*)?{YAML_USES_KEY_PATTERN}\s*:\s*{YAML_NODE_PROPERTIES_PATTERN}(?P<quote>['\"]?)(?P<reference>\S+?)(?P=quote)(?P<flow_suffix>\s*(?:,{FLOW_MAPPING_CONTENT_PATTERN})?\}})(?:[ \t]*(?:#[^\r\n]*)?)?(?=\r?$)"
)
FLOW_ACTION_PIN_PATTERN = re.compile(
    rf"(?m)^(?P<prefix>\s*(?:-\s*)?\{{{FLOW_MAPPING_CONTENT_PATTERN}?(?:\?\s*)?{YAML_USES_KEY_PATTERN}\s*:\s*{YAML_NODE_PROPERTIES_PATTERN})(?P<quote>['\"]?)(?P<action>{YAML_ACTION_REFERENCE_PATTERN}){YAML_ACTION_REVISION_SEPARATOR_PATTERN}(?P<sha>{YAML_ACTION_SHA_PATTERN})(?P=quote)(?P<flow_suffix>\s*(?:,{FLOW_MAPPING_CONTENT_PATTERN})?\}})(?P<comment>[ \t]*(?:#[^\r\n]*)?)(?=\r?$)"
)
FLOW_INLINE_USES_PATTERN = re.compile(
    rf"(?P<prefix>[{{,]\s*(?:\?\s*)?{YAML_USES_KEY_PATTERN}\s*:\s*{YAML_NODE_PROPERTIES_PATTERN})(?P<quote>['\"]?)(?P<reference>\S+?)(?P=quote)(?=\s*(?:[,}}]))"
)
FLOW_INLINE_ACTION_PIN_PATTERN = re.compile(
    rf"(?P<prefix>[{{,]\s*(?:\?\s*)?{YAML_USES_KEY_PATTERN}\s*:\s*{YAML_NODE_PROPERTIES_PATTERN})(?P<quote>['\"]?)(?P<action>{YAML_ACTION_REFERENCE_PATTERN}){YAML_ACTION_REVISION_SEPARATOR_PATTERN}(?P<sha>{YAML_ACTION_SHA_PATTERN})(?P=quote)(?P<flow_inline>)(?=\s*(?:[,}}]))"
)
ALIAS_MAPPING_KEY_PATTERN = re.compile(
    r"(?m)^\s*(?:-\s*)?(?:\?\s*)?\*(?P<alias>[A-Za-z0-9_-]+)\s*:"
)
EXPLICIT_ALIAS_MAPPING_KEY_PATTERN = re.compile(
    r"(?m)^\s*(?:-\s*)?\?\s*\*(?P<alias>[A-Za-z0-9_-]+)\s*\r?\n\s*:"
)
FLOW_ALIAS_MAPPING_KEY_PATTERN = re.compile(
    r"(?P<prefix>[{,]\s*(?:\?\s*)?)\*(?P<alias>[A-Za-z0-9_-]+)\s*:"
)
FLOW_ANCHORED_ACTION_REFERENCE_PATTERN = re.compile(
    rf"(?P<prefix>&(?P<anchor>[A-Za-z0-9_-]+)\s+(?:{YAML_TAG_PATTERN}\s+)*)(?P<quote>['\"]?)(?P<reference>\S+?)(?P=quote)(?=\s*(?:[,}}]))"
)
FLOW_ANCHORED_ACTION_PIN_PATTERN = re.compile(
    rf"(?P<prefix>&(?P<anchor>[A-Za-z0-9_-]+)\s+(?:{YAML_TAG_PATTERN}\s+)*)(?P<quote>['\"]?)(?P<action>{YAML_ACTION_REFERENCE_PATTERN}){YAML_ACTION_REVISION_SEPARATOR_PATTERN}(?P<sha>{YAML_ACTION_SHA_PATTERN})(?P=quote)(?P<flow_inline>)(?=\s*(?:[,}}]))"
)
ANCHORED_ACTION_REFERENCE_PATTERN = re.compile(
    rf"(?m)^(?P<prefix>{YAML_ANCHORED_VALUE_PREFIX_PATTERN})(?P<quote>['\"]?)(?P<reference>\S+?)(?P=quote)(?:[ \t]*(?:#[^\r\n]*)?)?(?=\r?$)"
)
ANCHORED_ACTION_PIN_PATTERN = re.compile(
    rf"(?m)^(?P<prefix>{YAML_ANCHORED_VALUE_PREFIX_PATTERN})(?P<quote>['\"]?)(?P<action>{YAML_ACTION_REFERENCE_PATTERN}){YAML_ACTION_REVISION_SEPARATOR_PATTERN}(?P<sha>{YAML_ACTION_SHA_PATTERN})(?P=quote)(?P<comment>[ \t]*(?:#[^\r\n]*)?)(?=\r?$)"
)
ANCHORED_BLOCK_SCALAR_ACTION_REFERENCE_PATTERN = re.compile(
    rf"(?m)^(?P<prefix>{YAML_ANCHORED_VALUE_PREFIX_PATTERN}[>|][0-9+-]*[ \t]*(?:#[^\r\n]*)?\r?\n[ \t]*)(?P<quote>)(?P<reference>\S+?)(?:[ \t]*(?:#[^\r\n]*)?)?(?=\r?$)"
)
ANCHORED_BLOCK_SCALAR_ACTION_PIN_PATTERN = re.compile(
    rf"(?m)^(?P<prefix>{YAML_ANCHORED_VALUE_PREFIX_PATTERN}[>|][0-9+-]*[ \t]*(?:#[^\r\n]*)?\r?\n[ \t]*)(?P<quote>)(?P<action>{YAML_ACTION_REFERENCE_PATTERN}){YAML_ACTION_REVISION_SEPARATOR_PATTERN}(?P<sha>{YAML_ACTION_SHA_PATTERN})(?P<comment>[ \t]*)(?=\r?$)"
)
CONTINUED_ANCHORED_ACTION_PIN_PATTERN = re.compile(
    rf'(?m)^(?P<prefix>{YAML_ANCHORED_VALUE_PREFIX_PATTERN})(?P<quote>")(?=(?:[^"\r\n]|{YAML_DOUBLE_QUOTED_CONTINUATION_PATTERN})*{YAML_DOUBLE_QUOTED_CONTINUATION_PATTERN})(?P<action>{YAML_CONTINUED_ACTION_COMPONENT_PATTERN}{YAML_ACTION_PATH_SEPARATOR_PATTERN}{YAML_CONTINUED_ACTION_COMPONENT_PATTERN}(?:{YAML_ACTION_PATH_SEPARATOR_PATTERN}{YAML_CONTINUED_ACTION_COMPONENT_PATTERN})*){YAML_ACTION_REVISION_SEPARATOR_PATTERN}(?P<sha>(?:[0-9a-fA-F]|{YAML_DOUBLE_QUOTED_ESCAPE_PATTERN}|{YAML_DOUBLE_QUOTED_CONTINUATION_PATTERN})+)(?P=quote)(?P<comment>[ \t]*(?:#[^\r\n]*)?)(?=\r?$)'
)
BLOCK_SCALAR_HEADER_PATTERN = re.compile(
    rf"^(?P<indent> *)(?:(?:-\s*)?[^#\r\n]+:\s*{YAML_NODE_PROPERTIES_PATTERN}|-\s*{YAML_NODE_PROPERTIES_PATTERN}|(?:-\s*)?\?\s*{YAML_NODE_PROPERTIES_PATTERN})(?P<style>[>|][0-9+-]*)[ \t]*(?:#.*)?(?:\r?\n)?$"
)
FLOW_NODE_START_PATTERN = re.compile(
    rf"(?m)^[ \t]*(?:(?:-[ \t]+)?(?:[^:#'\"\[\]{{}}\r\n]+|'(?:[^']|'')*'|\"(?:[^\"\\]|\\.)*\"):[ \t]*|-[ \t]+|(?:-[ \t]+)?\?[ \t]+)?{YAML_NODE_PROPERTIES_PATTERN}(?=[\[{{'\"])"
)
BLOCK_MAPPING_VALUE_PATTERN = re.compile(
    rf"""^(?P<indent> *)(?P<sequence>(?:-[ \t]+)+)?(?:[^:#'"\[\]{{}}\r\n]+|'(?:[^']|'')*'|"(?:[^"\\]|\\.)*"):[ \t]+{YAML_NODE_PROPERTIES_PATTERN}(?P<value>\S[^\r\n]*)"""
)
BLOCK_SEQUENCE_VALUE_PATTERN = re.compile(
    rf"^(?P<indent> *)(?P<sequence>(?:-[ \t]+)+){YAML_NODE_PROPERTIES_PATTERN}(?P<value>\S[^\r\n]*)"
)
REPOSITORY_PATTERN = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
ACTION_REFERENCE_VALUE_PATTERN = re.compile(r"[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+")
SHA_PATTERN = re.compile(r"[0-9a-f]{40}")
RELEASE_TAG_PATTERN = re.compile(
    r"v(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?"
)
STABLE_ACTION_TAG_PATTERN = re.compile(r"v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)")
WORKFLOW_DIRECTORIES = (
    Path(".github/workflows"),
)
ALLOWED_ACTION_REPOSITORIES = frozenset(
    {
        "actions/attest",
        "actions/cache",
        "actions/checkout",
        "actions/dependency-review-action",
        "actions/download-artifact",
        "actions/labeler",
        "actions/setup-python",
        "actions/setup-node",
        "actions/stale",
        "actions/upload-artifact",
        "davidanson/markdownlint-cli2-action",
        "dependabot/fetch-metadata",
        "github/codeql-action",
        "googleapis/release-please-action",
        "lycheeverse/lychee-action",
        "ossf/scorecard-action",
        "peter-evans/create-pull-request",
    }
)
TAG_LIST_ACTION_REPOSITORIES = frozenset({"github/codeql-action"})


class DuplicateJsonMember(ValueError):
    """Raised when a GitHub API response contains ambiguous duplicate members."""


def unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Build a JSON object while rejecting duplicate member names."""
    document: dict[str, Any] = {}
    for key, value in pairs:
        if key in document:
            raise DuplicateJsonMember(f"duplicate JSON member {key!r}")
        document[key] = value
    return document


@dataclass(frozen=True)
class ActionRelease:
    """An immutable commit resolved from an action's stable release tag."""

    tag: str
    sha: str


def action_repository(action: str) -> str:
    """Return the owner/repository part of an action or sub-action reference."""
    return "/".join(action.split("/")[:2]).casefold()


def _is_link_or_reparse(path: Path) -> bool:
    """Return whether an existing path is a symlink or Windows reparse point."""
    if path.is_symlink():
        return True
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return False
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    attributes = getattr(metadata, "st_file_attributes", 0)
    return stat.S_ISLNK(metadata.st_mode) or bool(attributes & reparse_flag)


def _path_has_link_or_reparse(path: Path, repository_root: Path) -> bool:
    """Return whether a repository-relative path crosses a link-like boundary."""
    boundary = Path(os.path.abspath(repository_root))
    candidate = Path(os.path.abspath(path))
    try:
        relative = candidate.relative_to(boundary)
    except ValueError:
        return True
    current = boundary
    for part in (None, *relative.parts):
        if part is not None:
            current /= part
        if _is_link_or_reparse(current):
            return True
        if not os.path.lexists(current):
            break
    return False


def workflow_paths(
    repository_root: Path,
    workflow_directories: tuple[Path, ...] = WORKFLOW_DIRECTORIES,
) -> list[Path]:
    """Return every tracked workflow that carries a synchronized action pin."""
    repository_root = Path(os.path.abspath(repository_root))
    if not repository_root.is_dir() or _path_has_link_or_reparse(
        repository_root, repository_root
    ):
        raise ValueError(f"repository root is missing or unsafe: {repository_root}")
    paths: list[Path] = []
    for relative_directory in workflow_directories:
        if (
            relative_directory.is_absolute()
            or ".." in relative_directory.parts
            or not relative_directory.parts
        ):
            raise ValueError(
                f"workflow directory must be a safe relative path: {relative_directory}"
            )
        directory = repository_root / relative_directory
        if (
            _path_has_link_or_reparse(directory, repository_root)
            or not directory.is_dir()
        ):
            raise ValueError(
                f"workflow directory is missing or unsafe: {relative_directory}"
            )
        # glob may suppress a scan error and silently omit one file extension.
        try:
            with os.scandir(directory) as entries:
                for entry in entries:
                    if not os.path.normcase(entry.name).endswith((".yml", ".yaml")):
                        continue
                    path = directory / entry.name
                    if _path_has_link_or_reparse(path, repository_root):
                        raise ValueError(f"workflow file is unsafe: {path}")
                    if entry.is_file(follow_symlinks=False):
                        paths.append(path)
        except OSError as error:
            raise ValueError(
                f"could not enumerate workflow directory: {relative_directory}: {error}"
            ) from error
    if not paths:
        raise ValueError("no workflow files were found for action-pin synchronization")
    return sorted(paths)


def write_workflow_bytes(
    repository_root: Path, path: Path, content: str, expected_content: str
) -> None:
    """Write one workflow only when its validated source has not changed."""
    if _path_has_link_or_reparse(path, repository_root):
        raise ValueError(f"workflow file is unsafe: {path}")
    try:
        current_content = path.read_bytes().decode("utf-8")
    except (OSError, UnicodeError) as error:
        raise ValueError(
            f"could not reread workflow file before writing: {path}"
        ) from error
    if current_content != expected_content:
        raise ValueError(f"workflow file changed during synchronization: {path}")
    if _path_has_link_or_reparse(path, repository_root):
        raise ValueError(f"workflow file is unsafe: {path}")
    path.write_bytes(content.encode("utf-8"))


def block_scalar_content_ranges(content: str) -> tuple[tuple[int, int], ...]:
    """Return offsets occupied by YAML literal or folded scalar content."""
    return _flow_syntax_spans(content)[2]


def quoted_scalar_content_ranges(content: str) -> tuple[tuple[int, int], ...]:
    """Return offsets occupied by multiline YAML single- or double-quoted text."""
    return tuple((start, end) for kind, start, end in _flow_syntax_spans(content)[1]
                 if kind in {"'", '"'} and "\n" in content[start:end])


def _plain_scalar_end(lines: list[str], number: int, indentation: int) -> int:
    """Find indented plain continuations; comments terminate the scalar."""
    end_line = number + 1
    continued = False
    while end_line < len(lines):
        line = lines[end_line]
        if line.strip():
            if (len(line) - len(line.lstrip(" ")) <= indentation
                    or line.lstrip().startswith("#")):
                break
            continued = True
        end_line += 1
    return end_line if continued else number + 1


def _flow_syntax_spans(content: str) -> tuple[
    tuple[tuple[str, int, int], ...], tuple[tuple[str, int, int], ...],
    tuple[tuple[int, int], ...]
]:
    """Locate collections and scalar text in one shared lexical context."""
    ranges: list[tuple[str, int, int]] = []
    ignored: list[tuple[str, int, int]] = []
    block_ranges: list[tuple[int, int]] = []
    collections: list[tuple[str, int]] = []
    quote: str | None = None
    quote_start = 0
    plain = False
    index = 0
    closing = {"{": "}", "[": "]"}
    node_starts = {match.end() for match in FLOW_NODE_START_PATTERN.finditer(content)}
    properties = re.compile(YAML_NODE_PROPERTIES_PATTERN)
    lines = content.splitlines(keepends=True)
    line_starts: list[int] = []
    block_headers: dict[int, tuple[int, int]] = {}
    plain_headers: dict[int, tuple[int, int]] = {}
    offset = 0
    for number, line in enumerate(lines):
        line_starts.append(offset)
        header = BLOCK_SCALAR_HEADER_PATTERN.fullmatch(line)
        if header is not None:
            block_headers[offset + header.start("style")] = (number, len(header.group("indent")))
        header = BLOCK_MAPPING_VALUE_PATTERN.match(line)
        mapping = header is not None
        if header is None:
            header = BLOCK_SEQUENCE_VALUE_PATTERN.match(line)
        if header is not None:
            value = header.group("value")
            node_starts.add(offset + header.start("value"))
            if (value[0] not in "'\"[{]}|>&*!%@`#,"
                    and not (value[0] in "-?:" and (len(value) == 1 or value[1].isspace()))
                    and re.search(r"\s#", value) is None):
                sequence = header.group("sequence") or ""
                indentation = len(header.group("indent")) + (len(sequence) if mapping else sequence.rfind("-"))
                plain_headers[offset + header.start("value")] = (number, indentation)
        offset += len(line)
    while index < len(content):
        if quote is None and not collections and index in plain_headers:
            number, indentation = plain_headers[index]
            end_line = _plain_scalar_end(lines, number, indentation)
            end = line_starts[end_line] if end_line < len(lines) else len(content)
            if end_line > number + 1:
                ignored.append(("plain", index, end))
            index = end
            continue
        if quote is None and not collections and index in block_headers:
            number, indentation = block_headers[index]
            end_line = number + 1
            while end_line < len(lines):
                line = lines[end_line]
                if line.strip() and len(line) - len(line.lstrip(" ")) <= indentation:
                    break
                end_line += 1
            start = line_starts[number] + len(lines[number])
            end = line_starts[end_line] if end_line < len(lines) else len(content)
            block_ranges.append((start, end))
            index = end
            continue
        character = content[index]
        if quote == "'":
            if character == "'":
                if index + 1 < len(content) and content[index + 1] == "'":
                    index += 2
                    continue
                ignored.append((quote, quote_start, index + 1))
                quote = None
        elif quote == '"':
            if character == "\\":
                index += 2
                continue
            if character == '"':
                ignored.append((quote, quote_start, index + 1))
                quote = None
        elif character == "#" and (index == 0 or content[index - 1].isspace()):
            newline = content.find("\n", index)
            ignored.append(("#", index, newline if newline >= 0 else len(content)))
            if newline < 0:
                break
            index = newline
        elif collections and not plain and character in {"!", "&"}:
            node_properties = properties.match(content, index)
            if node_properties is not None and node_properties.end() > index:
                index = node_properties.end()
                continue
        elif character in {"'", '"'} and not plain and (collections or index in node_starts):
            quote = character
            quote_start = index
        elif character in closing and (collections or index in node_starts):
            collections.append((character, index))
            plain = False
        elif collections and character == closing[collections[-1][0]]:
            opening, start = collections.pop()
            ranges.append((opening, start, index + 1))
            plain = False
        elif collections:
            following = content[index + 1:index + 2]
            if (character == "," or (character == ":" and
                    (not plain or following.isspace() or following in {"[", "]", "{", "}", ","}))
                    or (character == "?" and not plain and following.isspace())):
                plain = False
            elif not character.isspace():
                # Mid-scalar quote characters are literal, not a new quoted node.
                plain = True
        index += 1
    if quote is not None:
        ignored.append((quote, quote_start, len(content)))
    return tuple(ranges), tuple(ignored), tuple(block_ranges)


def flow_collection_spans(content: str) -> tuple[tuple[str, int, int], ...]:
    """Locate flow nodes, without treating punctuation inside block scalars as nodes."""
    return _flow_syntax_spans(content)[0]


def flow_collection_content_ranges(content: str) -> tuple[tuple[int, int], ...]:
    """Return ranges within multiline YAML flow collections."""
    return tuple((start + 1, end - 1) for _, start, end in flow_collection_spans(content)
                 if "\n" in content[start:end])


def _matches_in_flow_mappings(
    pattern: re.Pattern[str], content: str
) -> tuple[re.Match[str], ...]:
    """Return flow-field matches that lie in a balanced flow mapping."""
    collections, ignored, blocks = _flow_syntax_spans(content)
    scalar_ranges = (
        *blocks,
        *((start, end) for _, start, end in ignored),
    )
    mapping_ranges = tuple((start, end) for opening, start, end in collections if opening == "{")
    return tuple(
        match
        for match in pattern.finditer(content)
        if any(
            start <= match.start()
            and match.end() <= end
            and (match.start() == 0 or content[match.start() - 1] != "{")
            for start, end in mapping_ranges
        )
        and not any(start <= match.start() < end for start, end in scalar_ranges)
    )


def _matches_outside_block_scalars(
    pattern: re.Pattern[str], content: str
) -> tuple[re.Match[str], ...]:
    """Return regex matches that are not embedded in YAML scalar text."""
    collections, ignored, blocks = _flow_syntax_spans(content)
    ranges = (*blocks,
              *((start, end) for kind, start, end in ignored
                if kind == "plain" or (kind in {"'", '"'} and "\n" in content[start:end])),
              *((start + 1, end - 1) for _, start, end in collections
                if "\n" in content[start:end]))
    return tuple(
        match
        for match in pattern.finditer(content)
        if not any(start <= match.start() + len(match.group()) - len(match.group().lstrip()) < end
                   for start, end in ranges)
    )


def normalized_double_quoted_scalar(value: str) -> str:
    """Return the logical value of a double-quoted YAML scalar."""
    escapes = {
        "0": "\0",
        "a": "\a",
        "b": "\b",
        "t": "\t",
        "n": "\n",
        "v": "\v",
        "f": "\f",
        "r": "\r",
        "e": "\x1b",
        " ": " ",
        '"': '"',
        "/": "/",
        "\\": "\\",
        "N": "\u0085",
        "_": "\u00a0",
        "L": "\u2028",
        "P": "\u2029",
    }

    def decode_escape(match: re.Match[str]) -> str:
        escape = match.group(0)[1:]
        if len(escape) == 1:
            return escapes[escape]
        return chr(int(escape[1:], 16))

    return re.sub(
        YAML_DOUBLE_QUOTED_ESCAPE_PATTERN,
        decode_escape,
        re.sub(YAML_DOUBLE_QUOTED_CONTINUATION_PATTERN, "", value),
    )


def normalized_uses_reference(match: re.Match[str]) -> str:
    """Return a ``uses`` value, decoding only valid double-quoted escapes."""
    reference = match.group("reference")
    return (
        normalized_double_quoted_scalar(reference)
        if match.groupdict().get("quote") == '"'
        else reference
    )


def normalized_action_pin_part(match: re.Match[str], part: str) -> str:
    """Return one pin field, decoding only valid double-quoted escapes."""
    value = match.group(part)
    return (
        normalized_double_quoted_scalar(value)
        if match.groupdict().get("quote") == '"'
        else value
    )


def action_pin_has_valid_scalar_style(match: re.Match[str]) -> bool:
    """Validate the decoded action and SHA, rejecting non-YAML escapes."""
    quote = match.groupdict().get("quote")
    if quote != '"' and ("\\" in match.group("action") or "\\" in match.group("sha")):
        return False
    return (
        ACTION_REFERENCE_VALUE_PATTERN.fullmatch(
            normalized_action_pin_part(match, "action")
        )
        is not None
        and SHA_PATTERN.fullmatch(normalized_action_pin_part(match, "sha").casefold())
        is not None
    )


def action_pin_matches(content: str) -> tuple[re.Match[str], ...]:
    """Return immutable direct or alias-backed action pins outside scalar text."""
    plain_ranges = [(start, end) for kind, start, end in _flow_syntax_spans(content)[1]
                    if kind == "plain"]
    matches = {
        (match.start(), match.end()): match
        for match in _matches_outside_block_scalars(ACTION_PIN_PATTERN, content)
    }
    matches.update(
        {
            (match.start(), match.end()): match
            for match in _matches_outside_block_scalars(
                EXPLICIT_ACTION_PIN_PATTERN, content
            )
        }
    )
    matches.update(
        {
            (match.start(), match.end()): match
            for match in _matches_outside_block_scalars(
                CONTINUED_DOUBLE_QUOTED_ACTION_PIN_PATTERN, content
            )
            if SHA_PATTERN.fullmatch(normalized_action_pin_part(match, "sha"))
            is not None
        }
    )
    matches.update(
        {
            (match.start(), match.end()): match
            for match in _matches_outside_block_scalars(
                EXPLICIT_BLOCK_ACTION_PIN_PATTERN, content
            )
        }
    )
    matches.update(
        {
            (match.start(), match.end()): match
            for match in _matches_outside_block_scalars(
                BLOCK_SCALAR_ACTION_PIN_PATTERN, content
            )
        }
    )
    flow_matches = _matches_outside_block_scalars(FLOW_ACTION_PIN_PATTERN, content)
    matches.update({(match.start(), match.end()): match for match in flow_matches})
    for match in _matches_in_flow_mappings(FLOW_INLINE_ACTION_PIN_PATTERN, content):
        if not any(
            flow_match.start() <= match.start() < flow_match.end()
            for flow_match in flow_matches
        ):
            matches[(match.start(), match.end())] = match
    aliases = referenced_action_aliases(content)
    continued_anchored_matches = _matches_outside_block_scalars(
        CONTINUED_ANCHORED_ACTION_PIN_PATTERN, content
    )
    for match in continued_anchored_matches:
        if match.group("anchor") in aliases:
            matches[(match.start(), match.end())] = match
    for match in _matches_in_flow_mappings(FLOW_ANCHORED_ACTION_PIN_PATTERN, content):
        if match.group("anchor") in aliases and not any(
            existing.start() <= match.start() < existing.end()
            for existing in matches.values()
        ):
            matches[(match.start(), match.end())] = match
    for match in _matches_outside_block_scalars(ANCHORED_ACTION_PIN_PATTERN, content):
        if match.group("anchor") in aliases and not any(
            continued.start() <= match.start() < continued.end()
            for continued in continued_anchored_matches
        ):
            matches[(match.start(), match.end())] = match
    for match in _matches_outside_block_scalars(
        ANCHORED_BLOCK_SCALAR_ACTION_PIN_PATTERN, content
    ):
        if match.group("anchor") in aliases:
            matches[(match.start(), match.end())] = match
    return tuple(
        match
        for _, match in sorted(matches.items())
        if action_pin_has_valid_scalar_style(match)
        and not any(start <= match.start("action") < end for start, end in plain_ranges)
    )


def workflow_uses_matches(content: str) -> tuple[re.Match[str], ...]:
    """Return workflow ``uses`` mappings, excluding YAML scalar content."""
    continued_matches = _matches_outside_block_scalars(
        CONTINUED_DOUBLE_QUOTED_USES_PATTERN, content
    )
    matches = {
        (match.start(), match.end()): match
        for match in _matches_outside_block_scalars(USES_PATTERN, content)
        if match.group("reference")[0] not in {"|", ">"}
        and not any(
            continued.start() <= match.start() < continued.end()
            for continued in continued_matches
        )
    }
    matches.update({(match.start(), match.end()): match for match in continued_matches})
    matches.update(
        {
            (match.start(), match.end()): match
            for match in _matches_outside_block_scalars(EXPLICIT_USES_PATTERN, content)
        }
    )
    matches.update(
        {
            (match.start(), match.end()): match
            for match in _matches_outside_block_scalars(
                EXPLICIT_BLOCK_USES_PATTERN, content
            )
        }
    )
    matches.update(
        {
            (match.start(), match.end()): match
            for match in _matches_outside_block_scalars(
                BLOCK_SCALAR_USES_PATTERN, content
            )
        }
    )
    flow_matches = _matches_outside_block_scalars(FLOW_USES_PATTERN, content)
    matches.update({(match.start(), match.end()): match for match in flow_matches})
    for match in _matches_in_flow_mappings(FLOW_INLINE_USES_PATTERN, content):
        if not any(
            flow_match.start() <= match.start() < flow_match.end()
            for flow_match in flow_matches
        ):
            matches[(match.start(), match.end())] = match
    return tuple(match for _, match in sorted(matches.items()))


def aliased_mapping_key_matches(content: str) -> tuple[re.Match[str], ...]:
    """Return mapping keys that rely on a YAML alias rather than literal text."""
    matches = {
        (match.start(), match.end()): match
        for match in _matches_outside_block_scalars(ALIAS_MAPPING_KEY_PATTERN, content)
    }
    matches.update(
        {
            (match.start(), match.end()): match
            for match in _matches_outside_block_scalars(
                EXPLICIT_ALIAS_MAPPING_KEY_PATTERN, content
            )
        }
    )
    matches.update(
        {
            (match.start(), match.end()): match
            for match in _matches_in_flow_mappings(
                FLOW_ALIAS_MAPPING_KEY_PATTERN, content
            )
        }
    )
    return tuple(match for _, match in sorted(matches.items()))


def referenced_action_aliases(content: str) -> frozenset[str]:
    """Return YAML aliases that are consumed by workflow ``uses`` mappings."""
    return frozenset(
        match.group("reference")[1:]
        for match in workflow_uses_matches(content)
        if match.groupdict().get("quote") == ""
        and match.group("reference").startswith("*")
    )


def anchored_action_reference_matches(content: str) -> tuple[re.Match[str], ...]:
    """Return action-valued YAML anchors referenced by workflow ``uses`` mappings."""
    aliases = referenced_action_aliases(content)
    continued_matches = _matches_outside_block_scalars(
        CONTINUED_ANCHORED_ACTION_REFERENCE_PATTERN, content
    )
    block_matches = _matches_outside_block_scalars(
        ANCHORED_BLOCK_SCALAR_ACTION_REFERENCE_PATTERN, content
    )
    matches = {
        (match.start(), match.end()): match
        for match in _matches_outside_block_scalars(
            ANCHORED_ACTION_REFERENCE_PATTERN, content
        )
        if match.group("anchor") in aliases
        and match.group("reference")[0] not in {"|", ">"}
        and not any(
            continued.start() <= match.start() < continued.end()
            for continued in continued_matches
        )
    }
    matches.update(
        {
            (match.start(), match.end()): match
            for match in continued_matches
            if match.group("anchor") in aliases
        }
    )
    matches.update(
        {
            (match.start(), match.end()): match
            for match in block_matches
            if match.group("anchor") in aliases
        }
    )
    for match in _matches_in_flow_mappings(
        FLOW_ANCHORED_ACTION_REFERENCE_PATTERN, content
    ):
        if match.group("anchor") in aliases:
            # The block-style matcher can also consume an entire inline mapping.
            # Prefer its precise flow value rather than retaining two targets.
            matches = {
                key: existing for key, existing in matches.items()
                if not (existing.start() <= match.start() < existing.end())
            }
            matches[(match.start(), match.end())] = match
    return tuple(match for _, match in sorted(matches.items()))


def auditable_action_repositories(path: Path, content: str) -> set[str]:
    """Collect every externally hosted action pinned to an immutable SHA."""
    if aliased_mapping_key_matches(content):
        raise ValueError(f"workflow mapping keys must not use YAML aliases: {path}")
    repositories: set[str] = set()
    pins = {
        normalized_uses_reference(match)
        for match in workflow_uses_matches(content)
        if not (
            match.groupdict().get("quote") == ""
            and match.group("reference").startswith("*")
        )
    }
    pins.update(
        normalized_uses_reference(match)
        for match in anchored_action_reference_matches(content)
    )
    pinned_references = {
        f"{normalized_action_pin_part(match, 'action')}@{normalized_action_pin_part(match, 'sha')}"
        for match in action_pin_matches(content)
    }
    for reference in pins:
        if reference.startswith(("./", "docker://")):
            continue
        if reference not in pinned_references:
            raise ValueError(f"workflow action is not pinned to a full SHA: {path}")
        action = reference.rsplit("@", 1)[0]
        repository = action_repository(action)
        repositories.add(repository)
    return repositories


def action_repositories(path: Path, content: str) -> set[str]:
    """Collect only reviewed action repositories for the write-capable synchronizer."""
    repositories = auditable_action_repositories(path, content)
    for repository in repositories:
        if repository not in ALLOWED_ACTION_REPOSITORIES:
            raise ValueError(
                f"workflow action is not in the synchronization allowlist: {repository}"
            )
    return repositories


class RejectRedirectHandler(HTTPRedirectHandler):
    """Reject redirects so the workflow token never leaves GitHub's API host."""

    def redirect_request(
        self,
        request: Any,
        response: Any,
        code: int,
        message: str,
        headers: Any,
        new_url: str,
    ) -> Request | None:
        raise ValueError("GitHub API redirects are not allowed")


GITHUB_API_OPENER = build_opener(RejectRedirectHandler())


class GitHubReleaseClient:
    """Load stable release tags and immutable commits from GitHub's REST API."""

    def __init__(self, token: str, opener: Callable[..., Any] | None = None) -> None:
        if not token:
            raise ValueError("GITHUB_TOKEN is required to synchronize action pins")
        self.token = token
        self.opener = opener or GITHUB_API_OPENER.open

    def _get_document(self, path: str) -> Any:
        """Fetch one JSON document with the workflow token and an explicit timeout."""
        request = Request(
            f"{GITHUB_API_URL}{path}",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        try:
            with self.opener(request, timeout=30) as response:
                payload = response.read(MAX_RESPONSE_BYTES + 1)
        except (OSError, UnicodeError) as error:
            raise ValueError(
                f"GitHub API request failed for {path}: {error}"
            ) from error
        if len(payload) > MAX_RESPONSE_BYTES:
            raise ValueError(f"GitHub API response exceeds the size limit for {path}")
        try:
            return json.loads(
                payload.decode("utf-8"), object_pairs_hook=unique_json_object
            )
        except (
            UnicodeError,
            ValueError,
            RecursionError,
        ) as error:
            raise ValueError(
                f"GitHub API request failed for {path}: {error}"
            ) from error

    def get_json(self, path: str) -> dict[str, Any]:
        """Fetch one bounded GitHub API object with the workflow token."""
        document = self._get_document(path)
        if not isinstance(document, dict):
            raise ValueError(f"GitHub API response is not an object for {path}")
        return document

    def get_json_list(self, path: str) -> list[dict[str, Any]]:
        """Fetch a bounded GitHub API list whose entries are all objects."""
        document = self._get_document(path)
        if (
            not isinstance(document, list)
            or len(document) > 100
            or any(not isinstance(item, dict) for item in document)
        ):
            raise ValueError(
                f"GitHub API response is not a bounded object list for {path}"
            )
        return document

    def latest_action_tag(self, repository: str) -> ActionRelease:
        """Resolve the latest stable action tag when releases contain non-action tags."""
        releases: list[tuple[tuple[int, int, int], ActionRelease]] = []
        for page in range(1, MAX_ACTION_TAG_PAGES + 1):
            tags = self.get_json_list(
                f"/repos/{repository}/tags?per_page=100&page={page}"
            )
            for tag_document in tags:
                tag = tag_document.get("name")
                commit = tag_document.get("commit")
                match = (
                    STABLE_ACTION_TAG_PATTERN.fullmatch(tag)
                    if isinstance(tag, str)
                    else None
                )
                sha = commit.get("sha") if isinstance(commit, dict) else None
                if (
                    match is not None
                    and isinstance(tag, str)
                    and isinstance(sha, str)
                    and SHA_PATTERN.fullmatch(sha)
                ):
                    version: tuple[int, int, int] = (
                        int(match.group(1)),
                        int(match.group(2)),
                        int(match.group(3)),
                    )
                    releases.append(
                        (
                            version,
                            ActionRelease(tag=tag, sha=sha),
                        )
                    )
            if len(tags) < 100:
                break
        else:
            raise ValueError(
                f"action tag inventory exceeds {MAX_ACTION_TAG_PAGES} pages: {repository}"
            )
        if not releases:
            raise ValueError(f"no stable action tag could be resolved: {repository}")
        return max(releases, key=lambda item: item[0])[1]

    def latest_release(self, repository: str) -> ActionRelease:
        """Resolve the stable latest release tag to its immutable commit SHA."""
        if REPOSITORY_PATTERN.fullmatch(repository) is None:
            raise ValueError(f"invalid action repository: {repository}")
        if repository in TAG_LIST_ACTION_REPOSITORIES:
            return self.latest_action_tag(repository)
        release = self.get_json(f"/repos/{repository}/releases/latest")
        tag = release.get("tag_name")
        if not isinstance(tag, str) or RELEASE_TAG_PATTERN.fullmatch(tag) is None:
            raise ValueError(f"latest action release has an invalid tag: {repository}")
        reference = self.get_json(
            f"/repos/{repository}/git/ref/tags/{quote(tag, safe='')}"
        )
        object_document = reference.get("object")
        if not isinstance(object_document, dict):
            raise ValueError(f"latest action release has no tag object: {repository}")
        tag_depth = 0
        while object_document.get("type") == "tag":
            if tag_depth >= MAX_ANNOTATED_TAG_DEPTH:
                raise ValueError(
                    f"latest action release tag nesting exceeds "
                    f"{MAX_ANNOTATED_TAG_DEPTH}: {repository}"
                )
            sha = object_document.get("sha")
            if not isinstance(sha, str) or SHA_PATTERN.fullmatch(sha) is None:
                break
            object_document = self.get_json(f"/repos/{repository}/git/tags/{sha}").get(
                "object"
            )
            if not isinstance(object_document, dict):
                raise ValueError(f"latest action release tag is invalid: {repository}")
            tag_depth += 1
        object_type = object_document.get("type")
        sha = object_document.get("sha")
        if (
            object_type != "commit"
            or not isinstance(sha, str)
            or SHA_PATTERN.fullmatch(sha) is None
        ):
            raise ValueError(
                f"latest action release does not resolve to a commit: {repository}"
            )
        return ActionRelease(tag=tag, sha=sha)


def synchronize_action_pins(
    repository_root: Path,
    release_lookup: Callable[[str], ActionRelease],
    *,
    write: bool,
    workflow_directories: tuple[Path, ...] = WORKFLOW_DIRECTORIES,
) -> list[Path]:
    """Update all allowed action pins after resolving every release."""
    contents = {
        path: path.read_bytes().decode("utf-8")
        for path in workflow_paths(repository_root, workflow_directories)
    }
    repositories = sorted(
        {
            repository
            for path, content in contents.items()
            for repository in action_repositories(path, content)
        }
    )
    releases = {repository: release_lookup(repository) for repository in repositories}

    def replace(match: re.Match[str]) -> str:
        action = normalized_action_pin_part(match, "action")
        release = releases[action_repository(action)]
        if match.groupdict().get("flow_inline") is not None:
            if normalized_action_pin_part(match, "sha").casefold() == release.sha:
                return match.group(0)
            quote = match.group("quote")
            return f"{match.group('prefix')}{quote}{action}@{release.sha}{quote}"
        comment = match.group("comment")
        flow_suffix = match.groupdict().get("flow_suffix") or ""
        if flow_suffix:
            if normalized_action_pin_part(
                match, "sha"
            ).casefold() == release.sha and comment.strip() == (f"# {release.tag}"):
                return match.group(0)
            prefix = comment[: comment.index("#")] if "#" in comment else " "
            quote = match.group("quote")
            return (
                f"{match.group('prefix')}{quote}{action}@{release.sha}{quote}"
                f"{flow_suffix}{prefix}# {release.tag}"
            )
        if match.re in (BLOCK_SCALAR_ACTION_PIN_PATTERN, ANCHORED_BLOCK_SCALAR_ACTION_PIN_PATTERN):
            if normalized_action_pin_part(match, "sha").casefold() == release.sha:
                return match.group(0)
            quote = match.group("quote")
            # A block scalar treats a hash as part of the action reference.
            return (
                f"{match.group('prefix')}{quote}{action}@{release.sha}{quote}{comment}"
            )
        if normalized_action_pin_part(
            match, "sha"
        ).casefold() == release.sha and comment.strip() == (f"# {release.tag}"):
            return match.group(0)
        prefix = comment[: comment.index("#")] if "#" in comment else " "
        quote = match.group("quote")
        return (
            f"{match.group('prefix')}{quote}{action}@{release.sha}{quote}"
            f"{prefix}# {release.tag}"
        )

    replacements: dict[Path, str] = {}
    for path, content in contents.items():
        replacement_parts: list[str] = []
        previous_end = 0
        for match in action_pin_matches(content):
            replacement_parts.extend(
                (content[previous_end : match.start()], replace(match))
            )
            previous_end = match.end()
        replacement_parts.append(content[previous_end:])
        replacements[path] = "".join(replacement_parts)
    changed = [path for path in contents if replacements[path] != contents[path]]
    if write:
        for path in changed:
            write_workflow_bytes(
                repository_root, path, replacements[path], contents[path]
            )
    return changed


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse the repository root, optional workflow scope, and write authorization."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, default=Path("."))
    parser.add_argument(
        "--workflow-directory",
        action="append",
        type=Path,
        help="Relative workflow directory to synchronize; repeat to include more.",
    )
    parser.add_argument("--write", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Synchronize pins and print the changed paths for the PR creator."""
    arguments = parse_args(argv)
    try:
        client = GitHubReleaseClient(os.environ.get("GITHUB_TOKEN", ""))
        changed = synchronize_action_pins(
            arguments.repository_root.resolve(),
            client.latest_release,
            write=arguments.write,
            workflow_directories=(
                tuple(arguments.workflow_directory)
                if arguments.workflow_directory is not None
                else WORKFLOW_DIRECTORIES
            ),
        )
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    if changed:
        for path in changed:
            print(path.as_posix())
    else:
        print("Action pins are already current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
