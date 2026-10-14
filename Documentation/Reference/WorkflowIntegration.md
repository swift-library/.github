# Workflow Integration

Package-local `.github/release.json` owns the version file and extraction pattern,
changelog path, check command, CI matrix, supported platform generations and
minimum Swift compiler. The shared keys are:

| Key | Meaning |
| --- | --- |
| `repository` | Canonical owner/repository identity |
| `version_file` | Path to the package's canonical version declaration |
| `version_pattern` | Regular expression with one version capture |
| `changelog` | Path to the release notes |
| `check_command` | Default package validation command |
| `ci` | Matrix with an `include` list of validation jobs |
| `platforms` | Package-owned supported platform generations |
| `minimum_swift` | Minimum tested Swift compiler, equal to `swift-tools-version` |

Other keys belong to the package's own check scripts. Compiler jobs include
`swift-X.Y` or `swift-X.Y.Z` in their hyphen-separated name; formatting-only jobs
have no compiler label. The lowest declared compiler must equal `minimum_swift`
and be at least 6.0. The optional installed `swift` toolchain must match its job's
compiler major and minor versions. Every declared compiler job runs the package
checks, so validation must pass on the declared minimum.
The check command runs in the caller's checkout. Each matrix entry defines a
unique name, hosted runner and optional installed Xcode version, macOS Swift toolchain version and check command.
The `swift` field installs an official release toolchain after selecting Xcode;
its bundle identifier selects the same compiler for `swift`, `xcrun` and
`xcodebuild`. That Xcode still owns the Darwin SDK. Validate compiler and SDK compatibility together.
Use a format-only entry with a consistent formatter toolchain, and compiler-check
entries for each supported compiler. All entries must pass for acceptance.
Each entry may set `timeout_minutes` to an integer from 1 to 360; omitted values
use 45 minutes. The package owns this execution budget for its validation workload.
Exceeding the budget fails the job and the aggregate validation result.

`swift-package-ci.yml` accepts a configuration path and optional source ref. It
checks out one commit, runs the declared matrix with read permissions, preserves
logs, and returns that source commit. Failed matrix jobs fail the reusable call.
The `result` job runs after both configuration and the matrix. It succeeds only
when both succeeded, so callers can require `validate / result` without coupling
branch rules to individual compiler or platform names.

`swift-package-release.yml` accepts an existing version tag and the accepted
commit returned by the successful validation workflow. Its publication job
checks tag identity and its signature with the embedded shared validator, downloads
the same run's validation artifacts, and publishes a matching draft. Its token
has contents write and actions read permissions. It does not build source.

Call both workflows using their full shared-repository commit SHA. The caller's
publication job depends on the successful validation call and grants the write
permission explicitly. Keep version selection and tag creation outside the
publication workflow.

`Scripts/validate-version` in this repository owns version validation. Packages
use its embedded workflow copies and do not ship a separate validator. It supports
`--root`, `--configuration`, `--tag`, `--require-clean`, `--notes` and `--json`.
It checks the canonical SemVer declaration, one nonempty Changelog entry and the
minimum compiler contract. With `--tag` it requires an annotated tag at the
candidate commit, the message `<repository> X.Y.Z`, and a valid signature from
`git verify-tag`. Local SSH verification uses the signing configuration in
[MAINTENANCE.md](../../MAINTENANCE.md#signing); publication trusts the owner's
public SSH signing keys returned by GitHub.

The CI workflow writes `.build/release-validation/version.json` after each
successful package check. It identifies the source, minimum compiler, dependency
lock and shared checker digests. The package check command adds toolchain, OS,
SDK and completed check evidence to the same directory. Run
`python3 Scripts/sync-version-workflows.py` and
`python3 Scripts/sync-policy-workflow.py` after changing the shared validator.

Review shared changes in their owning repository, validate workflow syntax, and
exercise them through a consumer before upgrading another caller's pin. Generated
packages use the template's stamping command to set their repository identity,
module name and copyright owner before their first validation or publication.

## Source policy

Call `.github/workflows/policy.yml` at the same reviewed full commit SHA from a
job named `policy` in a separate caller, `.github/workflows/source-policy.yml`.
That caller runs on default-branch pushes and the `opened`, `synchronize`,
`reopened` and `edited` pull request activity types, with `contents: read`.
Title corrections rerun only policy. The validation caller runs on
`opened`, `synchronize` and `reopened`, pushes to `master` and
`workflow_dispatch`. Retain its existing job identifiers and required check
contexts, including `validate / result` for shared package validation.
Do not skip validation with a job condition on `edited`: a skipped check on
the same commit can replace a failing required result.

Both callers use workflow-level concurrency:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true
```

The workflow name separates policy from validation. Pull requests group by
number, including contributions from forks; pushes group by branch ref.
Release validation and publication callers have no cancelling concurrency
group. Publication serializes each tag with `cancel-in-progress: false`.
Release validation builds clean, independently of build caches.

The required check is `policy / policy`. Pull requests check the title for
Conventional Commit syntax, attribution and unapproved terms, then scan only
added lines. Contributor identities and signatures do not block pull requests.
Default-branch pushes require every new commit to be GitHub-verified with the
owner or GitHub as committer; external and bot authors are accepted. An initial
push checks the complete initial history. The embedded shared version validator
runs when `.github/release.json` exists.

The `allow-terms` input lists identifiers and product names required by the
repository, one per line. It does not exempt attribution, private paths or plan
files. Keep the list limited to the repository's actual public surface. Shared
policy sources and their tests name all supported tools, so this repository
declares those names in its own caller.

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
paths in every UTF-8 text file before uploading artifacts. SwiftPM's captured
manifest root is made relative to the package. The gate rejects remaining
private execution paths and plan references, including text inside compressed
DocC and nested evidence archives. Archives retain their bytes so package-owned
checksums remain valid; their producers must emit portable text before archiving.
Other binary artifacts retain their bytes and are not interpreted as text. Symlinks and unsafe tar
members fail the gate. A failed gate prevents the evidence upload and fails
validation.

`Scripts/check-evidence.py` owns this gate. Run
`python3 Scripts/sync-evidence-workflow.py` after editing it; `Scripts/check`
verifies the embedded reusable-workflow copy. Package producers should still
emit portable logs locally. The shared gate enforces the upload boundary for
all package consumers and preserves meaningful product and dependency names.

## API evidence and comparison

The shared package CI also runs an independent `api` job. It checks out the
same candidate commit selected by `configure`, including the tested merge
commit on pull requests. Required `result` validation depends only on
`configure` and `check`; the API job has `continue-on-error: true`. Interface
changes, missing baselines and collection or upload failures do not turn this
report into a release gate.

This observation job uses macOS 26 and Xcode 26.6. Those are the collector's
execution configuration, not additional claims about the package's minimum
compiler or supported platforms. Its SwiftPM collection scope is public/open
interfaces of library products, with SPI and source locations excluded. The
snapshot records the actual compiler build, SDK and target. Conditional APIs
outside this configuration remain unobserved; this job does not schedule a
package platform matrix.

`Scripts/api-evidence.py` owns the collector pin, source-archive digest, envelope
schema, baseline acquisition, collection and report orchestration. It builds
that reviewed release of swift-interface-distiller, whose CLI owns extraction
and field-level comparison. It fetches the release baseline before executing
the candidate package and withholds the repository token from build processes.
The embedded script comes from the pinned shared workflow, not a script in the
caller. `Scripts/sync-api-workflows.py` derives both workflow copies and the API
job's evidence gate; run it after changing either API orchestration or the
shared evidence gate. `Scripts/check` verifies all generated copies.

The artifact `api-evidence-<commit>` contains:

- `api-evidence.json`: envelope schema 1, repository, source commit, collector
  identity, `complete`/`incomplete`/`failed` status, reason and a snapshot or null;
- `api-report.json`: report-only comparison status, release and asset identity,
  counts by category and the collector's field-level differences;
- `api-report.md` and `collection.log`: a summary and normalized diagnostics.

The same privacy gate used for validation artifacts checks API evidence before
upload. Publication reads the exact candidate's artifact, verifies its source
identity, and attaches `api-evidence.json` alongside the validation archive. A
missing API artifact yields an explicit failed-collection envelope. An artifact
claiming a different repository or source commit is rejected as invalid
publication evidence. Existing attachments are compared byte-for-byte and are
never overwritten.

Baseline selection uses the latest published stable release's single API asset,
its download digest and its resolved tag commit. A missing release or asset
reports `unavailable`; there is no fallback to committed files or a baseline
rebuilt from candidate-controlled sources. Incomplete evidence reports
`unavailable`, and different toolchain/configuration identities or selection
scopes report `incomparable`. `equal` means equality of these observed snapshots,
not a compatibility guarantee. The release and promotion rules are owned by
[VERSIONING.md](../../VERSIONING.md#public-interface-evidence).

Adopt a reviewed full shared SHA in all policy, validation and release callers
together after a pinned consumer run. Older releases keep their existing assets;
the first release after adoption establishes the remote API baseline. The
package template carries the same pin for new repositories.

## Published icon validation

The shared standards CI checks repository icons on pull requests, master pushes,
manual runs and weekly. Its `icons` job checks out `showxu/skills` at the reviewed
full SHA declared in the workflow, lints `DESIGN.md`, and compares the published
SVGs with that generator. The required `result` check also requires icon success.

`.github/icon-sources.json` maps each design icon to its owning repository and
canonical published path. It must cover every icon in the design family.
`Scripts/check-icons.py --generator PATH` downloads those files from master into
`.build/published-icons` and runs the generator's drift check. A missing file,
API failure, palette finding or byte difference fails validation. It never
updates a repository logo; each owning repository publishes regenerated assets
through its own reviewed change.
