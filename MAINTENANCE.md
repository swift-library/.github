# Maintenance

How changes reach the swift-library repositories, and the GitHub settings that
enforce it. A change to any setting, ruleset, App, or credential updates this
file in the same pull request.

## Change Flow

1. Work on a branch. Commits use the owner's name and noreply email and are
   SSH-signed. Tool identities and attribution trailers never appear.
2. Run the repository's own check before pushing, for a Swift package
   `Scripts/check`.
3. Open a pull request against the default branch.
4. Merge only when every required check is green and every review thread is
   resolved: each automatic review finding is fixed or answered on the pull
   request.
5. Squash-merge the reviewed head commit, for example
   `gh pr merge <number> --squash --match-head-commit <sha>`.

A new repository is the one exception: its prepared, signed history is pushed
once to the empty repository, and the ruleset is applied immediately after.

## GitHub Settings

**Merging.** Squash merge only, with the pull request title as the commit
subject and its commit messages as the body. Merge commits and rebase merges
are off, and merged branches are deleted.

**Workflow token.** The default `GITHUB_TOKEN` permission is `read`, and
workflows cannot approve pull requests, at organization and repository level.
Each workflow declares the permissions it needs.

**Rulesets.** Every public repository has two active rulesets:

- `default branch` on `~DEFAULT_BRANCH`, with no bypass actors: `deletion`, `non_fast_forward`,
  `required_signatures`, `pull_request` (squash only, zero approvals, review
  threads resolved), and `required_status_checks` for the checks below, each
  bound to GitHub Actions;
- `Immutable release tags` on `v*` tags, retaining the organization-admin
  exception declared in [VERSIONING.md](VERSIONING.md#immutable-tags).

| Repository | Required checks |
| --- | --- |
| `.github` | None yet |
| `skills` | `validate-commit-messages` |
| `homebrew-tap` | `verify (macos-26, 26.6)`, `verify (macos-15, 26.0.1, 6.3.3)` |
| `swift-sh` | `validate / configure`, `validate / strict-format`, `validate / linux-swift-6.3`, `validate / macos-15-swift-6.3`, `validate / macos-26-swift-6.3`, `validate-commit-messages` |
| `swift-codex` | `Repository quality`, `Swift 6.2 baseline`, `Current hosted Swift`, `Windows products`, `Windows native process runtime`, `AppServer and MCP binary integration`, `validate-commit-messages` |
| `swift-package-template` | `validate / configure`, `validate / strict-format`, `validate / macos-15-swift-6.0`, `validate / macos-26-swift-6.3`, `validate-commit-messages` |
| `swift-data-writable` | `validate / configure`, `validate / strict-format`, `validate / macos-15-swift-6.2`, `validate / macos-26-swift-6.3`, `validate-commit-messages` |
| `swift-benchmark` | `validate / configure`, `validate / strict-format`, `validate / macos-15-swift-6.0`, `validate / macos-26-swift-6.3`, `validate-commit-messages` |
| `swift-redux` | `validate / configure`, `validate / ios-build`, `validate / macos-15-swift-6.0`, `validate / macos-26-swift-6.3` |
| `swift-userdefault` | `validate / configure`, `validate / ios-build`, `validate / macos-15-swift-6.0`, `validate / macos-26-swift-6.3` |
| `swift-gyb` | `validate / configure`, `validate / linux-swift-6.2`, `validate / macos-26-swift-6.3` |
| `swift-semver` | `validate / configure`, `validate / strict-format`, `validate / linux-swift-6.0`, `validate / macos-15-swift-6.0`, `validate / macos-26-swift-6.3`, `validate-commit-messages` |

A renamed or added CI job updates its ruleset and this table in the same
sitting; until then every pull request in that repository waits on the old
name.

**Apps.**

| App | Permissions | Installed on | Credentials | Stored in |
| --- | --- | --- | --- | --- |
| ChatGPT Codex Connector | actions, contents, issues, pull requests, workflows: write; checks, statuses, metadata: read | All repositories | Managed by OpenAI | None in GitHub |

No Actions secrets or variables exist at organization or repository level.

### Settings declaration

`Scripts/check-settings.py` reads this declaration and the required-check table
above. The declaration owns exact API parameters; the table owns job names.
Changes to either must accompany the corresponding GitHub setting change.
The checker reads metadata only and never retrieves secret values.

```json
{
  "organization": "swift-library",
  "default_branch": "master",
  "merge": {
    "allow_squash_merge": true,
    "allow_merge_commit": false,
    "allow_rebase_merge": false,
    "delete_branch_on_merge": true,
    "squash_merge_commit_title": "PR_TITLE",
    "squash_merge_commit_message": "COMMIT_MESSAGES"
  },
  "workflow_token": {
    "default_workflow_permissions": "read",
    "can_approve_pull_request_reviews": false
  },
  "branch_ruleset": {
    "name": "default branch",
    "target": "branch",
    "enforcement": "active",
    "bypass_actors": [],
    "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
    "rules": [
      {"type": "deletion"},
      {"type": "non_fast_forward"},
      {"type": "required_signatures"},
      {"type": "pull_request", "parameters": {
        "allowed_merge_methods": ["squash"],
        "required_approving_review_count": 0,
        "dismiss_stale_reviews_on_push": false,
        "dismissal_restriction": {"allowed_actors": [], "enabled": false},
        "require_code_owner_review": false,
        "require_extra_approval_for_unattributed_changes": true,
        "require_last_push_approval": false,
        "required_review_thread_resolution": true,
        "required_reviewers": []
      }}
    ]
  },
  "status_checks": {
    "integration_id": 15368,
    "strict_required_status_checks_policy": false,
    "do_not_enforce_on_create": false
  },
  "tag_ruleset": {
    "name": "Immutable release tags",
    "target": "tag",
    "enforcement": "active",
    "bypass_actors": [{"actor_id": null, "actor_type": "OrganizationAdmin", "bypass_mode": "always"}],
    "conditions": {"ref_name": {"include": ["refs/tags/v*"], "exclude": []}},
    "rules": [{"type": "deletion"}, {"type": "update"}, {"type": "non_fast_forward"}]
  },
  "organization_actions": {"secrets": [], "variables": {}},
  "repository_actions": {"secrets": [], "variables": {}},
  "repository_action_overrides": {},
  "apps": {
    "chatgpt-codex-connector": {
      "repository_selection": "all",
      "permissions": {
        "actions": "write", "contents": "write", "issues": "write",
        "pull_requests": "write", "workflows": "write", "checks": "read",
        "statuses": "read", "metadata": "read"
      }
    }
  }
}
```

## Automatic Review

Codex code review runs on every pull request, with Automatic review turned on
in Codex settings for each repository. It reads the `## Code Review Rules`
section of the repository's `AGENTS.md`, and the nested `AGENTS.md` nearest to
each changed file. Its findings are advisory, but the ruleset requires every
review thread to be resolved before merging.

## Open Items

- `homebrew-tap`'s scheduled updater pushes verified formula updates with the
  workflow token, which the `default branch` ruleset rejects. It moves to an
  organization-owned Updater App (`contents` and `pull_requests` write,
  installed only on `homebrew-tap`) that opens a pull request with auto-merge.
  The formula currently matches the latest `swift-sh` release.
- Commits on default branches from before this flow are unsigned. They stay as
  they are; history is not rewritten for signatures.
