#!/usr/bin/env python3
"""Render the Atlas x Kungfu workflow feature article as a designed PDF."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path

from design_system import install_tex_style
from render_atlas_lite_guide import (
    code_block,
    inline_tex,
    normalize,
    strip_frontmatter,
    table_block,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = REPO_ROOT / "content/atlas-kungfu-agent-workflow/core/zh-CN.md"
DEFAULT_BUILD_DIR = REPO_ROOT / "_build/tex/atlas-kungfu-agent-workflow/zh-CN"
DEFAULT_OUTPUT = REPO_ROOT / "_build/pdf/atlas-kungfu-agent-workflow-zh-CN.pdf"


PREAMBLE = r"""
\documentclass[10.5pt,a4paper]{article}
\usepackage[a4paper,top=17mm,bottom=18mm,left=18mm,right=18mm,headheight=19pt]{geometry}
\usepackage{kungfu-publications}
\usepackage{microtype}
\usepackage{graphicx}
\usepackage{array}
\usepackage{booktabs}
\usepackage{tabularx}
\usepackage{enumitem}
\usepackage{needspace}
\usepackage{titlesec}
\usepackage{fancyhdr}
\usepackage{hyperref}
\usepackage{tikz}
\usepackage[most]{tcolorbox}
\usepackage{lastpage}
\usetikzlibrary{arrows.meta,positioning,calc,fit,backgrounds,shapes.geometric}

\hypersetup{
  colorlinks=true,
  linkcolor=KFGreen,
  urlcolor=KFGreen,
  pdftitle={Agent可靠工作法，30天，4000个PR},
  pdfsubject={Atlas 与 Kungfu 的 Work Runtime 与多 Agent 工作法},
  pdfauthor={Kungfu Origin Technology Limited},
  pdfkeywords={Atlas, Kungfu, multi-agent, delivery warrant, software workflow}
}

\setlength{\parindent}{0pt}
\setlength{\parskip}{0.66em}
\setlength{\emergencystretch}{2em}
\setlist[itemize]{leftmargin=1.45em,itemsep=0.34em,topsep=0.38em}
\setlist[enumerate]{leftmargin=1.7em,itemsep=0.34em,topsep=0.38em}
\renewcommand{\arraystretch}{1.35}

\pagestyle{fancy}
\fancyhf{}
\lhead{\footnotesize\color{KFSlate}\textbf{ATLAS × KUNGFU}}
\rhead{\footnotesize\color{KFSlate}以工作为核心的 Agent 组织系统}
\cfoot{\footnotesize\color{KFSlate}\thepage\ / \pageref*{LastPage}}
\renewcommand{\headrulewidth}{0.35pt}
\renewcommand{\headrule}{\hbox to\headwidth{\color{KFLine}\leaders\hrule height \headrulewidth\hfill}}

\titleformat{\subsection}{\large\bfseries\color{KFBlack}}{}{0pt}{}
\titleformat{\subsubsection}{\normalsize\bfseries\color{KFGreen}}{}{0pt}{}
\titlespacing*{\subsection}{0pt}{1.15em}{0.45em}
\titlespacing*{\subsubsection}{0pt}{0.9em}{0.35em}

\newcommand{\eyebrow}[1]{\textcolor{KFGreen}{\bfseries\footnotesize\MakeUppercase{#1}}}
\newtcolorbox{calloutbox}[1][]{
  enhanced,breakable,colback=KFLight,colframe=KFLine,boxrule=0.6pt,
  arc=3mm,left=4mm,right=4mm,top=3mm,bottom=3mm,
  borderline west={2.2pt}{0pt}{KFGreen},#1
}
\newtcolorbox{codebox}[1][]{
  enhanced,breakable,colback=KFBlack,colframe=KFBlack,boxrule=0pt,
  arc=2.5mm,left=3.5mm,right=3.5mm,top=3mm,bottom=3mm,
  fontupper=\ttfamily\footnotesize\color{white},#1
}
\newtcolorbox{diagrambox}[1][]{
  enhanced,colback=KFLighter,colframe=KFLine,boxrule=0.6pt,
  arc=3mm,left=3mm,right=3mm,top=3mm,bottom=3mm,#1
}
\newtcolorbox{storybox}[1][]{
  enhanced,breakable,colback=KFBlack,colframe=KFBlack,boxrule=0pt,
  arc=3mm,left=5mm,right=5mm,top=4mm,bottom=4mm,
  fontupper=\color{white},#1
}

\tikzset{
  flow/.style={rounded corners=2mm,draw=KFLine,fill=white,very thick,
    text=KFBlack,align=center,minimum height=10mm,inner xsep=4mm,inner ysep=2mm},
  flowgreen/.style={flow,draw=KFGreen!55,fill=KFMint},
  flowdark/.style={flow,draw=KFBlack,fill=KFBlack,text=white},
  arrow/.style={-{Stealth[length=2.5mm]},very thick,draw=KFGreen!75},
  softarrow/.style={-{Stealth[length=2mm]},thick,draw=KFSlate!45},
  warningarrow/.style={-{Stealth[length=2mm]},thick,dashed,draw=KFCoral!85}
}

\newcommand{\chapterlead}[2]{%
  \par\vspace{0.5em}
  \begin{tcolorbox}[enhanced,colback=KFBlack,colframe=KFBlack,arc=3mm,
    left=5mm,right=5mm,top=4mm,bottom=4mm]
    {\color{KFAqua}\bfseries\footnotesize #1}\par\vspace{0.25em}
    {\color{white}\Large\bfseries #2}
  \end{tcolorbox}
}

\begin{document}
"""


COVER = r"""
\begin{titlepage}
\thispagestyle{empty}
\begin{tikzpicture}[remember picture,overlay]
  \fill[KFBlack] (current page.south west) rectangle (current page.north east);
  \fill[KFGreen] ([xshift=-32mm,yshift=-23mm]current page.north east) circle (58mm);
  \fill[KFAqua,opacity=0.12] ([xshift=4mm,yshift=12mm]current page.south west) circle (67mm);
  \foreach \x/\y in {18/61,52/82,88/58,124/90,162/63,193/104}
    \fill[KFAqua] ([xshift=\x mm,yshift=\y mm]current page.south west) circle (2mm);
  \draw[KFAqua,opacity=0.5,line width=1pt]
    ([xshift=18mm,yshift=61mm]current page.south west) --
    ([xshift=52mm,yshift=82mm]current page.south west) --
    ([xshift=88mm,yshift=58mm]current page.south west) --
    ([xshift=124mm,yshift=90mm]current page.south west) --
    ([xshift=162mm,yshift=63mm]current page.south west) --
    ([xshift=193mm,yshift=104mm]current page.south west);
\end{tikzpicture}

\vspace*{11mm}
{\color{KFAqua}\bfseries\footnotesize ATLAS × KUNGFU · FEATURE ARTICLE 2026}\par
\vspace{23mm}

{\fontsize{46}{52}\selectfont\bfseries\color{white}Agent可靠工作法\par}
\vspace{2mm}
{\fontsize{29}{36}\selectfont\bfseries\color{white}30天，4000个PR\par}
\vspace{8mm}
{\fontsize{17}{24}\selectfont\color{KFAqua}
Agent 时代最重要的不是 Agent，而是工作本身\par}

\vspace{12mm}
\begin{tcolorbox}[enhanced,width=0.84\textwidth,colback=KFSlate,colframe=white!16,
  boxrule=0.5pt,arc=3mm,left=5mm,right=5mm,top=4mm,bottom=4mm]
{\color{white}\large
从百万级软件工程到千万流水小公司\\[1mm]
Work Runtime 如何把执行力变成组织能力}
\end{tcolorbox}

\vfill
{\color{white!68}\large Agent 提供执行力。Work Runtime 提供组织能力。}\par
{\color{white}\Large\bfseries Work State 是用户真正拥有的数据资产。}\par
\vspace{11mm}
{\color{white!48}\footnotesize Kungfu Origin Technology Limited \quad | \quad 2026-08-27}
\end{titlepage}
"""


def diagram_tex(index: int, locale: str) -> str:
    diagrams = {
        1: r"""
\begin{diagrambox}\centering
\resizebox{0.98\linewidth}{!}{\begin{tikzpicture}[node distance=8mm and 10mm]
\node[flowdark] (main) {稳定主线};
\node[flow,above right=7mm and 13mm of main] (a) {Agent A\\独立工作区};
\node[flow,right=13mm of main] (b) {Agent B\\独立工作区};
\node[flow,below right=7mm and 13mm of main] (c) {Agent C\\独立工作区};
\node[flowgreen,right=17mm of b] (gate) {独立审核\\机器门禁};
\node[flowdark,right=of gate] (land) {有序进入主线};
\draw[softarrow] (main)--(a); \draw[softarrow] (main)--(b); \draw[softarrow] (main)--(c);
\draw[arrow] (a)--(gate); \draw[arrow] (b)--(gate); \draw[arrow] (c)--(gate);
\draw[arrow] (gate)--(land);
\end{tikzpicture}}
\end{diagrambox}
""",
        2: r"""
\begin{diagrambox}\centering
\resizebox{0.96\linewidth}{!}{\begin{tikzpicture}[node distance=8mm and 11mm]
\node[flowdark] (work) {持续存在的工作记录};
\node[flow,above right=7mm and 16mm of work] (s1) {Session A};
\node[flow,right=16mm of work] (s2) {Session B};
\node[flow,below right=7mm and 16mm of work] (s3) {另一家模型\\或 Agent};
\node[flowgreen,right=18mm of s2] (e) {结果、证据\\下一步};
\draw[arrow] (work)--(s1); \draw[arrow] (work)--(s2); \draw[arrow] (work)--(s3);
\draw[softarrow] (s1)--(e); \draw[softarrow] (s2)--(e); \draw[softarrow] (s3)--(e);
\draw[arrow,bend left=33] (e.north) to (work.north);
\end{tikzpicture}}
\end{diagrambox}
""",
        3: r"""
\begin{diagrambox}\centering
\resizebox{0.98\linewidth}{!}{\begin{tikzpicture}[node distance=7mm]
\node[flowdark] (a) {候选开始\\重度验证};
\node[flow,right=of a] (b) {主线继续前进};
\node[flow,right=of b] (c) {验证完成};
\node[flow,draw=KFCoral!70,fill=KFCoral!8,right=of c] (d) {候选已经落后};
\node[flowgreen,right=of d] (e) {重新同步\\再次验证};
\draw[arrow] (a)--(b); \draw[arrow] (b)--(c); \draw[warningarrow] (c)--(d); \draw[warningarrow] (d)--(e);
\draw[warningarrow,bend left=42] (e.north) to (b.north);
\end{tikzpicture}}
\end{diagrambox}
""",
        4: r"""
\begin{diagrambox}\centering
\resizebox{0.98\linewidth}{!}{\begin{tikzpicture}[node distance=7mm]
\node[flow] (p) {大量候选\\并行准备};
\node[flowgreen,right=of p] (s) {选择一个\\就绪候选};
\node[flowdark,right=of s] (w) {获得\\交付授权};
\node[flow,right=of w] (h) {完整编译\\重度验证};
\node[flowgreen,right=of h] (q) {最终交付队列};
\node[flowdark,right=of q] (m) {有序进入主线};
\draw[arrow] (p)--(s); \draw[arrow] (s)--(w); \draw[arrow] (w)--(h);
\draw[arrow] (h)--(q); \draw[arrow] (q)--(m);
\end{tikzpicture}}
\end{diagrambox}
""",
        5: r"""
\begin{diagrambox}\centering
\resizebox{0.94\linewidth}{!}{\begin{tikzpicture}[node distance=7mm]
\node[flowdark] (r) {真实工作};
\node[flow,right=of r] (f) {暴露摩擦};
\node[flowgreen,right=of f] (i) {形成改进任务};
\node[flow,right=of i] (a) {Agent 实施修复};
\node[flowgreen,right=of a] (g) {审核与门禁};
\node[flowdark,right=of g] (n) {系统获得新能力};
\draw[arrow] (r)--(f); \draw[arrow] (f)--(i); \draw[arrow] (i)--(a);
\draw[arrow] (a)--(g); \draw[arrow] (g)--(n);
\draw[arrow,bend left=46] (n.north) to (r.north);
\end{tikzpicture}}
\end{diagrambox}
""",
    }
    if index not in diagrams:
        raise ValueError(f"unexpected Mermaid diagram {index}")
    diagram = diagrams[index]
    if locale == "en-US":
        replacements = {
            "稳定主线": "Stable mainline",
            "独立工作区": "isolated workspace",
            "独立审核\\\\机器门禁": "independent review\\\\machine gates",
            "有序进入主线": "ordered landing",
            "持续存在的工作记录": "durable work record",
            "另一家模型\\\\或 Agent": "another model\\\\or Agent",
            "结果、证据\\\\下一步": "results, evidence\\\\next action",
            "候选开始\\\\重度验证": "candidate starts\\\\heavy validation",
            "主线继续前进": "mainline keeps moving",
            "验证完成": "validation completes",
            "候选已经落后": "candidate is stale",
            "重新同步\\\\再次验证": "resync\\\\validate again",
            "大量候选\\\\并行准备": "many candidates\\\\prepare in parallel",
            "选择一个\\\\就绪候选": "select one\\\\ready candidate",
            "获得\\\\交付授权": "grant\\\\Delivery Warrant",
            "完整编译\\\\重度验证": "full build\\\\heavy validation",
            "最终交付队列": "final delivery queue",
            "真实工作": "real work",
            "暴露摩擦": "expose friction",
            "形成改进任务": "create improvement task",
            "审核与门禁": "review and gates",
            "系统获得新能力": "system gains capability",
            "Agent 实施修复": "Agent implements fix",
        }
        for source, target in replacements.items():
            diagram = diagram.replace(source, target)
    return diagram


def markdown_to_tex(markdown: str, locale: str) -> str:
    lines = strip_frontmatter(normalize(markdown).splitlines())
    output: list[str] = []
    paragraph: list[str] = []
    list_kind: str | None = None
    diagram_index = 0
    chapter_index = 0
    opening_seen = False
    toc_inserted = False
    index = 0

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            output.append(inline_tex(" ".join(part.strip() for part in paragraph)) + "\n")
            paragraph = []

    def close_list() -> None:
        nonlocal list_kind
        if list_kind:
            output.append(rf"\end{{{list_kind}}}")
            list_kind = None

    while index < len(lines):
        stripped = lines[index].strip()

        if stripped.startswith("```"):
            flush_paragraph()
            close_list()
            language = stripped[3:].strip()
            block_lines: list[str] = []
            index += 1
            while index < len(lines) and lines[index].strip() != "```":
                block_lines.append(lines[index])
                index += 1
            if language == "mermaid":
                diagram_index += 1
                output.append(diagram_tex(diagram_index, locale))
            else:
                output.append(code_block(block_lines, language))
            index += 1
            continue

        if stripped.startswith("|") and stripped.endswith("|"):
            flush_paragraph()
            close_list()
            rows: list[list[str]] = []
            while index < len(lines):
                candidate = lines[index].strip()
                if not (candidate.startswith("|") and candidate.endswith("|")):
                    break
                rows.append([cell.strip() for cell in candidate.strip("|").split("|")])
                index += 1
            output.append(table_block(rows))
            continue

        if stripped.startswith("# "):
            flush_paragraph()
            close_list()
            index += 1
            continue

        if stripped.startswith("## "):
            flush_paragraph()
            close_list()
            title = stripped[3:].strip()
            if not opening_seen:
                opening_seen = True
                output.append(r"\chapterlead{THE STORY FIRST}{" + inline_tex(title) + "}")
            else:
                chapter_index += 1
                if title == "Appendix: a multi-dimensional comparison of the KFD workflow and mainstream Agent methods":
                    output.append(r"\clearpage")
                else:
                    output.append(r"\Needspace{0.30\textheight}")
                output.append(r"\refstepcounter{section}\phantomsection")
                output.append(
                    r"\addcontentsline{toc}{section}{\protect\numberline{\thesection}"
                    + inline_tex(title)
                    + "}"
                )
                output.append(
                    rf"\chapterlead{{CHAPTER {chapter_index:02d}}}{{{inline_tex(title)}}}"
                )
            index += 1
            continue

        if stripped.startswith("### "):
            flush_paragraph()
            close_list()
            output.append(rf"\subsection{{{inline_tex(stripped[4:].strip())}}}")
            index += 1
            continue

        if stripped.startswith("#### "):
            flush_paragraph()
            close_list()
            output.append(rf"\subsubsection{{{inline_tex(stripped[5:].strip())}}}")
            index += 1
            continue

        if stripped.startswith("> "):
            flush_paragraph()
            close_list()
            quotes: list[str] = []
            while index < len(lines) and lines[index].strip().startswith("> "):
                quotes.append(lines[index].strip()[2:])
                index += 1
            if opening_seen:
                output.append(r"\begin{calloutbox}")
                output.append(inline_tex(" ".join(quotes)))
                output.append(r"\end{calloutbox}")
            continue

        unordered = re.match(r"^-\s+(.*)$", stripped)
        ordered = re.match(r"^\d+\.\s+(.*)$", stripped)
        if unordered or ordered:
            flush_paragraph()
            desired = "itemize" if unordered else "enumerate"
            if list_kind != desired:
                close_list()
                output.append(rf"\begin{{{desired}}}")
                list_kind = desired
            output.append(r"\item " + inline_tex((unordered or ordered).group(1)))
            index += 1
            continue

        if stripped == "---":
            flush_paragraph()
            close_list()
            if opening_seen and not toc_inserted:
                output.append(r"\clearpage\tableofcontents\clearpage")
                toc_inserted = True
            index += 1
            continue

        if not stripped:
            flush_paragraph()
            close_list()
            index += 1
            continue

        paragraph.append(stripped)
        index += 1

    flush_paragraph()
    close_list()
    if diagram_index != 5:
        raise ValueError(f"expected 5 Mermaid diagrams, found {diagram_index}")
    if not toc_inserted:
        raise ValueError("opening separator did not create the table of contents")
    return "\n".join(output)


ENDING = r"""
\clearpage
\thispagestyle{empty}
\begin{tikzpicture}[remember picture,overlay]
  \fill[KFBlack] (current page.south west) rectangle (current page.north east);
  \fill[KFGreen] ([xshift=-24mm,yshift=-18mm]current page.north east) circle (54mm);
  \fill[KFAqua,opacity=0.12] ([xshift=8mm,yshift=10mm]current page.south west) circle (65mm);
\end{tikzpicture}
\vspace*{25mm}
{\color{KFAqua}\bfseries\footnotesize FROM AGENT TO ORGANIZATION}\par\vspace{6mm}
{\color{white}\fontsize{28}{36}\selectfont\bfseries
Agent 提供执行力。\\
Work Runtime 提供组织能力。\par}
\vspace{12mm}
{\color{white!78}\Large
Agent 可以更换，Session 可以结束，\\
但 Work 不会归零，现实不会失忆。\par}
\vspace{18mm}
\begin{tcolorbox}[enhanced,colback=KFSlate,colframe=white!14,boxrule=0.5pt,arc=3mm,
  left=5mm,right=5mm,top=5mm,bottom=5mm]
{\color{white}\large
聊天记录保存我们说过什么。\\[2mm]
\textbf{Work State 保存现实现在是什么。}}
\end{tcolorbox}
\vfill
{\color{KFAqua}\bfseries Atlas × Kungfu}\quad
{\color{white!55}Agent可靠工作法，30天，4000个PR}
\end{document}
"""


def source_locale(markdown: str) -> str:
    match = re.search(r"^locale:\s*([^\s]+)\s*$", markdown, flags=re.MULTILINE)
    return match.group(1) if match else "zh-CN"


def localized_static(template: str, locale: str) -> str:
    if locale == "zh-CN":
        return template
    if locale != "en-US":
        raise ValueError(f"unsupported feature article locale: {locale}")
    replacements = [
        ("Agent可靠工作法，30天，4000个PR", "Reliable Agent Workflow, 30 Days, 4,000 PRs"),
        ("Atlas 与 Kungfu 的 Work Runtime 与多 Agent 工作法", "The Atlas and Kungfu Work Runtime and multi-Agent workflow"),
        ("以工作为核心的 Agent 组织系统", "A Work-Centered Agent System"),
        ("Agent 时代最重要的不是 Agent，而是工作本身", "The most important thing in the Agent era is not the Agent, but the work"),
        ("从百万级软件工程到千万流水小公司", "From million-line software to a multimillion-revenue business"),
        ("Work Runtime 如何把执行力变成组织能力", "How a Work Runtime turns execution into organization"),
        ("30天，4000个PR", "30 DAYS. 4,000 PRs."),
        (
            r"{\fontsize{46}{52}\selectfont\bfseries\color{white}Agent可靠工作法\par}",
            r"{\fontsize{33}{39}\selectfont\bfseries\color{white}\mbox{RELIABLE AGENT WORKFLOW}\par}",
        ),
        ("Agent 提供执行力。Work Runtime 提供组织能力。", "Agents provide execution. The Work Runtime provides organization."),
        ("Work State 是用户真正拥有的数据资产。", "Work State is the data asset the user truly owns."),
        ("Agent 提供执行力。", "Agents execute."),
        ("Work Runtime 提供组织能力。", "Work Runtime organizes."),
        ("Agent 可以更换，Session 可以结束，", "Agents can change. Sessions can end."),
        ("但 Work 不会归零，现实不会失忆。", "Work does not return to zero. Reality does not forget."),
        ("聊天记录保存我们说过什么。", "Chat history records what we said."),
        ("Work State 保存现实现在是什么。", "Work State records what reality is now."),
    ]
    localized = template
    for source, target in replacements:
        localized = localized.replace(source, target)
    return localized


def build_pdf(source: Path, build_dir: Path, output: Path) -> None:
    markdown = source.read_text(encoding="utf-8")
    locale = source_locale(markdown)
    build_dir.mkdir(parents=True, exist_ok=True)
    install_tex_style(build_dir)
    output.parent.mkdir(parents=True, exist_ok=True)
    tex_path = build_dir / "atlas-kungfu-workflow-article.tex"
    tex_path.write_text(
        localized_static(PREAMBLE, locale)
        + localized_static(COVER, locale)
        + markdown_to_tex(markdown, locale)
        + localized_static(ENDING, locale),
        encoding="utf-8",
    )
    tectonic = shutil.which("tectonic")
    if tectonic is None:
        raise RuntimeError("tectonic is required to build PDF projections")
    subprocess.run(
        [
            tectonic,
            "--keep-logs",
            "--keep-intermediates",
            "--outdir",
            str(build_dir),
            str(tex_path),
        ],
        cwd=REPO_ROOT,
        check=True,
    )
    built_pdf = build_dir / "atlas-kungfu-workflow-article.pdf"
    if not built_pdf.exists():
        raise FileNotFoundError(f"Tectonic did not create {built_pdf}")
    output.write_bytes(built_pdf.read_bytes())
    print(output)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--build-dir", type=Path, default=DEFAULT_BUILD_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    build_pdf(args.source.resolve(), args.build_dir.resolve(), args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
