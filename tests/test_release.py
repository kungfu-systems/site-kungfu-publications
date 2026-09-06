import contextlib
import importlib.util
import io
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


spec = importlib.util.spec_from_file_location("publish", Path(__file__).resolve().parents[1] / "scripts/publish.py")
publish = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publish)


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.tag = "v2026.08.1-alpha.0"
        self.data = {"release_tag": self.tag, "publications": [{
            "pdf_filename": "article-{locale}.pdf", "locales": {
                "zh-CN": {"status": "published", "core": "zh-CN.md"},
                "en-US": {"status": "draft", "core": "en-US.md"},
                "fr-FR": {"status": "planned"},
            }}]}
        for name in ["_build/pdf/article-zh-CN.pdf", "_build/pdf/article-en-US.pdf",
                     ".buildchain/artifacts/pdf-manifest.json", ".buildchain/artifacts/pdf-summary.json"]:
            p = self.root / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(name)
        for mock in [patch.object(publish, "ROOT", self.root),
                     patch.object(publish, "catalog", return_value=self.data),
                     patch.dict(os.environ, RELEASE_TAG=self.tag)]:
            mock.start()
            self.addCleanup(mock.stop)

    def test_dry_run_excludes_drafts_without_side_effects(self):
        output = io.StringIO()
        with patch.object(publish.subprocess, "run") as run, contextlib.redirect_stdout(output):
            publish.publish_release(dry_run=True)
        plan = json.loads(output.getvalue())
        self.assertIn("_build/pdf/article-zh-CN.pdf", plan["upload"])
        self.assertNotIn("_build/pdf/article-en-US.pdf", plan["upload"])
        self.assertNotIn("en-US", plan["checksums"])
        self.assertIn("--prerelease", plan["create"])
        self.assertIn("--latest=false", plan["create"])
        run.assert_not_called()
        self.assertFalse((self.root / "_build/release").exists())

    def test_alpha_publish_checksums_cover_exact_uploaded_pdfs(self):
        with patch.object(publish.subprocess, "run", return_value=subprocess.CompletedProcess([], 1)) as run:
            publish.publish_release()
        create = run.call_args_list[1].args[0]
        upload = run.call_args_list[2].args[0]
        self.assertIn("--verify-tag", create)
        self.assertIn("--prerelease", create)
        self.assertIn("--latest=false", create)
        self.assertNotIn("_build/pdf/article-en-US.pdf", upload)
        checksums = (self.root / "_build/release/SHA256SUMS").read_text().splitlines()
        self.assertEqual(len(checksums), 1)
        self.assertTrue(checksums[0].endswith("  article-zh-CN.pdf"))
        self.assertEqual(checksums[0].split()[0], publish.hashlib.sha256(
            (self.root / "_build/pdf/article-zh-CN.pdf").read_bytes()).hexdigest())

    def test_stable_tag_does_not_get_alpha_flags(self):
        self.data["release_tag"] = "v2026.08.1"
        output = io.StringIO()
        with patch.dict(os.environ, RELEASE_TAG="v2026.08.1"), contextlib.redirect_stdout(output):
            publish.publish_release(dry_run=True)
        self.assertNotIn("--prerelease", json.loads(output.getvalue())["create"])

    def test_wrong_tag_fails_before_remote_mutation(self):
        with patch.dict(os.environ, RELEASE_TAG="v2026.08.2-alpha.0"), patch.object(publish.subprocess, "run") as run:
            with self.assertRaisesRegex(RuntimeError, "catalog"):
                publish.publish_release()
            run.assert_not_called()

    def test_missing_published_pdf_fails_before_remote_mutation(self):
        (self.root / "_build/pdf/article-zh-CN.pdf").unlink()
        with patch.object(publish.subprocess, "run") as run:
            with self.assertRaisesRegex(RuntimeError, "missing release asset"):
                publish.publish_release()
            run.assert_not_called()

    def test_existing_stable_release_cannot_be_reused_as_alpha(self):
        state = subprocess.CompletedProcess([], 0, stdout='{"isPrerelease":false,"isDraft":false}')
        with patch.object(publish.subprocess, "run", return_value=state) as run:
            with self.assertRaisesRegex(RuntimeError, "classification"):
                publish.publish_release()
            self.assertEqual(run.call_count, 1)

    def test_upload_failure_is_not_reported_as_success(self):
        state = subprocess.CompletedProcess([], 0, stdout='{"isPrerelease":true,"isDraft":false}')
        with patch.object(publish.subprocess, "run", side_effect=[state, subprocess.CalledProcessError(1, "upload")]):
            with self.assertRaises(subprocess.CalledProcessError):
                publish.publish_release()


if __name__ == "__main__":
    unittest.main()
