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
family shares geometry, lighting, and band rhythm; each repository has its own
hue so the icons stay distinct side by side. Pages around the icons stay
quiet: light neutral surfaces, near-black text, no decoration.

## Colors

- **Primary** (`#f12e1d`) and **Primary Light** (`#ff9d36`) are the
  organization icon's face; they appear only in the organization icon and its
  derived assets.
- **Badge Swift** (`#F05138`) colors the Swift version badge.
- **Ink**, **Ink Secondary**, and **Ink Tertiary** set repository names,
  summaries, and owner labels on social preview cards.
- **Surface** to **Surface Dim** is the vertical gradient behind social
  preview cards.
- The **Terminal** colors define the dark window used for command-line demos,
  with a green prompt and light output text.
- Repository icon colors live in the Iconography section, one hue per
  repository.

## Typography

Social preview text uses Inter and Inter Display (SIL Open Font License),
converted to outlines so cards never depend on installed fonts. Repository
names are bold display weight; summaries are regular weight and wrap to at
most three lines. Terminal demos use the viewer's monospace font at 14 px.

## Layout

Social preview cards are 1280 by 640. The icon sits centered at x 300 with a
420 px square; text starts at x 560 and wraps before x 1200, vertically
centered as one block. README headers center the logo at 160 px above the
repository name.

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

- Do give each new repository its own hue, spaced away from existing hues.
- Do keep symbols that must be read upright (rotation -45) and lay symmetric
  marks along the face axes (rotation 0).
- Do derive banner and social preview art from the icons, never redraw them.
- Don't use Apple system fonts, SF Symbols, or other restricted glyph sets.
- Repository glyphs are original. The organization's supplied Swift bird is
  limited to its avatar; its source ownership is recorded in
  [Brand/Avatar/README.md](Brand/Avatar/README.md).
- Don't put text inside icons or banners.

## Iconography

Entries under `icons` render repository logos at 1024 px with
`apple-framework-icon-design`. Colors are OKLCH. Regenerate after changing
an entry and replace the owning repository’s `Logo.svg` and `Logo.png`.

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
        "oklch(0.58 0.21 18)",
        "oklch(0.67 0.2 10)",
        "oklch(0.8 0.11 2)"
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
        "oklch(0.82 0.14 52)",
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
        "oklch(0.27 0.05 172)"
      ],
      "band_colors": [
        "oklch(0.36 0.07 170)",
        "oklch(0.5 0.11 166)",
        "oklch(0.66 0.14 162)",
        "oklch(0.82 0.15 158)"
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
        "oklch(0.8 0.11 290)",
        "oklch(0.6 0.19 272)"
      ],
      "band_colors": [
        "oklch(0.64 0.17 272)",
        "oklch(0.72 0.14 282)",
        "oklch(0.81 0.1 292)"
      ]
    },
    "swift-json-schema": {
      "hue": 292,
      "mode": "glow",
      "bands": 3,
      "texture": "grid",
      "texture_opacity": 0.16,
      "face_colors": [
        "oklch(0.47 0.16 295)",
        "oklch(0.34 0.13 290)"
      ],
      "band_colors": [
        "oklch(0.42 0.16 292)",
        "oklch(0.57 0.19 292)",
        "oklch(0.73 0.14 292)"
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
        "width": 14,
        "transform": "scale(0.01)",
        "d": "M-58 -86 H22 L60 -48 V86 H-58 Z M22 -86 V-48 H60 M-32 -10 H34 M-32 20 H34 M-32 50 H10"
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
