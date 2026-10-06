#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH Swift-exception
"""Normalize execution paths in logs and reject private context in uploadable text."""

import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import tarfile

# Product identifiers and source filenames are meaningful evidence, not attribution.
PRIVATE_PATH = re.compile(r"/(?:Users|home)/[^/\s]+/|\.(?:workspace|agent)/|(?:^|[\s/])(?:[^\s/]+\.plan\.md|PLANS\.md)(?:$|[\s:])")


def findings(data, name):
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return []
    return [f"{name}:{number}: private execution path or plan reference"
            for number, line in enumerate(text.splitlines(), 1) if PRIVATE_PATH.search(line)]


def archive_findings(data, name, depth=0):
    if depth > 4:
        return [f"{name}: nested archive depth exceeds the evidence check limit"]
    errors = []
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as archive:
        for member in archive:
            label = name + "!" + member.name
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts or member.issym() or member.islnk():
                errors.append(f"{label}: unsafe archive member")
                continue
            if member.isfile():
                content = archive.extractfile(member).read()
                if member.name.endswith((".tar.gz", ".tgz", ".tar")):
                    errors.extend(archive_findings(content, label, depth + 1))
                else:
                    errors.extend(findings(content, label))
    return errors


def check(directory, replacements):
    """Normalize plain-text logs; scan UTF-8 files and compressed DocC contents."""
    errors = []
    if not directory.is_dir():
        return ["Validation evidence directory is missing"]
    replacements = sorted(((source, value) for source, value in replacements if len(source) > 1),
                          key=lambda pair: len(pair[0]), reverse=True)
    for path in sorted(directory.rglob("*")):
        name = path.relative_to(directory).as_posix()
        if path.is_symlink():
            errors.append(f"{name}: evidence must not contain symbolic links")
            continue
        if not path.is_file():
            continue
        content = path.read_bytes()
        if path.suffix == ".log":
            try:
                text = content.decode("utf-8")
            except UnicodeDecodeError:
                errors.append(f"{name}: log is not UTF-8")
                continue
            for source, value in replacements:
                text = text.replace(source, value)
            content = text.encode("utf-8")
            path.write_bytes(content)
        if name == "package.json":
            manifest = json.loads(content)
            package_kind = manifest.get("packageKind", {})
            if package_kind.get("root") == [str(Path.cwd())]:
                package_kind["root"] = ["."]
                content = (json.dumps(manifest, indent=2) + "\n").encode()
                path.write_bytes(content)
        errors.extend(findings(name.encode(), name))
        if path.name.endswith((".tar.gz", ".tgz", ".tar")):
            errors.extend(archive_findings(content, name))
        else:
            errors.extend(findings(content, name))
    return errors


def main():
    replacements = [(str(Path.cwd()), "<package>"), (str(Path.home()), "<home>")]
    for key in ("RUNNER_TEMP", "TMPDIR"):
        if os.environ.get(key):
            replacements.append((os.environ[key].rstrip("/"), "<temporary>"))
    errors = check(Path(".build/release-validation"), replacements)
    if errors:
        raise SystemExit("\n".join(errors))
    print("validation evidence paths checked")


if __name__ == "__main__":
    main()
