"""Exercise actual exporter outputs and failures in disposable directories."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins/yada/skills/dproj-generator"
sys.path.insert(0, str(SKILL / "scripts"))
from build_share_url import compress_to_encoded_uri_component
from pack_dproj import validate_diagram


class YadaTests(unittest.TestCase):
    def setUp(self):
        self.diagram = json.loads((SKILL / "assets/example-diagram.json").read_text())

    def run_export(self, script, *args):
        return subprocess.run(
            [sys.executable, str(SKILL / "scripts" / script), *map(str, args)],
            text=True, capture_output=True,
        )

    def test_project_contains_complete_unchanged_example(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "example.dproj"
            result = self.run_export(
                "pack_dproj.py", output, SKILL / "assets/example-workspace.json",
                SKILL / "assets/example-diagram.json",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            with zipfile.ZipFile(output) as archive:
                self.assertEqual(set(archive.namelist()), {"workspace.json", "diagram.json"})
                self.assertEqual(json.loads(archive.read("diagram.json")), self.diagram)
            self.assertNotIn("Auto-repaired", result.stdout)

    def test_invalid_endpoint_rejected_without_output(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "invalid.json"
            output = Path(folder) / "invalid.dproj"
            self.diagram["logicalData"]["edges"][0]["targetId"] = "missing"
            source.write_text(json.dumps(self.diagram))
            result = self.run_export(
                "pack_dproj.py", output, SKILL / "assets/example-workspace.json", source,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("not found", result.stdout)
            self.assertFalse(output.exists())

    def test_preview_written_without_printing_payload(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "preview.md"
            result = self.run_export(
                "build_share_url.py", SKILL / "assets/example-diagram.json",
                "--name", "Orders", "--output-md", output,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("https://bishoku.github.io/yada/#share=", output.read_text())
            self.assertNotIn("#share=", result.stdout + result.stderr)

    def test_compression_matches_javascript_reference_vectors(self):
        # Generated independently with upstream lz-string 1.5.0.
        vectors = json.loads((ROOT / "tests/lz-string-vectors.json").read_text())
        for text, expected in vectors:
            with self.subTest(text=text):
                self.assertEqual(compress_to_encoded_uri_component(text), expected)

    def test_missing_visual_edge_is_invalid(self):
        diagram = copy.deepcopy(self.diagram)
        diagram["visualData"]["layoutEdges"].pop("e1")
        self.assertTrue(validate_diagram(diagram))


if __name__ == "__main__":
    unittest.main()
