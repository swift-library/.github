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
    def test_push_committer_and_verification(self):
        self.assertEqual(policy.commit_findings("a", record()), [])
        self.assertIn("not Verified", policy.commit_findings("a", record(False))[0])
        self.assertTrue(policy.commit_findings("a", record(email="another@example.test")))
        for author in ("external@example.test", "update[bot]@users.noreply.github.com"):
            commit = record()
            commit["commit"]["author"]["email"] = author
            commit["commit"]["committer"]["email"] = "noreply@github.com"
            self.assertEqual(policy.commit_findings("a", commit), [])

    def test_pr_titles(self):
        for title in ("fix: validate input", "feat(api)!: change request shape", "ci(deps): update action"):
            self.assertEqual(policy.title_findings(title, set()), [])
        for title in ("Update dependency", "fix: ", "unknown: change", "fix: Codex attribution"):
            self.assertTrue(policy.title_findings(title, set()))
        self.assertEqual(policy.title_findings("fix: Codex requests", {"codex"}), [])
        self.assertTrue(policy.title_findings("fix: Generated " + "with helper", set()))

    def test_content_and_allowlist(self):
        self.assertTrue(policy.content_findings("a", 3, "Co-authored-by: helper", set()))
        workstation = "/" + "Users/fixture/project"
        self.assertTrue(policy.content_findings("a", 3, workstation, set()))
        self.assertTrue(policy.content_findings("a", 3, "/" + "home/fixture/project", set()))
        self.assertTrue(policy.content_findings("a", 3, "." + "workspace/cache", set()))
        for text in (".agent/plans/x.md", ".agent/PLANS.md", "PLANS.md", "release.plan.md"):
            with self.subTest(text=text):
                self.assertEqual(policy.content_findings("a", 3, text, set()), [])
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
                self.assertEqual(policy.check_range("example/repo", policy.ZERO_SHA, base, set(), verify_commits=True, fetch_commit=lambda *_: record()), [])
                self.assertEqual(policy.check_range("example/repo", policy.ZERO_SHA, base, set(),
                    fetch_commit=lambda *_: self.fail("PRs must not inspect commit identities")), [])
                head = commit("clean\n/" + "home/fixture/private\n")
                findings = policy.check_range("example/repo", base, head, set(), verify_commits=True, fetch_commit=lambda *_: record())
                self.assertEqual(findings, ["sample.txt:2: private execution path"])
                byte_fixture = commit(b"invalid UTF-8: \xfa\n")
                self.assertEqual(policy.check_range("example/repo", head, byte_fixture, set(), verify_commits=True, fetch_commit=lambda *_: record()), [])
                unsafe_fixture = commit(b"invalid UTF-8: \xfa\n/" + b"home/fixture/private\n")
                self.assertEqual(policy.check_range("example/repo", byte_fixture, unsafe_fixture, set(), verify_commits=True, fetch_commit=lambda *_: record()),
                                 ["sample.txt:2: private execution path"])
            finally:
                os.chdir(previous)

    def test_real_git_private_file_paths(self):
        output = ROOT / ".build/policy-tests"
        output.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=output) as directory:
            previous = Path.cwd()
            os.chdir(directory)
            try:
                subprocess.run(["git", "init", "-q"], check=True)
                def commit():
                    policy.git("add", "--all", "--force")
                    policy.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.test",
                               "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", "commit", "-qm", "fix: fixture")
                    return policy.git("rev-parse", "HEAD").strip()
                # Plan basenames and suffixes are matched case-sensitively.
                public_paths = ("sample.txt", ".agent-notes/x.md", ".workspace-notes/x.md",
                                "docs/PLANS.md.example", "release.plan.md/guide.md", "plans.md", "docs/Release.PLAN.md")
                for name in public_paths:
                    path = Path(name)
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text("Document .agent/plans/x.md, .agent/PLANS.md and release.plan.md.\n")
                base = commit()
                self.assertEqual(policy.check_range("example/repo", policy.ZERO_SHA, base, set()), [])
                private_paths = (".agent/plans/x.md", ".agent/plans/draft notes.md", "docs/PLANS.md", "x.plan.md",
                                 "." + "workspace/state.json", "docs/.agent/x.md", "docs/." + "workspace/state.json")
                expected = sorted(f"{name}: private execution file" for name in private_paths)
                for name in private_paths:
                    path = Path(name)
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text("initial\n")
                added = commit()
                self.assertEqual(sorted(policy.check_range("example/repo", base, added, set())), expected)
                self.assertEqual(sorted(policy.check_range("example/repo", policy.ZERO_SHA, added, set())), expected)
                self.assertEqual(sorted(policy.check_range("example/repo", base, added, set(),
                    verify_commits=True, fetch_commit=lambda *_: record())), expected)
                self.assertEqual(sorted(policy.check_range("example/repo", base, added, set(),
                    verify_commits=True, fetch_commit=lambda *_: record(False))),
                    sorted([*expected, f"{added}: commit is not Verified by GitHub"]))
                for name in private_paths:
                    Path(name).write_text("modified\n")
                modified = commit()
                self.assertEqual(sorted(policy.check_range("example/repo", added, modified, set())), expected)
                self.assertEqual(sorted(policy.check_range("example/repo", added, modified, set(),
                    verify_commits=True, fetch_commit=lambda *_: record())), expected)
                Path("sample.txt").write_text("updated documentation\n")
                unchanged = commit()
                self.assertEqual(policy.check_range("example/repo", modified, unchanged, set()), [])
                for name in private_paths:
                    Path(name).unlink()
                deleted = commit()
                self.assertEqual(policy.check_range("example/repo", unchanged, deleted, set()), [])
                self.assertEqual(policy.check_range("example/repo", unchanged, deleted, set(),
                    verify_commits=True, fetch_commit=lambda *_: record()), [])
            finally:
                os.chdir(previous)

    def test_real_git_renames_and_standalone_agent_file(self):
        output = ROOT / ".build/policy-tests"
        output.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=output) as directory:
            previous = Path.cwd()
            os.chdir(directory)
            try:
                subprocess.run(["git", "init", "-q"], check=True)
                def commit():
                    policy.git("add", "--all", "--force")
                    policy.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.test",
                               "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", "commit", "-qm", "fix: fixture")
                    return policy.git("rev-parse", "HEAD").strip()
                Path("sample.txt").write_text("clean\n")
                base = commit()
                Path(".agent").mkdir()
                Path("sample.txt").rename(".agent/sample.txt")
                moved_in = commit()
                self.assertEqual(policy.check_range("example/repo", base, moved_in, set()),
                                 [".agent/sample.txt: private execution file"])
                Path(".agent/sample.txt").rename("sample.txt")
                moved_out = commit()
                self.assertEqual(policy.check_range("example/repo", moved_in, moved_out, set()), [])
                Path(".agent").rmdir()
                Path("sample.txt").rename(".agent")
                standalone = commit()
                self.assertEqual(policy.check_range("example/repo", moved_out, standalone, set()),
                                 [".agent: private execution file"])
            finally:
                os.chdir(previous)


if __name__ == "__main__":
    unittest.main()
