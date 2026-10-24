"""Build the PDF of the bonus article The Illusion of the Given from the Markdown in source/.

Usage (from this folder):  python build-pdf.py
Needs:  pip install markdown-it-py playwright   (then: python -m playwright install chromium)
        If Chromium is installed elsewhere, set CHROMIUM_PATH to its executable.

What it does:
  - joins source/*.md in file-name order (title, Part I, Part II, Part III, sources)
  - styles each "# PART ..." heading and the italic line under it as a part title,
    with an ornament between parts; the sources list starts on a new page
  - converts straight quotes and apostrophes to typographic ones
  - lays out an A4 page with the running title and page number in the footer
Outputs: output/the-illusion-of-the-given.html (for preview) and output/the-illusion-of-the-given.pdf
"""
import os
import re
from pathlib import Path

from markdown_it import MarkdownIt
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
SRC = HERE / "source"
OUT = HERE / "output"
HTML_OUT = OUT / "the-illusion-of-the-given.html"
PDF_OUT = OUT / "the-illusion-of-the-given.pdf"

RUNNING_TITLE = "The Illusion of the Given — Expanded Edition"

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif:ital,wght@0,400;0,700;1,400;1,700&display=swap');
body { font-family: 'Noto Serif', 'DejaVu Serif', serif; font-size: 10.5pt; line-height: 1.6; color: #222; }
p { text-align: justify; margin: 0 0 .7em; hyphens: auto; }
.title { text-align: center; font-size: 25pt; font-weight: 400; margin: 2.2em 0 .2em; letter-spacing: 0; }
.title-sub { text-align: center; font-style: italic; color: #555; font-size: 12pt; margin: 0 auto 1.4em; max-width: 34em; text-align: center; }
.orn { text-align: center; color: #888; font-size: 13pt; margin: 1.4em 0 1.6em; }
.part { text-align: center; letter-spacing: .08em; font-size: 15pt; margin: .4em 0 .3em; break-after: avoid; }
.part-sub { text-align: center; font-style: italic; letter-spacing: .08em; font-size: 10pt; margin: 0 0 1.2em;
  padding-bottom: .8em; border-bottom: 1.5px solid #222; text-align: center; }
.new-page { break-before: page; }
h2 { font-size: 13.5pt; border-bottom: 1px solid #e5e5e5; padding-bottom: .2em; margin: 1.4em 0 .6em; break-after: avoid; }
h3 { font-size: 11pt; margin: 1.1em 0 .4em; break-after: avoid; }
ul, ol { margin: 0 0 .8em 1.4em; padding-left: 1em; }
li { margin-bottom: .35em; }
li p { margin: 0; }
blockquote { margin: 1em 0; padding: .7em 1em; background: #f6f6f6; border-left: 4px solid #666; }
blockquote p { margin: 0; }
table { border-collapse: collapse; width: 100%; font-size: 8.8pt; line-height: 1.45; margin: .6em 0 1em; }
tr { break-inside: avoid; }
th, td { border: 1px solid #aaa; padding: 6px 8px; vertical-align: top; text-align: left; }
th { background: #f1f1f1; }
"""

FOOTER = (
    "<div style='width:100%;font:italic 8px serif;color:#777;padding:0 21mm;"
    "display:flex;justify-content:space-between'>"
    f"<span>{RUNNING_TITLE}</span>"
    "<span class='pageNumber' style='font-style:normal'></span></div>"
)


def heading_block(md_text, first):
    """Split off the '# Heading' and '*subtitle*' lines at the top of a source file."""
    lines = md_text.strip().splitlines()
    heading = lines[0].lstrip("# ").strip()
    sub = lines[2].strip().strip("*") if len(lines) > 2 and lines[2].startswith("*") else ""
    rest = "\n".join(lines[3:] if sub else lines[1:])
    return heading, sub, rest


def build_html():
    md = MarkdownIt("commonmark", {"typographer": True}).enable(["table", "smartquotes", "replacements"])
    parts = []
    for i, path in enumerate(sorted(SRC.glob("*.md"))):
        heading, sub, rest = heading_block(path.read_text(encoding="utf-8"), i == 0)
        inline = lambda t: md.renderInline(t)
        if i == 0:
            parts.append(f"<h1 class='title'>{inline(heading)}</h1><p class='title-sub'>{inline(sub)}</p>")
        else:
            new_page = "sources" in path.stem
            if not new_page:
                parts.append("<div class='orn'>❧</div>")
            cls = "part new-page" if new_page else "part"
            parts.append(f"<h1 class='{cls}'>{inline(heading)}</h1>")
            if sub:
                parts.append(f"<p class='part-sub'>{inline(sub)}</p>")
        parts.append(md.render(rest))
    body = "\n".join(parts)
    return (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        f"<title>The Illusion of the Given</title><style>{CSS}</style></head>"
        f"<body>{body}</body></html>"
    )


def main():
    OUT.mkdir(exist_ok=True)
    doc = build_html()
    HTML_OUT.write_text(doc, encoding="utf-8")
    launch = {"executable_path": os.environ["CHROMIUM_PATH"]} if os.environ.get("CHROMIUM_PATH") else {}
    with sync_playwright() as p:
        browser = p.chromium.launch(**launch)
        page = browser.new_page()
        page.goto(HTML_OUT.as_uri(), wait_until="networkidle")
        page.pdf(
            path=str(PDF_OUT),
            format="A4",
            print_background=True,
            display_header_footer=True,
            header_template="<span></span>",
            footer_template=FOOTER,
            margin={"top": "22mm", "bottom": "24mm", "left": "21mm", "right": "21mm"},
        )
        browser.close()
    print(f"Wrote {PDF_OUT.relative_to(HERE)}")


if __name__ == "__main__":
    main()
