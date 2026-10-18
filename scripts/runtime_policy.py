"""Đọc policy runtime và phát hiện bản ổn định chưa được review."""

from pathlib import Path
import json
import sys


def main() -> int:
    policy = json.loads((Path(__file__).resolve().parents[1] / ".github/runtime-support.json").read_text(encoding="utf-8"))
    if sys.argv[1:] == ["matrix"]:
        print("matrix=" + json.dumps({"python": policy["python_versions"], "os": policy["operating_systems"]}, separators=(",", ":")))
        return 0
    if sys.argv[1:] == ["release-runtime"]:
        print("python=" + policy["python_versions"][-1])
        return 0
    if sys.argv[1:] == ["check-current"]:
        current = f"{sys.version_info.major}.{sys.version_info.minor}"
        if current not in policy["python_versions"]:
            print(f"::error::Python {current} chưa có trong policy đã review; không tự nâng phiên bản.")
            return 1
        print(f"Python {current} nằm trong policy đã review.")
        return 0
    print("Cách dùng: runtime_policy.py matrix | release-runtime | check-current")
    return 2


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
