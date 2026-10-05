# Contributing

Keep each Swift package's code, version decisions and release evidence in its
own repository. Read its contributor and release policy before changing it.

For this shared repository, describe the affected package behavior in the pull
request. Changes to workflows need workflow syntax validation and a consumer
workflow run before dependent repositories update their pinned commit.

Every change lands through a pull request with green required checks and
resolved review threads; [MAINTENANCE.md](MAINTENANCE.md) describes the flow.
Use Conventional Commits for commit subjects. Shared workflow references and
third-party actions are pinned to full commit SHAs. Maintenance updates require
review and preserve package-local policy ownership.
