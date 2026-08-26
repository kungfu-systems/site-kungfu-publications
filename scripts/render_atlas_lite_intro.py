#!/usr/bin/env python3
"""Generate a ten-slide, plain-language Atlas workflow PDF.

The deck is intentionally free of command-line and Git implementation detail.
It uses Tectonic and vector TikZ artwork so the PDF remains sharp at any scale.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

from design_system import install_tex_style


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = REPO_ROOT / "content/atlas-lite-introduction/core/zh-CN.json"
SOURCE_LOCALE = REPO_ROOT / "content/atlas-lite-introduction/core/zh-CN.json"
DEFAULT_BUILD_DIR = REPO_ROOT / "_build/tex/atlas-lite-introduction/zh-CN"
DEFAULT_OUTPUT = (
    REPO_ROOT / "_build/pdf/atlas-lite-working-method-introduction-zh-CN.pdf"
)


TEX = r"""
\documentclass[12pt]{article}
\usepackage[paperwidth=13.333in,paperheight=7.5in,margin=0in]{geometry}
\usepackage{kungfu-publications}
\usepackage{tikz}
\usepackage{hyperref}
\usetikzlibrary{arrows.meta,calc,positioning,shapes.geometric}

\hypersetup{
  pdftitle={Atlas Lite 普通人的多 Agent 工作法},
  pdfsubject={为什么聊天式 Agent 不够，以及独立工作区如何带来可靠交付},
  pdfauthor={Atlas Working Method},
  pdfkeywords={Atlas Lite, multi-agent, independent workspace, KFD}
}
\pagestyle{empty}
\setlength{\parindent}{0pt}

\tikzset{
  arrow/.style={-{Stealth[length=3mm,width=2.2mm]},line width=1.5pt,draw=KFGreen},
  softarrow/.style={-{Stealth[length=2.5mm,width=2mm]},line width=1.1pt,draw=KFSlate!45},
  reversearrow/.style={-{Stealth[length=2.5mm,width=2mm]},line width=1.1pt,dashed,draw=KFCoral},
  pill/.style={rounded corners=4mm,inner xsep=4mm,inner ysep=2.2mm},
  room/.style={rounded corners=3mm,draw=KFLine,line width=1.1pt,fill=white,
    minimum width=35mm,minimum height=23mm,align=center},
  flow/.style={rounded corners=3mm,draw=KFLine,line width=1.1pt,fill=white,
    minimum width=30mm,minimum height=14mm,align=center,inner sep=3mm}
}

\newcommand{\fullbg}[1]{%
  \begin{tikzpicture}[remember picture,overlay]
    \fill[#1] (current page.south west) rectangle (current page.north east);
  \end{tikzpicture}%
}
\newcommand{\pageno}[2]{%
  \node[anchor=south east,text=#1,font=\fontsize{9}{11}\selectfont]
    at ([xshift=-0.46in,yshift=0.28in]current page.south east) {#2 / 10};
}
\newcommand{\eyebrow}[2]{%
  \node[anchor=north west,text=#1,font=\bfseries\fontsize{9}{11}\selectfont]
    at ([xshift=0.62in,yshift=-0.38in]current page.north west) {#2};
}

\begin{document}

% 01 — Cover
\fullbg{KFBlack}
\begin{tikzpicture}[remember picture,overlay]
  \fill[KFGreen] ([xshift=-0.72in,yshift=-0.5in]current page.north east) circle (1.35in);
  \fill[KFAqua,opacity=.12] ([xshift=0.15in,yshift=0.2in]current page.south west) circle (1.8in);
  \draw[KFAqua!75,line width=1.4pt]
    ([xshift=8.35in,yshift=-1.34in]current page.north west) --
    ([xshift=9.58in,yshift=-2.10in]current page.north west) --
    ([xshift=8.72in,yshift=-3.08in]current page.north west) --
    ([xshift=10.05in,yshift=-4.03in]current page.north west) --
    ([xshift=8.95in,yshift=-5.20in]current page.north west);
  \foreach \x/\y in {8.35/1.34,9.58/2.10,8.72/3.08,10.05/4.03,8.95/5.20}{
    \fill[KFAqua] ([xshift=\x in,yshift=-\y in]current page.north west) circle (2.5mm);
    \draw[KFAqua,opacity=.22,line width=8pt]
      ([xshift=\x in,yshift=-\y in]current page.north west) circle (4.2mm);
  }
  \node[anchor=north west,text=KFAqua,font=\bfseries\fontsize{10}{12}\selectfont]
    at ([xshift=.68in,yshift=-.50in]current page.north west)
    {ATLAS LITE · 普通人的多 AGENT 工作法};
  \node[anchor=west,text=white,text width=7.4in,align=left,
    font=\bfseries\fontsize{35}{43}\selectfont]
    at ([xshift=.68in,yshift=-2.25in]current page.north west)
    {一个人，不该成为\\AI 团队的传话筒};
  \node[anchor=north west,text=white!72,text width=6.9in,align=left,
    font=\fontsize{17}{24}\selectfont]
    at ([xshift=.72in,yshift=-4.68in]current page.north west)
    {真正的多 Agent 工作法，\\不是多开几个聊天窗口。};
  \draw[KFAqua,line width=3pt]
    ([xshift=.70in,yshift=.79in]current page.south west) --
    ([xshift=2.18in,yshift=.79in]current page.south west);
  \node[anchor=west,text=white!62,font=\fontsize{10}{12}\selectfont]
    at ([xshift=2.38in,yshift=.79in]current page.south west)
    {把复杂工作变成可见、可查、可交付的协作过程};
  \pageno{white!45}{01}
\end{tikzpicture}
\null\newpage

% 02 — Chat limitation
\fullbg{KFLighter}
\begin{tikzpicture}[remember picture,overlay]
  \eyebrow{KFGreen}{01 · 问题从哪里开始}
  \node[anchor=north west,text=KFBlack,text width=11.7in,align=left,
    font=\bfseries\fontsize{28}{35}\selectfont]
    at ([xshift=.64in,yshift=-.88in]current page.north west)
    {聊天式 Agent 很聪明，\\却没有稳定的工作现场};

  \node[anchor=north west,rounded corners=4mm,fill=white,draw=KFLine,line width=1pt,
    minimum width=4.25in,minimum height=.72in,text=KFSlate,align=left,
    font=\fontsize{14}{18}\selectfont,inner xsep=5mm]
    at ([xshift=.72in,yshift=-2.62in]current page.north west) {背景资料放在哪里？};
  \node[anchor=north west,rounded corners=4mm,fill=KFMint,draw=KFGreen!25,line width=1pt,
    minimum width=3.75in,minimum height=.72in,text=KFGreen,align=left,
    font=\bfseries\fontsize{14}{18}\selectfont,inner xsep=5mm]
    at ([xshift=1.18in,yshift=-3.50in]current page.north west) {现在应该改哪个版本？};
  \node[anchor=north west,rounded corners=4mm,fill=white,draw=KFLine,line width=1pt,
    minimum width=4.25in,minimum height=.72in,text=KFSlate,align=left,
    font=\fontsize{14}{18}\selectfont,inner xsep=5mm]
    at ([xshift=.72in,yshift=-4.38in]current page.north west) {上次做到哪里，谁来继续？};

  \draw[KFLine,line width=8pt,rounded corners=5mm]
    ([xshift=7.00in,yshift=-2.30in]current page.north west) --
    ([xshift=9.10in,yshift=-2.30in]current page.north west) --
    ([xshift=9.10in,yshift=-3.50in]current page.north west) --
    ([xshift=11.12in,yshift=-3.50in]current page.north west);
  \draw[KFCoral,line width=8pt,rounded corners=5mm]
    ([xshift=11.12in,yshift=-3.50in]current page.north west) --
    ([xshift=11.78in,yshift=-3.50in]current page.north west);
  \draw[KFCoral,line width=2pt]
    ([xshift=11.82in,yshift=-3.14in]current page.north west) --
    ([xshift=11.82in,yshift=-3.86in]current page.north west);
  \node[anchor=north,text=KFSlate,font=\fontsize{12}{15}\selectfont]
    at ([xshift=8.05in,yshift=-1.83in]current page.north west) {一次回答};
  \node[anchor=north,text=KFSlate,font=\fontsize{12}{15}\selectfont]
    at ([xshift=10.12in,yshift=-3.03in]current page.north west) {继续聊天};
  \node[anchor=north,text=KFCoral,font=\bfseries\fontsize{13}{16}\selectfont]
    at ([xshift=11.82in,yshift=-4.10in]current page.north west) {正式成果？};

  \node[anchor=south west,text=KFSlate,text width=11.5in,align=left,
    font=\fontsize{16}{23}\selectfont]
    at ([xshift=.72in,yshift=.66in]current page.south west)
    {聊天擅长回答问题；真实工作还要跨时间、跨角色，能够检查，也能够恢复。};
  \pageno{KFSlate!55}{02}
\end{tikzpicture}
\null\newpage

% 03 — Four kinds of chaos
\fullbg{KFBlack}
\begin{tikzpicture}[remember picture,overlay]
  \eyebrow{KFAqua}{02 · 聊天一多，问题会放大}
  \node[anchor=north west,text=white,text width=11.7in,align=left,
    font=\bfseries\fontsize{28}{35}\selectfont]
    at ([xshift=.64in,yshift=-.88in]current page.north west)
    {任务一多，四种混乱会一起出现};
  \draw[KFAqua!75,line width=1.4pt]
    ([xshift=2.20in,yshift=-3.20in]current page.north west) .. controls
    ([xshift=4.2in,yshift=-2.2in]current page.north west) and
    ([xshift=5.0in,yshift=-5.5in]current page.north west) ..
    ([xshift=6.65in,yshift=-3.70in]current page.north west) .. controls
    ([xshift=8.2in,yshift=-1.9in]current page.north west) and
    ([xshift=9.0in,yshift=-5.4in]current page.north west) ..
    ([xshift=11.18in,yshift=-3.15in]current page.north west);
  \foreach \x/\y/\c/\title/\sub in {
    2.20/3.20/KFCoral/版本混乱/不知道哪份才是最新,
    4.68/4.55/KFAmber/责任混乱/不知道谁正在处理,
    7.78/2.82/KFAqua/完成混乱/说完成却无法验收,
    11.18/3.15/KFBlue/恢复混乱/中断后要重新解释}{
    \fill[\c,opacity=.18] ([xshift=\x in,yshift=-\y in]current page.north west) circle (16mm);
    \fill[\c] ([xshift=\x in,yshift=-\y in]current page.north west) circle (4mm);
    \node[anchor=north,text=white,font=\bfseries\fontsize{15}{18}\selectfont]
      at ([xshift=\x in,yshift=-\dimexpr\y in+0.42in\relax]current page.north west) {\title};
    \node[anchor=north,text=white!58,text width=2.15in,align=center,
      font=\fontsize{10.5}{14}\selectfont]
      at ([xshift=\x in,yshift=-\dimexpr\y in+0.72in\relax]current page.north west) {\sub};
  }
  \node[anchor=south,text=white,
    font=\bfseries\fontsize{19}{24}\selectfont]
    at ([yshift=.61in]current page.south) {Agent 越多，人越像信息中转站。};
  \pageno{white!45}{03}
\end{tikzpicture}
\null\newpage

% 04 — More agents != more delivery
\fullbg{KFLight}
\begin{tikzpicture}[remember picture,overlay]
  \eyebrow{KFGreen}{03 · 忙碌不等于产出}
  \node[anchor=north west,text=KFBlack,text width=11.7in,align=left,
    font=\bfseries\fontsize{28}{35}\selectfont]
    at ([xshift=.64in,yshift=-.88in]current page.north west)
    {多开几个 Agent，不等于多做成几件事};

  \fill[white,rounded corners=5mm,draw=KFLine,line width=1pt]
    ([xshift=.70in,yshift=-2.02in]current page.north west) rectangle
    ([xshift=6.30in,yshift=-5.90in]current page.north west);
  \node[anchor=north west,text=KFCoral,font=\bfseries\fontsize{11}{14}\selectfont]
    at ([xshift=1.04in,yshift=-2.34in]current page.north west) {所有人挤在同一张桌子};
  \fill[KFBlack!7,rounded corners=2mm]
    ([xshift=2.02in,yshift=-3.04in]current page.north west) rectangle
    ([xshift=5.02in,yshift=-5.28in]current page.north west);
  \node[text=KFSlate,font=\fontsize{11}{14}\selectfont]
    at ([xshift=3.52in,yshift=-4.17in]current page.north west) {同一份工作};
  \foreach \x/\y/\lab in {1.45/3.08/A,5.56/3.20/B,1.62/5.15/C}{
    \fill[KFCoral] ([xshift=\x in,yshift=-\y in]current page.north west) circle (5mm);
    \node[text=white,font=\bfseries\fontsize{11}{12}\selectfont]
      at ([xshift=\x in,yshift=-\y in]current page.north west) {\lab};
    \draw[-{Stealth[length=2.5mm]},KFCoral,line width=1.2pt]
      ([xshift=\x in,yshift=-\y in]current page.north west) --
      ([xshift=3.52in,yshift=-4.17in]current page.north west);
  }

  \node[anchor=north west,text=KFBlack,font=\bfseries\fontsize{42}{48}\selectfont]
    at ([xshift=7.05in,yshift=-2.43in]current page.north west) {更多忙碌};
  \node[anchor=north west,text=KFCoral,font=\bfseries\fontsize{44}{48}\selectfont]
    at ([xshift=8.08in,yshift=-3.38in]current page.north west) {≠};
  \node[anchor=north west,text=KFGreen,font=\bfseries\fontsize{42}{48}\selectfont]
    at ([xshift=7.05in,yshift=-4.28in]current page.north west) {更多交付};
  \node[anchor=south west,text=KFSlate,text width=11.6in,align=left,
    font=\fontsize{15}{21}\selectfont]
    at ([xshift=.72in,yshift=.55in]current page.south west)
    {如果工作现场没有分开，增加 Agent 只会增加等待、覆盖和返工。};
  \pageno{KFSlate!55}{04}
\end{tikzpicture}
\null\newpage

% 05 — Independent workspaces
\fullbg{KFLighter}
\begin{tikzpicture}[remember picture,overlay]
  \eyebrow{KFGreen}{04 · 第一个关键改变}
  \node[anchor=north west,text=KFBlack,text width=11.9in,align=left,
    font=\bfseries\fontsize{27}{34}\selectfont]
    at ([xshift=.64in,yshift=-.86in]current page.north west)
    {独立工作区，就是给每个 Agent\\一间自己的工作室};

  \node[room] (r1) at ([xshift=2.25in,yshift=-3.62in]current page.north west)
    {\textbf{研究工作室}\\[2mm]\small 只负责找事实};
  \node[room] (r2) at ([xshift=5.00in,yshift=-3.62in]current page.north west)
    {\textbf{写作工作室}\\[2mm]\small 只负责做初稿};
  \node[room] (r3) at ([xshift=7.75in,yshift=-3.62in]current page.north west)
    {\textbf{检查工作室}\\[2mm]\small 只负责找问题};
  \node[rounded corners=4mm,fill=KFGreen,minimum width=2.05in,minimum height=.78in,
    text=white,align=center,font=\bfseries\fontsize{13}{16}\selectfont]
    (shared) at ([xshift=10.62in,yshift=-3.62in]current page.north west)
    {共同目标与资料};
  \draw[softarrow] (shared.west) -- (r3.east);
  \draw[softarrow] (r3.west) -- (r2.east);
  \draw[softarrow] (r2.west) -- (r1.east);
  \foreach \x/\c in {2.25/KFAmber,5.00/KFAqua,7.75/KFBlue}{
    \fill[\c] ([xshift=\x in,yshift=-2.65in]current page.north west) circle (4mm);
    \draw[\c,line width=1pt]
      ([xshift=\x in,yshift=-2.90in]current page.north west) --
      ([xshift=\x in,yshift=-3.08in]current page.north west);
  }
  \node[anchor=north west,text=KFSlate,text width=11.6in,align=left,
    font=\fontsize{16}{23}\selectfont]
    at ([xshift=.72in,yshift=-5.28in]current page.north west)
    {大家共享同一个目标，但各自在自己的空间完成工作，互不覆盖、互不打断。};
  \pageno{KFSlate!55}{05}
\end{tikzpicture}
\null\newpage

% 06 — Ordered collaboration
\fullbg{KFBlack}
\begin{tikzpicture}[remember picture,overlay]
  \eyebrow{KFAqua}{05 · 独立之后，仍然需要秩序}
  \node[anchor=north west,text=white,text width=11.8in,align=left,
    font=\bfseries\fontsize{27}{34}\selectfont]
    at ([xshift=.64in,yshift=-.86in]current page.north west)
    {独立不是各干各的，\\而是同一目标下的有序分工};

  \foreach \x/\w/\lab/\num in {
    1.18/1.60/写清目标/01,
    3.35/1.60/拆开任务/02,
    5.52/1.78/独立完成/03,
    7.87/1.78/独立检查/04,
    10.22/1.78/正式交付/05}{
    \node[anchor=west,rounded corners=3mm,fill=white!10!KFBlack,draw=white!22!KFBlack,line width=1pt,
      minimum width=\w in,minimum height=.90in,text=white,align=center,
      font=\bfseries\fontsize{14}{17}\selectfont]
      at ([xshift=\x in,yshift=-3.72in]current page.north west) {\lab};
    \node[anchor=south west,text=KFAqua,font=\bfseries\fontsize{9}{11}\selectfont]
      at ([xshift=\x in,yshift=-3.12in]current page.north west) {\num};
  }
  \foreach \a/\b in {2.78/3.35,4.95/5.52,7.30/7.87,9.65/10.22}{
    \draw[-{Stealth[length=2.4mm]},KFAqua,line width=1.3pt]
      ([xshift=\a in,yshift=-3.72in]current page.north west) --
      ([xshift=\b in,yshift=-3.72in]current page.north west);
  }
  \draw[reversearrow]
    ([xshift=8.76in,yshift=-4.27in]current page.north west) .. controls
    ([xshift=7.60in,yshift=-5.25in]current page.north west) and
    ([xshift=6.80in,yshift=-5.25in]current page.north west) ..
    ([xshift=6.40in,yshift=-4.27in]current page.north west);
  \node[anchor=north,text=KFCoral,font=\fontsize{10.5}{13}\selectfont]
    at ([xshift=7.58in,yshift=-5.17in]current page.north west) {发现问题，就退回修改};
  \node[anchor=south,text=white!72,
    font=\fontsize{15}{21}\selectfont]
    at ([yshift=.66in]current page.south) {并行发生在中间；目标与验收仍然只有一套。};
  \pageno{white!45}{06}
\end{tikzpicture}
\null\newpage

% 07 — KFD
\fullbg{KFLight}
\begin{tikzpicture}[remember picture,overlay]
  \eyebrow{KFGreen}{06 · KFD 的核心理念}
  \node[anchor=north west,text=KFBlack,text width=11.7in,align=left,
    font=\bfseries\fontsize{28}{35}\selectfont]
    at ([xshift=.64in,yshift=-.88in]current page.north west)
    {先有可靠事实，才有可靠合作};

  \fill[white,rounded corners=4mm,draw=KFLine,line width=1pt]
    ([xshift=.78in,yshift=-2.12in]current page.north west) rectangle
    ([xshift=4.40in,yshift=-5.72in]current page.north west);
  \fill[KFMint,rounded corners=4mm,draw=KFGreen!25,line width=1pt]
    ([xshift=4.85in,yshift=-2.12in]current page.north west) rectangle
    ([xshift=8.47in,yshift=-5.72in]current page.north west);
  \fill[KFBlack,rounded corners=4mm]
    ([xshift=8.92in,yshift=-2.12in]current page.north west) rectangle
    ([xshift=12.54in,yshift=-5.72in]current page.north west);
  \node[anchor=north west,text=KFGreen,font=\bfseries\fontsize{11}{14}\selectfont]
    at ([xshift=1.08in,yshift=-2.46in]current page.north west) {KFD-1};
  \node[anchor=north west,text=KFBlack,font=\bfseries\fontsize{21}{26}\selectfont]
    at ([xshift=1.08in,yshift=-3.02in]current page.north west) {事实不漂移};
  \node[anchor=north west,text=KFSlate,text width=2.95in,align=left,
    font=\fontsize{13.5}{20}\selectfont]
    at ([xshift=1.08in,yshift=-3.78in]current page.north west) {大家看到的是同一件事，\\不会各说各话。};
  \node[anchor=north west,text=KFGreen,font=\bfseries\fontsize{11}{14}\selectfont]
    at ([xshift=5.15in,yshift=-2.46in]current page.north west) {KFD-2};
  \node[anchor=north west,text=KFBlack,font=\bfseries\fontsize{21}{26}\selectfont]
    at ([xshift=5.15in,yshift=-3.02in]current page.north west) {信任可检查};
  \node[anchor=north west,text=KFSlate,text width=2.95in,align=left,
    font=\fontsize{13.5}{20}\selectfont]
    at ([xshift=5.15in,yshift=-3.78in]current page.north west) {不是“相信我”，\\而是“你可以验证”。};
  \node[anchor=north west,text=KFAqua,font=\bfseries\fontsize{11}{14}\selectfont]
    at ([xshift=9.22in,yshift=-2.46in]current page.north west) {KFD-3};
  \node[anchor=north west,text=white,font=\bfseries\fontsize{21}{26}\selectfont]
    at ([xshift=9.22in,yshift=-3.02in]current page.north west) {合作有价值};
  \node[anchor=north west,text=white!72,text width=2.95in,align=left,
    font=\fontsize{13.5}{20}\selectfont]
    at ([xshift=9.22in,yshift=-3.78in]current page.north west) {规则、选择和限制，\\都提前说清楚。};
  \draw[arrow] ([xshift=4.40in,yshift=-3.92in]current page.north west) --
    ([xshift=4.85in,yshift=-3.92in]current page.north west);
  \draw[arrow] ([xshift=8.47in,yshift=-3.92in]current page.north west) --
    ([xshift=8.92in,yshift=-3.92in]current page.north west);
  \node[anchor=south,text=KFSlate,font=\fontsize{12.5}{17}\selectfont]
    at ([yshift=.52in]current page.south) {顺序很重要：没有事实，信任就没有地基。};
  \pageno{KFSlate!55}{07}
\end{tikzpicture}
\null\newpage

% 08 — Atlas chain
\fullbg{KFLighter}
\begin{tikzpicture}[remember picture,overlay]
  \eyebrow{KFGreen}{07 · ATLAS 如何把方法落到工作里}
  \node[anchor=north west,text=KFBlack,text width=11.8in,align=left,
    font=\bfseries\fontsize{27}{34}\selectfont]
    at ([xshift=.64in,yshift=-.88in]current page.north west)
    {Atlas 把一次聊天，\\变成一条可以交付的工作链};

  \node[flow,fill=KFBlack,text=white,draw=KFBlack,minimum width=1.65in]
    (goal) at ([xshift=1.35in,yshift=-3.82in]current page.north west) {你的目标};
  \node[flow,fill=KFMint,draw=KFGreen!40,minimum width=1.75in]
    (coord) at ([xshift=3.64in,yshift=-3.82in]current page.north west) {协调与拆分};
  \node[room,minimum width=1.55in,minimum height=.62in]
    (a) at ([xshift=6.25in,yshift=-2.83in]current page.north west) {独立任务 A};
  \node[room,minimum width=1.55in,minimum height=.62in]
    (b) at ([xshift=6.25in,yshift=-3.82in]current page.north west) {独立任务 B};
  \node[room,minimum width=1.55in,minimum height=.62in]
    (c) at ([xshift=6.25in,yshift=-4.81in]current page.north west) {独立任务 C};
  \node[flow,fill=white,minimum width=1.70in]
    (review) at ([xshift=8.86in,yshift=-3.82in]current page.north west) {检查与汇总};
  \node[flow,fill=KFGreen,text=white,draw=KFGreen,minimum width=1.75in]
    (done) at ([xshift=11.35in,yshift=-3.82in]current page.north west) {正式成果};
  \draw[arrow] (goal)--(coord);
  \draw[arrow] (coord)--(a); \draw[arrow] (coord)--(b); \draw[arrow] (coord)--(c);
  \draw[softarrow] (a)--(review); \draw[softarrow] (b)--(review); \draw[softarrow] (c)--(review);
  \draw[arrow] (review)--(done);
  \node[anchor=south,text=KFSlate,
    font=\fontsize{16}{22}\selectfont]
    at ([yshift=.66in]current page.south) {复杂性留给系统，判断权留给人。};
  \pageno{KFSlate!55}{08}
\end{tikzpicture}
\null\newpage

% 09 — Values
\fullbg{KFLight}
\begin{tikzpicture}[remember picture,overlay]
  \eyebrow{KFGreen}{08 · 最终得到什么}
  \node[anchor=north west,text=KFBlack,text width=11.8in,align=left,
    font=\bfseries\fontsize{27}{34}\selectfont]
    at ([xshift=.64in,yshift=-.88in]current page.north west)
    {你真正得到的，不是更多 Agent，\\而是五种工作价值};

  \foreach \y/\num/\col/\title/\desc in {
    2.56/01/KFGreen/更多有效产出/只并行真正独立的任务,
    3.29/02/KFAqua/更少混乱/每个 Agent 都有独立现场,
    4.02/03/KFBlue/更可靠质量/有验收标准，也有独立检查,
    4.75/04/KFAmber/更容易恢复/过程留下可回看的记录,
    5.48/05/KFCoral/更低管理负担/系统负责派工、追踪和收口}{
    \fill[\col] ([xshift=.82in,yshift=-\y in]current page.north west) circle (3.5mm);
    \node[anchor=west,text=\col,font=\bfseries\fontsize{10}{12}\selectfont]
      at ([xshift=1.08in,yshift=-\y in]current page.north west) {\num};
    \node[anchor=west,text=KFBlack,font=\bfseries\fontsize{17}{21}\selectfont]
      at ([xshift=1.62in,yshift=-\y in]current page.north west) {\title};
    \node[anchor=west,text=KFSlate,font=\fontsize{13}{17}\selectfont]
      at ([xshift=6.55in,yshift=-\y in]current page.north west) {\desc};
    \draw[KFLine,line width=.7pt]
      ([xshift=.82in,yshift=-\dimexpr\y in+0.36in\relax]current page.north west) --
      ([xshift=12.35in,yshift=-\dimexpr\y in+0.36in\relax]current page.north west);
  }
  \node[anchor=south west,rounded corners=3mm,fill=white,draw=KFLine,line width=.8pt,
    text=KFSlate,text width=10.7in,align=left,inner xsep=4mm,inner ysep=2.5mm,
    font=\fontsize{11.5}{16}\selectfont]
    at ([xshift=.80in,yshift=.47in]current page.south west)
    {诚实边界：不承诺固定倍数提速；先减少碰撞、返工和人工协调。};
  \pageno{KFSlate!55}{09}
\end{tikzpicture}
\null\newpage

% 10 — Closing
\fullbg{KFBlack}
\begin{tikzpicture}[remember picture,overlay]
  \fill[KFGreen] ([xshift=-.45in,yshift=.15in]current page.south east) circle (1.55in);
  \fill[KFAqua,opacity=.10] ([xshift=.1in,yshift=-.1in]current page.north west) circle (1.65in);
  \node[anchor=north west,text=KFAqua,font=\bfseries\fontsize{10}{12}\selectfont]
    at ([xshift=.68in,yshift=-.50in]current page.north west) {ATLAS LITE · 最后的分工};
  \node[anchor=north west,text=white,text width=11.5in,align=left,
    font=\bfseries\fontsize{31}{39}\selectfont]
    at ([xshift=.68in,yshift=-1.12in]current page.north west)
    {人负责方向，\\系统负责把工作做稳};

  \fill[white!7,rounded corners=4mm,draw=white!16,line width=1pt]
    ([xshift=.72in,yshift=-3.15in]current page.north west) rectangle
    ([xshift=6.28in,yshift=-5.77in]current page.north west);
  \fill[white!7,rounded corners=4mm,draw=white!16,line width=1pt]
    ([xshift=6.62in,yshift=-3.15in]current page.north west) rectangle
    ([xshift=12.18in,yshift=-5.77in]current page.north west);
  \node[anchor=north west,text=KFAqua,font=\bfseries\fontsize{12}{15}\selectfont]
    at ([xshift=1.08in,yshift=-3.53in]current page.north west) {你负责};
  \node[anchor=north west,text=KFBlack,text width=4.65in,align=left,
    font=\bfseries\fontsize{20}{29}\selectfont]
    at ([xshift=1.08in,yshift=-4.02in]current page.north west)
    {目标 · 价值 · 优先级\\最终判断};
  \node[anchor=north west,text=KFAqua,font=\bfseries\fontsize{12}{15}\selectfont]
    at ([xshift=6.98in,yshift=-3.53in]current page.north west) {系统负责};
  \node[anchor=north west,text=KFBlack,text width=4.75in,align=left,
    font=\bfseries\fontsize{20}{29}\selectfont]
    at ([xshift=6.98in,yshift=-4.02in]current page.north west)
    {拆分 · 隔离 · 执行\\检查 · 记录 · 恢复};
  \node[anchor=south west,text=white!75,text width=10.8in,align=left,
    font=\fontsize{15}{21}\selectfont]
    at ([xshift=.72in,yshift=.60in]current page.south west)
    {让每份工作都能被看见、检查和交付。};
  \pageno{white!45}{10}
\end{tikzpicture}
\null

\end{document}
"""


def iter_localized_strings(value: object, key: str = ""):
    if isinstance(value, dict):
        for child_key, child_value in value.items():
            if child_key in {"eyebrow", "title", "lead", "body", "points", "steps"}:
                yield from iter_localized_strings(child_value, child_key)
            elif child_key == "cards":
                yield from iter_localized_strings(child_value, child_key)
            elif child_key == "slides":
                yield from iter_localized_strings(child_value, child_key)
    elif isinstance(value, list):
        for child in value:
            yield from iter_localized_strings(child, key)
    elif isinstance(value, str) and key not in {"label", "number"}:
        yield value


def tex_value(value: str) -> str:
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
    }
    escaped = "".join(replacements.get(char, char) for char in value)
    return escaped.replace("\n", r"\\")


def localized_tex(source: Path) -> str:
    base = json.loads(SOURCE_LOCALE.read_text(encoding="utf-8"))
    target = json.loads(source.read_text(encoding="utf-8"))
    base_strings = list(iter_localized_strings(base["slides"]))
    target_strings = list(iter_localized_strings(target["slides"]))
    if len(base_strings) != len(target_strings):
        raise ValueError("localized slide core does not match the source-locale schema")

    tex = TEX
    pairs = sorted(zip(base_strings, target_strings), key=lambda pair: len(pair[0]), reverse=True)
    for original, replacement in pairs:
        original_tex = original.replace("\n", r"\\")
        if original_tex not in tex:
            raise ValueError(f"slide core text is not represented in the PDF template: {original!r}")
        if original != replacement:
            tex = tex.replace(original_tex, tex_value(replacement))
    return tex


def build(source: Path, build_dir: Path, output: Path) -> None:
    build_dir.mkdir(parents=True, exist_ok=True)
    install_tex_style(build_dir)
    output.parent.mkdir(parents=True, exist_ok=True)
    tex_path = build_dir / "atlas-lite-plain-language-slides.tex"
    tex_path.write_text(localized_tex(source), encoding="utf-8")

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
        check=True,
        cwd=REPO_ROOT,
    )
    generated = build_dir / "atlas-lite-plain-language-slides.pdf"
    shutil.copy2(generated, output)
    print(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--build-dir", type=Path, default=DEFAULT_BUILD_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    build(args.source.resolve(), args.build_dir.resolve(), args.output.resolve())


if __name__ == "__main__":
    main()
