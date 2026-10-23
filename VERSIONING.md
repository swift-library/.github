# Versioning and Release

This is the release standard for every swift-library repository except
swift-package-template, which is not versioned; new packages are created from
its default branch. Each package's release reference,
`Documentation/Reference/Release.md`, records its version
source, compatibility surface, tested environments and release entry points;
the rules below are shared. Repository scope and default branches follow
[Maintenance](MAINTENANCE.md#repository-scope).

## Tags

- Each repository releases independently under
  [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).
- Tags are written `vMAJOR.MINOR.PATCH`. Pre-releases append `-alpha.N`,
  `-beta.N` or `-rc.N`, with N starting at 1.
- Tags are signed annotated tags with the message `<repository> X.Y.Z`.

## When to release

Where a delivery workflow governs the project, it decides when to release;
otherwise:

Release once a change is complete: everything it needs, including
documentation, is merged and verified. A change that spans several pull
requests or repositories releases once, when all of it has landed, or at
milestones its owner names before the work starts. Its intermediate steps,
review fixes, documentation fixes and pin updates do not release on their own.

## Choosing the next version

### 0.x (initial development)

Anything may change at any time, without deprecation windows or a release
cadence. Breaking changes bump MINOR; everything else bumps PATCH.

### 1.0.0

Release `1.0.0` when the owner decides the interface is stable and
compatibility is promised.

### 1.0 and later

Change an interface by adding the new form compatibly, keeping the old form
working and deprecating it. Remove the old form only in a planned major.

Breaking changes appear only in planned majors, on a roughly yearly cadence
like platform releases. A major may also mark a significant feature release.
Never cut a major because of a single change.

New features, including value or output changes consumers absorb without
changing their usage, bump MINOR. Fixes, performance work and documentation
corrections bump PATCH.

Reset less significant components to zero when bumping MAJOR or MINOR.
Version numbers never tagged or published to users do not constrain the first
release, which may start at `0.1.0`.

### Breaking changes

A breaking change is anything that can stop a consumer from building or change
behavior it relies on:

- removing or renaming public API, or changing what it means;
- changing serialized output, CLI options, exit codes, or file locations that
  callers depend on;
- raising a deployment target, the `swift-tools-version`, or the minimum
  toolchain;
- removing a product or a trait;
- moving a dependency to a range that cannot resolve alongside the previous one.

The products of one repository share its version. CI, formatting, repository
hygiene and documentation changes don't need a release, unless the published
documentation is wrong.

## One version source

Each repository has exactly one declaration of its version:

- libraries and plugin collections use a `VERSION` file at the repository root;
- executables use the source file that `--version` prints.

A plugin collection's manifest versions and its marketplace `metadata.version`
mirror `VERSION` and must equal it.

Swift packages name that declaration in `.github/release.json` with
`version_file` and `version_pattern`. The shared version validator reads that
declaration and checks it against the changelog and, during publication, the
signed tag. Checks fail on drift and never rewrite version inputs. Packages use
the validator in
[github-workflows](https://github.com/swift-library/github-workflows#readme).

## Changelog

`CHANGELOG.md` starts with `## Unreleased`, followed by one `## X.Y.Z` section
per release, newest first. A version's section is its release notes: it
describes shipped behavior, and for a breaking change, how to upgrade.
From `1.0` onward, record deprecations in the changelog and list a planned
major's removals beforehand.

## Release procedure

1. On a branch based on `master`, update the version source and its mirrors and
   move the unreleased entries under `## X.Y.Z`. Swift packages also update the
   README dependency snippet to `.upToNextMinor(from: "X.Y.Z")`.
2. Open a Conventional Commit-titled pull request. After required checks pass
   and review threads are resolved, squash-merge its exact reviewed head as
   described in [Maintenance](MAINTENANCE.md#change-flow).
3. Check out the accepted merge commit and create its signed annotated tag:
   `git tag -s vX.Y.Z -m "<repository> X.Y.Z"`. Push it with
   `git push origin vX.Y.Z`.
4. Swift packages call the shared `swift-package.yml` workflow to validate the
   tagged commit, then call `swift-package-release.yml` to verify the accepted
   commit, signed annotated tag, version declaration and changelog entry and
   publish the release notes. The
   [github-workflows README](https://github.com/swift-library/github-workflows#calling-release)
   defines the caller. Other repositories publish as their release reference
   describes.

## Consumers and pins

During 0.x, depend on swift-library packages with `.upToNextMinor(from:)`.
When a swift-library package adopts a breaking minor of another one, it raises
its own pin in the same change; for example, swift-userdefault pins swift-gyb.

## Platforms and toolchains

These rules apply to Swift packages.

- Deployment floors use the current Xcode minimums: iOS 15, macOS 12, tvOS 15,
  watchOS 9 and visionOS 1. A package declares higher floors when it needs
  newer APIs.
- Packages test the three most recent formally released major generations of
  each platform they declare. Count actual releases, not version numbers.
- Swift compiler and SwiftSyntax minimums are chosen separately from the system
  window. CI job results record the toolchain, OS and SDK combinations that
  were actually tested.
- Every package requires Swift 6.0 or later. `minimum_swift` in
  `.github/release.json` equals `swift-tools-version` in `Package.swift` and
  the oldest compiler tested by the `compilers` list in
  `.github/swift-package.json`. The shared validator checks
  these declarations; the minimum compiler must have a CI entry.
- Raising any floor or minimum is a breaking change.
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

## Acceptance

Acceptance is a signed annotated tag on a commit whose shared validation passed,
with a consistent version declaration and changelog entry. The tag identifies
that accepted source. A changed source revision or validation configuration
requires fresh validation.

The shared Swift package workflows run validation with read-only repository
permissions and publication as a separate job with scoped contents write
permission. Callers pin the shared workflows by full commit SHA.

## Public interface changes

Maintainers assess public interface and behavior changes against
[Choosing the next version](#choosing-the-next-version), and describe the
compatibility impact in the changelog entry. The signed tag identifies the
released interface and its version declaration.

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
- [Shared workflows](https://github.com/swift-library/github-workflows#readme)
- [Shared CI contract](https://github.com/swift-library/skills/blob/master/skills/swiftpm-github-release/references/shared-ci.md)
