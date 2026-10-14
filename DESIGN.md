---
version: alpha
name: swift-library
description: Visual identity for swift-library repository pages, icons, social preview cards, and terminal demos.
colors:
  primary: "#f12e1d"
  primary-light: "#ff9d36"
  badge-swift: "#F05138"
  ink: "#1d1d1f"
  ink-secondary: "#424245"
  ink-tertiary: "#6e6e73"
  surface: "#fbfbfd"
  surface-dim: "#f0f0f3"
  terminal-surface: "#0d1117"
  terminal-bar: "#161b22"
  terminal-border: "#30363d"
  terminal-prompt: "#3fb950"
  terminal-command: "#e6edf3"
  terminal-output: "#c9d1d9"
  terminal-dim: "#8b949e"
  terminal-light-surface: "#f6f8fa"
  terminal-light-bar: "#eaeef2"
  terminal-light-border: "#d0d7de"
  terminal-light-prompt: "#1a7f37"
  terminal-light-command: "#1f2328"
  terminal-light-output: "#24292f"
  terminal-light-dim: "#57606a"
typography:
  card-owner:
    fontFamily: Inter
    fontSize: 30px
    fontWeight: 500
  card-title:
    fontFamily: Inter Display
    fontSize: 76px
    fontWeight: 700
  card-body:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: 400
    lineHeight: 1.35
  terminal:
    fontFamily: ui-monospace
    fontSize: 14px
    lineHeight: 21px
rounded:
  none: 0px
  terminal-window: 10px
spacing:
  card-text-left: 560px
  card-text-right: 1200px
  terminal-padding: 20px
components:
  org-icon-face:
    backgroundColor: "{colors.primary-light}"
  org-icon-face-front:
    backgroundColor: "{colors.primary}"
  badge-swift:
    backgroundColor: "{colors.badge-swift}"
  social-card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.card-title}"
    rounded: "{rounded.none}"
    width: 1280px
    height: 640px
  social-card-summary:
    textColor: "{colors.ink-secondary}"
    typography: "{typography.card-body}"
  social-card-owner:
    textColor: "{colors.ink-tertiary}"
    typography: "{typography.card-owner}"
  terminal-window:
    backgroundColor: "{colors.terminal-surface}"
    textColor: "{colors.terminal-output}"
    typography: "{typography.terminal}"
    rounded: "{rounded.terminal-window}"
    padding: "{spacing.terminal-padding}"
  terminal-title-bar:
    backgroundColor: "{colors.terminal-bar}"
    textColor: "{colors.terminal-dim}"
    height: 34px
  terminal-divider:
    backgroundColor: "{colors.terminal-border}"
    height: 1px
  terminal-prompt:
    textColor: "{colors.terminal-prompt}"
  terminal-command:
    textColor: "{colors.terminal-command}"
  readme-logo:
    size: 160px
  profile-logo:
    size: 128px
  table-logo:
    size: 40px
---

# swift-library Design

## Overview

swift-library presents independently versioned Swift packages as one family.
Each repository has an isometric stacked-slab icon: a rounded square seen from
above, built from colored bands, with a raised glyph on its top face. The
family shares geometry, lighting, and band rhythm. Member repositories have
distinct hues; a member may share its hue only with the umbrella icon. Pages around the icons stay
quiet: light neutral surfaces, near-black text, no decoration.

## Colors

- **Primary** (`#f12e1d`) and **Primary Light** (`#ff9d36`) are the
  organization icon's face and its derived assets.
- **Badge Swift** (`#F05138`) colors the Swift version badge.
- **Ink**, **Ink Secondary**, and **Ink Tertiary** set repository names,
  summaries, and owner labels on social preview cards.
- **Surface** to **Surface Dim** is the vertical gradient behind social
  preview cards.
- The **Terminal** colors define the dark window used for command-line demos.
  **Terminal Light** supplies the corresponding light appearance. Both use a
  green prompt and keep commands distinct from output.
- Repository icon colors live in the Iconography section. Members use distinct
  hues and may share a hue only with the umbrella icon.

## Typography

Social preview text uses Inter and Inter Display (SIL Open Font License),
converted to outlines so cards never depend on installed fonts. Repository
names are bold display weight; summaries are regular weight and wrap to at
most two lines. Terminal demos use the viewer's monospace font at 14 px.

## Layout

Social preview cards are 1280 by 640. The icon sits centered at x 300 with a
420 px square; text starts at x 560 and wraps before x 1200, vertically
centered as one block. README headers center the logo at 160 px above the
repository name.

## Repository presentation

The first screen answers what the repository does, why it differs, and how to
start. Every image identifies, demonstrates, or compares. An icon accompanies
its linked name; the umbrella mark at the top of the organization profile is
the only standalone icon. Text remains text.

Every repository uses the same centered header: a linked 160 px logo, an `h1`
name, the tagline, exactly four flat badges, and the navigation row. Badge order
is CI, Swift X.Y+, platforms, license. Use `CI`, `Swift X.Y+`, `Platforms: …`,
and `License: Apache-2.0 WITH Swift-exception` for their accessible labels; the
Swift badge uses Badge Swift. Values come from the repository's current
requirements. The tagline equals the GitHub description.

Section and navigation order is Overview, Quick look, Install, Usage,
Requirements, Documentation, Contributing, License. Overview has two or three
sentences. Put details, measurements, scope, and limits in Documentation and
link to them. Library Quick look sections show at most 12 lines of working
Swift. Command-line tools show a real recorded session, rendered with the
terminal tokens by `Scripts/render-terminal.py`. Commit the recording and
light/dark SVG variants, use `<picture>` with `prefers-color-scheme`, and check
generated bytes in CI. Do not add emoji, badge walls, or another table of contents.

Review every custom image in light and dark. GitHub presentation changes are
reviewed through draft PRs with rendered light/dark screenshots of the profile,
a library README, and a command-line README before merging.

## Copy

Lead with the reader's outcome in one active sentence. A verb opening is
preferred, not required. Name a distinction supported by current code, tests,
or CI. Use present tense, sentence case, and a final period. Avoid hype,
unverifiable superiority, and openings such as “A Swift package that”.

Visitor-facing profile and website copy, descriptions, and taglines state what
the reader gets. Process terms such as evidence, independent versioning,
signed tags, and provenance belong in standards documents and repositories
whose products provide them.

The tagline, Overview opening, and Quick look each add different information.
Overview explains why and how in other words. Quick look needs an introductory
sentence only when it adds information.

Repository descriptions, taglines, catalog summaries, and social-card About
text use the same sentence, at most 110 characters. Keep drifting counts and release
versions out of these short fields; put them in generated or measured
documentation. Fixed standard identifiers, such as SemVer 2.0.0, can identify
the implemented contract. Keep README and DocC introductions consistent.

Use about 5–10 accurate search topics. Swift package repositories retain
`swift` and `swift-package-manager`; non-package repositories do not use
`swift-package-manager`. Topics describe supported domains, protocols, inputs,
or outputs. Distinguish current behavior, plans, selected configurations,
and guarantees, and keep unknown observations explicit. These rules apply
across the family without per-repository exceptions.

## Organization profile and catalog

The centered profile header uses the existing 128 px red-orange four-tile
umbrella mark, the organization promise as a heading, one secondary line, and
Documentation · Contributing · Security · Support. The account description is
the compact form of the same promise, at most 160 characters. The Swift bird avatar remains governed
by [Brand/Avatar/README.md](Brand/Avatar/README.md).

`profile/catalog.json` owns the promise, navigation roles, reader-job groups,
ordering, and reviewed outcome sentences. `Scripts/render-profile.py`
generates the profile; CI checks byte-identical output and complete membership
of public self-owned repositories. Each catalog row has a linked 40 px icon,
a bold linked name, and the outcome sentence, in HTML tables without header
rows. Navigation repositories appear
in the header rather than as duplicate catalog rows. Do not assemble
membership-dependent presentation artifacts by hand.

The footer uses `<sub>` for “Maintained by @showxu (https://showxu.github.io)”,
with linked owner and website. The website landing uses the same promise,
job grouping, and umbrella icon.

## Elevation & Depth

Depth lives inside the icons: stacked bands read as physical thickness, and
raised glyphs cast a soft contact shadow on the face. Pages and cards stay
flat. A faint radial glow in the repository's hue may sit behind the icon on
social cards.

## Shapes

Repository icons use continuous corners at an isometric angle, with a
vertical squash of 0.75 and a stack depth of 0.36 of the icon width. The
framework icon generator owns the shared corner geometry. Native avatar
masks come from Icon Composer. Terminal windows have 10 px corners; cards
are square.

## Components

- **Social card**: icon, owner label, repository name, and the About sentence.
  Nothing else.
- **Terminal window**: title bar with three window dots and an optional
  centered title, then real command output.
- **Logos**: 160 px in README headers, 128 px on the organization profile,
  40 px in profile tables.

## Do's and Don'ts

- Do space member hues apart. A member may share a hue only with the umbrella icon.
- Do keep symbols that must be read upright (rotation -45) and lay symmetric
  marks along the face axes (rotation 0).
- Do derive social preview art from the icons, never redraw them.
- Don't use Apple system fonts, SF Symbols, or other restricted glyph sets.
- Repository glyphs are original. The organization's supplied Swift bird is
  limited to its avatar; its source ownership is recorded in
  [Brand/Avatar/README.md](Brand/Avatar/README.md).
- Don't put text inside icons.

## Iconography

Entries under `icons` render repository logos at 1024 px with
`skills/apple-framework-icon-design` in
[showxu/skills](https://github.com/showxu/skills). Consumers pin the generator to
a reviewed full commit SHA. Colors are OKLCH. Regenerate after changing
an entry and replace the owning repository’s `Logo.svg` and `Logo.png`.
Custom glyph shapes use plain unit coordinates; the generator owns browser
rendering correctness.

The `app_icons` entry supplies `apple-app-icon-design` with the organization
avatar’s background, material groups, and source layers. Its dot field uses
Primary Light over Primary, and the bird receives native relief and lighting.
The avatar and repository logo serve different surfaces. All native
appearances and web sizes derive from these layers and this entry.

```json
{
  "icons": {
    "swift-userdefault": {
      "hue": 10,
      "face_colors": [
        "oklch(0.72 0.18 8)",
        "oklch(0.64 0.21 14)"
      ],
      "band_colors": [
        "oklch(0.63 0.21 16)",
        "oklch(0.7 0.19 10)",
        "oklch(0.77 0.15 4)"
      ],
      "glyph": "toggle",
      "texture": "dots",
      "glyph_rotation": -45
    },
    "swift-library": {
      "hue": 40,
      "bands": 4,
      "face_colors": [
        "oklch(0.78 0.16 62)",
        "oklch(0.62 0.23 30)"
      ],
      "band_colors": [
        "oklch(0.6 0.23 28)",
        "oklch(0.66 0.21 38)",
        "oklch(0.74 0.18 52)",
        "oklch(0.83 0.14 68)"
      ],
      "glyph": "tiles",
      "texture": "dots",
      "glyph_rotation": 0
    },
    "swift-benchmark": {
      "hue": 40,
      "texture": "grid",
      "face_colors": [
        "oklch(0.78 0.14 52)",
        "oklch(0.68 0.19 34)"
      ],
      "band_colors": [
        "oklch(0.66 0.18 33)",
        "oklch(0.5 0.012 50)",
        "oklch(0.37 0.01 50)"
      ],
      "objects": [
        {
          "kind": "cube",
          "x": 0.04,
          "y": 0.3,
          "s": 0.07,
          "h": 0.14
        },
        {
          "kind": "cube",
          "x": 0.04,
          "y": 0.1,
          "s": 0.07,
          "h": 0.24
        },
        {
          "kind": "cube",
          "x": 0.04,
          "y": -0.1,
          "s": 0.07,
          "h": 0.36
        },
        {
          "kind": "cube",
          "x": 0.04,
          "y": -0.3,
          "s": 0.07,
          "h": 0.5
        }
      ]
    },
    "swift-package-template": {
      "hue": 58,
      "mode": "deepen",
      "bands": 3,
      "glyph": "dashed_plus",
      "texture": "lines",
      "glyph_rotation": 0,
      "glyph_scale": 0.32
    },
    "homebrew-tap": {
      "hue": 84,
      "mode": "deepen",
      "bands": 3,
      "glyph": "mug",
      "texture": "dots",
      "glyph_rotation": -45
    },
    "swift-appstoreconnect": {
      "hue": 106,
      "mode": "deepen",
      "bands": 3,
      "texture": "dots",
      "glyph_rotation": -45,
      "glyph_scale": 0.32,
      "custom_glyph": {
        "style": "stroke",
        "width": 0.15,
        "d": "M-0.38 -0.48 H0.16 Q0.58 -0.48 0.58 -0.06 V0.36 M-0.62 -0.26 V0.10 Q-0.62 0.50 -0.22 0.50 H0.16",
        "rects": [
          [
            -0.88,
            -0.82,
            0.58,
            0.58
          ],
          [
            0.28,
            0.2,
            0.58,
            0.58
          ]
        ],
        "round": 0.12
      }
    },
    "swift-semver": {
      "hue": 128,
      "mode": "deepen",
      "bands": 3,
      "glyph": "tag",
      "texture": "grid",
      "glyph_rotation": -45
    },
    "swift-sh": {
      "hue": 160,
      "bands": 4,
      "glyph": "shebang",
      "glyph_hue": 160,
      "texture": "lines",
      "texture_opacity": 0.15,
      "face_colors": [
        "oklch(0.42 0.07 168)",
        "oklch(0.3 0.05 172)"
      ],
      "band_colors": [
        "oklch(0.35 0.07 170)",
        "oklch(0.42 0.09 167)",
        "oklch(0.49 0.11 164)",
        "oklch(0.56 0.12 160)"
      ],
      "glyph_rotation": -45
    },
    "swift-gyb": {
      "hue": 195,
      "mode": "deepen",
      "bands": 3,
      "glyph": "braces",
      "texture": "lines",
      "glyph_rotation": -45
    },
    "swift-data-writable": {
      "hue": 232,
      "mode": "deepen",
      "bands": 3,
      "glyph": "cylinder",
      "texture": "grid",
      "glyph_rotation": -45
    },
    "skills": {
      "hue": 260,
      "face_colors": [
        "oklch(0.4 0.01 260)",
        "oklch(0.33 0.01 260)"
      ],
      "neutral_bands": "glow",
      "bands": 3,
      "glyph": "spark",
      "glyph_hue": 92,
      "texture": "constellation",
      "glyph_rotation": -45
    },
    "swift-codex": {
      "hue": 272,
      "bands": 3,
      "glyph": "prompt",
      "texture": "constellation",
      "glyph_rotation": -45,
      "face_colors": [
        "oklch(0.76 0.13 290)",
        "oklch(0.6 0.19 272)"
      ],
      "band_colors": [
        "oklch(0.64 0.17 272)",
        "oklch(0.7 0.15 282)",
        "oklch(0.76 0.13 292)"
      ]
    },
    "swift-json-schema": {
      "hue": 292,
      "mode": "glow",
      "bands": 3,
      "texture": "grid",
      "texture_opacity": 0.16,
      "face_colors": [
        "oklch(0.6 0.17 296)",
        "oklch(0.48 0.17 291)"
      ],
      "band_colors": [
        "oklch(0.48 0.17 292)",
        "oklch(0.57 0.19 292)",
        "oklch(0.66 0.17 292)"
      ],
      "glyph_rotation": -45,
      "glyph_scale": 0.32,
      "custom_glyph": {
        "style": "stroke",
        "width": 0.16,
        "d": "M-0.44 -0.76 H-0.62 Q-0.78 -0.76 -0.78 -0.52 V-0.22 Q-0.78 0 -0.98 0 Q-0.78 0 -0.78 0.22 V0.52 Q-0.78 0.76 -0.62 0.76 H-0.44 M0.44 -0.76 H0.62 Q0.78 -0.76 0.78 -0.52 V-0.22 Q0.78 0 0.98 0 Q0.78 0 0.78 0.22 V0.52 Q0.78 0.76 0.62 0.76 H0.44",
        "extra": "M-0.28 0.02 L-0.06 0.24 L0.34 -0.24"
      }
    },
    "swift-redux": {
      "hue": 312,
      "face_colors": [
        "oklch(1 0 0)",
        "oklch(0.95 0.004 312)"
      ],
      "band_colors": [
        "oklch(0.92 0.004 312)",
        "oklch(0.66 0.15 316)",
        "oklch(0.57 0.15 306)"
      ],
      "glyph": "loop3",
      "glyph_rotation": -45,
      "glyph_color": "oklch(0.6 0.18 314)",
      "glyph_side": "oklch(0.46 0.15 308)",
      "texture": "none"
    },
    "swift-pdf": {
      "hue": 338,
      "mode": "deepen",
      "bands": 3,
      "texture": "lines",
      "glyph_rotation": -45,
      "glyph_scale": 0.33,
      "drift": 0,
      "vivid": 1.1,
      "custom_glyph": {
        "style": "stroke",
        "width": 0.14,
        "d": "M-0.58 -0.86 H0.22 L0.60 -0.48 V0.86 H-0.58 Z M0.22 -0.86 V-0.48 H0.60 M-0.32 -0.10 H0.34 M-0.32 0.20 H0.34 M-0.32 0.50 H0.10"
      }
    },
    "swift-interface-distiller": {
      "hue": 214,
      "mode": "glow",
      "bands": 3,
      "texture": "grid",
      "glyph_rotation": -45,
      "face_colors": [
        "oklch(0.60 0.12 214)",
        "oklch(0.49 0.10 214)"
      ],
      "band_colors": [
        "oklch(0.53 0.12 214)",
        "oklch(0.62 0.15 214)",
        "oklch(0.71 0.16 214)"
      ],
      "glyph_scale": 0.34,
      "custom_glyph": {
        "style": "stroke",
        "width": 0.13,
        "d": "M-0.20 -0.82 H0.20 V-0.37 L0.76 0.64 Q0.84 0.80 0.64 0.80 H-0.64 Q-0.84 0.80 -0.76 0.64 L-0.20 -0.37 Z M-0.30 -0.82 H0.30",
        "extra": "M-0.57 0.30 H0.57 M0.19 -0.02 H0.38 M0.39 0.57 H0.67"
      }
    }
  },
  "app_icons": {
    "swift-library": {
      "background": "#f12e1d",
      "gradient": true,
      "groups": [
        {
          "name": "Warm dot field",
          "layers": [
            {
              "source": "Brand/Avatar/Dots.svg",
              "name": "Dots"
            }
          ],
          "shadow": {
            "kind": "neutral",
            "opacity": 0
          },
          "translucency": {
            "enabled": false,
            "value": 0
          }
        },
        {
          "name": "Swift bird",
          "layers": [
            {
              "source": "Brand/Avatar/Bird.svg",
              "name": "Bird"
            }
          ],
          "shadow": {
            "kind": "neutral",
            "opacity": 0.5
          },
          "translucency": {
            "enabled": false,
            "value": 0
          }
        }
      ]
    }
  }
}
```

### Documentation pages

Each package's DocC landing page shows its repository icon and a page color,
following the DocC landing identity rule of the `swiftpm-docs` skill. The icon is
a copy of the repository's `Logo.png`. DocC accepts only named page colors, so
the color comes from the icon hue:

| Icon hue (OKLCH) | Page color |
| --- | --- |
| 330 to 35 | `red` |
| 35 to 75 | `orange` |
| 75 to 115 | `yellow` |
| 115 to 185 | `green` |
| 185 to 265 | `blue` |
| 265 to 330 | `purple` |

## Website

The project catalog gives the icon family space to carry the color. Page
surfaces, navigation, borders, and typography stay neutral. The homepage uses
a 128 px organization app icon above its name and purpose, followed by grouped
project cards. Repository names, descriptions, versions, documentation links,
and installation commands remain the primary content.

### Typography and layout

- Self-host the unmodified Inter 4.1 variable WOFF2 with its SIL Open Font
  License. Use optical sizing, regular body copy, and semibold headings.
- Limit the main content to 1120 px. Use a two-column catalog with 20 px gaps;
  below 760 px use one column and 20 px page margins.
- The hero heading scales from 44 to 72 px. Card headings use 21 px, body copy
  15 px, and supplementary labels at least 12 px. Installation commands use a
  system monospace face and horizontal overflow within their own region.
- Cards use a 20 px corner radius, a subtle border, and a solid surface. Their
  repository icon is 64 px. Avoid extra decorative artwork around the family.
- Navigation stays on one line. Put license, contributors, and versioning links
  in the footer; the header links to contributing and GitHub.

### Appearance tokens

Use the system color preference with CSS. Clipboard copying is the only
JavaScript behavior. Content and installation commands remain available
without JavaScript or clipboard permission.

| Role | Light | Dark |
| --- | --- | --- |
| Canvas | `#fbfbfd` | `#141417` |
| Card | `#ffffff` | `#1d1d21` |
| Command background | `#f0f0f3` | `#28282d` |
| Main text | `#1d1d1f` | `#f5f5f7` |
| Secondary text | `#424245` | `#d1d1d7` |
| Supplementary text | `#606068` | `#aaaab3` |
| Decorative border | `#d9d9df` | `#393940` |
| Control border | `#76767c` | `#82828c` |
| Focus ring | `#005cc5` | `#8eb8ff` |

Text must meet WCAG AA contrast against its actual background. Controls retain
visible keyboard focus, copy outcomes are announced through a status region,
and motion respects reduced-motion preferences. Check the homepage,
contributing page, and error page at desktop, intermediate, and mobile widths
in both appearances before publishing.
