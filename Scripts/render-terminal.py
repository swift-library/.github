#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH Swift-exception
"""Render a recorded command session with the shared DESIGN.md terminal tokens."""

import argparse
from html import escape
import json
import math
from pathlib import Path
import re


def render(record, design, theme):
    colors = dict(re.findall(r'^  (terminal-[\w-]+): "(#[0-9a-fA-F]+)"$', design, re.M))
    terminal = re.search(r"^  terminal:\n((?:    .+\n)+)", design, re.M)[1]
    font_size = int(re.search(r"fontSize: (\d+)px", terminal)[1])
    line_height = int(re.search(r"lineHeight: (\d+)px", terminal)[1])
    padding = int(re.search(r"terminal-padding: (\d+)px", design)[1])
    radius = int(re.search(r"terminal-window: (\d+)px", design)[1])
    title_height = int(re.search(r"  terminal-title-bar:\n.*?    height: (\d+)px", design, re.S)[1])
    prefix = "terminal-light-" if theme == "light" else "terminal-"
    color = lambda role: colors[prefix + role]
    lines = []
    for command in record["commands"]:
        if command["exit_code"] != 0:
            raise ValueError("Presentation sessions must record successful commands")
        lines.append(("command", command["command"]))
        lines.extend(("output", line) for line in command["stdout"].splitlines())
        lines.append(("output", ""))
    lines.pop()
    if any(any(ord(char) < 32 for char in value) for _, value in lines):
        raise ValueError("Record plain output without terminal control sequences")
    width = max(560, math.ceil(max(len(value) + (2 if role == "command" else 0)
                                   for role, value in lines) * font_size * 0.62 + padding * 2))
    height = title_height + padding * 2 + len(lines) * line_height
    title = escape(record["title"])
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'  <title id="title">{title}</title>',
        '  <desc id="desc">Recorded commands and standard output. Build diagnostics are written to standard error.</desc>',
        f'  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="{radius}" fill="{color("surface")}" stroke="{color("border")}"/>',
        f'  <path d="M {radius} 0.5 H {width - radius} Q {width - 0.5} 0.5 {width - 0.5} {radius} V {title_height} H 0.5 V {radius} Q 0.5 0.5 {radius} 0.5 Z" fill="{color("bar")}"/>',
        f'  <path d="M 0.5 {title_height} H {width - 0.5}" stroke="{color("border")}"/>',
        '  <circle cx="20" cy="17" r="5" fill="#ff5f57"/><circle cx="38" cy="17" r="5" fill="#febc2e"/><circle cx="56" cy="17" r="5" fill="#28c840"/>',
        f'  <g font-family="ui-monospace, monospace" font-size="{font_size}">',
        f'    <text x="{width / 2:g}" y="22" text-anchor="middle" fill="{color("dim")}">{title}</text>',
    ]
    for index, (role, value) in enumerate(lines):
        y = title_height + padding + font_size + index * line_height
        if role == "command":
            text = f'<tspan fill="{color("prompt")}">$ </tspan><tspan fill="{color("command")}">{escape(value)}</tspan>'
        else:
            text = escape(value)
        svg.append(f'    <text x="{padding}" y="{y}" fill="{color("output")}" xml:space="preserve">{text}</text>')
    svg += ['  </g>', '</svg>', '']
    return "\n".join(svg)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--design", type=Path, default=Path(__file__).resolve().parent.parent / "DESIGN.md")
    parser.add_argument("--record", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    record = json.loads(args.record.read_text())
    design = args.design.read_text()
    for theme in ("light", "dark"):
        path = args.output_dir / f"Demo-{theme}.svg"
        value = render(record, design, theme)
        if args.check:
            if path.read_text() != value:
                raise SystemExit(f"{path.name} differs from its recording and design tokens")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value)


if __name__ == "__main__":
    main()
