#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH Swift-exception
"""Validate the source range of a pull request or default-branch push."""

import json
import os
from pathlib import Path
import re
import subprocess
import sys

OWNER_EMAIL = "10173746+showxu@users.noreply.github.com"
CONVENTIONAL = re.compile(r"^(build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)(?:\([^()\r\n]+\))?!?: [^\s].*$")
ZERO_SHA = "0" * 40
TRAILER = re.compile(
    r"^(Co-authored-by|Made-with|Generated-by|Generated-with|Assisted-by|Signed-off-by):"
    r"|Generated with|cursor\.com|anthropic\.com|claude\.ai|openai\.com", re.I | re.M)
PRIVATE_PATH = re.compile(r"/(?:Users|home)/[^/\s]+/|[.]workspace/")
AGENT = re.compile(r"\b(ChatGPT|Codex|Cursor|Claude)\b", re.I)


def git(*arguments, errors="strict"):
    return subprocess.check_output(["git", *arguments], encoding="utf-8", errors=errors,
                                   stdin=subprocess.DEVNULL)


def api_commit(repository, sha):
    return json.loads(subprocess.check_output(
        ["gh", "api", f"repos/{repository}/commits/{sha}"], text=True))


def commit_findings(sha, record):
    commit = record["commit"]
    findings = []
    email = commit["committer"]["email"].lower()
    if email not in {OWNER_EMAIL, "noreply@github.com"}:
        findings.append(f"{sha}: unexpected committer identity")
    if not commit.get("verification", {}).get("verified", False):
        findings.append(f"{sha}: commit is not Verified by GitHub")
    return findings


def title_findings(title, allow_terms):
    findings = content_findings("PR title", 1, title, allow_terms)
    if not CONVENTIONAL.fullmatch(title):
        findings.append("PR title: expected a Conventional Commit subject")
    return findings


def content_findings(path, number, text, allow_terms):
    reasons = []
    if TRAILER.search(text):
        reasons.append("attribution trailer or tool attribution")
    if PRIVATE_PATH.search(text):
        reasons.append("private execution path")
    terms = sorted({match.group() for match in AGENT.finditer(text)
                    if match.group().lower() not in allow_terms})
    if terms:
        reasons.append("unapproved product/tool term: " + ", ".join(terms))
    return [f"{path}:{number}: {reason}" for reason in reasons]


def added_lines(patch):
    number = None
    for line in patch.splitlines():
        match = re.match(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
        if match:
            number = int(match.group(1))
        elif number is not None:
            if line.startswith("+"):
                yield number, line[1:]
                number += 1
            elif line.startswith(" "):
                number += 1


def source_range(event, name):
    if name == "pull_request":
        return event["pull_request"]["base"]["sha"], event["pull_request"]["head"]["sha"]
    if name == "push" and not event.get("deleted", False):
        return event["before"], event["after"]
    raise ValueError("Policy requires a pull_request or non-deletion push event")


def check_range(repository, base, head, allow_terms, *, verify_commits=False, fetch_commit=api_commit):
    for sha in (base, head):
        if not re.fullmatch(r"[0-9a-f]{40}", sha):
            raise ValueError("Event contains an invalid source SHA")
    if head == ZERO_SHA:
        raise ValueError("Policy requires a source commit")
    new_branch = base == ZERO_SHA
    revision = head if new_branch else f"{base}..{head}"
    commits = git("rev-list", "--reverse", revision).splitlines()
    findings = []
    if verify_commits:
        for sha in commits:
            findings.extend(commit_findings(sha, fetch_commit(repository, sha)))

    if new_branch:
        comparison = git("hash-object", "-t", "tree", "--stdin").strip()
    else:
        comparison = git("merge-base", base, head).strip()
    paths = git("diff", "--name-only", "--no-renames", "--diff-filter=d", "-z", comparison, head).split("\0")
    for path in filter(None, paths):
        file = Path(path)
        if (any(part in {".agent", ".workspace"} for part in file.parts)
                or file.name == "PLANS.md" or file.name.endswith(".plan.md")):
            findings.append(f"{path}: private execution file")
        # Git can emit byte fixtures as text when they contain no NUL. Keep
        # scanning their readable content without requiring valid UTF-8.
        patch = git("diff", "--no-ext-diff", "--no-color", "--no-renames", "--unified=0",
                    comparison, head, "--", path, errors="replace")
        for number, line in added_lines(patch):
            findings.extend(content_findings(path, number, line, allow_terms))
    return findings


def main():
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
    name = os.environ["GITHUB_EVENT_NAME"]
    base, head = source_range(event, name)
    allow_terms = {x.strip().lower() for x in os.environ.get("ALLOW_TERMS", "").splitlines() if x.strip()}
    findings = check_range(os.environ["GITHUB_REPOSITORY"], base, head, allow_terms,
                           verify_commits=name == "push")
    if name == "pull_request":
        findings.extend(title_findings(event["pull_request"]["title"], allow_terms))
    if findings:
        print("\n".join(findings))
        return 1
    print("policy ok")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        print(f"policy: {error}", file=sys.stderr)
        sys.exit(1)
