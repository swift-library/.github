---
description: Route changes in swift-library's shared standards repository to their owning documents and checks.
---
# swift-library Shared Standards Agent Guide

Read `README.md` first. This repository owns shared policy, community
documents, the profile catalog, design sources and the instruction units that
member packages install. Shared automation belongs to
swift-library/github-workflows. Package-specific source, versions and
validation remain in each package.

## Task Route

- Read `VERSIONING.md` before changing release policy.
- Read `MAINTENANCE.md` before changing a GitHub setting, ruleset, App or
  required check, and update it in the same pull request.
- Change the package template's generated files through their producers and
  the [composition](MAINTENANCE.md#package-template), not in the template.
  Package adoption belongs in [CONTRIBUTING.md](CONTRIBUTING.md#new-packages);
  workflow interfaces belong in the
  [github-workflows README](https://github.com/swift-library/github-workflows#readme).
- `.agent/instructions/shared/` holds the instruction units member packages
  install. A change there reaches a package when that package regenerates its
  `AGENTS.md`; state only rules that hold for every member package.
- Keep thin callers in `.github/workflows` and variable values in
  package-owned configuration.
- Render presentation assets locally with the
  [github-readme-design toolchain](https://github.com/showxu/skills/blob/master/skills/github-readme-design/references/renderers.md).

## Validation

Run actionlint for caller changes, `git diff --check` and relative Markdown
link checks. Run the local profile check against `profile/README.md` using the
commands in `DESIGN.md`. Verify a pinned workflow run before adopting a caller
revision.
