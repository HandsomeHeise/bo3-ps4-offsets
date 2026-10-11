import argparse
import json
from pathlib import Path
from .catalog import load_catalog


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the validated BO3 offset index")
    parser.add_argument("--check", action="store_true", help="Fail if the index differs")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    try:
        entries = load_catalog(root)
        profiles = json.loads((root / "profiles.json").read_text(encoding="utf-8"))
        output = json.dumps({"profiles": profiles, "entries": entries}, indent=2) + "\n"
        target = root / "docs/offsets.json"
        if args.check:
            if not target.exists() or target.read_text(encoding="utf-8") != output:
                print("Generated index is missing or stale")
                return 1
            print("Generated index matches the validated catalog")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(output, encoding="utf-8", newline="\n")
            print(f"Built index with {len(entries)} entries")
        return 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"Build failed: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
