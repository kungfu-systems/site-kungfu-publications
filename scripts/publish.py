#!/usr/bin/env python3
"""Build and verify Markdown and PDF projections from publication cores."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "catalog.json"


def catalog() -> dict:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def strip_frontmatter(markdown: str) -> str:
    return re.sub(r"\A---\n.*?\n---\n+", "", markdown, count=1, flags=re.DOTALL)


def release_url(filename: str) -> str:
    return (
        "https://github.com/kungfu-systems/site-kungfu-publications/"
        f"releases/latest/download/{filename}"
    )


def markdown_breaks(value: str) -> str:
    return value.replace("\n", "<br>\n")


def render_slides_markdown(core: dict, filename: str) -> str:
    lines = [
        f"# {core['title']}",
        "",
        f"> {core['subtitle']}",
        "",
    ]
    for slide in core["slides"]:
        lines.extend(
            [
                f"<!-- slide: {slide['number']} -->",
                "",
                f"## {slide['eyebrow']}",
                "",
                markdown_breaks(slide["title"]),
                "",
            ]
        )
        if slide.get("lead"):
            lines.extend([f"**{markdown_breaks(slide['lead'])}**", ""])
        for point in slide.get("points", []):
            lines.append(f"- {point}")
        for step in slide.get("steps", []):
            lines.append(f"- {step}")
        if slide.get("points") or slide.get("steps"):
            lines.append("")
        for card in slide.get("cards", []):
            label = f"{card.get('label')} · " if card.get("label") else ""
            lines.extend([f"### {label}{card['title']}", "", markdown_breaks(card["body"]), ""])
        if slide.get("body"):
            lines.extend([slide["body"], ""])
    return "\n".join(lines).rstrip() + "\n"


def markdown_projection(publication: dict, locale: str, locale_spec: dict) -> str:
    core_path = ROOT / locale_spec["core"]
    pdf_name = publication["pdf_filename"].format(locale=locale)
    if publication["core_format"] == "markdown":
        body = strip_frontmatter(core_path.read_text(encoding="utf-8"))
    elif publication["core_format"] == "slides-json":
        body = render_slides_markdown(json.loads(core_path.read_text(encoding="utf-8")), pdf_name)
    else:
        raise ValueError(f"unsupported core format: {publication['core_format']}")
    notice = (
        "<!-- Generated from the locale core. Edit content/, not this projection. -->\n\n"
        f"> [Download PDF]({release_url(pdf_name)}) · "
        f"[Publication catalog](../../README.md#publications)\n\n"
    )
    return notice + body


def published_locales(publication: dict):
    for locale, locale_spec in publication["locales"].items():
        if locale_spec.get("status") == "published":
            yield locale, locale_spec


def build_markdown(check: bool) -> None:
    for publication in catalog()["publications"]:
        for locale, locale_spec in published_locales(publication):
            target = ROOT / "docs" / locale / f"{publication['id']}.md"
            expected = markdown_projection(publication, locale, locale_spec)
            if check:
                if not target.exists() or target.read_text(encoding="utf-8") != expected:
                    raise SystemExit(f"stale Markdown projection: {target.relative_to(ROOT)}")
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(expected, encoding="utf-8")
                print(target.relative_to(ROOT))


def build_pdfs() -> None:
    for publication in catalog()["publications"]:
        renderer = "render_atlas_lite_guide.py" if publication["layout"] == "guide" else "render_atlas_lite_intro.py"
        for locale, locale_spec in published_locales(publication):
            output = ROOT / "_build" / "pdf" / publication["pdf_filename"].format(locale=locale)
            build_dir = ROOT / "_build" / "tex" / publication["id"] / locale
            subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / renderer),
                    "--source",
                    str(ROOT / locale_spec["core"]),
                    "--build-dir",
                    str(build_dir),
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                check=True,
            )
            verify_pdf(output, publication)


def verify_pdf(pdf: Path, publication: dict) -> None:
    pdfinfo = shutil.which("pdfinfo")
    pdftotext = shutil.which("pdftotext")
    if pdfinfo is None or pdftotext is None:
        raise RuntimeError("Poppler pdfinfo and pdftotext are required for PDF verification")
    info = subprocess.run([pdfinfo, str(pdf)], check=True, capture_output=True, text=True).stdout
    match = re.search(r"^Pages:\s+(\d+)$", info, flags=re.MULTILINE)
    if match is None or int(match.group(1)) != publication["expected_pages"]:
        actual = match.group(1) if match else "unknown"
        raise RuntimeError(
            f"unexpected page count for {pdf.name}: {actual}; expected {publication['expected_pages']}"
        )
    text = subprocess.run(
        [pdftotext, "-layout", str(pdf), "-"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    pages = [page.strip() for page in text.split("\f") if page.strip()]
    if len(pages) != publication["expected_pages"]:
        raise RuntimeError(f"one or more PDF pages have no extractable text: {pdf.name}")
    if publication["text_probe"] not in text:
        raise RuntimeError(f"expected text is missing from PDF: {publication['text_probe']}")
    print(f"verified PDF: {pdf.relative_to(ROOT)} ({len(pages)} pages)")


def verify() -> None:
    data = catalog()
    ids = [publication["id"] for publication in data["publications"]]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate publication id")
    for publication in data["publications"]:
        if publication["source_locale"] not in publication["locales"]:
            raise SystemExit(f"missing source locale for {publication['id']}")
        for locale, locale_spec in published_locales(publication):
            core_path = ROOT / locale_spec["core"]
            if not core_path.is_file():
                raise SystemExit(f"missing core: {core_path.relative_to(ROOT)}")
            if locale_spec["core"].split("/")[-1].split(".")[0] != locale:
                raise SystemExit(f"locale/core mismatch for {publication['id']} {locale}")
    build_markdown(check=True)
    print(f"verified {len(ids)} publications")


def checksums() -> None:
    pdfs = sorted((ROOT / "_build" / "pdf").glob("*.pdf"))
    if not pdfs:
        raise SystemExit("no PDFs found; run make pdf first")
    lines = []
    for pdf in pdfs:
        digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
        lines.append(f"{digest}  {pdf.name}")
    target = ROOT / "_build" / "pdf" / "SHA256SUMS"
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(target.relative_to(ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("md", "pdf", "all", "verify", "checksums"))
    args = parser.parse_args()
    if args.command in {"md", "all"}:
        build_markdown(check=False)
    if args.command in {"pdf", "all"}:
        build_pdfs()
    if args.command == "verify":
        verify()
    if args.command in {"pdf", "all", "checksums"}:
        checksums()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
