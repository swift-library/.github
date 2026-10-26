---
description: Flag shared policy, workflow and release-claim problems in swift-library's shared standards repository.
---
## Code Review Rules

### Shared policy and ownership

- Flag shared policy that fixes a package-specific version, platform window or
  toolchain outside the owning package. Safe path: derive variable values from
  caller configuration and state only the shared invariant here.

### Workflow compatibility

- Flag a caller change that disagrees with the shared workflow interface or
  required check names. Safe path: follow the github-workflows README and the
  required-check table in MAINTENANCE.md, then validate the pinned caller.

### Claims and release integrity

- Flag an acceptance or release claim without evidence for the identified
  source, or instructions that could replace an immutable published identity.
  Safe path: report the actual validation state and follow `VERSIONING.md`.
