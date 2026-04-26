import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent


class TestSyncFlow(unittest.TestCase):
    def test_build_dist(self):
        """Verify that npm run build creates the dist folder and required files."""
        # Run build
        npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
        result = subprocess.run(
            [npm_cmd, "run", "build"], cwd=str(ROOT), capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, f"Build failed: {result.stderr}")

        dist_path = ROOT / "dist"
        self.assertTrue(dist_path.exists(), "dist folder not created")
        self.assertTrue((dist_path / "index.html").exists(), "index.html missing in dist")
        # V28: dashboard_data.js and intel.js are runtime artifacts, not vite bundle outputs

    def test_sync_script_structure(self):
        """Verify that x_intel_instant_sync.py has the correct sequence."""
        sync_script = ROOT / "engine" / "x_intel_instant_sync.py"
        content = sync_script.read_text(encoding="utf-8")

        # Check for key steps
        self.assertIn("image_analyzer.py", content)
        self.assertIn("visual_buzz_aggregator.py", content)
        self.assertIn("generate_CPO_BRAIN.py", content)
        self.assertIn("npm", content)
        self.assertIn("run", content)
        self.assertIn("build", content)
        self.assertIn("deploy", content)


if __name__ == "__main__":
    unittest.main()
