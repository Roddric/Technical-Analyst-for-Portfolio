"""
md_to_pdf.py — convert a markdown file to PDF (pure pip: markdown + xhtml2pdf).
Usage: python md_to_pdf.py <input.md> [output.pdf]
"""
import sys
import os
import markdown
from xhtml2pdf import pisa

CSS = """
@page { size: A4 portrait; margin: 1.6cm 1.4cm; }
body { font-family: Helvetica, Arial, sans-serif; font-size: 9.5pt; color:#1a1a1a; line-height:1.4; }
h1 { font-size: 17pt; color:#0b3d63; border-bottom:2px solid #0b3d63; padding-bottom:3px; }
h2 { font-size: 13pt; color:#0b3d63; margin-top:14px; border-bottom:1px solid #bcd; padding-bottom:2px; }
h3 { font-size: 11pt; color:#204d2e; margin-top:10px; }
p, li { font-size: 9.5pt; }
code { font-family: Courier, monospace; background:#f0f0f0; font-size: 8.5pt; }
blockquote { background:#f5f8fb; border-left:3px solid #0b3d63; padding:5px 9px; color:#333; }
table { width:100%; border-collapse:collapse; margin:6px 0; }
th { background:#0b3d63; color:#fff; font-size:8pt; padding:4px 5px; text-align:left; }
td { border:1px solid #ccc; font-size:8pt; padding:3px 5px; vertical-align:top; }
tr:nth-child(even) td { background:#f3f6f9; }
hr { border:0; border-top:1px solid #ccc; }
strong { color:#000; }
"""


def convert(md_path: str, pdf_path: str) -> None:
    with open(md_path, "r", encoding="utf-8") as fh:
        text = fh.read()
    html_body = markdown.markdown(
        text, extensions=["tables", "fenced_code", "sane_lists"]
    )
    html = f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{html_body}</body></html>"
    with open(pdf_path, "wb") as out:
        result = pisa.CreatePDF(html, dest=out, encoding="utf-8")
    if result.err:
        raise RuntimeError(f"PDF generation reported {result.err} error(s)")
    print(f"[write] {pdf_path}  ({os.path.getsize(pdf_path)//1024} KB)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python md_to_pdf.py <input.md> [output.pdf]"); sys.exit(1)
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(src)[0] + ".pdf"
    convert(src, dst)
