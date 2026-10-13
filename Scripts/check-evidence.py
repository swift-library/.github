#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH Swift-exception
"""Normalize execution paths and reject private context in uploadable text."""

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


def normalize_text(data, replacements):
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return data
    for source, value in replacements:
        text = text.replace(source, value)
    return text.encode("utf-8")


def normalize_archive(data, name, replacements, depth=0):
    if depth > 4:
        return data, [f"{name}: nested archive depth exceeds the evidence check limit"]
    errors = []
    changed = False
    output = io.BytesIO()
    mode = "w:gz" if name.endswith((".tar.gz", ".tgz")) else "w"
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as archive, \
            tarfile.open(fileobj=output, mode=mode) as normalized:
        for member in archive:
            label = name + "!" + member.name
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts or member.issym() or member.islnk():
                errors.append(f"{label}: unsafe archive member")
                continue
            if member.isfile():
                content = archive.extractfile(member).read()
                if member.name.endswith((".tar.gz", ".tgz", ".tar")):
                    replacement, nested_errors = normalize_archive(content, label, replacements, depth + 1)
                    errors.extend(nested_errors)
                else:
                    replacement = normalize_text(content, replacements)
                    errors.extend(findings(replacement, label))
                changed |= content != replacement
                member.size = len(replacement)
                normalized.addfile(member, io.BytesIO(replacement))
            else:
                normalized.addfile(member)
    return (output.getvalue() if changed and not errors else data), errors


def check(directory, replacements):
    """Normalize UTF-8 files and archive contents before checking for private paths."""
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
                content.decode("utf-8")
            except UnicodeDecodeError:
                errors.append(f"{name}: log is not UTF-8")
                continue
        if name == "package.json":
            manifest = json.loads(content)
            package_kind = manifest.get("packageKind", {})
            if package_kind.get("root") == [str(Path.cwd())]:
                package_kind["root"] = ["."]
                content = (json.dumps(manifest, indent=2) + "\n").encode()
        errors.extend(findings(name.encode(), name))
        if path.name.endswith((".tar.gz", ".tgz", ".tar")):
            content, archive_errors = normalize_archive(content, name, replacements)
            errors.extend(archive_errors)
        else:
            content = normalize_text(content, replacements)
            errors.extend(findings(content, name))
        if content != path.read_bytes():
            path.write_bytes(content)
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
