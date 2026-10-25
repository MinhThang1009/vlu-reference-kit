"""Inspect dependency metadata at the exact Action commits, without executing it."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha1, sha256
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, build_opener
import base64
import argparse
import json
import os
import re

import sync_action_pins

MAX_BYTES = 4 * 1024 * 1024
MAX_ACTIONS = 32
MAX_PACKAGES = 256
METADATA = {"package.json", "package-lock.json", "npm-shrinkwrap.json", "yarn.lock",
            "pnpm-lock.yaml", "requirements.txt", "requirements.lock", "pyproject.toml",
            "poetry.lock", "uv.lock", "go.mod", "go.sum", "Cargo.toml", "Cargo.lock",
            "Gemfile", "Gemfile.lock", "Dockerfile", "action.yml", "action.yaml"}
SUPPORTED_METADATA = {"package.json", "package-lock.json", "npm-shrinkwrap.json",
                      "action.yml", "action.yaml"}
NPM_NAME = re.compile(r"(?:@[a-z0-9][a-z0-9_.-]*/)?[a-z0-9][a-z0-9_.-]*\Z")
NPM_OPENER = build_opener(sync_action_pins.RejectRedirectHandler())


def latest_npm(package: str) -> str:
    """Read registry latest as metadata only; never install unreviewed dependencies."""
    if NPM_NAME.fullmatch(package) is None:
        raise ValueError(f"Unsupported npm package name: {package}")
    request = Request("https://registry.npmjs.org/" + quote(package, safe="") + "/latest",
                      headers={"Accept": "application/json", "Cache-Control": "no-cache"})
    with NPM_OPENER.open(request, timeout=25) as response:
        raw = response.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("npm metadata exceeds the response limit")
    document = json.loads(raw.decode("utf-8"), object_pairs_hook=sync_action_pins.unique_json_object)
    if not isinstance(document, dict):
        raise ValueError("npm latest metadata is not an object")
    version = document.get("version")
    if not isinstance(version, str) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?", version):
        raise ValueError(f"Invalid npm latest version: {package}")
    return version


def source_file(client, repository: str, entry: dict, sha: str) -> bytes:
    """Verify GitHub content against its Git object ID, including large-file fallback."""
    path = quote(entry["path"], safe="/")
    document = client.get_json(f"/repos/{repository}/contents/{path}?ref={sha}")
    if document.get("size", 0) > MAX_BYTES:
        raise ValueError(f"Action metadata exceeds limit: {entry['path']}")
    if document.get("encoding") != "base64" or not document.get("content"):
        document = client.get_json(f"/repos/{repository}/git/blobs/{entry['sha']}")
    if document.get("encoding") != "base64" or not isinstance(document.get("content"), str):
        raise ValueError("Unsupported GitHub content encoding")
    raw = base64.b64decode("".join(document["content"].split()), validate=True)
    if len(raw) > MAX_BYTES or sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest() != entry["sha"]:
        raise ValueError("Action metadata does not match its Git object")
    return raw


def inspect_npm(files: dict[str, bytes]) -> dict:
    """Inventory every npm lock entry and direct constraint, without semver guesses."""
    unsupported = sorted(set(files) & (METADATA - SUPPORTED_METADATA))
    if unsupported:
        raise ValueError("Dependency metadata requires unsupported format review: " + ", ".join(unsupported))
    if "package.json" not in files:
        raise ValueError("No npm manifest; this Action's dependency format requires explicit support")
    locks = sorted(set(files) & {"package-lock.json", "npm-shrinkwrap.json"})
    if not locks:
        raise ValueError("No supported npm lockfile; other lock formats are inventory-only")
    if len(locks) != 1:
        raise ValueError("Multiple lockfiles require explicit resolution; coverage incomplete")
    lock_name = locks[0]
    package = json.loads(files["package.json"], object_pairs_hook=sync_action_pins.unique_json_object)
    lock = json.loads(files[lock_name], object_pairs_hook=sync_action_pins.unique_json_object)
    if not isinstance(package, dict) or not isinstance(lock, dict):
        raise ValueError("npm manifest and lock must be objects")
    manager = package.get("packageManager")
    if manager is not None and (not isinstance(manager, str) or not manager.startswith("npm@")):
        raise ValueError("Declared packageManager is not a supported npm manager")
    packages = lock["packages"]
    if not isinstance(packages, dict) or len(packages) > 10000:
        raise ValueError("Invalid or oversized npm lock inventory")
    root = packages[""]
    if not isinstance(root, dict):
        raise ValueError("npm lock root must be an object")
    if package.get("workspaces") or root.get("workspaces") or any(
            name and not name.startswith("node_modules/") for name in packages):
        raise ValueError("Workspace or local package manifests require additional traversal; coverage incomplete")
    for name, item in packages.items():
        if not isinstance(item, dict):
            raise ValueError(f"Invalid npm lock entry: {name}")
        if "version" in item and (not isinstance(item["version"], str) or
                                  not item["version"].strip() or item["version"] != item["version"].strip()):
            raise ValueError(f"Invalid npm locked version: {name}")
    direct = []
    for kind in ("dependencies", "devDependencies", "optionalDependencies", "peerDependencies"):
        declared = package.get(kind, {})
        if not isinstance(declared, dict) or root.get(kind, {}) != declared:
            raise ValueError(f"Manifest and lock root disagree: {kind}")
        for name, constraint in declared.items():
            if len(direct) >= MAX_PACKAGES or not isinstance(constraint, str):
                raise ValueError("Invalid or oversized direct dependency inventory")
            entry = packages.get("node_modules/" + name, {})
            if (any(character in constraint for character in ":/\\")
                    or constraint.startswith(".") or constraint.lower().endswith((".tgz", ".tar.gz", ".tar"))
                    or entry.get("name", name) != name):
                raise ValueError(f"Dependency requires source-specific alias/Git/URL/local inspection: {name}; coverage incomplete")
            locked = entry.get("version")
            direct.append({"name": name, "kind": kind, "constraint": constraint,
                           "locked": locked, "range_compatibility": "not_evaluated"})
    inventory = {}
    for name, item in packages.items():
        if name:
            inventory[name] = {k: item[k] for k in ("version", "resolved", "integrity", "link", "dev", "optional") if k in item}
    return {"package_name": package.get("name"), "package_version": package.get("version"),
            "root_metadata_differences": [key for key in ("name", "version", "engines") if package.get(key) != root.get(key)],
            "lockfile": lock_name, "lockfile_version": lock.get("lockfileVersion"),
            "direct": direct, "locked_packages": inventory,
            "transitive_latest_versions_checked": False,
            "bundle_independently_rebuilt": False}


def node_runtime(files: dict[str, bytes]) -> str:
    """Recognize simple block-form runs metadata, never examples in scalar text."""
    manifest = files.get("action.yml", files.get("action.yaml", b"")).decode("utf-8")
    sections = sync_action_pins._matches_outside_block_scalars(
        re.compile(r"(?m)^[^ \t\r\n#][^\r\n]*"), manifest)
    runs = [index for index, section in enumerate(sections)
            if re.match(r"(?:runs|'runs'|\"runs\")[ \t]*:", section.group())]
    if len(runs) != 1 or not re.fullmatch(r"runs[ \t]*:(?:[ \t]+#[^\r\n]*)?[ \t]*\r?", sections[runs[0]].group()):
        raise ValueError("Unsupported or ambiguous runs metadata; coverage incomplete")
    index = runs[0]
    start = sections[index].end()
    end = sections[index + 1].start() if index + 1 < len(sections) else len(manifest)
    fields = [match for match in sync_action_pins._matches_outside_block_scalars(
        re.compile(r"(?m)^(?P<indent> +)(?P<key>[^\s:#][^:\r\n]*):(?P<value>[^\r\n]*)"), manifest)
        if start <= match.start() < end]
    if not fields:
        raise ValueError("Missing runs fields; coverage incomplete")
    indent = min(len(match.group("indent")) for match in fields)
    using = [match for match in fields if len(match.group("indent")) == indent
             and match.group("key").strip() == "using"]
    value = using[0].group("value") if len(using) == 1 else ""
    runtime = re.fullmatch(r"[ \t]*(?P<quote>['\"]?)(?P<runtime>node20|node24)(?P=quote)(?:[ \t]+#[^\r\n]*)?[ \t]*\r?", value)
    if runtime is None or any(match.group("key").strip() in ("uses", "steps") for match in fields):
        raise ValueError("Non-Node or nested Action requires additional dependency traversal; coverage incomplete")
    return runtime.group("runtime")


def inspect_actions(root: Path, directories: tuple[Path, ...], client, npm_lookup=latest_npm) -> dict:
    """Cover every current workflow reference; unsupported metadata is an explicit error."""
    refs = {}
    local = set()
    unsupported = {}
    for path in sync_action_pins.workflow_paths(root, directories):
        text = path.read_text(encoding="utf-8")
        sync_action_pins.auditable_action_repositories(path, text)
        for match in sync_action_pins.action_pin_matches(text):
            action = sync_action_pins.normalized_action_pin_part(match, "action")
            sha = sync_action_pins.normalized_action_pin_part(match, "sha")
            refs.setdefault((action, sha), []).append(path.relative_to(root).as_posix())
        anchors = {}
        for match in sync_action_pins.anchored_action_reference_matches(text):
            anchors.setdefault(match.group("anchor"), []).append(match)
        for match in sync_action_pins.workflow_uses_matches(text):
            reference = sync_action_pins.normalized_uses_reference(match)
            error = None
            if match.groupdict().get("quote") == "" and reference.startswith("*"):
                targets = anchors.get(reference[1:], [])
                if len(targets) == 1:
                    reference = sync_action_pins.normalized_uses_reference(targets[0])
                else:
                    error = "Action alias cannot be resolved unambiguously; coverage incomplete"
            if reference.startswith("./"):
                local.add(reference)
            elif reference.startswith("docker://"):
                error = "Container Action requires separate image dependency inspection; coverage incomplete"
            if error:
                record = unsupported.setdefault(reference, {"action": reference, "sha": None,
                    "metadata": [], "workflows": set(), "status": "indeterminate", "error": error})
                record["workflows"].add(path.relative_to(root).as_posix())
    if len(refs) + len(local) + len(unsupported) > MAX_ACTIONS:
        raise ValueError("Action dependency inventory exceeds its action limit")
    records = [{**record, "workflows": sorted(record["workflows"])}
               for _, record in sorted(unsupported.items())]
    for (action, sha), workflows in sorted(refs.items()):
        record = {"action": action, "sha": sha, "workflows": sorted(set(workflows)), "metadata": []}
        try:
            parts = action.split("/");repository = "/".join(parts[:2]);subpath = "/".join(parts[2:])
            if subpath:
                raise ValueError("Action subpath requires separate manifest/lock resolution; coverage incomplete")
            entries = {}
            for directory in dict.fromkeys(["", subpath]):
                suffix = "/" + quote(directory, safe="/") if directory else ""
                listing = client.get_json_list(f"/repos/{repository}/contents{suffix}?ref={sha}")
                for entry in listing:
                    if entry.get("name") in METADATA and entry.get("type") == "file":
                        entries[entry["name"]] = entry
            files = {}
            for name, entry in sorted(entries.items()):
                raw = source_file(client, repository, entry, sha)
                files[name] = raw
                record["metadata"].append({"path": entry["path"], "git_blob": entry["sha"],
                    "bytes": len(raw), "sha256": sha256(raw).hexdigest(),
                    "url": f"https://github.com/{repository}/blob/{sha}/{entry['path']}"})
            record["runtime"] = node_runtime(files)
            record.update(inspect_npm(files), status="inspected")
        except (OSError, ValueError, KeyError, TypeError, RecursionError) as error:
            record.update(status="indeterminate", error=str(error))
        records.append(record)
    for action in sorted(local):
        record = {"action": action, "sha": "local-working-tree", "metadata": []}
        try:
            directory = root / action[2:]
            if sync_action_pins._path_has_link_or_reparse(directory, root) or not directory.resolve().is_relative_to(root.resolve()):
                raise ValueError("Unsafe local Action path")
            files = {}
            for path in directory.iterdir():
                if path.name in METADATA and path.is_file():
                    if sync_action_pins._path_has_link_or_reparse(path, root) or path.stat().st_size > MAX_BYTES:
                        raise ValueError("Unsafe local Action metadata")
                    files[path.name] = path.read_bytes()
                    record["metadata"].append({"path": path.relative_to(root).as_posix(),
                        "sha256": sha256(files[path.name]).hexdigest(), "bytes": len(files[path.name])})
            record.update(inspect_npm(files), status="inspected", runtime=node_runtime(files))
        except (OSError, ValueError, KeyError, TypeError, RecursionError) as error:
            record.update(status="indeterminate", error=str(error))
        records.append(record)
    names = sorted({d["name"] for record in records for d in record.get("direct", [])})
    if len(names) > MAX_PACKAGES:
        raise ValueError("Action dependency inventory exceeds its package lookup limit")
    def lookup(name):
        try:return name, {"version": npm_lookup(name)}
        except (OSError, ValueError, RecursionError) as error:return name, {"error": str(error)}
    with ThreadPoolExecutor(max_workers=4) as pool:
        latest = dict(pool.map(lookup, names))
    for record in records:
        for direct in record.get("direct", []):
            lookup_result = latest[direct["name"]]
            direct.update(registry_latest=lookup_result.get("version"),
                          registry_error=lookup_result.get("error"))
    return {"checked-at": datetime.now(timezone.utc).isoformat(),
            "github-sha": os.environ.get("GITHUB_SHA"),
            "actions": records, "unique_registry_queries": len(names),
            "scope": "Exact Action manifest/lock metadata and all locked entries; registry latest for direct dependencies only. No remote dependency is executed, no bundle rebuild or transitive latest/vulnerability claim."}


def inspection_complete(report: dict) -> bool:
    return all(record["status"] == "inspected" and
               all(d["registry_error"] is None and d["locked"] is not None
                   for d in record.get("direct", [])) for record in report["actions"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, default=Path("."))
    parser.add_argument("--json-output", type=Path, required=True)
    arguments = parser.parse_args()
    client = sync_action_pins.GitHubReleaseClient(os.environ.get("GITHUB_TOKEN", ""))
    report = inspect_actions(arguments.repository_root.resolve(), (Path(".github/workflows"),), client)
    arguments.json_output.parent.mkdir(parents=True, exist_ok=True)
    arguments.json_output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    complete = inspection_complete(report)
    print(f"Inspected {len(report['actions'])} Actions; metadata/registry coverage complete: {complete}.")
    return 0 if complete else 2


if __name__ == "__main__":
    raise SystemExit(main())
