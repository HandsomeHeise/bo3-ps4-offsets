from pathlib import Path
import datetime
import json
import re


def load_catalog(root: Path) -> list[dict]:
    profiles = json.loads((root / "profiles.json").read_text(encoding="utf-8"))
    entries = []
    for path in sorted((root / "data").glob("*/*/*.yaml")):
        entry = json.loads(path.read_text(encoding="utf-8"))
        required = ("id", "title_id", "game", "version", "module", "kind", "name",
                    "rva", "confidence", "description", "added", "by", "source")
        if not isinstance(entry, dict) or any(
                not isinstance(entry.get(key), str) or not entry[key].strip() for key in required):
            raise ValueError(f"{path}: required fields must be nonempty strings")
        title, version = path.parent.parent.name, path.parent.name
        if (entry["id"] != path.stem or entry["title_id"] != title or entry["version"] != version
                or not re.fullmatch(r"[A-Za-z0-9_]+", entry["id"])
                or not re.fullmatch(r"CUSA\d{5}", title)):
            raise ValueError(f"{path}: entry identity does not match its path")
        profile = profiles.get(f"{title}/{version}")
        if not isinstance(profile, dict) or any(
                entry[key] != profile.get(key) for key in ("game", "module")):
            raise ValueError(f"{path}: unknown or mismatched build profile")
        if not re.fullmatch(r"[0-9a-f]{64}", str(profile.get("sha256", ""))):
            raise ValueError(f"{path}: profile SHA256 is invalid")
        if entry["kind"] != "function":
            raise ValueError(f"{path}: this initial catalog supports function entries only")
        if entry["confidence"] not in {"verified-live", "decompiled", "inferred", "guess"}:
            raise ValueError(f"{path}: unknown confidence")
        if entry["confidence"] != "guess" and (
                not isinstance(entry.get("evidence"), str) or not entry["evidence"].strip()):
            raise ValueError(f"{path}: evidence is required above guess confidence")
        if not re.fullmatch(r"0x[0-9a-fA-F]+", entry["rva"]):
            raise ValueError(f"{path}: RVA must be hexadecimal")
        rva = int(entry["rva"], 16)
        if not any(start <= rva < end for start, end in profile["executable_rva_ranges"]):
            raise ValueError(f"{path}: function RVA is outside the executable profile range")
        datetime.date.fromisoformat(entry["added"])
        if "aob" in entry and (not isinstance(entry["aob"], str) or not re.fullmatch(
                r"(?:[0-9a-fA-F]{2}|\?\?)(?: (?:[0-9a-fA-F]{2}|\?\?))*", entry["aob"])):
            raise ValueError(f"{path}: malformed AOB signature")
        entries.append(entry)
    if not entries:
        raise ValueError("Catalog has no entries")
    return entries
