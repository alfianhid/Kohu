"""Verify P14: the scanned PDF has no text layer and OCR recovers its text."""
import sys

import fitz  # PyMuPDF
from pypdf import PdfReader
from rapidocr_onnxruntime import RapidOCR

results = []


def check(name, cond, detail=""):
    results.append(bool(cond))
    print(("PASS" if cond else "FAIL"), "-", name, detail)


reader = PdfReader("corpus/scanned-note.pdf")
check("scanned PDF is 1 page", len(reader.pages) == 1, str(len(reader.pages)))
layer = (reader.pages[0].extract_text() or "").strip()
check("no text layer (truly scanned)", layer == "", "%d chars" % len(layer))

doc = fitz.open("corpus/scanned-note.pdf")
pix = doc[0].get_pixmap(dpi=200)
pix.save("corpus/scanned-note-raster.png")

engine = RapidOCR()
out = engine("corpus/scanned-note-raster.png")
texts = []
if out and out[0]:
    texts = [t for _, t, _ in out[0]]
ocr_text = " ".join(texts)
print("OCR lines: %d" % len(texts))
with open("corpus/scanned-note-ocr.txt", "w", encoding="utf-8") as f:
    f.write(ocr_text + "\n")

low = ocr_text.lower()
check("OCR finds 'field note'", "field note" in low)
check("OCR finds 'dune'", "dune" in low)
check("OCR finds 'largest deal'", "largest deal" in low)
check("OCR finds 'demo data' stamp", "demo data" in low)

print()
print("ALL PASS" if all(results) else "SOME FAILED")
sys.exit(0 if all(results) else 1)
