# Versioning and Release

The default branch for organization standards, templates and adopted packages is
`master`. Each repository owns its history and release versions.

This document owns the organization's defaults for participating Swift packages.
Package-local release policy records the package's version owner, compatibility
surface, platform window and validation entry points. Existing policy documents
retain their role when a package adopts these defaults.

## Compatibility and Versions

Each repository releases independently using Semantic Versioning 2.0.0. Tags
use `vMAJOR.MINOR.PATCH`, with optional `-alpha.N`, `-beta.N` or `-rc.N` suffixes;
N begins at one. Version selection and compatibility review are manual.

| Released change | During 0.x | From 1.0.0 |
| --- | --- | --- |
| Compatible bug fix | PATCH | PATCH |
| Compatible feature | MINOR | MINOR |
| Incompatible API, output, CLI, or requirement change | MINOR | MAJOR |

Reset lower components when increasing MINOR or MAJOR. Package products share
the repository version unless their ownership document defines independent
release units. Library consumers should use a next-minor dependency range during
0.x development. Documentation, formatting and CI changes alone do not require
a product release.

One declaration owns a package's release version: a runtime version declaration
for executable packages, or a package-local VERSION file for source libraries.
The matching CHANGELOG entry explains the shipped behavior and upgrade reason.
Checks fail on drift and leave declarations unchanged. A Git tag binds the version
to one accepted source commit; installed binaries do not choose the next version.

## Apple Platform Window

Participating packages support the three most recent formally released major
generations of each Apple platform they declare. Count actual releases rather
than subtracting from the displayed version number. Package.swift owns deployment
floors; package-local policy records the selected generations.

Review the window when selecting a release. New system releases do not edit
existing tags or automatically raise deployment floors. Raising a system or
compiler minimum is a compatibility change under the version table above.

Swift compiler and SwiftSyntax requirements are maintained independently of the
system window. Record the toolchain, OS and SDK combinations actually tested.
Compile checks, simulator runs and native runtime runs are distinct evidence.
Prerelease operating systems and toolchains are optional compatibility probes.

## Licensing and Ownership

New self-owned Swift libraries use Apache License 2.0 with the Swift Runtime
Library Exception (`Apache-2.0 WITH Swift-exception`). Include the full license
and exception text, accurate project copyright notice and source identifiers.

Review existing code ownership before a license migration. Preserve licenses,
copyright notices and required attribution for copied or adapted code. Referenced
designs and package dependencies are distinguished from incorporated source.
Existing repositories and upstream-derived packages retain their license until
their owners approve a migration.

## Candidate Acceptance and Publication

Build, test, formatting and consumer validation run on an identified candidate.
Release acceptance requires a clean committed source tree, consistent version
and changelog, dependency lock review, declared compiler compatibility and
platform evidence. Library consumers must work from the remote candidate and
subsequently its SemVer tag using a fresh dependency graph.

CI records commit/tree, dependency lock digest, toolchain, OS, SDK and validation
logs. Preserve evidence as build artifacts and release attachments. A changed
source revision, dependency lock, configuration or checker needs fresh affected
validation. Temporary execution state belongs in ignored build output.

Published tags and source identities are immutable. Correct an untagged failed
candidate under the same intended version. A tagged source correction needs a
new version. Retry an interrupted publication with the same tag and verified
release notes; an existing published release is checked rather than overwritten.

Validation jobs use read-only repository permissions. Publication is a separate
job with scoped contents write permission after successful validation. Workflow
callers pin the shared workflow's complete commit SHA. Binary distribution adds
artifact-specific installation acceptance under its owning package policy.

## Maintenance

Maintain the latest released line by default. Older-line security and correctness
backports are decided per issue and documented when shipped. Keep prior releases
and changelog entries available.

Dependabot checks Swift dependencies and GitHub Actions weekly. Updates use pull
requests with compatibility, lockfile, notice and CI review before merging.
Packages publish contributor instructions and a working private security report
route. Existing forks preserve upstream tag and provenance conventions during
incremental adoption.

## References

- [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
- [Swift Runtime Library Exception](https://spdx.org/licenses/Swift-exception.html)
- [Apple SDK and system requirements](https://developer.apple.com/xcode/system-requirements)
