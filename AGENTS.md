# swift-library Shared Standards Agent Guide

Read README.md first. This repository owns shared policy, community documents,
the profile catalog and design sources. Shared automation belongs to swift-library/github-workflows.
Package-specific source, versions and validation remain in each package.

## First-Principles Work

Name the affected behavior, owning package, compatibility invariant, variable
inputs and validation before editing. Caller changes need syntax validation
and a pinned workflow run before adoption.

## Canonical Artifacts

- Treat conversation, review feedback, plans, and intermediate attempts as
  editing input. Recompute the complete accepted result before finalizing.
- Active artifacts depend only on that result and their repository role, not
  on the editing path. Apply this to code, symbols, files, wrappers, branches,
  configuration, schemas, defaults, generated sources, scripts, templates,
  automation, comments, DocC, diagrams, tests, fixtures, snapshots, examples,
  and normative docs.
- If an intermediate result is `A + B` and the accepted result is `A`, express
  `A` directly. Remove `B` and its residual surface rather than retaining names
  such as `AOnly` or `AWithoutB`, or prose such as "B was removed."
- Normalize by semantic identity and artifact role, not by token. A rejected
  current capability does not invalidate a distinct historical fact,
  migration, ownership record, or safety boundary that uses the same term.
- Keep a negative constraint only when excluding `B` is independently required
  by a current compatibility, safety, or ownership invariant.
- A disabled B flag, skipped B test, dead B branch, retained B fixture, or
  "do not add B" rule is residue when it exists only because B was attempted;
  disabled state alone is not an invariant.
- Keep change history only in commits, pull requests, changelogs, release
  records, migrations, archives, or accepted decision records with durable
  value. Do not create a history artifact merely to preserve a correction.
- Preserve role-owned facts unless separate evidence changes them; do not
  rewrite history or ownership merely to make a rejected term disappear.
- Leave an already-correct history, migration, provenance, ownership, or safety
  artifact unchanged when the task does not change its facts. Do not polish or
  restate it merely because it is relevant to the current edit.
- Comments explain non-obvious current semantics and invariants, not the
  sequence of edits.
- Before handoff, verify that a new agent with no editing conversation can
  derive the complete current behavior, boundaries, and operating guidance
  without mentally subtracting a rejected concept.

## Task Route

Read VERSIONING.md before changing release policy. Read MAINTENANCE.md before
changing a GitHub setting, ruleset, App, or required check, and update it in
the same pull request. Change the package template's generated files through
their producers and the [composition](MAINTENANCE.md#package-template), not in
the template. Package adoption belongs in
[CONTRIBUTING.md](CONTRIBUTING.md#new-packages); workflow interfaces belong in the
[github-workflows README](https://github.com/swift-library/github-workflows#readme).
Keep thin callers in .github/workflows and variable values in package-owned
configuration. Render presentation assets locally with the
[github-readme-design toolchain](https://github.com/showxu/skills/blob/master/skills/github-readme-design/references/renderers.md).

## Authority

VERSIONING.md owns current shared release policy. Each caller repository
owns its source, package graph, version declaration and changelog.

## Boundary Guardrails

Derive repository, version, toolchain and platform values from caller inputs or
package-owned configuration. Keep run outputs in ignored build directories.
Preserve existing source ownership and historical records.

## Validation

Run actionlint for caller changes, git diff --check and relative Markdown link
checks. Run the local profile check against profile/README.md using the commands
in DESIGN.md. Verify a pinned workflow run before adopting a caller revision.

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
