# Maintenance

How changes reach the swift-library repositories, and the GitHub settings that
enforce it. A change to any setting, ruleset, App, or credential updates this
file in the same pull request.

## Change Flow

1. Work on a branch. Maintainer commits use the owner's name and noreply email
   and are SSH-signed. Attribution trailers never appear.
2. Run the affected repository's declared validation before pushing. This
   repository's local checks are in [Contributing](CONTRIBUTING.md).
3. Open a pull request against `master`. Its title and commit subjects follow
   Conventional Commits: `type(scope)!: subject`, with optional scope and `!`.
   Types are `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`,
   `revert`, `style` and `test`.
4. Merge only when every required check is green and every review thread is
   resolved: each automatic review finding is fixed or answered on the pull
   request.
5. Squash-merge the reviewed head commit with an empty body, for example
   `gh pr merge <number> --squash --match-head-commit <sha> --body ''`.
   Without `--body ''`, `gh` sends GitHub's default body, which carries the
   branch's commit messages and trailers, instead of the repository's blank
   setting.

External pull requests and bot-authored changes are welcome. Pull-request
policy checks the title, added content and added or modified file paths, as
defined in [shared policy workflow](https://github.com/swift-library/github-workflows#calling-validation-and-policy).
Default-branch push policy requires
GitHub-verified commits committed by GitHub or the owner; it does not restrict
the original author. Dependabot, updater Apps and GitHub Actions may author
changes. Product names are allowed only through the caller's `allow-terms`.

## Repository Scope

All self-owned repositories use `master` and these shared standards. GitHub
forks of upstream projects follow their upstream branch and tag conventions
and are outside the organization rulesets.

## Signing

Configure signing locally in each repository, using the owner's registered SSH
signing key. Do not change global Git configuration:

```sh
git config user.name showxu
git config user.email 10173746+showxu@users.noreply.github.com
git config gpg.format ssh
git config user.signingkey ~/.ssh/signing_key.pub
git config commit.gpgsign true
git config tag.gpgsign true
git config gpg.ssh.allowedSignersFile ~/.ssh/allowed_signers
```

Replace the key and allowed-signers paths with the local signing configuration.
The allowed-signers file contains the signer's email followed by the SSH public
key. Register that public key as a signing key on GitHub. Verify commits with
`git verify-commit HEAD` and tags with `git verify-tag vX.Y.Z`.
Release tags use the signed annotated format in [Versioning](VERSIONING.md#tags).

## GitHub Settings

**Presentation.** The organization account description follows the promise
heading in `profile/catalog.json`. Repository descriptions and topics follow
the copy rules in [DESIGN.md](DESIGN.md); each README tagline equals its
repository description. Verify these fields after publication.

**Merging.** Squash merge only, with the pull request title as the commit
subject and an empty commit body. Merge commits and rebase merges
are off, and merged branches are deleted.

**Workflow token.** The default `GITHUB_TOKEN` permission is `read`, and
workflows cannot approve pull requests, at organization and repository level.
Each workflow declares the permissions it needs.

**Rulesets.** Every public self-owned repository has two active rulesets:

- `default branch` on `~DEFAULT_BRANCH`, with no bypass actors: `deletion`, `non_fast_forward`,
  `required_signatures`, `pull_request` (squash only, zero approvals, review
  threads resolved), and `required_status_checks` for the checks below, each
  bound to GitHub Actions;
- `Immutable release tags` on `v*` tags, with no bypass actors, as required by
  [VERSIONING.md](VERSIONING.md#immutable-tags).

These rulesets own branch protection. Legacy branch-protection rules are absent;
overlapping rules can otherwise retain a branch lock or a different approval
requirement. Migrate a legacy rule only after verifying the active ruleset,
including its required checks, signatures and pull-request requirements.

| Repository | Required checks |
| --- | --- |
| `.github` | `policy / policy`, `result` |
| `github-workflows` | `policy / policy`, `result` |
| `skills` | `policy / policy`, `result` |
| `swift-library.github.io` | `policy / policy`, `result` |
| `homebrew-tap` | `policy / policy`, `result` |
| `swift-sh` | `policy / policy`, `validate / result` |
| `swift-codex` | `policy / policy`, `result` |
| `swift-package-template` | `policy / policy`, `validate / result` |
| `swift-data-writable` | `policy / policy`, `validate / result` |
| `swift-benchmark` | `policy / policy`, `validate / result` |
| `swift-redux` | `policy / policy`, `validate / result` |
| `swift-userdefault` | `policy / policy`, `validate / result` |
| `swift-gyb` | `policy / policy`, `validate / result` |
| `swift-semver` | `policy / policy`, `validate / result` |
| `swift-pdf` | `policy / policy`, `validate / result` |
| `swift-json-schema` | `policy / policy`, `validate / result` |
| `swift-appstoreconnect` | `policy / policy`, `validate / result` |
| `swift-interface-distiller` | `policy / policy`, `validate / result` |

`swift-codex`'s `result` aggregates the shared validation with its Windows
product builds and real-binary integration tests.

`policy / policy` comes from the `policy` job in `source-policy.yml`, which
includes pull-request title edits. Validation callers run on `opened`,
`synchronize`, `reopened`, `master` pushes and manual dispatch. Each caller
cancels superseded runs using its workflow name and pull-request number or
branch ref; release and publication runs are never cancelled. See
[github-workflows](https://github.com/swift-library/github-workflows#calling-validation-and-policy)
for the caller contract. Check this table against active rulesets before
upgrading callers, and verify the resulting check names on their pull requests.

A renamed or added CI job updates its ruleset and this table in the same
sitting; until then every pull request in that repository waits on the old
name.

**Apps.**

| App | Permissions | Installed on | Credentials | Stored in |
| --- | --- | --- | --- | --- |
| ChatGPT Codex Connector | actions, contents, issues, pull requests, workflows: write; checks, statuses, metadata: read | All repositories | Managed by OpenAI | None in GitHub |

No Actions secrets or variables exist at organization or repository level.

### Settings declaration

The [organization checker](https://github.com/swift-library/github-workflows#organization-checks)
reads this declaration. Family defaults own the API parameters; each repository
entry owns its description, topics, branch, required checks and release-tag
patterns. Keep the required-check table above consistent with those entries.
Changes to the declaration accompany the corresponding GitHub setting change.

This repository's caller uses public mode to compare catalog membership and
About descriptions. Online mode additionally checks repository settings,
workflow-token permissions, private vulnerability reporting and complete
branch/tag rulesets. It requires an administrative read token. The checker uses
read-only API requests; unavailable observations and drift fail the check.

The supplemental legacy-protection, Actions credential metadata and App fields
record family policy for maintainer review; the shared checker validates the
`defaults` and `repositories` sections.

<!-- settings-declaration -->
```json
{
  "schema": 1,
  "defaults": {
    "repository": {
      "allow_squash_merge": true,
      "allow_merge_commit": false,
      "allow_rebase_merge": false,
      "delete_branch_on_merge": true,
      "squash_merge_commit_title": "PR_TITLE",
      "squash_merge_commit_message": "BLANK"
    },
    "workflow_token": {
      "default_workflow_permissions": "read",
      "can_approve_pull_request_reviews": false
    },
    "private_vulnerability_reporting": {
      "enabled": true
    },
    "branch_ruleset": {
      "name": "default branch",
      "target": "branch",
      "enforcement": "active",
      "bypass_actors": [],
      "conditions": {
        "ref_name": {
          "include": [
            "~DEFAULT_BRANCH"
          ],
          "exclude": []
        }
      },
      "rules": [
        {
          "type": "deletion"
        },
        {
          "type": "non_fast_forward"
        },
        {
          "type": "required_signatures"
        },
        {
          "type": "pull_request",
          "parameters": {
            "allowed_merge_methods": [
              "squash"
            ],
            "required_approving_review_count": 0,
            "dismiss_stale_reviews_on_push": false,
            "dismissal_restriction": {
              "allowed_actors": [],
              "enabled": false
            },
            "require_code_owner_review": false,
            "require_extra_approval_for_unattributed_changes": true,
            "require_last_push_approval": false,
            "required_review_thread_resolution": true,
            "required_reviewers": []
          }
        }
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
      "bypass_actors": [],
      "conditions": {
        "ref_name": {
          "include": [
            "refs/tags/v*"
          ],
          "exclude": []
        }
      },
      "rules": [
        {
          "type": "deletion"
        },
        {
          "type": "update"
        },
        {
          "type": "non_fast_forward"
        }
      ]
    }
  },
  "repositories": {
    "swift-library/.github": {
      "default_branch": "master",
      "description": "Publish independently versioned Swift packages with shared checks.",
      "topics": [
        "community",
        "continuous-integration",
        "documentation",
        "github-actions",
        "release-automation",
        "swift"
      ],
      "required_checks": [
        "policy / policy",
        "result"
      ],
      "release_tag_patterns": [
        "refs/tags/v*"
      ]
    },
    "swift-library/skills": {
      "default_branch": "master",
      "description": "Build and maintain Swift packages and Apple apps with agent skills in a single plugin.",
      "topics": [
        "agent-skills",
        "ai-agents",
        "claude-code",
        "codex",
        "ios",
        "macos",
        "swift",
        "swiftui",
        "uikit"
      ],
      "required_checks": [
        "policy / policy",
        "result"
      ],
      "release_tag_patterns": [
        "refs/tags/v*"
      ]
    },
    "swift-library/swift-library.github.io": {
      "default_branch": "master",
      "description": "Find Swift packages, copy install commands, and read their API documentation.",
      "topics": [
        "developer-tools",
        "docc",
        "documentation",
        "github-pages",
        "swift"
      ],
      "required_checks": [
        "policy / policy",
        "result"
      ],
      "release_tag_patterns": [
        "refs/tags/v*"
      ]
    },
    "swift-library/homebrew-tap": {
      "default_branch": "master",
      "description": "Install swift-library command-line tools from release archives verified by SHA-256.",
      "topics": [
        "cli",
        "developer-tools",
        "homebrew",
        "homebrew-tap",
        "swift"
      ],
      "required_checks": [
        "policy / policy",
        "result"
      ],
      "release_tag_patterns": [
        "refs/tags/v*"
      ]
    },
    "swift-library/swift-sh": {
      "default_branch": "master",
      "description": "Run single-file Swift scripts with package dependencies declared inline.",
      "topics": [
        "cli",
        "developer-tools",
        "scripting",
        "shebang",
        "swift",
        "swift-package-manager",
        "swift-script"
      ],
      "required_checks": [
        "policy / policy",
        "validate / result"
      ],
      "release_tag_patterns": [
        "refs/tags/v*"
      ]
    },
    "swift-library/swift-codex": {
      "default_branch": "master",
      "description": "Drive the Codex CLI from Swift through separate exec, App Server, and MCP interfaces.",
      "topics": [
        "ai-agents",
        "client-library",
        "codex",
        "developer-tools",
        "json-rpc",
        "jsonl",
        "mcp",
        "swift",
        "swift-package-manager",
        "websocket"
      ],
      "required_checks": [
        "policy / policy",
        "result"
      ],
      "release_tag_patterns": [
        "refs/tags/v*"
      ]
    },
    "swift-library/swift-package-template": {
      "default_branch": "master",
      "description": "A complete Swift package to create new swift-library packages from, with shared CI and release checks.",
      "topics": [
        "developer-tools",
        "github-actions",
        "release-automation",
        "swift",
        "swift-package-manager",
        "template"
      ],
      "required_checks": [
        "policy / policy",
        "validate / result"
      ],
      "release_tag_patterns": [
        "refs/tags/v*"
      ]
    },
    "swift-library/swift-data-writable": {
      "default_branch": "master",
      "description": "Insert, delete, and reorder SwiftData query results through a projected collection.",
      "topics": [
        "data-binding",
        "persistence",
        "swift",
        "swift-macros",
        "swift-package-manager",
        "swiftdata",
        "swiftui"
      ],
      "required_checks": [
        "policy / policy",
        "validate / result"
      ],
      "release_tag_patterns": [
        "refs/tags/v*"
      ]
    },
    "swift-library/swift-benchmark": {
      "default_branch": "master",
      "description": "Catch performance regressions beside your tests with JSON baselines and metric budgets.",
      "topics": [
        "benchmark",
        "ci",
        "instrumentation",
        "performance",
        "performance-testing",
        "profiling",
        "swift",
        "swift-package-manager",
        "swift-testing"
      ],
      "required_checks": [
        "policy / policy",
        "validate / result"
      ],
      "release_tag_patterns": [
        "refs/tags/v*"
      ]
    },
    "swift-library/swift-redux": {
      "default_branch": "master",
      "description": "Manage unidirectional app state with one store, reducers, middleware, and live subscriptions.",
      "topics": [
        "middleware",
        "redux",
        "state-management",
        "subscriptions",
        "swift",
        "swift-package-manager",
        "unidirectional-data-flow"
      ],
      "required_checks": [
        "policy / policy",
        "validate / result"
      ],
      "release_tag_patterns": [
        "refs/tags/v*"
      ]
    },
    "swift-library/swift-userdefault": {
      "default_branch": "master",
      "description": "Persist primitives, raw-value enums, and Codable models through one UserDefaults property wrapper.",
      "topics": [
        "codable",
        "persistence",
        "preferences",
        "property-wrapper",
        "swift",
        "swift-package-manager",
        "userdefaults"
      ],
      "required_checks": [
        "policy / policy",
        "validate / result"
      ],
      "release_tag_patterns": [
        "refs/tags/v*"
      ]
    },
    "swift-library/swift-gyb": {
      "default_branch": "master",
      "description": "Generate Swift sources and resource files from Python templates during SwiftPM builds.",
      "topics": [
        "code-generation",
        "gyb",
        "python",
        "swift",
        "swift-package-manager",
        "swiftpm-plugin",
        "templating"
      ],
      "required_checks": [
        "policy / policy",
        "validate / result"
      ],
      "release_tag_patterns": [
        "refs/tags/v*"
      ]
    },
    "swift-library/swift-semver": {
      "default_branch": "master",
      "description": "Parse, compare, constrain, and increment SemVer 2.0.0 versions using only the Swift standard library.",
      "topics": [
        "semantic-versioning",
        "semver",
        "swift",
        "swift-package-manager",
        "version-comparison",
        "versioning"
      ],
      "required_checks": [
        "policy / policy",
        "validate / result"
      ],
      "release_tag_patterns": [
        "refs/tags/v*"
      ]
    },
    "swift-library/swift-pdf": {
      "default_branch": "master",
      "description": "Build PDF viewers in SwiftUI with search, page overlays, and navigation driven by your controls.",
      "topics": [
        "document-viewer",
        "ios",
        "macos",
        "pdf",
        "pdfkit",
        "swift",
        "swift-package-manager",
        "swiftui"
      ],
      "required_checks": [
        "policy / policy",
        "validate / result"
      ],
      "release_tag_patterns": [
        "refs/tags/v*"
      ]
    },
    "swift-library/swift-json-schema": {
      "default_branch": "master",
      "description": "Validate JSON against JSON Schema without losing number precision.",
      "topics": [
        "cli",
        "json",
        "json-schema",
        "serialization",
        "swift",
        "swift-package-manager",
        "validation"
      ],
      "required_checks": [
        "policy / policy",
        "validate / result"
      ],
      "release_tag_patterns": [
        "refs/tags/v*"
      ]
    },
    "swift-library/swift-appstoreconnect": {
      "default_branch": "master",
      "description": "Build typed App Store Connect integrations and preview CLI writes before confirming them.",
      "topics": [
        "app-store",
        "app-store-connect",
        "cli",
        "code-signing",
        "openapi",
        "swift",
        "swift-package-manager",
        "testflight"
      ],
      "required_checks": [
        "policy / policy",
        "validate / result"
      ],
      "release_tag_patterns": [
        "refs/tags/v*"
      ]
    },
    "swift-library/swift-interface-distiller": {
      "default_branch": "master",
      "description": "Distill a Swift package to its public API: a compact interface to read, evidence to query and diff.",
      "topics": [
        "ai-agents",
        "api-diff",
        "api-documentation",
        "cli",
        "developer-tools",
        "public-api",
        "swift",
        "swift-package-manager",
        "symbol-graph"
      ],
      "required_checks": [
        "policy / policy",
        "validate / result"
      ],
      "release_tag_patterns": [
        "refs/tags/v*"
      ]
    },
    "swift-library/github-workflows": {
      "default_branch": "master",
      "description": "Shared GitHub Actions workflows and checks for swift-library repositories.",
      "topics": [],
      "required_checks": [
        "policy / policy",
        "result"
      ],
      "release_tag_patterns": [
        "refs/tags/v*"
      ]
    }
  },
  "legacy_branch_protection": null,
  "organization_actions": {
    "secrets": [],
    "variables": {}
  },
  "repository_actions": {
    "secrets": [],
    "variables": {}
  },
  "repository_action_overrides": {},
  "apps": {
    "chatgpt-codex-connector": {
      "repository_selection": "all",
      "permissions": {
        "actions": "write",
        "contents": "write",
        "issues": "write",
        "pull_requests": "write",
        "workflows": "write",
        "checks": "read",
        "statuses": "read",
        "metadata": "read"
      }
    }
  }
}
```

## Automatic Review

Codex is the selected advisory reviewer. Its GitHub App is installed on all
repositories; automatic review activation is pending in Codex settings.
Repository rules live in the `## Code Review Rules` section of `AGENTS.md`,
with area-specific rules in nested guides. Required checks enforce the merge
gate, and the ruleset requires every review thread to be resolved before merging.

## Tool Release Updates

`homebrew-tap` checks published releases for the tools in its metadata catalog.
The scheduled workflow verifies candidates with read permissions, then uses a
separate job with `issues: write` to open a release notice. Open and closed
notices identify releases by repository and Release ID to prevent repeats.
Maintainers review each candidate and update the tap through the normal signed
pull-request flow. See the tap's
[Release Updates](https://github.com/swift-library/homebrew-tap/blob/master/Documentation/ReleaseUpdates.md)
for validation and publication steps.
