import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("hub_validate", ROOT / "scripts/validate.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CatalogTests(unittest.TestCase):
    def test_catalogs_match_packages(self):
        self.assertGreater(module.validate(), 0)

    def test_stale_catalog_version_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in ("plugins", ".agents", ".github"):
                shutil.copytree(ROOT / name, root / name)
            path = root / ".github/plugin/marketplace.json"
            data = json.loads(path.read_text())
            data["plugins"][0]["version"] = "0.0.0"
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, "stale version"):
                module.validate(root)
