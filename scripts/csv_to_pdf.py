"""
Convert the detailed CSV produced by generate_camboai_csv.py into a readable PDF.
One page per CSV row (file). Uses ReportLab. Requires `reportlab` pip package.

Usage:
    python csv_to_pdf.py

Input (default): d:\CamboAI\scripts\camboai_files_full_detailed.csv
Output (default): d:\CamboAI\scripts\camboai_files_full_detailed.pdf
"""
import csv
import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import simpleSplit


INPUT_CSV = os.path.join(os.path.dirname(__file__), "camboai_files_full_detailed.csv")
OUTPUT_PDF = os.path.join(os.path.dirname(__file__), "camboai_files_full_detailed.pdf")

PAGE_SIZE = letter
MARGIN = inch * 0.75
FONT_MAIN = "Helvetica"
FONT_BOLD = "Helvetica-Bold"
FONT_SIZE_TITLE = 12
FONT_SIZE_BODY = 10
LEADING = 14


def draw_paragraph(c, text, x, y, max_width, font=FONT_MAIN, size=FONT_SIZE_BODY, leading=LEADING):
    if text is None:
        return y
    lines = []
    # Normalize newlines
    text = str(text)
    paragraphs = text.splitlines() if "\n" in text else [text]
    for p in paragraphs:
        if not p:
            lines.append("")
            continue
        wrapped = simpleSplit(p, font, size, max_width)
        lines.extend(wrapped)
    for line in lines:
        if y < MARGIN + leading:
            return None  # signal to caller to new page
        c.setFont(font, size)
        c.drawString(x, y, line)
        y -= leading
    return y


def render_row_to_pdf(c, row):
    width, height = PAGE_SIZE
    x = MARGIN
    y = height - MARGIN
    # Title: relative_path
    title = row.get("relative_path") or row.get("absolute_path") or "(unknown)"
    c.setFont(FONT_BOLD, FONT_SIZE_TITLE)
    c.drawString(x, y, title)
    y -= LEADING * 1.5

    fields = [
        ("Full docstring", "full_docstring"),
        ("Public symbols", "public_symbols"),
        ("Imports", "imports"),
        ("Environment hint lines", "env_var_lines"),
        ("External service hints", "external_service_hints"),
        ("Primary purpose", "primary_purpose"),
        ("Benefits notes", "benefits_notes"),
        ("Detailed description", "detailed_description"),
    ]
    for label, key in fields:
        value = row.get(key, "")
        if value is None or value == "":
            continue
        # Label
        c.setFont(FONT_BOLD, FONT_SIZE_BODY)
        c.drawString(x, y, f"{label}:")
        y -= LEADING
        # Body
        y_after = draw_paragraph(c, value, x + 8, y, width - 2 * MARGIN - 8)
        if y_after is None:
            return False  # indicates page full
        y = y_after - LEADING * 0.5
    return True


def main():
    if not os.path.exists(INPUT_CSV):
        print(f"Input CSV not found: {INPUT_CSV}")
        sys.exit(2)
    c = canvas.Canvas(OUTPUT_PDF, pagesize=PAGE_SIZE)
    rows_written = 0
    with open(INPUT_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ok = render_row_to_pdf(c, row)
            if not ok:
                # If row didn't fit (rare), still write what we have and create extra page for remainder
                c.showPage()
                _ = render_row_to_pdf(c, row)
            c.showPage()
            rows_written += 1
    c.save()
    print(f"Wrote {rows_written} pages to {OUTPUT_PDF}")


if __name__ == '__main__':
    main()
