# SPDX-License-Identifier: Apache-2.0 WITH Swift-exception
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("policy", ROOT / "Scripts/check-policy.py")
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


def record(verified=True, message="fix: validate input", email=policy.OWNER_EMAIL):
    return {"commit": {"author": {"email": email}, "committer": {"email": email},
                       "message": message, "verification": {"verified": verified}},
            "author": {"login": "showxu"}, "committer": {"login": "showxu"}}


class PolicyTests(unittest.TestCase):
    def test_identity_signature_and_trailer(self):
        self.assertEqual(policy.commit_findings("a", record(), set()), [])
        self.assertIn("not Verified", policy.commit_findings("a", record(False), set())[0])
        self.assertTrue(policy.commit_findings("a", record(email="another@example.test"), set()))
        self.assertTrue(policy.commit_findings("a", record(message="fix: input\n\nCo-authored-by: helper"), set()))

    def test_bot_permission_does_not_skip_verification(self):
        bot = record(False, email="bot@example.test")
        bot.update(author={"login": "update[bot]"}, committer={"login": "update[bot]"})
        findings = policy.commit_findings("a", bot, {"update[bot]"})
        self.assertEqual(len(findings), 1)
        self.assertIn("not Verified", findings[0])

    def test_content_and_allowlist(self):
        workstation = "/" + "Users/fixture/project"
        self.assertTrue(policy.content_findings("a", 3, workstation, set()))
        self.assertTrue(policy.content_findings("a", 3, "." + "workspace/cache", set()))
        self.assertTrue(policy.content_findings("a", 3, "example." + "plan.md", set()))
        self.assertTrue(policy.content_findings("a", 3, "Codex", set()))
        self.assertEqual(policy.content_findings("a", 3, "Codex API", {"codex"}), [])
        self.assertTrue(policy.content_findings("a", 3, workstation + " Codex", {"codex"}))

    def test_added_lines_ignore_context_and_deleted_content(self):
        patch = "@@ -2,2 +2,2 @@\n-private\n unchanged\n+new\n@@ -20,0 +21 @@\n+last\n"
        self.assertEqual(list(policy.added_lines(patch)), [(3, "new"), (21, "last")])

    def test_push_and_pull_request_ranges(self):
        self.assertEqual(policy.source_range({"before": "a", "after": "b"}, "push"), ("a", "b"))
        self.assertEqual(policy.source_range({"pull_request": {"base": {"sha": "a"}, "head": {"sha": "b"}}}, "pull_request"), ("a", "b"))
        with self.assertRaises(ValueError):
            policy.source_range({"deleted": True}, "push")

    def test_real_git_range_and_new_branch(self):
        output = ROOT / ".build/policy-tests"
        output.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=output) as directory:
            previous = Path.cwd()
            os.chdir(directory)
            try:
                subprocess.run(["git", "init", "-q"], check=True)
                def commit(text):
                    Path("sample.txt").write_bytes(text if isinstance(text, bytes) else text.encode())
                    policy.git("add", "sample.txt")
                    policy.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.test",
                               "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", "commit", "-qm", "fix: fixture")
                    return policy.git("rev-parse", "HEAD").strip()
                base = commit("clean\n")
                self.assertEqual(policy.check_range("example/repo", policy.ZERO_SHA, base, set(), set(), lambda *_: record()), [])
                head = commit("clean\n/" + "home/fixture/private\n")
                findings = policy.check_range("example/repo", base, head, set(), set(), lambda *_: record())
                self.assertEqual(findings, ["sample.txt:2: private execution path"])
                byte_fixture = commit(b"invalid UTF-8: \xfa\n")
                self.assertEqual(policy.check_range("example/repo", head, byte_fixture, set(), set(), lambda *_: record()), [])
                unsafe_fixture = commit(b"invalid UTF-8: \xfa\n/" + b"home/fixture/private\n")
                self.assertEqual(policy.check_range("example/repo", byte_fixture, unsafe_fixture, set(), set(), lambda *_: record()),
                                 ["sample.txt:2: private execution path"])
            finally:
                os.chdir(previous)


if __name__ == "__main__":
    unittest.main()
