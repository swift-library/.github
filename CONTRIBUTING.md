# Contributing

External contributions are welcome. Report a bug or propose a behavior change in
an issue in the affected repository when you want the maintainers to act on
it. A pull request that makes the change itself describes it and needs no
separate issue; keep it focused on that change. Read the repository's README,
agent guide and documented checks first.

Commit subjects and pull-request titles follow Conventional Commits:
`type(scope)!: subject`, with optional scope and breaking-change marker. Use
`build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`,
`style` or `test`. Describe the resulting behavior and compatibility impact.
Do not add attribution trailers or private execution context to contributions.

Run the affected repository's declared checks before pushing and include the
results in the pull request. Here, run `actionlint`, `git diff --check` and
check relative Markdown links. Render the profile, social previews and terminal
SVGs locally with the
[github-readme-design toolchain](https://github.com/showxu/skills/blob/master/skills/github-readme-design/references/renderers.md).
Use its `profile check`, `social-preview check` and `terminal check` commands
for the outputs you change; [DESIGN.md](DESIGN.md#organization-profile-and-catalog)
shows the profile commands. CI checks organization membership and About text
through the shared organization workflow. Actions and reusable workflows use
full commit SHAs.

Open pull requests against `master`. Required checks must pass and review
threads must be resolved before the reviewed head is squash-merged. The PR
title becomes the merge subject and its body is empty. Maintainers follow the
[signing setup](https://github.com/swift-library/.github/blob/master/MAINTENANCE.md#signing).
External contributors retain their own author identity.

Each package owns its source, version, compatibility surface and changelog.
Follow the shared
[versioning standard](https://github.com/swift-library/.github/blob/master/VERSIONING.md)
for changes to those contracts.

Participation follows the
[code of conduct](https://github.com/swift-library/.github/blob/master/CODE_OF_CONDUCT.md).
Report vulnerabilities through the affected repository's private Security
reporting route. [Support](https://github.com/swift-library/.github/blob/master/SUPPORT.md)
describes where to ask usage questions.

## New packages

Create a repository from
[swift-package-template](https://github.com/swift-library/swift-package-template)
and follow its identity setup. Declare package validation in
`.github/swift-package.json` and release metadata in `.github/release.json`.
Use the [github-workflows README](https://github.com/swift-library/github-workflows#readme)
for the job catalog, caller interfaces and pinning, and the
[shared CI contract](https://github.com/swift-library/skills/blob/master/skills/swiftpm-github-release/references/shared-ci.md)
for package requirements. Declare exactly `policy / policy` and
`validate / result` as required checks, and add the repository to the
[maintenance declaration](MAINTENANCE.md#settings-declaration) and profile catalog.
