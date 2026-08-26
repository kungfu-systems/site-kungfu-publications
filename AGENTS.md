# Agent Entry Point

This repository publishes reviewed, multilingual explanations of reliable
agent-assisted work.

- To read or use a publication, start with [`docs/MAP.md`](docs/MAP.md).
- To add or modify content, locales, renderers, or release automation, read
  [`CONTRIBUTING.md`](CONTRIBUTING.md).
- Treat `content/` as authoritative. Do not edit generated Markdown under
  `docs/<locale>/` directly.
- Treat `design-system/tokens/` as authoritative for shared visual decisions.
  Regenerate the shared style and declare reusable SVGs in the asset manifest.
- Do not commit `_build/` outputs. PDF projections are GitHub Release assets.

Run `make check` before proposing a change. Run `make all` when the PDF
toolchain is available and the change affects published content or layout.
