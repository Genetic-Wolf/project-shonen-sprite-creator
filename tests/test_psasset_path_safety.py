"""Regression checks for portable artwork package path safety.

Run: python -m unittest discover -s tests -p 'test_psasset_path_safety.py'
"""
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

import asset_package


class PackagePathSafetyTests(unittest.TestCase):
    def test_rejects_unsafe_ids(self):
        for value in ("../outside", "..", "a/b", "a\\b", "", ".hidden", "a b", "x" * 129):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    asset_package._valid_id(value)

    def test_accepts_portable_ids(self):
        for value in ("base_male", "head-armor-001", "A", "abc123"):
            self.assertEqual(asset_package._valid_id(value), value)

    def test_rejects_traversal_id_before_import(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "unsafe.psasset"
            manifest = {
                "schemaVersion": 2,
                "packageType": "Project Shonen Reusable Piece",
                "asset": {"id": "../../escape", "name": "Unsafe", "outputs": {}},
                "checksums": {},
            }
            with zipfile.ZipFile(package, "w") as archive:
                archive.writestr("manifest.json", json.dumps(manifest))
            with self.assertRaises(ValueError):
                asset_package.inspect_package(package)
            with self.assertRaises(ValueError):
                asset_package.import_piece(package)


if __name__ == "__main__":
    unittest.main()
