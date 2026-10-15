#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH Swift-exception
"""Compare MAINTENANCE.md with live public-repository settings, without mutations."""

import argparse
import base64
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent


def declaration(text):
    section = re.search(r"^## GitHub Settings\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not section:
        raise ValueError("Missing GitHub Settings section")
    blocks = re.findall(r"^```json\n(.*?)^```", section[1], re.S | re.M)
    if len(blocks) != 1:
        raise ValueError("Expected one JSON settings declaration")
    settings = json.loads(blocks[0])
    checks = {}
    for repository, cell in re.findall(r"^\| `([^`]+)` \| (.*?) \|$", section[1], re.M):
        if repository in checks:
            raise ValueError("Duplicate required-check row: " + repository)
        names = re.findall(r"`([^`]+)`", cell)
        if not names and cell != "None yet":
            raise ValueError("Malformed required-check row: " + repository)
        checks[repository] = names
    if not checks:
        raise ValueError("Missing required-check table")
    return settings, checks


def gh(path, paginate=False):
    command = ["gh", "api", path]
    if paginate:
        command += ["--paginate", "--slurp"]
    return json.loads(subprocess.check_output(command, text=True))


def collection(path, key=None):
    pages = gh(path, paginate=True)
    return [item for page in pages for item in (page[key] if key else page)]


def legacy_protection(path, branch):
    try:
        return gh(path + "/branches/" + branch + "/protection")
    except subprocess.CalledProcessError as error:
        try:
            response = json.loads(error.output)
        except (TypeError, ValueError):
            raise error
        if str(response.get("status")) == "404" and response.get("message") == "Branch not protected":
            return None
        raise


def compare(label, actual, expected):
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return [label + ": expected an object"]
        return [finding for key, value in expected.items()
                for finding in compare(label + "." + key, actual.get(key), value)]
    if actual != expected:
        # Values may include organizational variable contents; print only the field name.
        return [label + ": differs from declaration"]
    return []


def canonical_ruleset(value):
    selected = {key: value.get(key) for key in (
        "name", "target", "enforcement", "bypass_actors", "conditions", "rules")}
    selected["rules"] = sorted(selected["rules"] or [], key=lambda rule: rule["type"])
    for rule in selected["rules"]:
        parameters = rule.get("parameters", {})
        if "required_status_checks" in parameters:
            parameters["required_status_checks"] = sorted(
                parameters["required_status_checks"], key=lambda item: item["context"])
    return selected


def expected_rulesets(settings, checks):
    branch = deepcopy(settings["branch_ruleset"])
    if checks:
        parameters = {key: value for key, value in settings["status_checks"].items()
                      if key != "integration_id"}
        parameters["required_status_checks"] = [
            {"context": name, "integration_id": settings["status_checks"]["integration_id"]}
            for name in checks]
        branch["rules"].append({"type": "required_status_checks", "parameters": parameters})
    return [branch, deepcopy(settings["tag_ruleset"])]


def check_actions(path, expected):
    secrets = collection(path + "/actions/secrets?per_page=100", "secrets")
    variables = collection(path + "/actions/variables?per_page=100", "variables")
    findings = compare(path + ".secret_names", sorted(x["name"] for x in secrets), sorted(expected["secrets"]))
    actual_variables = {x["name"]: x["value"] for x in variables}
    if actual_variables != expected["variables"]:
        findings.append(path + ".variables: differs from declaration")
    return findings


def check_repository(repository, settings, checks):
    name = repository["name"]
    path = f"repos/{settings['organization']}/{name}"
    findings = compare(path + ".default_branch", repository["default_branch"], settings["default_branch"])
    findings += compare(path, gh(path), settings["merge"])
    findings += compare(path + ".workflow_token", gh(path + "/actions/permissions/workflow"), settings["workflow_token"])
    expected_actions = settings["repository_action_overrides"].get(name, settings["repository_actions"])
    findings += check_actions(path, expected_actions)
    if name not in checks:
        findings.append(path + ": missing required-check declaration")
        return findings
    findings += compare(path + ".legacy_branch_protection",
                        legacy_protection(path, repository["default_branch"]),
                        settings["legacy_branch_protection"])
    actual = [gh(path + "/rulesets/" + str(rule["id"])) for rule in collection(path + "/rulesets?per_page=100")]
    expected = expected_rulesets(settings, checks[name])
    if sorted(x["name"] for x in actual) != sorted(x["name"] for x in expected):
        findings.append(path + ".rulesets: names or count differ from declaration")
    for expected_rule in expected:
        matches = [x for x in actual if x["name"] == expected_rule["name"]]
        if len(matches) == 1 and canonical_ruleset(matches[0]) != canonical_ruleset(expected_rule):
            findings.append(path + ".rulesets." + expected_rule["name"] + ": parameters differ from declaration")
    return findings


def check(settings, checks):
    org = settings["organization"]
    path = "orgs/" + org
    findings = compare(path + ".workflow_token", gh(path + "/actions/permissions/workflow"), settings["workflow_token"])
    findings += check_actions(path, settings["organization_actions"])
    installations = collection(path + "/installations?per_page=100", "installations")
    actual_apps = {item["app_slug"]: {"repository_selection": item["repository_selection"], "permissions": item["permissions"]}
                   for item in installations}
    if actual_apps != settings["apps"]:
        findings.append(path + ".apps: installed Apps, permissions or selection differ from declaration")
    repositories = [x for x in collection(path + "/repos?type=public&per_page=100") if not x["fork"] and not x["private"]]
    missing = set(checks) - {x["name"] for x in repositories}
    findings += ["Required-check declaration has no public non-fork repository: " + name for name in sorted(missing)]
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = executor.map(lambda repository: check_repository(repository, settings, checks), repositories)
        for result in results:
            findings.extend(result)
    return sorted(findings)


def shared_callers(organization, repository):
    path = f"repos/{organization}/{repository['name']}/contents/.github/workflows"
    try:
        entries = gh(path + "?ref=" + repository["default_branch"])
    except subprocess.CalledProcessError as error:
        response = json.loads(error.output)
        if str(response.get("status")) == "404":
            return []
        raise
    callers = []
    pattern = re.compile(r"^\s*(?:-\s*)?uses:\s*['\"]?" + re.escape(organization)
                         + r"/\.github/\.github/workflows/[^@\s]+@([^\s'\"#]+)", re.M)
    for entry in entries:
        if entry["type"] != "file" or Path(entry["name"]).suffix not in (".yml", ".yaml"):
            continue
        value = gh(entry["url"])
        source = base64.b64decode(value["content"]).decode()
        callers += [{"workflow": entry["path"], "ref": match[1]} for match in pattern.finditer(source)]
    return callers


def pin_drift(settings):
    """Observe reviewed pins separately from enforced repository settings."""
    organization = settings["organization"]
    result = {"target": None, "repositories_with_callers": 0, "caller_count": 0,
              "drift": [], "unavailable": []}
    try:
        result["target"] = gh(f"repos/{organization}/.github/commits/master")["sha"]
        repositories = [repository for repository in collection(f"orgs/{organization}/repos?type=all&per_page=100")
                        if not repository["fork"]]
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        result["unavailable"].append({"repository": organization, "reason": type(error).__name__})
        return result

    def inspect(repository):
        try:
            return repository["name"], shared_callers(organization, repository), None
        except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
            return repository["name"], [], type(error).__name__

    with ThreadPoolExecutor(max_workers=4) as executor:
        for name, callers, error in executor.map(inspect, sorted(repositories, key=lambda item: item["name"])):
            if error:
                result["unavailable"].append({"repository": name, "reason": error})
            if callers:
                result["repositories_with_callers"] += 1
                result["caller_count"] += len(callers)
                outdated = [caller for caller in callers if caller["ref"] != result["target"]]
                if outdated:
                    result["drift"].append({"repository": name, "callers": outdated})
    return result


def pin_summary(report):
    lines = ["shared pin target: " + (report["target"] or "unavailable")]
    if report["drift"]:
        lines += ["shared pin drift (report only):"]
        for repository in report["drift"]:
            lines += ["- " + repository["repository"] + ": " + ", ".join(
                caller["workflow"] + "@" + caller["ref"] for caller in repository["callers"])]
    else:
        lines += ["shared pin drift: " + ("none observed" if report["unavailable"] else "none")
                  + " (" + str(report["repositories_with_callers"])
                  + " repositories, " + str(report["caller_count"]) + " callers)"]
    for item in report["unavailable"]:
        lines += ["shared pin observation unavailable: " + item["repository"] + " (" + item["reason"] + ")"]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--declaration", type=Path, default=ROOT / "MAINTENANCE.md")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    settings, checks = declaration(args.declaration.read_text())
    findings = check(settings, checks)
    pins = pin_drift(settings)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps({"organization": settings["organization"], "findings": findings,
                                          "shared_pin": pins}, indent=2) + "\n")
    print("\n".join(findings) if findings else "settings ok")
    print(pin_summary(pins))
    return int(bool(findings))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        print(f"settings: could not verify declared state: {error}", file=sys.stderr)
        sys.exit(1)
