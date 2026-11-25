#!/usr/bin/env python3
"""Write four local pages that imitate GitHub's README column, for looking at the category cards.

Desktop (column 846px) and phone (column 308px), each on a dark (#0d1117) and a light (#ffffff)
page. The cards are always the night palette; only the page behind it changes. Images are
top-aligned and inline, so the segments of one card (one paragraph) touch like `align="top"`
images on github.com, and the paragraphs are 16px apart like GitHub's paragraph margin.
Output goes to assets/src/preview/ (gitignored); nothing committed is touched.

Usage: python3 assets/src/preview.py
"""
import html
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "preview"

THEMES = {  # page background, text, border, code background, link
    "dark": ("#0d1117", "#e6edf3", "#3d444d", "#151b23", "#4493f8"),
    "light": ("#ffffff", "#1f2328", "#d1d9e0", "#f6f8fa", "#0969da"),
}
FONT = '-apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif'
MONO = 'ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace'


def markdown(src: str) -> str:
    """The subset the README uses: headings, one fenced block, raw HTML paragraphs."""
    out = []
    for block in re.split(r"\n\s*\n", src.strip()):
        if block.startswith("```") or "\n```" in block:
            code = block.split("\n", 1)[1].rsplit("\n```", 1)[0]
            pre = block.split("\n```text\n")
            if len(pre) == 2:  # heading and fence in one block
                out.append(f"<h2>{html.escape(pre[0].lstrip('# ').strip())}</h2>")
                code = pre[1].rsplit("\n```", 1)[0]
            out.append(f"<pre><code>{html.escape(code)}</code></pre>")
        elif block.startswith("### "):
            out.append(f"<h3>{html.escape(block[4:])}</h3>")
        elif block.startswith("## "):
            out.append(f"<h2>{html.escape(block[3:])}</h2>")
        else:
            out.append(f"<p>{block}</p>")
    return "\n".join(out)


def page(theme: str, kind: str, body: str) -> str:
    bg, fg, line, code, link = THEMES[theme]
    column, viewport = (846, 846 + 2 * 45) if kind == "desktop" else (308, 390)
    pad = (viewport - column) // 2
    return f"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>README preview {kind} {theme}</title>
<style>
html {{ background: {bg}; }}
body {{ margin: 0; padding: 32px {pad}px 48px; width: {column}px; box-sizing: content-box; background: {bg}; color: {fg};
        font: 16px/1.5 {FONT}; word-wrap: break-word; }}
p {{ margin: 0 0 16px; }}
a {{ color: {link}; text-decoration: none; }}
img {{ max-width: 100%; vertical-align: top; display: inline-block; border-style: none; box-sizing: content-box; }}
h2 {{ font-size: 1.5em; font-weight: 600; line-height: 1.25; margin: 24px 0 16px; padding-bottom: .3em; border-bottom: 1px solid {line}; }}
h3 {{ font-size: 1.25em; font-weight: 600; line-height: 1.25; margin: 24px 0 16px; }}
pre {{ margin: 0 0 16px; padding: 16px; overflow: auto; background: {code}; border-radius: 6px; font: 85%/1.45 {MONO}; }}
code {{ font-family: {MONO}; }}
sub {{ font-size: smaller; vertical-align: sub; line-height: 0; }}
</style></head><body>
{body}
</body></html>
"""


def main():
    OUT.mkdir(exist_ok=True)
    subprocess.run([sys.executable, str(HERE / "build.py"), "--out", str(OUT / "build")], check=True)
    body = markdown((OUT / "build" / "README.md").read_text())
    body = re.sub(r'(src|srcset)="', r'\1="build/', body)
    for theme in THEMES:
        for kind in ("desktop", "phone"):
            f = OUT / f"{kind}-{theme}.html"
            f.write_text(page(theme, kind, body))
            print(f)


if __name__ == "__main__":
    main()
