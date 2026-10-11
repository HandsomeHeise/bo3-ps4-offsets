import json
from pathlib import Path
import tempfile
import unittest

from tools.catalog import load_catalog


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root / "profiles.json").write_text(json.dumps({
            "CUSA02624/1.33": {"game": "BO3", "module": "eboot.bin",
                "sha256": "a" * 64, "executable_rva_ranges": [[0, 0x1000]]}}))
        self.path = self.root / "data/CUSA02624/1.33/example.yaml"
        self.path.parent.mkdir(parents=True)
        self.entry = {"id": "example", "title_id": "CUSA02624", "game": "BO3",
            "version": "1.33", "module": "eboot.bin", "kind": "function",
            "name": "example", "rva": "0x100", "confidence": "decompiled",
            "evidence": "Read-only synthetic fixture", "description": "Test fixture",
            "added": "2026-10-11", "by": "codex", "source": "synthetic-test"}

    def write(self):
        self.path.write_text(json.dumps(self.entry), encoding="utf-8")

    def test_valid_entry_retains_metadata(self):
        self.write()
        self.assertEqual(load_catalog(self.root), [self.entry])

    def test_missing_evidence_rejected(self):
        self.entry["evidence"] = ""
        self.write()
        with self.assertRaises(ValueError):
            load_catalog(self.root)

    def test_wrong_path_identity_rejected(self):
        self.entry["id"] = "other"
        self.write()
        with self.assertRaises(ValueError):
            load_catalog(self.root)

    def test_wrong_profile_rejected(self):
        self.entry["version"] = "1.34"
        self.write()
        with self.assertRaises(ValueError):
            load_catalog(self.root)

    def test_out_of_range_function_rejected(self):
        self.entry["rva"] = "0x1000"
        self.write()
        with self.assertRaises(ValueError):
            load_catalog(self.root)

    def test_unknown_confidence_rejected(self):
        self.entry["confidence"] = "proven"
        self.write()
        with self.assertRaises(ValueError):
            load_catalog(self.root)

    def test_non_string_version_rejected(self):
        self.entry["version"] = 1.33
        self.write()
        with self.assertRaises(ValueError):
            load_catalog(self.root)

    def test_invalid_signature_rejected(self):
        self.entry["aob"] = "55 INVALID"
        self.write()
        with self.assertRaises(ValueError):
            load_catalog(self.root)
