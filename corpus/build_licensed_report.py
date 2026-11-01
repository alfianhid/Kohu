"""Build the licensed report PDF (all content fictional).

Output (stamped DEMO DATA - FICTIONAL on every page):
  corpus/licensed-report.pdf  6 pages, licensed-only report quoting the
                              licensed-market.xlsx dataset (Q3 7.1% at
                              Q3-Growth!E12), with vendor/coverage/expiry
                              metadata for the Steward view.
Run:  python corpus/build_licensed_report.py
"""
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

MARKER = "DEMO DATA \u2014 FICTIONAL"
HERE = os.path.dirname(os.path.abspath(__file__))

styles = getSampleStyleSheet()
h1 = styles["Heading1"]
h2 = styles["Heading2"]
body = styles["BodyText"]
small = styles["Normal"]

TABLE_STYLE = TableStyle(
    [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#9ca3af")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f4f6")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]
)


def stamp(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(colors.HexColor("#b91c1c"))
    canvas.drawString(inch * 0.75, 10.5 * inch, MARKER)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#6b7280"))
    canvas.drawString(inch * 0.75, 0.6 * inch, MARKER + "  |  Kohu demo corpus  |  p.%d" % doc.page)
    canvas.restoreState()


def build_licensed_report(path):
    doc = SimpleDocTemplate(path, pagesize=LETTER,
                            leftMargin=0.75 * inch, rightMargin=0.75 * inch,
                            topMargin=0.9 * inch, bottomMargin=0.9 * inch,
                            title="Licensed Market Report Q3 (demo)", author="Kohu demo")
    s = [Paragraph("Licensed Market Report — Q3", h1),
         Paragraph(MARKER + " — licensed-only demo data for Analyst and Steward roles.", small),
         Spacer(1, 12),
         Paragraph("Vendor: Fictional Dataworks. Coverage: Product X growth, Q1–Q4. "
                   "License expiry: 2026-12-31. Seat scope: Licensed Analyst, Data Steward. "
                   "All vendors, teams, and figures are fictional.", body)]
    s += [PageBreak(), Paragraph("Key findings", h2),
          Paragraph("Q3 growth for product X: 7.1% (licensed figure, see dataset "
                    "licensed-market.xlsx sheet Q3-Growth, range E12). The licensed figure "
                    "differs from the sales-deck narrative figure — Steward to review.", body)]
    s += [PageBreak(), Paragraph("Regional Q3 table (p.3)", h2),
          Paragraph("Quoted from the licensed dataset for citable answers.", body),
          Spacer(1, 12),
          Table([["Region", "Q3 Growth %", "Dataset cell"],
                 ["Atlas", "6.8", "Q3-Growth!E4"],
                 ["Beacon", "7.4", "Q3-Growth!E7"],
                 ["Cobalt", "6.1", "Q3-Growth!E9"],
                 ["All regions (Product X rollup)", "7.1", "Q3-Growth!E12"]],
                colWidths=[2.6 * inch, 1.4 * inch, 1.6 * inch], style=TABLE_STYLE)]
    for pg, title in ((4, "Methodology"), (5, "Limitations"), (6, "Appendix")):
        s += [PageBreak(), Paragraph(title, h2),
              Paragraph("Fictional %s text for page %d of the licensed report. Figures on "
                        "this page are illustrative; citable numbers live on pages 2 and 3."
                        % (title.lower(), pg), body)]
    doc.build(s, onFirstPage=stamp, onLaterPages=stamp)


if __name__ == "__main__":
    build_licensed_report(os.path.join(HERE, "licensed-report.pdf"))
    print("wrote licensed-report.pdf (6 pp, licensed-only, quotes Q3-Growth!E12 = 7.1%)")
