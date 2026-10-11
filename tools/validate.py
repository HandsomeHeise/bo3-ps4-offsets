from pathlib import Path
from .catalog import load_catalog


def main() -> int:
    try:
        entries = load_catalog(Path(__file__).resolve().parent.parent)
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"Validation failed: {error}")
        return 1
    print(f"Validated {len(entries)} function entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
