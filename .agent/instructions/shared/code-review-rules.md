---
description: Flag unsupported public claims, undocumented public API, and unrecorded or untested behavior changes in a swift-library package.
---
## Code Review Rules

### Public claims

- Flag README, DocC or release-note statements that the code, tests and CI do
  not support: missing capabilities, existing behavior described as new, or
  platforms CI does not build. Flag public prose that compares the package
  with other projects or describes internal process. Safe path: state only
  this package's verified behavior.

### Public documentation

- Flag a new public symbol without a documentation comment. Safe path:
  document what the symbol does and how it fails.

### Behavior and compatibility

- Flag a change to public API or observable behavior, including serialized
  output, products, traits and raised minimum platform, Swift tools or
  toolchain versions, that lacks a test failing before the change or a
  `CHANGELOG.md` entry under `## Unreleased` as the
  [organization VERSIONING](https://github.com/swift-library/.github/blob/master/VERSIONING.md)
  requires. Safe path: add the test, record the change, mark breaking changes
  **Breaking** with the new minimums or upgrade path, and leave the version
  bump to release preparation.
