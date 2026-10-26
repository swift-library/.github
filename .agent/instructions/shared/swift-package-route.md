---
description: Route a swift-library package change to its versioning, release, CI and documentation owners.
---
## Package Route

- Read `README.md` and `CONTRIBUTING.md` before editing.
- Before changing versions, dependencies, packaging or release workflows, read
  the [organization VERSIONING](https://github.com/swift-library/.github/blob/master/VERSIONING.md),
  `.github/release.json` and, when present, `Documentation/Reference/Release.md`.
- `.github/swift-package.json` declares CI validation, and `CONTRIBUTING.md`
  names the required checks. Run the local checks in `CONTRIBUTING.md` before
  handing off.
- Read toolchain, platform and deployment minimums from `Package.swift` and
  `.github/swift-package.json` instead of restating them.
- When `Documentation/README.md` exists, read it before changing documentation,
  and read the architecture documents it lists before changing package
  structure.
