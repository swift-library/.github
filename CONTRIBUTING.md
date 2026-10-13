# Contributing

External contributions are welcome. Open an issue in the affected repository
for a bug or proposed behavior, then keep the pull request focused on that
change. Read the repository's README, agent guide and documented checks first.

Commit subjects and pull-request titles follow Conventional Commits:
`type(scope)!: subject`, with optional scope and breaking-change marker. Use
`build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`,
`style` or `test`. Describe the resulting behavior and compatibility impact.
Do not add attribution trailers or private execution context to contributions.

Run the repository's declared checks before pushing. For Swift packages this
is normally `Scripts/check`. Include the relevant results in the pull request.
Shared workflow changes also need a consuming repository run at the proposed
pin. Actions and reusable workflows use full commit SHAs.

Open pull requests against `master`. Required checks must pass and review
threads must be resolved before the reviewed head is squash-merged. The PR
title becomes the merge subject and its body is empty. Maintainers follow the
[signing setup](https://github.com/swift-library/.github/blob/master/MAINTENANCE.md#signing).
External contributors retain their own author identity.

Each package owns its source, version, compatibility surface and release
evidence. Follow the shared
[versioning standard](https://github.com/swift-library/.github/blob/master/VERSIONING.md)
for changes to those contracts. Shared repository checks run with `Scripts/check`.

Participation follows the
[code of conduct](https://github.com/swift-library/.github/blob/master/CODE_OF_CONDUCT.md).
Report vulnerabilities through the affected repository's private Security
reporting route. [Support](https://github.com/swift-library/.github/blob/master/SUPPORT.md)
describes where to ask usage questions.
