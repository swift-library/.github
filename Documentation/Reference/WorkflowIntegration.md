# Workflow Integration

Package-local `.github/release.json` owns the version file and extraction pattern,
changelog path, check command, CI matrix and supported platform generations.
The check command runs in the caller's checkout. Each matrix entry defines a
unique name, hosted runner and optional installed Xcode version, macOS Swift toolchain version and check command.
The `swift` field installs an official release toolchain after selecting Xcode;
that Xcode still owns the Darwin SDK. Validate compiler and SDK compatibility together.
Use a format-only entry with a consistent formatter toolchain, and compiler-check
entries for each supported compiler. All entries must pass for acceptance.

`swift-package-ci.yml` accepts a configuration path and optional source ref. It
checks out one commit, runs the declared matrix with read permissions, preserves
logs, and returns that source commit. Failed matrix jobs fail the reusable call.
The `result` job runs after both configuration and the matrix. It succeeds only
when both succeeded, so callers can require `validate / result` without coupling
branch rules to individual compiler or platform names.

`swift-package-release.yml` accepts an existing version tag and the accepted
commit returned by the successful validation workflow. Its publication job
checks tag identity, calls the package's `Scripts/validate-version`, downloads
the same run's validation artifacts, and publishes a matching draft. Its token
has contents write and actions read permissions. It does not build source.

Call both workflows using their full shared-repository commit SHA. The caller's
publication job depends on the successful validation call and grants the write
permission explicitly. Keep version selection and tag creation outside the
publication workflow.

The package's version checker supports `--tag`, `--require-clean`, `--notes` and
`--json`. It checks the canonical SemVer declaration, one nonempty Changelog
entry and an existing tag at the candidate commit. Its JSON identifies source,
dependency lock and checker digests. The package check command adds toolchain,
OS, SDK and completed check evidence to `.build/release-validation`.

Review shared changes in their owning repository, validate workflow syntax, and
exercise them through a consumer before upgrading another caller's pin. Generated
packages use the template's stamping command to set their repository identity,
module name and copyright owner before their first validation or publication.

## Source policy

Call `.github/workflows/policy.yml` at the same reviewed full commit SHA from a
job named `policy`. The caller runs on pull requests and default-branch pushes
with `contents: read`; the required check is `policy / policy`. The workflow
checks every commit in the event's source range against GitHub's verification
record, the declared owner identity, and attribution rules. It scans added
lines and paths, then invokes the caller's `Scripts/validate-version` when that
file exists. An initial push checks the complete initial history.

The `allow-terms` input lists identifiers and product names required by the
repository, one per line. A pagination cursor or CSS cursor keyword retains
its own meaning. It does not exempt private paths or plan files. `allow-bots` lists bot
logins permitted for author or committer identity; their commits must still be
Verified. Keep both lists limited to the repository's actual public surface.
Shared policy sources and their tests name all supported tools, so this
repository declares those names in its own caller.

`Scripts/check-policy.py` owns the policy implementation. Run
`python3 Scripts/sync-policy-workflow.py` after editing it. The generated
workflow embeds that implementation so a caller checkout cannot replace the
policy script. `Scripts/check` checks this derivation, tests the behavior and
lints the workflows.

Before changing required checks, run the new pinned caller and verify its
actual check names. Update the required-check table and GitHub rules together,
then run `Scripts/check-settings.py` with an organization administrator's
read access. That check compares live merge settings, token permissions,
rulesets, credential metadata and App installations with the declaration in
`MAINTENANCE.md`. A permission or API failure is an unverified result and exits
nonzero; the checker never changes settings or reads secret values.

## Validation evidence

The shared package CI normalizes the current checkout, home and temporary
paths in UTF-8 `.log` files before uploading artifacts. SwiftPM's captured
manifest root is made relative to the package; dependency locations retain
their values and are checked. The gate rejects remaining
private execution paths and plan references in UTF-8 evidence, including the
contents of compressed DocC and nested evidence archives. Binary artifacts
retain their bytes; they are not interpreted as text. Symlinks and unsafe tar
members fail the gate. A failed gate prevents the evidence upload and fails
validation.

`Scripts/check-evidence.py` owns this gate. Run
`python3 Scripts/sync-evidence-workflow.py` after editing it; `Scripts/check`
verifies the embedded reusable-workflow copy. Package producers should still
emit portable logs locally. The shared gate enforces the upload boundary for
all package consumers and preserves meaningful product and dependency names.
