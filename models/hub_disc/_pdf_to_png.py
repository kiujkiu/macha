"""Render PDF -> PNG preview using pypdfium2 at scale 3.0.

Prefers the freshly-written hub_disc_drawing.NEW.pdf if it is newer than the
locked hub_disc_drawing.pdf, so the preview always reflects the latest build."""
from pathlib import Path
import pypdfium2 as pdfium

HERE = Path(__file__).parent
pdf_main = HERE / "hub_disc_drawing.pdf"
pdf_new  = HERE / "hub_disc_drawing.NEW.pdf"
png_path = HERE / "hub_disc_drawing_preview.png"

def _newest(*paths):
    existing = [p for p in paths if p.exists()]
    if not existing:
        raise FileNotFoundError(f"no PDF found among: {paths}")
    return max(existing, key=lambda p: p.stat().st_mtime)

pdf_path = _newest(pdf_new, pdf_main)
pdf = pdfium.PdfDocument(str(pdf_path))
page = pdf[0]
pil = page.render(scale=3.0).to_pil()
pil.save(png_path, "PNG")
print(f"wrote {png_path}  {pil.width}x{pil.height}  (from {pdf_path.name})")
