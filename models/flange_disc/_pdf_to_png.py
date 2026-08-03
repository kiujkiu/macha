"""Quick PDF to PNG preview converter using PyMuPDF (fitz)."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
pdf_path = os.path.join(HERE, "flange_disc_drawing.pdf")
png_path = os.path.join(HERE, "flange_disc_drawing_preview.png")

try:
    import fitz  # PyMuPDF
except ImportError:
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "pymupdf"], check=True)
    import fitz

doc = fitz.open(pdf_path)
page = doc.load_page(0)
mat = fitz.Matrix(120/72, 120/72)  # 120 DPI
pix = page.get_pixmap(matrix=mat)
pix.save(png_path)
print(f"wrote {png_path}  {pix.width}x{pix.height}")
