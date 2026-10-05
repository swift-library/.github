# Versioning and Release

This is the release standard for every swift-library repository. Each package's
own release policy records its version source, compatibility surface and tested
environments; the rules below are shared. The default branch is `master`.

## Tags

- Each repository releases independently under
  [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).
- Tags are written `vMAJOR.MINOR.PATCH`. Pre-releases append `-alpha.N`,
  `-beta.N` or `-rc.N`, with N starting at 1.
- swift-gyb's `0.0.1` and `0.0.2` were published without the prefix and stay as
  published. SwiftPM orders both spellings correctly.

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
`version_pattern`, and `Scripts/validate-version` reads nothing else. Checks
fail on drift and never rewrite the declaration.

## Changelog

`CHANGELOG.md` starts with `## Unreleased`, followed by one `## X.Y.Z` section
per release, newest first. A version's section is its release notes: it
describes shipped behavior, and for a breaking change, how to upgrade.

## Release procedure

1. On `master`, make one commit that bumps the version source, moves the
   unreleased entries under `## X.Y.Z`, and updates the README dependency
   snippet to `.upToNextMinor(from: "X.Y.Z")`.
2. When CI passes on that commit, tag it `vX.Y.Z` and push the tag.
3. Run the repository's `Release` workflow with that tag. It validates the
   tagged commit through the shared `swift-package-ci.yml`, then the shared
   `swift-package-release.yml` runs
   `Scripts/validate-version --tag vX.Y.Z --require-clean`, attaches the
   validation evidence and publishes the GitHub release.
4. Resolve the new tag from a fresh consumer package.

## Consumers and pins

During 0.x, depend on swift-library packages with `.upToNextMinor(from:)`.
When a swift-library package adopts a breaking minor of another one, it raises
its own pin in the same change; for example, swift-userdefault pins swift-gyb.

## Platforms and toolchains

- Deployment floors are never lower than the oldest targets the current Xcode
  release can build for. For Xcode 27 these are iOS 15, macOS 12, tvOS 15 and
  watchOS 9. A package declares higher floors when it needs newer APIs.
- Packages test the three most recent formally released major generations of
  each platform they declare. Count actual releases, not version numbers.
- Swift compiler and SwiftSyntax minimums are chosen separately from the system
  window. Release evidence records the toolchain, OS and SDK combinations that
  were actually tested.
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

- A published tag never moves. Repository rulesets block updating or deleting
  `v*` tags, and only organization admins can bypass them.
- A tagged mistake is fixed by a new patch release. A candidate that failed
  before it was tagged is corrected under the same intended version.
- An interrupted publication is retried with the same tag. An existing release
  is checked, never overwritten.

## History cleanup

Content that has to leave a public history is removed by rewriting the existing
repository and force-pushing it. A repository is deleted and recreated only when
its owner explicitly asks for that.

1. Merge or close open pull requests, and rotate any exposed credential first.
2. Rewrite, verify, and force-push the branches and tags.
3. If published tags moved, publish a new patch release right away so consumers
   have a version that never moved.

Rewritten commits stay reachable by SHA, through pull request refs, and in
forks and existing clones. That residue is accepted.

Consumers that resolved a tag before it moved get a SwiftPM fingerprint error
saying the revision "does not match previously recorded value". They recover by
updating to the new patch release, or by deleting that package's file in
`~/Library/org.swift.swiftpm/security/fingerprints/` (macOS) or
`~/.swiftpm/security/fingerprints/` (Linux) and resolving again.

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
