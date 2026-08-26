# Font Policy

Kungfu Publications does not redistribute font binaries. The build selects the
first installed font from each documented stack:

| Role | Preferred | Fallbacks |
| --- | --- | --- |
| Latin sans | Helvetica Neue | TeX Gyre Heros, Arial |
| Simplified Chinese sans | PingFang SC | Noto Sans CJK SC, Source Han Sans SC |
| Monospace | Menlo | DejaVu Sans Mono, TeX Gyre Cursor |

The exact machine-readable stacks live in
[`../tokens/typography.json`](../tokens/typography.json). macOS builds normally
use Helvetica Neue, PingFang SC, and Menlo. Linux builders should install one of
the listed open fallbacks before rendering localized PDFs.

Do not commit font files here unless their license explicitly permits
redistribution and the repository records the license and provenance.
