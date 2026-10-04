# Workflow Integration

Package-local `.github/release.json` owns the version file and extraction pattern,
changelog path, check command, CI matrix and supported platform generations.
The check command runs in the caller's checkout. Each matrix entry defines a
unique name, hosted runner and optional installed Xcode version, Swift toolchain version and check command.
The `swift` field installs an official release toolchain after selecting Xcode;
that Xcode still owns the Darwin SDK. Validate compiler and SDK compatibility together.
Use a format-only entry with a consistent formatter toolchain, and compiler-check
entries for each supported compiler. All entries must pass for acceptance.

`swift-package-ci.yml` accepts a configuration path and optional source ref. It
checks out one commit, runs the declared matrix with read permissions, preserves
logs, and returns that source commit. Failed matrix jobs fail the reusable call.

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
