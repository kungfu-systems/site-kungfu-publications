# Kungfu Publications Design System

This directory is the reusable visual material pack for Kungfu Publications.
It turns the visual language already used by the Atlas Lite PDFs into reviewed,
versioned source assets that can be reused by future guides, decks, and locale
projections.

## Design Principles

1. Start with the reader's problem and the value they can recognize.
2. Use structure before decoration: hierarchy, grouping, flow, and evidence.
3. Keep surfaces calm and reserve saturated colors for meaning.
4. Make review, uncertainty, and delivery boundaries visible.
5. Prefer source-auditable vectors over opaque generated imagery.

## Package Map

```text
tokens/       canonical color, typography, and layout decisions
styles/       generated LaTeX package consumed by PDF renderers
templates/    minimal A4 guide and 16:9 slide starting points
assets/       licensed SVG marks, backgrounds, illustrations, and icons
fonts/        font selection and redistribution policy
examples/     GitHub-viewable asset gallery
```

The JSON tokens are authoritative. Do not hand-edit
`styles/kungfu-publications.sty`; regenerate it with `make design`.

## Color Language

| Role | Token | Hex | Typical use |
| --- | --- | --- | --- |
| Primary ink | `KFBlack` | `#111827` | Titles and high-emphasis copy |
| Secondary ink | `KFSlate` | `#374151` | Body copy and labels |
| Brand/action | `KFGreen` | `#0F766E` | Paths, anchors, and positive action |
| Accent | `KFAqua` | `#2DD4BF` | Active nodes and highlights |
| Caution | `KFAmber` | `#F5B942` | Attention without alarm |
| Friction | `KFCoral` | `#F97360` | Problems, reversal, and risk |
| Information | `KFBlue` | `#4F86F7` | Documents and neutral information |
| Surfaces | `KFMint`, `KFLight`, `KFLighter` | light | Panels and page backgrounds |

The complete machine-readable palette is in
[`tokens/colors.json`](tokens/colors.json). Asset validation rejects colors
outside this palette.

## Typography and Layout

The design system chooses installed fonts from documented fallback stacks; it
does not ship font binaries. See [`fonts/README.md`](fonts/README.md).

Two first-class formats are defined in [`tokens/layout.json`](tokens/layout.json):

- A4 portrait for guides, white papers, and printable tutorials;
- 16:9 landscape for plain-language decks and screen-first explainers.

Start new renderers from [`templates/`](templates/) so font and color behavior
stays shared. A template is a structural starting point, not a requirement to
make every publication look identical.

Tectonic resolves the shared package when a renderer imports
`install_tex_style` from `design_system` and places the generated `.sty` beside
the temporary `.tex` file. New Python renderers should follow the same pattern;
the templates are intentionally source files rather than standalone binaries.

## SVG Material Pack

The assets are intentionally compact, scalable, and language-light. The
machine-readable [`assets/manifest.json`](assets/manifest.json) records usage
and Chinese alternative text. Browse the
[`asset gallery`](examples/asset-gallery.md) directly on GitHub.

SVG assets must:

- include a `viewBox`, `<title>`, and `<desc>`;
- use only design-token colors;
- contain no embedded raster image;
- be declared in the asset manifest.

## Build and Review

```sh
make design       # regenerate the shared LaTeX style from tokens
make design-check # detect stale style, invalid assets, and template drift
make all          # regenerate Markdown and PDF projections, then verify
```

Changing a token or shared style can affect every publication. Rebuild all PDF
projections, render every page to images, and inspect them before merging.

## Licensing

The SVG pack is covered by [`assets/LICENSE.md`](assets/LICENSE.md). Brand names
and marks remain subject to the repository's trademark policy.
