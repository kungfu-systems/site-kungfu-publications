# Contributing

## Source and Projection Boundary

Every publication is registered in `catalog.json` and stores reviewed content
under `content/<publication>/core/`.

- Markdown cores use `<locale>.md`.
- Structured slide cores use `<locale>.json`.
- `docs/<locale>/` contains generated Markdown projections.
- `_build/pdf/` contains generated PDF projections and is not committed.

Edit a core, then regenerate its projections. Never patch a generated Markdown
file as the source of a correction.

## Add a Publication

1. Add a unique publication entry to `catalog.json`.
2. Add the reviewed source-locale core under `content/<id>/core/`.
3. Select or implement a renderer without mixing content into release logic.
4. Run `make all` and inspect every rendered PDF page.
5. Commit the generated Markdown projection, but not `_build/`.

## Add a Locale

1. Translate from the registered `source_locale`; do not translate from a PDF.
2. Preserve headings, claims, cautions, links, and structural relationships.
3. Add the locale core with `status` set to `draft` while it is being reviewed.
4. Change the locale registry status to `published` only after linguistic and
   subject review.
5. Generate both Markdown and PDF projections and inspect the complete PDF.

Machine translation may create a draft. It does not by itself establish review
or publication status.

## Checks

```sh
make md
make check
make pdf
```

`make check` verifies the catalog, core paths, locale bindings, Python syntax,
and generated Markdown freshness. `make pdf` creates PDF files and SHA-256
checksums under `_build/pdf/`.

## Commit Requirements

- Use Developer Certificate of Origin sign-off.
- Use lightweight Conventional Commits.
- Write commit messages and pull request descriptions in English.

Example:

```sh
git commit -s -m "feat(publications): add reviewed atlas lite sources"
```

## Public-Surface Review

Do not publish credentials, tokens, private logs, private paths, internal
control-plane records, or claims that exceed available evidence. Mark planned,
inferred, version-sensitive, or unverified statements clearly.
