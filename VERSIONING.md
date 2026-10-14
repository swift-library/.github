# Versioning and Release

This is the release standard for every swift-library repository. Each package's
own release policy records its version source, compatibility surface and tested
environments; the rules below are shared. Repository scope and default branches
follow [Maintenance](MAINTENANCE.md#repository-scope).

## Tags

- Each repository releases independently under
  [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).
- Tags are written `vMAJOR.MINOR.PATCH`. Pre-releases append `-alpha.N`,
  `-beta.N` or `-rc.N`, with N starting at 1.
- Tags are signed annotated tags with the message `<repository> X.Y.Z`.

## Choosing the next version

| Released change | During 0.x | From 1.0.0 |
| --- | --- | --- |
| Compatible fix, performance work or documentation correction | PATCH | PATCH |
| Compatible addition | PATCH | MINOR |
| Breaking change | MINOR | MAJOR |

A breaking change is anything that can stop a consumer from building or change
behavior it relies on:

- removing or renaming public API, or changing what it means;
- changing serialized output, CLI options, exit codes, or file locations that
  callers depend on;
- raising a deployment target, the `swift-tools-version`, or the minimum
  toolchain;
- removing a product or a trait;
- moving a dependency to a range that cannot resolve alongside the previous one.

Reset the lower components when MINOR or MAJOR increases. The products of one
repository share its version. CI, formatting, repository hygiene and
documentation changes don't need a release, unless the published documentation
is wrong.

## One version source

Each repository has exactly one declaration of its version:

- libraries use a `VERSION` file at the repository root;
- executables use the source file that `--version` prints.

`.github/release.json` names that declaration with `version_file` and
`version_pattern`. The shared version validator reads that declaration and
checks it against the changelog and, during publication, the signed tag.
Checks fail on drift and never rewrite version inputs. Packages use the
validator embedded in the shared workflows.

## Changelog

`CHANGELOG.md` starts with `## Unreleased`, followed by one `## X.Y.Z` section
per release, newest first. A version's section is its release notes: it
describes shipped behavior, and for a breaking change, how to upgrade.

## Release procedure

1. On a branch based on `master`, update the version source, move the
   unreleased entries under `## X.Y.Z`, and update the README dependency
   snippet to `.upToNextMinor(from: "X.Y.Z")`.
2. Open a Conventional Commit-titled pull request. After required checks pass
   and review threads are resolved, squash-merge its exact reviewed head as
   described in [Maintenance](MAINTENANCE.md#change-flow).
3. Check out the accepted merge commit and create its signed annotated tag:
   `git tag -s vX.Y.Z -m "<repository> X.Y.Z"`. Push it with
   `git push origin vX.Y.Z`.
4. Run the repository's `Release` workflow with that tag. It validates the
   tagged commit through the shared `swift-package-ci.yml`, then the shared
   `swift-package-release.yml` runs its embedded validator with
   `--tag vX.Y.Z --require-clean`, attaches the
   validation evidence and `api-evidence.json`, then publishes the GitHub release.
5. Resolve the new tag from a fresh consumer package.

## Consumers and pins

During 0.x, depend on swift-library packages with `.upToNextMinor(from:)`.
When a swift-library package adopts a breaking minor of another one, it raises
its own pin in the same change; for example, swift-userdefault pins swift-gyb.

## Platforms and toolchains

- Deployment floors use the current Xcode minimums: iOS 15, macOS 12, tvOS 15,
  watchOS 9 and visionOS 1. A package declares higher floors when it needs
  newer APIs.
- Packages test the three most recent formally released major generations of
  each platform they declare. Count actual releases, not version numbers.
- Swift compiler and SwiftSyntax minimums are chosen separately from the system
  window. Release evidence records the toolchain, OS and SDK combinations that
  were actually tested.
- Every package requires Swift 6.0 or later. `minimum_swift` in
  `.github/release.json` equals `swift-tools-version` in `Package.swift` and
  the oldest compiler tested by its `ci` matrix. The shared validator checks
  these declarations; the minimum compiler must have a CI entry.
- Raising any floor or minimum is a breaking change in the table above.
  Existing releases keep their original requirements.

## License

Every swift-library project is licensed under the Apache License 2.0 with the
Swift Runtime Library Exception (`Apache-2.0 WITH Swift-exception`).
Repositories ship the full license and exception text, a `NOTICE` file and SPDX
identifiers in source headers. Because of the exception, code compiled into an
app needs no attribution.

Releases published under an earlier license keep that license. Third-party code
and test data keep their own notices.

## Immutable tags

- Published `v*` tags are never moved or deleted. Repository rulesets block
  tag updates and deletion without bypass actors.
- Published history is not rewritten. An exposed credential is rotated;
  rewriting history does not revoke a credential or remove existing copies.
- A tagged mistake is fixed by a new patch release. A candidate that failed
  before it was tagged is corrected under the same intended version.
- An interrupted publication is retried with the same tag. An existing release
  is checked, never overwritten.

## Acceptance and evidence

A candidate is accepted from a clean committed tree with a consistent version
and changelog, a reviewed dependency lock, passing builds and tests on the
declared compilers and platforms, and a consumer that resolves it from the
remote.

CI records the commit and tree, dependency lock digest, toolchain, OS, SDK and
validation logs. That evidence is kept as build artifacts and attached to the
release; public attachments contain no workstation paths or user names. A
changed source revision, dependency lock, configuration or checker needs fresh
validation.

Validation jobs use read-only repository permissions. Publication is a separate
job with scoped contents write permission. Callers pin the shared workflows by
full commit SHA.

## Public interface evidence

Each release attaches `api-evidence.json`: a versioned envelope binding the
repository and signed tag commit to the collector pin, collection status and
compiler-reported snapshot. The snapshot records its actual toolchain, SDK,
target, scope and gaps. A failed collection records that failure; it does not
manufacture an empty compatible interface. Existing release assets remain
unchanged. For historical releases without this asset, comparison starts when a
subsequent release publishes evidence.

The shared API report compares the candidate commit with the asset on GitHub's
latest published stable release. It verifies the asset digest and binds the
baseline to that release's tag commit. A pull request cannot select or rewrite
the baseline in its source tree. Drafts and pre-releases are excluded from
baseline selection; a pre-release candidate is still compared with the latest
stable release. The same rule applies during 0.x. Version choices continue to
follow the table above.

Comparisons use one pinned collector version for both inputs. When the verified
release asset used a different collector, the shared job checks out that release's
resolved tag commit in its build directory and recollects it with the current pin
before collecting the candidate. The report identifies the release commit, attached
collector and recollection collector. Baseline files stay in build outputs. A failed
recollection reports an unavailable comparison and preserves the candidate's collection
result; evidence from different extractor versions is never compared.

Missing evidence, collection failures, unsupported schemas, incomplete module
coverage and mismatched configurations or scopes are explicit unknown or
incomparable results. They never prove compatibility. Field changes distinguish
interface, documentation, availability and provenance; these observations do
not decide whether behavior changed or which version to publish.

The API job is report-only and is outside required validation. Promoting any
observation into a blocking rule requires a separate owner-approved policy
change, representative consumer evidence across supported configurations,
documented failure and exception behavior, and a reviewed required-check
update. Existing package-owned API checks retain their own authority until
separately reviewed for replacement.

## Maintenance

The latest released line is maintained. Backports to older lines are decided
per issue and documented when shipped. Dependabot checks Swift dependencies and
GitHub Actions weekly; updates arrive as pull requests and need compatibility,
lockfile, notice and CI review before merging. Every package publishes
contributor instructions and a private security reporting route.

## References

- [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html)
- [Swift Runtime Library Exception](https://spdx.org/licenses/Swift-exception.html)
- [Xcode support and minimum deployment targets](https://developer.apple.com/support/xcode/)
- [Workflow integration](Documentation/Reference/WorkflowIntegration.md)
