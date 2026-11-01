"""Build the 2 demo decks for P12 (all content fictional).

Outputs (stamped DEMO DATA - FICTIONAL on every slide):
  corpus/product-deck.pptx   10 slides, product overview
  corpus/sales-deck.pptx      8 slides, sales review; slide 7 holds the seeded
                              Q3 figure (9.4%) that disagrees with the licensed
                              sheet (7.1% at licensed-market.xlsx Q3-Growth!D12)
Run:  python corpus/build_decks.py
"""
import os

from pptx import Presentation
from pptx.chart.data import ChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.util import Inches, Pt

MARKER = "DEMO DATA \u2014 FICTIONAL"
HERE = os.path.dirname(os.path.abspath(__file__))


def add_slide(prs, title, bullets, idx, total):
    slide = prs.slides.add_slide(prs.slide_layouts[1])  # title + content
    slide.shapes.title.text = title
    tf = slide.placeholders[1].text_frame
    tf.clear()
    for i, b in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = b
        p.level = 0
    # footer: stable slide number + fiction stamp
    box = slide.shapes.add_textbox(Inches(0.5), Inches(6.8), Inches(9), Inches(0.4))
    run = box.text_frame.paragraphs[0].add_run()
    run.text = "Slide %d of %d  |  %s" % (idx, total, MARKER)
    run.font.size = Pt(9)
    return slide


def build_product_deck(path):
    prs = Presentation()
    prs.core_properties.title = "Product deck (demo)"
    bodies = [
        ("Product X overview", ["Fictional product X: team hub for company knowledge.",
                                "This demo deck has 10 slides with stable numbers."]),
        ("Problem", ["Knowledge sits on laptops and in heads.",
                      "Licensed data goes unused.", "Search eats a quarter of the week."]),
        ("What Kohu does", ["Ingests PDFs, slides, and sheets as they are.",
                             "Role-based access incl. license coverage.",
                             "Every answer cites page, cell, or slide."]),
        ("Ingest", ["Muse Spark parses tables, charts, scanned pages.",
                    "Chunks carry source id, license class, citation pointer."]),
        ("Agents", ["Planner, retrieval x3, policy, verifier, conflict flagger.",
                    "Run log shows every step and token use."]),
        ("Roles", ["Employee, Licensed Analyst, Manager, Data Steward.",
                   "Same query, visibly different answers."]),
        ("Citations", ["Page citations for PDFs.", "Cell ranges for sheets.",
                       "Slide numbers for decks."]),
        ("Conflict flagging", ["Deck vs sheet disagreements route to the Steward.",
                               "Agent never invents a resolution."]),
        ("Roadmap", ["Follow-ons: recording-to-guide, SAM 3.1 marks.",
                     "Full license backend after the hackathon."]),
        ("Close", ["Startup track, Build for Your World.",
                   "Repo link and video link in the submission."]),
    ]
    for i, (t, b) in enumerate(bodies, start=1):
        add_slide(prs, t, b, i, 10)
    prs.save(path)


def build_sales_deck(path):
    prs = Presentation()
    prs.core_properties.title = "Sales review deck (demo)"
    add_slide(prs, "Q3 sales review", ["Fictional Q3 review for product X.",
                                       "All figures fictional."], 1, 8)
    add_slide(prs, "Pipeline", ["Pipeline grew across all four fictional regions.",
                                "Beacon region led on volume."], 2, 8)
    add_slide(prs, "Win rate", ["Win rate steady at fictional 31%.",
                                "Losses cluster in overlong evaluations."], 3, 8)
    add_slide(prs, "Regions", ["Atlas, Beacon, Cobalt, Dune fictional results.",
                               "Dune slowest to close, largest deals."], 4, 8)
    add_slide(prs, "Drivers", ["Shared-hub pilot cut search time 16 to 10 minutes.",
                               "Faster answers preceded faster closes."], 5, 8)
    add_slide(prs, "Risks", ["Stale decks quoted against licensed data.",
                             "Steward queue catches the mismatches."], 6, 8)
    # Slide 7: seeded conflict figure + native embedded chart
    s7 = add_slide(prs, "Q3 growth (fictional)",
                   ["Q3 growth for product X: 9.4% (deck figure).",
                    "Source: sales narrative; differs from the licensed sheet — Steward to review."], 7, 8)
    chart_data = ChartData()
    chart_data.categories = ["Q1", "Q2", "Q3", "Q4"]
    chart_data.add_series("Growth %", (4.1, 6.2, 9.4, 8.0))
    s7.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.5), Inches(2.6),
                        Inches(5.5), Inches(3.4), chart_data)
    # data table beside the chart so the figure is text-extractable
    table_shape = s7.shapes.add_table(5, 2, Inches(6.5), Inches(2.6),
                                      Inches(3.0), Inches(3.4)).table
    for j, v in enumerate(["Quarter", "Q1", "Q2", "Q3", "Q4"]):
        table_shape.cell(j, 0).text = v
    for j, v in enumerate(["Growth %", "4.1", "6.2", "9.4", "8.0"]):
        table_shape.cell(j, 1).text = v
    add_slide(prs, "Next steps", ["Steward reconciles deck vs licensed sheet.",
                                  "Freeze deck figures after sign-off."], 8, 8)
    prs.save(path)


if __name__ == "__main__":
    build_product_deck(os.path.join(HERE, "product-deck.pptx"))
    build_sales_deck(os.path.join(HERE, "sales-deck.pptx"))
    print("wrote product-deck.pptx (10 slides) and sales-deck.pptx (8 slides)")
