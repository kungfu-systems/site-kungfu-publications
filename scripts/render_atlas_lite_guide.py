#!/usr/bin/env python3
"""Generate the commercial Atlas Lite tutorial PDF with Tectonic.

The source of truth remains the Markdown tutorial. This script applies a
brand-oriented LaTeX presentation inspired by the Kungfu Product White Paper.
It intentionally uses only the Python standard library; Tectonic owns the PDF
rendering step.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = REPO_ROOT / "content/atlas-lite-obsidian-hermes/core/zh-CN.md"
DEFAULT_BUILD_DIR = REPO_ROOT / "_build/tex/atlas-lite-obsidian-hermes/zh-CN"
DEFAULT_OUTPUT = REPO_ROOT / "_build/pdf/atlas-lite-obsidian-hermes-multi-agent-workflow-zh-CN.pdf"


def normalize(text: str) -> str:
    """Keep typography deterministic and avoid non-ASCII dash variants."""
    return (
        text.replace("\u2011", "-")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
        .replace("\u2212", "-")
    )


def tex_escape(text: str) -> str:
    text = normalize(text)
    replacements = {
        "\\": r"\textbackslash{}",
        "{": r"\{",
        "}": r"\}",
        "$": r"\$",
        "&": r"\&",
        "#": r"\#",
        "_": r"\_",
        "%": r"\%",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)


def inline_tex(text: str) -> str:
    """Convert the small inline Markdown subset used by the tutorial."""
    text = normalize(text)
    tokens: list[str] = []

    def stash(value: str) -> str:
        tokens.append(value)
        return f"@@TOKEN{len(tokens) - 1}@@"

    text = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        lambda match: stash(
            r"\href{" + match.group(2) + "}{" + tex_escape(match.group(1)) + "}"
        ),
        text,
    )
    text = re.sub(
        r"`([^`]+)`",
        lambda match: stash(r"\codeinline{" + tex_escape(match.group(1)) + "}"),
        text,
    )
    text = re.sub(
        r"\*\*([^*]+)\*\*",
        lambda match: stash(r"\textbf{" + tex_escape(match.group(1)) + "}"),
        text,
    )
    escaped = tex_escape(text)
    for index, token in enumerate(tokens):
        escaped = escaped.replace(f"@@TOKEN{index}@@", token)
    return escaped


PREAMBLE = r"""
\documentclass[10.5pt,a4paper]{article}
\usepackage[a4paper,top=17mm,bottom=18mm,left=18mm,right=18mm,headheight=19pt]{geometry}
\usepackage{fontspec}
\usepackage{xeCJK}
\usepackage{microtype}
\usepackage[table]{xcolor}
\usepackage{graphicx}
\usepackage{array}
\usepackage{booktabs}
\usepackage{tabularx}
\usepackage{longtable}
\usepackage{enumitem}
\usepackage{needspace}
\usepackage{titlesec}
\usepackage{fancyhdr}
\usepackage{hyperref}
\usepackage{tikz}
\usepackage[most]{tcolorbox}
\usepackage{lastpage}
\usepackage{amssymb}
\usetikzlibrary{arrows.meta,positioning,calc,fit,backgrounds,shapes.geometric}

\setmainfont{Helvetica Neue}
\setsansfont{Helvetica Neue}
\setmonofont{Menlo}[Scale=0.82]
\setCJKmainfont{PingFang SC}
\setCJKsansfont{PingFang SC}
\setCJKmonofont{PingFang SC}
\renewcommand{\familydefault}{\sfdefault}

\definecolor{KFBlack}{HTML}{111827}
\definecolor{KFSlate}{HTML}{374151}
\definecolor{KFGreen}{HTML}{0F766E}
\definecolor{KFMint}{HTML}{DFF5EF}
\definecolor{KFLight}{HTML}{F3F7F6}
\definecolor{KFLighter}{HTML}{FAFBFB}
\definecolor{KFLine}{HTML}{D8E5E1}
\definecolor{KFAqua}{HTML}{2DD4BF}
\definecolor{KFCoral}{HTML}{F97360}
\definecolor{KFAmber}{HTML}{F5B942}
\definecolor{KFBlue}{HTML}{4F86F7}

\hypersetup{
  colorlinks=true,
  linkcolor=KFGreen,
  urlcolor=KFGreen,
  pdftitle={Atlas Lite 多 Agent 工作法},
  pdfsubject={Obsidian + Hermes Agent + Git 普通用户完整教程},
  pdfauthor={Atlas Working Method},
  pdfkeywords={Atlas Lite, Obsidian, Hermes Agent, Git, worktree, multi-agent}
}

\setlength{\parindent}{0pt}
\setlength{\parskip}{0.62em}
\setlength{\emergencystretch}{2em}
\setlist[itemize]{leftmargin=1.45em,itemsep=0.32em,topsep=0.35em}
\setlist[enumerate]{leftmargin=1.7em,itemsep=0.32em,topsep=0.35em}
\setlist[description]{leftmargin=0pt,itemsep=0.4em}
\renewcommand{\arraystretch}{1.35}

\pagestyle{fancy}
\fancyhf{}
\lhead{\footnotesize\color{KFSlate}\textbf{ATLAS LITE} \quad Obsidian + Hermes Agent}
\rhead{\footnotesize\color{KFSlate}普通人的多 Agent 工作法}
\cfoot{\footnotesize\color{KFSlate}\thepage\ / \pageref*{LastPage}}
\renewcommand{\headrulewidth}{0.35pt}
\renewcommand{\headrule}{\hbox to\headwidth{\color{KFLine}\leaders\hrule height \headrulewidth\hfill}}

\titleformat{\section}
  {\Large\bfseries\color{KFBlack}}
  {\colorbox{KFGreen}{\color{white}\strut\hspace{0.35em}\thesection\hspace{0.35em}}}
  {0.7em}{}
\titleformat{\subsection}{\large\bfseries\color{KFBlack}}{}{0pt}{}
\titleformat{\subsubsection}{\normalsize\bfseries\color{KFGreen}}{}{0pt}{}
\titlespacing*{\section}{0pt}{1.6em}{0.75em}
\titlespacing*{\subsection}{0pt}{1.15em}{0.45em}
\titlespacing*{\subsubsection}{0pt}{0.9em}{0.35em}

\newcommand{\codeinline}[1]{\begingroup\setlength{\fboxsep}{1.6pt}\colorbox{KFLight}{\textcolor{KFGreen}{\ttfamily\scriptsize #1}}\endgroup}
\newcommand{\eyebrow}[1]{\textcolor{KFGreen}{\bfseries\footnotesize\MakeUppercase{#1}}}
\newcommand{\minilabel}[1]{\textcolor{KFGreen}{\bfseries\scriptsize #1}}
\newcommand{\checksquare}{\raisebox{0.05em}{\Large$\square$}\hspace{0.25em}}

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
\newtcolorbox{valuebox}[2][]{
  enhanced,colback=#2!8,colframe=#2!42,boxrule=0.55pt,
  arc=3mm,left=3.5mm,right=3.5mm,top=3mm,bottom=3mm,#1
}

\tikzset{
  flow/.style={rounded corners=2mm,draw=KFLine,fill=white,very thick,
    text=KFBlack,align=center,minimum height=10mm,inner xsep=4mm,inner ysep=2mm},
  flowgreen/.style={flow,draw=KFGreen!55,fill=KFMint},
  flowdark/.style={flow,draw=KFBlack,fill=KFBlack,text=white},
  decision/.style={diamond,aspect=2.2,draw=KFGreen!60,fill=KFMint,very thick,
    text=KFBlack,align=center,inner sep=1.5mm},
  arrow/.style={-{Stealth[length=2.5mm]},very thick,draw=KFGreen!75},
  softarrow/.style={-{Stealth[length=2mm]},thick,draw=KFSlate!45},
  dottedarrow/.style={-{Stealth[length=2mm]},thick,dashed,draw=KFCoral!80}
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
  \fill[KFGreen] ([xshift=-46mm,yshift=-28mm]current page.north east) circle (52mm);
  \fill[KFAqua,opacity=0.13] ([xshift=-15mm,yshift=18mm]current page.south west) circle (55mm);
  \draw[KFAqua,opacity=0.55,line width=1pt]
    ([xshift=20mm,yshift=53mm]current page.south west) --
    ([xshift=58mm,yshift=79mm]current page.south west) --
    ([xshift=95mm,yshift=54mm]current page.south west) --
    ([xshift=135mm,yshift=84mm]current page.south west) --
    ([xshift=177mm,yshift=57mm]current page.south west);
  \foreach \x/\y in {20/53,58/79,95/54,135/84,177/57}
    \fill[KFAqua] ([xshift=\x mm,yshift=\y mm]current page.south west) circle (2.2mm);
\end{tikzpicture}

\vspace*{12mm}
\eyebrow{ATLAS LITE · PRACTICAL GUIDE 2026}
\vspace{25mm}

{\fontsize{31}{39}\selectfont\bfseries\color{white}
一个人，带一组 AI 工作\par}
\vspace{7mm}
{\fontsize{18}{25}\selectfont\color{KFAqua}
Obsidian + Hermes Agent 的多 Agent 工作法\par}
\vspace{10mm}

\begin{tcolorbox}[enhanced,width=0.82\textwidth,colback=KFSlate,colframe=white!16,
  boxrule=0.5pt,arc=3mm,left=5mm,right=5mm,top=4mm,bottom=4mm]
{\color{white}\large
从安装、任务拆分和独立工作区，到审查、恢复与最终交付。\\[1mm]
一份普通人可以照着搭起来的完整商业实操手册。}
\end{tcolorbox}

\vfill
\begin{tabularx}{\textwidth}{>{\bfseries\color{KFAqua}}p{0.28\textwidth}>{\color{white}\arraybackslash}X}
工作台 & Obsidian 管理人能看懂的任务与成果 \\
协调层 & Hermes Agent 负责拆分、派工、追踪与收口 \\
隔离层 & Git worktree 让每个写入 Agent 拥有独立工作间 \\
质量层 & 验收标准、独立 Reviewer 与可恢复版本记录 \\
\end{tabularx}
\vspace{11mm}
{\color{white!65}\footnotesize Atlas Working Method \quad | \quad 2026-08-25}
\end{titlepage}
"""


VALUE_PAGE = r"""
\thispagestyle{empty}
\eyebrow{THE VALUE PROMISE}
\vspace{2mm}
{\Huge\bfseries\color{KFBlack}先看价值，再学方法\par}
\vspace{2mm}
{\large\color{KFSlate}这套系统交付的不是“多开几个聊天窗口”，而是五个可观察的工作结果。\par}
\vspace{7mm}

\begin{valuebox}{KFGreen}
\minilabel{01 · THROUGHPUT}\quad{\Large\bfseries 同时推进更多工作}\par
只把真正互不依赖的任务并行派给多个 Agent，让等待时间变成有效产出时间。
\end{valuebox}
\begin{valuebox}{KFBlue}
\minilabel{02 · CLARITY}\quad{\Large\bfseries 更少混乱和返工}\par
每个写入 Agent 使用独立 worktree 和 branch，不在同一张桌子上抢改同一份文件。
\end{valuebox}
\begin{valuebox}{KFAqua}
\minilabel{03 · QUALITY}\quad{\Large\bfseries 知道工作是否真的完成}\par
任务开始前写清验收标准，执行者提交证据，Reviewer 再独立检查。
\end{valuebox}
\begin{valuebox}{KFAmber}
\minilabel{04 · RECOVERY}\quad{\Large\bfseries 出错以后能够恢复}\par
Hermes checkpoint 保存短期现场，Git commit 保存长期里程碑。
\end{valuebox}
\begin{valuebox}{KFCoral}
\minilabel{05 · LEVERAGE}\quad{\Large\bfseries 不再充当人工传话筒}\par
协调 Agent 负责拆分、派工、收集、审查与合入；人只处理价值、优先级和高后果选择。
\end{valuebox}

\vfill
\begin{calloutbox}
\textbf{诚实边界：}独立工作区能防止互相覆盖，却不能自动保证内容正确。质量来自任务定义、验收标准、独立审查和可恢复证据。本方法不承诺固定倍数的提速。
\end{calloutbox}
\clearpage
"""


def diagram_tex(index: int) -> str:
    diagrams: dict[int, str] = {
        1: r"""
\begin{diagrambox}\centering
\resizebox{0.98\linewidth}{!}{\begin{tikzpicture}[node distance=7mm and 9mm]
\node[flowdark] (goal) {你的目标};
\node[flowgreen,right=of goal] (card) {可执行任务卡};
\node[decision,right=of card] (split) {能否并行?};
\node[flow,above right=5mm and 12mm of split] (a) {Agent A\\独立工作间};
\node[flow,right=12mm of split] (b) {Agent B\\独立工作间};
\node[flow,below right=5mm and 12mm of split] (c) {Agent C\\独立工作间};
\node[flowgreen,right=16mm of b] (review) {汇总 + 验收\\独立 Review};
\node[flowdark,right=of review] (done) {正式交付};
\draw[arrow] (goal)--(card); \draw[arrow] (card)--(split);
\draw[arrow] (split)--(a); \draw[arrow] (split)--(b); \draw[arrow] (split)--(c);
\draw[softarrow] (a)--(review); \draw[softarrow] (b)--(review); \draw[softarrow] (c)--(review);
\draw[arrow] (review)--(done);
\end{tikzpicture}}
\end{diagrambox}
""",
        2: r"""
\begin{diagrambox}\centering
\resizebox{0.93\linewidth}{!}{\begin{tikzpicture}[node distance=5mm]
\node[flowdark,minimum width=125mm] (human) {你：目标、优先级、价值判断};
\node[flowgreen,minimum width=125mm,below=of human] (obs) {OBSIDIAN 正式资料库\quad 首页 · 任务卡 · 正式成果 · 决策复盘};
\node[flow,minimum width=125mm,below=of obs] (coord) {HERMES 协调层\quad 协调 Agent · Reviewer};
\node[flow,minimum width=38mm,below left=5mm and -1mm of coord] (wa) {Worktree A\\Branch A};
\node[flow,minimum width=38mm,right=5mm of wa] (wb) {Worktree B\\Branch B};
\node[flow,minimum width=38mm,right=5mm of wb] (wc) {Worktree C\\Branch C};
\node[flowgreen,minimum width=125mm,below=6mm of wb] (proof) {安全与证据层\quad Git commits · diff · checkpoints · 验收记录};
\draw[arrow] (human)--(obs); \draw[arrow] (obs)--(coord);
\draw[softarrow] (coord)--(wa); \draw[softarrow] (coord)--(wb); \draw[softarrow] (coord)--(wc);
\draw[arrow] (wa)--(proof); \draw[arrow] (wb)--(proof); \draw[arrow] (wc)--(proof);
\end{tikzpicture}}
\end{diagrambox}
""",
        3: r"""
\begin{diagrambox}\centering
\resizebox{0.96\linewidth}{!}{\begin{tikzpicture}[node distance=7mm]
\node[flow] (inbox) {INBOX\\记录想法};
\node[flow,right=of inbox] (ready) {READY\\目标清楚};
\node[flowgreen,right=of ready] (working) {WORKING\\执行中};
\node[flow,right=of working] (review) {REVIEW\\等待审查};
\node[flowdark,right=of review] (done) {DONE\\正式交付};
\node[flow,below=8mm of working,draw=KFCoral!65,fill=KFCoral!8] (blocked) {BLOCKED\\缺输入或冲突};
\draw[arrow] (inbox)--(ready); \draw[arrow] (ready)--(working); \draw[arrow] (working)--(review); \draw[arrow] (review)--(done);
\draw[dottedarrow] (working)--(blocked); \draw[dottedarrow] (blocked)--(working); \draw[dottedarrow,bend left=28] (review) to node[above,font=\scriptsize]{退回修改} (working);
\end{tikzpicture}}
\end{diagrambox}
""",
        4: r"""
\begin{diagrambox}\centering
\resizebox{0.96\linewidth}{!}{\begin{tikzpicture}[node distance=6mm and 8mm]
\node[flowdark] (u) {用户};
\node[flow,right=of u] (coord) {协调 Agent};
\node[flow,right=of coord] (workers) {执行 Agent\\独立并行};
\node[flow,right=of workers] (review) {Reviewer};
\node[flowdark,right=of review] (main) {main\\正式资料库};
\node[below=11mm of u,font=\scriptsize,text=KFSlate] (t1) {给出目标};
\node[below=11mm of coord,font=\scriptsize,text=KFSlate] (t2) {建卡 · 基线 · 派工};
\node[below=11mm of workers,font=\scriptsize,text=KFSlate] (t3) {commit · 验证 · 风险};
\node[below=11mm of review,font=\scriptsize,text=KFSlate] (t4) {approved / 修改};
\node[below=11mm of main,font=\scriptsize,text=KFSlate] (t5) {串行合入 · 更新任务卡};
\draw[arrow] (u)--(coord); \draw[arrow] (coord)--(workers); \draw[arrow] (workers)--(review); \draw[arrow] (review)--(main);
\draw[dottedarrow,bend left=25] (review) to node[above,font=\scriptsize]{needs changes} (workers);
\draw[KFLine,thick] (t1)--(t2)--(t3)--(t4)--(t5);
\end{tikzpicture}}
\end{diagrambox}
""",
        5: r"""
\begin{diagrambox}\centering
\resizebox{0.82\linewidth}{!}{\begin{tikzpicture}[node distance=7mm and 11mm]
\node[flowdark] (start) {准备拆分子任务};
\node[decision,below=of start] (dep) {依赖另一个结果?};
\node[decision,below=of dep] (same) {会修改同一文件?};
\node[decision,below=of same] (accept) {验收能分别写清?};
\node[flowgreen,below left=8mm and 16mm of accept] (parallel) {可以并行};
\node[flow,below right=8mm and 16mm of accept,draw=KFAmber!70,fill=KFAmber!10] (clarify) {先澄清任务};
\node[flow,right=25mm of dep,draw=KFCoral!65,fill=KFCoral!8] (serial) {改为串行};
\draw[arrow] (start)--(dep); \draw[arrow] (dep)--node[left,font=\scriptsize]{否}(same); \draw[dottedarrow] (dep)--node[above,font=\scriptsize]{是}(serial);
\draw[arrow] (same)--node[left,font=\scriptsize]{否}(accept); \draw[dottedarrow] (same.east)--node[above,font=\scriptsize]{是}(serial.south);
\draw[arrow] (accept)--node[above left,font=\scriptsize]{是}(parallel); \draw[softarrow] (accept)--node[above right,font=\scriptsize]{否}(clarify);
\end{tikzpicture}}
\end{diagrambox}
""",
        6: r"""
\begin{diagrambox}\centering
\resizebox{0.94\linewidth}{!}{\begin{tikzpicture}[node distance=7mm and 10mm]
\node[flow] (safe) {安全与应急};
\node[flow,below=of safe] (budget) {装备与预算};
\node[flow,below=of budget] (weather) {天气与食品};
\node[flowgreen,right=18mm of budget] (draft) {汇总初稿};
\node[flow,right=of draft] (review) {独立审查};
\node[flowdark,right=of review] (final) {正式清单\\合入 main};
\draw[arrow] (safe)--(draft); \draw[arrow] (budget)--(draft); \draw[arrow] (weather)--(draft); \draw[arrow] (draft)--(review); \draw[arrow] (review)--(final);
\draw[dottedarrow,bend left=30] (review) to node[below,font=\scriptsize]{原作者修改} (draft);
\end{tikzpicture}}
\end{diagrambox}
""",
        7: r"""
\begin{diagrambox}\centering
\resizebox{0.97\linewidth}{!}{\begin{tikzpicture}[node distance=5mm]
\node[flowgreen] (g1) {门 1\\目标清楚};
\node[flow,right=of g1] (g2) {门 2\\文件隔离};
\node[flow,right=of g2] (g3) {门 3\\执行验证};
\node[flow,right=of g3] (g4) {门 4\\独立审查};
\node[flow,right=of g4] (g5) {门 5\\串行合入};
\node[flowdark,right=of g5] (done) {正式交付};
\draw[arrow] (g1)--(g2); \draw[arrow] (g2)--(g3); \draw[arrow] (g3)--(g4); \draw[arrow] (g4)--(g5); \draw[arrow] (g5)--(done);
\end{tikzpicture}}
\end{diagrambox}
""",
        8: r"""
\begin{diagrambox}\centering
\resizebox{0.88\linewidth}{!}{\begin{tikzpicture}[node distance=8mm and 15mm]
\node[flowdark] (edit) {Agent 正在修改文件};
\node[flowgreen,below left=of edit] (cp) {Hermes checkpoint};
\node[flowgreen,below right=of edit] (commit) {Git commit};
\node[flow,below=of cp] (short) {短期恢复点\\防止工具误改};
\node[flow,below=of commit] (long) {可审查里程碑\\branch / main / 长期历史};
\draw[arrow] (edit)--(cp); \draw[arrow] (edit)--(commit); \draw[softarrow] (cp)--(short); \draw[softarrow] (commit)--(long);
\end{tikzpicture}}
\end{diagrambox}
""",
        9: r"""
\begin{diagrambox}\centering
\resizebox{0.86\linewidth}{!}{\begin{tikzpicture}[node distance=7mm and 12mm]
\node[flowdark] (conflict) {发现合入冲突};
\node[decision,below=of conflict] (mechanical) {只是机械格式冲突?};
\node[flowgreen,below left=9mm and 14mm of mechanical] (coord) {规则明确\\协调 Agent 隔离处理};
\node[flow,below right=9mm and 14mm of mechanical,draw=KFCoral!65,fill=KFCoral!8] (author) {否或不确定\\退回原执行 Agent};
\node[flow,below=13mm of mechanical] (review) {同步 main · 重新验证 · Review};
\node[flowdark,below=of review] (main) {通过后串行合入 main};
\draw[arrow] (conflict)--(mechanical); \draw[arrow] (mechanical)--(coord); \draw[dottedarrow] (mechanical)--(author); \draw[softarrow] (coord)--(review); \draw[softarrow] (author)--(review); \draw[arrow] (review)--(main);
\end{tikzpicture}}
\end{diagrambox}
""",
        10: r"""
\begin{diagrambox}\centering
\resizebox{0.96\linewidth}{!}{\begin{tikzpicture}[node distance=5mm and 18mm]
\node[flowdark] (v1) {更多有效产出}; \node[flowgreen,right=of v1] (m1) {只并行真正独立的任务};
\node[flowdark,below=of v1] (v2) {更少混乱}; \node[flowgreen,right=of v2] (m2) {每个 Agent 独立工作区};
\node[flowdark,below=of v2] (v3) {更可靠质量}; \node[flowgreen,right=of v3] (m3) {验收标准 + 独立 Review};
\node[flowdark,below=of v3] (v4) {更容易恢复}; \node[flowgreen,right=of v4] (m4) {checkpoint + Git commit};
\node[flowdark,below=of v4] (v5) {更低管理负担}; \node[flowgreen,right=of v5] (m5) {Obsidian 任务卡 + 协调 Agent};
\foreach \a/\b in {v1/m1,v2/m2,v3/m3,v4/m4,v5/m5}{\draw[arrow] (\b)--(\a);}
\end{tikzpicture}}
\end{diagrambox}
""",
    }
    return diagrams[index]


def code_block(lines: list[str], language: str) -> str:
    label = tex_escape(language.upper() if language else "COPY & USE")
    body: list[str] = [
        rf"\begin{{codebox}}[title={{\color{{KFAqua}}\bfseries\scriptsize {label}}}]",
    ]
    for line in lines:
        if not line:
            body.append(r"\strut\par")
            continue
        escaped = tex_escape(line).replace(" ", r"\ ")
        body.append(escaped + r"\par")
    body.append(r"\end{codebox}")
    return "\n".join(body)


def table_block(rows: list[list[str]]) -> str:
    if len(rows) < 2:
        return ""
    header = rows[0]
    if len(rows) >= 2 and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in rows[1]):
        data = rows[2:]
    else:
        data = rows[1:]
    columns = len(header)
    font = r"\scriptsize" if columns >= 4 else r"\footnotesize"
    spec = "|".join([">{\\raggedright\\arraybackslash}X"] * columns)
    result = [
        r"\begin{center}",
        font,
        r"\setlength{\tabcolsep}{3.5pt}",
        rf"\begin{{tabularx}}{{\textwidth}}{{{spec}}}",
        r"\rowcolor{KFGreen!12}",
        " & ".join(r"\textbf{" + inline_tex(cell.strip()) + "}" for cell in header) + r" \\",
        r"\midrule",
    ]
    for row in data:
        padded = (row + [""] * columns)[:columns]
        result.append(" & ".join(inline_tex(cell.strip()) for cell in padded) + r" \\")
        result.append(r"\addlinespace[1.5pt]")
    result.extend([r"\bottomrule", r"\end{tabularx}", r"\end{center}"])
    return "\n".join(result)


def strip_frontmatter(lines: list[str]) -> list[str]:
    if not lines or lines[0].strip() != "---":
        return lines
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return lines[index + 1 :]
    return lines


def markdown_to_tex(markdown: str) -> str:
    lines = strip_frontmatter(normalize(markdown).splitlines())
    output: list[str] = []
    paragraph: list[str] = []
    list_kind: str | None = None
    diagram_index = 0
    chapter_index = 0
    index = 0

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            text = " ".join(part.strip() for part in paragraph)
            output.append(inline_tex(text) + "\n")
            paragraph = []

    def close_list() -> None:
        nonlocal list_kind
        if list_kind:
            output.append(rf"\end{{{list_kind}}}")
            list_kind = None

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

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
                output.append(diagram_tex(diagram_index))
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
            chapter_index += 1
            title = stripped[3:].strip()
            output.append(r"\Needspace{0.30\textheight}")
            output.append(r"\refstepcounter{section}\phantomsection")
            output.append(
                rf"\addcontentsline{{toc}}{{section}}{{\protect\numberline{{\thesection}}{inline_tex(title)}}}"
            )
            output.append(rf"\chapterlead{{CHAPTER {chapter_index:02d}}}{{{inline_tex(title)}}}")
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
            if chapter_index == 0:
                continue
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
            item = (unordered or ordered).group(1)
            if item.startswith("[ ] "):
                item_tex = r"\checksquare " + inline_tex(item[4:])
            elif item.startswith("[x] ") or item.startswith("[X] "):
                item_tex = r"\textcolor{KFGreen}{\checkmark}\hspace{0.25em}" + inline_tex(item[4:])
            else:
                item_tex = inline_tex(item)
            output.append(r"\item " + item_tex)
            index += 1
            continue

        if stripped == "---":
            flush_paragraph()
            close_list()
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
    if diagram_index != 10:
        raise ValueError(f"Expected 10 Mermaid diagrams, found {diagram_index}")
    return "\n".join(output)


ENDING = r"""
\clearpage
\thispagestyle{empty}
\begin{tikzpicture}[remember picture,overlay]
  \fill[KFBlack] (current page.south west) rectangle (current page.north east);
  \fill[KFGreen] ([xshift=-20mm,yshift=-14mm]current page.north east) circle (50mm);
  \fill[KFAqua,opacity=0.12] ([xshift=10mm,yshift=8mm]current page.south west) circle (62mm);
\end{tikzpicture}
\vspace*{24mm}
{\color{KFAqua}\bfseries\footnotesize FROM VALUE TO DELIVERY}\par\vspace{5mm}
{\color{white}\fontsize{27}{35}\selectfont\bfseries
真正的多 Agent 工作法，\\
不是把 Agent 数量变多。\par}
\vspace{9mm}
{\color{white!78}\Large
而是让每份工作都拥有清楚目标、独立现场、可检查结果和可恢复历史。\par}
\vspace{16mm}
\begin{tcolorbox}[enhanced,colback=KFSlate,colframe=white!14,boxrule=0.5pt,arc=3mm,
  left=5mm,right=5mm,top=5mm,bottom=5mm]
{\color{white}\large
\textbf{你负责：}价值、优先级和最终判断。\\[2mm]
\textbf{系统负责：}拆分、隔离、执行、审查、证据和恢复。}
\end{tcolorbox}
\vfill
{\color{KFAqua}\bfseries Atlas Lite}\quad
{\color{white!60}Obsidian + Hermes Agent + Git}\par
{\color{white!45}\footnotesize 一个人带一组 AI 工作 · 完整商业实操手册}
\end{document}
"""


def build_pdf(source: Path, build_dir: Path, output: Path) -> None:
    markdown = source.read_text(encoding="utf-8")
    build_dir.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    tex_path = build_dir / "atlas-lite-commercial.tex"
    tex_path.write_text(
        PREAMBLE
        + COVER
        + VALUE_PAGE
        + r"\tableofcontents\clearpage"
        + markdown_to_tex(markdown)
        + ENDING,
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
    built_pdf = build_dir / "atlas-lite-commercial.pdf"
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
