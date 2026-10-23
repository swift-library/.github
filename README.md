<div align="center">

<p align="center">
  <a href="https://github.com/swift-library/.github"><img src="Documentation/Assets/Logo.svg" width="160" alt=".github logo"></a>
</p>

<h1 align="center">.github</h1>

<p align="center">
  Publish independently versioned Swift packages with shared checks.
</p>

<p align="center">
  <a href="https://github.com/swift-library/.github/actions/workflows/ci.yml"><img src="https://github.com/swift-library/.github/actions/workflows/ci.yml/badge.svg?branch=master" alt="CI"></a>
  <a href="LICENSE.txt"><img src="https://img.shields.io/badge/license-Apache--2.0-blue?style=flat" alt="License: Apache-2.0 WITH Swift-exception"></a>
</p>

<p align="center">
  <a href="#overview">Overview</a> ·
  <a href="#quick-look">Quick look</a> ·
  <a href="#install">Install</a> ·
  <a href="#usage">Usage</a> ·
  <a href="#requirements">Requirements</a> ·
  <a href="#documentation">Documentation</a> ·
  <a href="#contributing">Contributing</a> ·
  <a href="#license">License</a>
</p>

</div>

## Overview

This repository holds the organization profile, catalog, community guidance, release policy and design sources. Shared CI and checkers live in [github-workflows](https://github.com/swift-library/github-workflows#readme); each package owns its source and validation configuration.

## Quick look

Call the shared validation workflow from a package:

```yaml
jobs:
  validate:
    uses: swift-library/github-workflows/.github/workflows/swift-package.yml@c73e5121f19dd64e85d3b506dfae95685647d065
```

## Install

Follow [package adoption](CONTRIBUTING.md#new-packages) to add package-owned configuration and callers pinned to full commit SHAs. Start a new repository with the [package template](https://github.com/swift-library/swift-package-template).

## Usage

Keep source, versions, compatibility, and validation commands in each package. Use [VERSIONING.md](VERSIONING.md) for release decisions, [MAINTENANCE.md](MAINTENANCE.md) for contribution and GitHub governance, and [DESIGN.md](DESIGN.md) for the shared presentation system.

## Requirements

- GitHub Actions for reusable workflow callers
- actionlint for caller syntax and GitHub CLI for live settings reads
- The [github-readme-design toolchain](https://github.com/showxu/skills/blob/master/skills/github-readme-design/references/renderers.md) for local rendering and checks
- The compiler, SDK, and platform declarations owned by each consuming package

## Documentation

- [Versioning and release](VERSIONING.md)
- [Shared workflow interfaces](https://github.com/swift-library/github-workflows#readme)
- [Package adoption](CONTRIBUTING.md#new-packages)
- [Design system](DESIGN.md)
- [Maintenance](MAINTENANCE.md)
- [Security reporting](SECURITY.md)

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) for local validation before submitting a pull request. Follow the [code of conduct](CODE_OF_CONDUCT.md) and [support guide](SUPPORT.md).

## License

[Apache-2.0 WITH Swift-exception](LICENSE.txt). Each package retains its own source and dependency notices.
