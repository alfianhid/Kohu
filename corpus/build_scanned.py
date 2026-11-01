"""Build the 1-page scanned PDF for P14 (all content fictional).

Renders the note as a slightly skewed, noisy page image and embeds it as an
image-only PDF: no text layer, so a real OCR step is required to read it.
Run:  python corpus/build_scanned.py
"""
import os
import random

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

MARKER = "DEMO DATA \u2014 FICTIONAL"
HERE = os.path.dirname(os.path.abspath(__file__))

LINES = [
    MARKER,
    "",
    "Field note \u2014 Q3 walkthrough (fictional)",
    "Date: 2026-09-30. Author: fictional rep J. Doe.",
    "",
    "Visited the Dune region office and confirmed",
    "their largest deal closed in Q3 after the",
    "shared-hub pilot cut search time.",
    "",
    "Follow-up: reconcile the deck Q3 figure",
    "with the licensed sheet before sign-off.",
    "",
    "All names and figures are fictional demo data.",
]


def load_font(size):
    for name in ("arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def build_scanned_pdf(path, png_path):
    W, H = 1240, 1754  # ~150 dpi letter page
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    title_font = load_font(40)
    body_font = load_font(34)
    y = 130
    for line in LINES:
        font = title_font if line == MARKER else body_font
        if line == MARKER:
            d.text((100, y), line, fill=(185, 28, 28), font=font)
        else:
            d.text((100, y), line, fill=(20, 20, 20), font=font)
        y += 62
    # scan noise: speckles + slight rotation
    rnd = random.Random(7)
    for _ in range(2500):
        x, yy = rnd.randrange(W), rnd.randrange(H)
        d.point((x, yy), fill=(200, 200, 200))
    img = img.rotate(0.6, resample=Image.BICUBIC, expand=False, fillcolor="white")
    img.save(png_path, "PNG")

    c = canvas.Canvas(path, pagesize=LETTER)
    c.drawImage(ImageReader(png_path), 0, 0, LETTER[0], LETTER[1])
    c.setTitle("Scanned note (demo)")
    c.setAuthor("Kohu demo")
    c.showPage()
    c.save()


if __name__ == "__main__":
    build_scanned_pdf(os.path.join(HERE, "scanned-note.pdf"),
                      os.path.join(HERE, "scanned-note.png"))
    print("wrote scanned-note.pdf (1 page, image-only) + scanned-note.png")
