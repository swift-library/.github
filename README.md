<div align="center">

<p align="center">
  <a href="https://github.com/swift-library/.github"><img src="Documentation/Assets/Logo.svg" width="160" alt=".github logo"></a>
</p>

<h1 align="center">.github</h1>

<p align="center">
  Publish independently versioned Swift packages with shared checks and release evidence.
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

Connect a package’s own check command and compiler matrix to reusable validation and publication workflows. Pull requests report public API changes for maintainer review, and releases attach validation results and a scoped API snapshot; the [workflow reference](Documentation/Reference/WorkflowIntegration.md) explains caller inputs and collection gaps.

## Quick look

Call the shared validation workflow from a package:

```yaml
jobs:
  validate:
    uses: swift-library/.github/.github/workflows/swift-package-ci.yml@9aa78ca8d6346242460006178b9808114beee9f8
```

## Install

Follow [workflow integration](Documentation/Reference/WorkflowIntegration.md) to add package-owned release configuration and callers pinned to full commit SHAs. Start a new repository with the [package template](https://github.com/swift-library/swift-package-template).

## Usage

Keep source, versions, compatibility, and validation commands in each package. Use [VERSIONING.md](VERSIONING.md) for release decisions, [MAINTENANCE.md](MAINTENANCE.md) for contribution and GitHub governance, and [DESIGN.md](DESIGN.md) for the shared presentation system.

## Requirements

- GitHub Actions for reusable workflow callers
- Python, actionlint, and GitHub CLI for local standards checks
- The compiler, SDK, and platform declarations owned by each consuming package

## Documentation

- [Versioning and release](VERSIONING.md)
- [Workflow integration](Documentation/Reference/WorkflowIntegration.md)
- [Design system](DESIGN.md)
- [Maintenance](MAINTENANCE.md)
- [Security reporting](SECURITY.md)

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) and run `Scripts/check` before submitting a pull request. Follow the [code of conduct](CODE_OF_CONDUCT.md) and [support guide](SUPPORT.md).

## License

[Apache-2.0 WITH Swift-exception](LICENSE.txt). Each package retains its own source and dependency notices.
