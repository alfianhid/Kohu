"""Build the 2 demo PDFs for P11 (all content fictional).

Outputs (stamped DEMO DATA - FICTIONAL on every page):
  corpus/handbook.pdf        12 pages, real tables on p.4 and p.7
  corpus/process-report.pdf   9 pages, vector charts + captions on p.3 and p.6
Run:  python corpus/build_pdfs.py
"""
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Flowable,
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


def bar_chart(values, width=468, height=150):
    """Simple vector bar chart as a Flowable."""

    class _Bars(Flowable):
        def __init__(self):
            super().__init__()
            self.width = width
            self.height = height

        def draw(self):
            c = self.canv
            maxv = max(v for _, v in values)
            n = len(values)
            gap = 14
            bw = (self.width - gap * (n + 1)) / n
            c.setStrokeColor(colors.HexColor("#9ca3af"))
            c.line(0, 0, self.width, 0)
            for i, (label, v) in enumerate(values):
                bh = (v / maxv) * (self.height - 30)
                x = gap + i * (bw + gap)
                c.setFillColor(colors.HexColor("#2563eb"))
                c.rect(x, 0, bw, bh, stroke=0, fill=1)
                c.setFillColor(colors.black)
                c.setFont("Helvetica", 7)
                c.drawCentredString(x + bw / 2, bh + 4, str(v))
                c.drawCentredString(x + bw / 2, -12, label)

    return _Bars()


def line_chart(values, width=468, height=150):
    """Simple vector line/trend chart as a Flowable."""

    class _Line(Flowable):
        def __init__(self):
            super().__init__()
            self.width = width
            self.height = height

        def draw(self):
            c = self.canv
            maxv = max(values)
            minv = min(values)
            span = maxv - minv or 1
            n = len(values)
            pts = [
                (10 + i * (self.width - 20) / (n - 1), 10 + (v - minv) / span * (self.height - 40))
                for i, v in enumerate(values)
            ]
            c.setStrokeColor(colors.HexColor("#9ca3af"))
            c.line(0, 0, self.width, 0)
            c.setStrokeColor(colors.HexColor("#16a34a"))
            c.setLineWidth(2)
            p = c.beginPath()
            p.moveTo(*pts[0])
            for pt in pts[1:]:
                p.lineTo(*pt)
            c.drawPath(p)
            c.setFillColor(colors.HexColor("#16a34a"))
            for x, y in pts:
                c.circle(x, y, 3, stroke=0, fill=1)

    return _Line()


def build_handbook(path):
    doc = SimpleDocTemplate(path, pagesize=LETTER,
                            leftMargin=0.75 * inch, rightMargin=0.75 * inch,
                            topMargin=0.9 * inch, bottomMargin=0.9 * inch,
                            title="Employee Handbook (demo)", author="Kohu demo")
    s = []
    s += [Paragraph("Employee Handbook", h1),
          Paragraph(MARKER + " — all people, teams, and figures are fictional.", small),
          Spacer(1, 12),
          Paragraph("Welcome to this fictional company. This handbook shows how Kohu ingests "
                    "a plain PDF with real tables and cites the exact page for each answer.", body)]
    s += [PageBreak(), Paragraph("How to use this handbook", h2),
          Paragraph("Sections cover time off, support hours, expenses, and remote work. "
                    "Tables on pages 4 and 7 carry the citable facts.", body)]
    s += [PageBreak(), Paragraph("Who this covers", h2),
          Paragraph("This fictional handbook covers full-time and part-time staff at all "
                    "four fictional offices. Contractors follow the contractor addendum.", body)]
    s += [PageBreak(), Paragraph("Time off", h2),
          Paragraph("Annual allowance depends on tenure. The table below is the source of truth.", body),
          Spacer(1, 12)]
    t1 = [["Tenure", "Vacation days", "Sick days", "Notes"],
          ["0-1 years", "15", "10", "Accrued monthly"],
          ["1-3 years", "18", "10", "Rollover up to 5"],
          ["3+ years", "22", "12", "Rollover up to 10"]]
    s += [Paragraph("Table 1: Time-off allowances by tenure (p.4).", small),
          Table(t1, colWidths=[1.4 * inch, 1.2 * inch, 1.0 * inch, 2.0 * inch], style=TABLE_STYLE)]
    for pg in (5, 6):
        s += [PageBreak(), Paragraph("Expenses" if pg == 5 else "Remote work", h2),
              Paragraph("Fictional policy text for page %d. Receipts under $25 need no approval; "
                        "remote staff overlap 4 hours with headquarters." % pg, body)]
    s += [PageBreak(), Paragraph("Support hours", h2),
          Paragraph("Coverage by channel is listed below.", body), Spacer(1, 12)]
    t2 = [["Channel", "Hours (HQ time)", "Response target", "Owner"],
          ["Chat", "Mon-Fri 8am-8pm", "Under 5 minutes", "Support team"],
          ["Email", "Mon-Fri 8am-6pm", "Under 4 hours", "Support team"],
          ["On-call", "24/7", "Under 30 minutes", "Duty rota"]]
    s += [Paragraph("Table 2: Support hours by channel (p.7).", small),
          Table(t2, colWidths=[1.3 * inch, 1.5 * inch, 1.4 * inch, 1.4 * inch], style=TABLE_STYLE)]
    for pg, title in ((8, "Security"), (9, "Onboarding"), (10, "Benefits"),
                      (11, "Travel"), (12, "Glossary")):
        s += [PageBreak(), Paragraph(title, h2),
              Paragraph("Fictional %s text for page %d of the handbook." % (title.lower(), pg), body)]
    doc.build(s, onFirstPage=stamp, onLaterPages=stamp)


def build_process_report(path):
    doc = SimpleDocTemplate(path, pagesize=LETTER,
                            leftMargin=0.75 * inch, rightMargin=0.75 * inch,
                            topMargin=0.9 * inch, bottomMargin=0.9 * inch,
                            title="Process Report (demo)", author="Kohu demo")
    s = [Paragraph("Process Report — Search Time", h1),
         Paragraph(MARKER + " — all figures are fictional.", small),
         Spacer(1, 12),
         Paragraph("This fictional report studies how much time teams lose searching for "
                   "documents. Charts on pages 3 and 6 carry captions and data tables so "
                   "Kohu can cite them exactly.", body)]
    s += [PageBreak(), Paragraph("Method", h2),
          Paragraph("We surveyed four fictional teams (Atlas, Beacon, Cobalt, Dune) over two "
                   "quarters and logged median minutes per search.", body)]
    s += [PageBreak(), Paragraph("Search time by team", h2),
          bar_chart([("Atlas", 11), ("Beacon", 14), ("Cobalt", 9), ("Dune", 17)]),
          Spacer(1, 18),
          Paragraph("Figure 1: Median minutes per search by team, Q2 (fictional). "
                    "Dune is slowest at 17 minutes; Cobalt fastest at 9 minutes.", small),
          Spacer(1, 12),
          Paragraph("Data behind Figure 1 (p.3).", small),
          Table([["Team", "Median minutes"], ["Atlas", "11"], ["Beacon", "14"],
                 ["Cobalt", "9"], ["Dune", "17"]],
                colWidths=[2.5 * inch, 2.5 * inch], style=TABLE_STYLE)]
    for pg, title in ((4, "Findings"), (5, "What changed")):
        s += [PageBreak(), Paragraph(title, h2),
              Paragraph("Fictional %s text for page %d. Teams with a shared hub search "
                        "faster than teams relying on chat history." % (title.lower(), pg), body)]
    s += [PageBreak(), Paragraph("Trend over six months", h2),
          line_chart([16, 15, 14, 12, 11, 10]),
          Spacer(1, 18),
          Paragraph("Figure 2: Median minutes per search, Jan-Jun (fictional). "
                    "Search time falls from 16 to 10 minutes after the hub pilot.", small),
          Spacer(1, 12),
          Paragraph("Data behind Figure 2 (p.6).", small),
          Table([["Month", "Median minutes"], ["Jan", "16"], ["Feb", "15"], ["Mar", "14"],
                 ["Apr", "12"], ["May", "11"], ["Jun", "10"]],
                colWidths=[2.5 * inch, 2.5 * inch], style=TABLE_STYLE)]
    for pg, title in ((7, "Recommendations"), (8, "Risks"), (9, "Appendix")):
        s += [PageBreak(), Paragraph(title, h2),
              Paragraph("Fictional %s text for page %d of the process report." % (title.lower(), pg), body)]
    doc.build(s, onFirstPage=stamp, onLaterPages=stamp)


if __name__ == "__main__":
    build_handbook(os.path.join(HERE, "handbook.pdf"))
    build_process_report(os.path.join(HERE, "process-report.pdf"))
    print("wrote handbook.pdf (12 pp) and process-report.pdf (9 pp)")
