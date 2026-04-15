import subprocess
import sys
import os

pdf_path = sys.argv[1]
out_path = sys.argv[2]

try:
    subprocess.run(["pdftotext", pdf_path, out_path], check=True)
    print(f"Successfully extracted text to {out_path}")
except Exception as e:
    print("Error with pdftotext:", e)
    # fallback to PyPDF2 or fitz if needed
    try:
        import fitz
        doc = fitz.open(pdf_path)
        with open(out_path, "w", encoding="utf-8") as f:
            for page in doc:
                f.write(page.get_text())
        print(f"Successfully extracted text to {out_path} using PyMuPDF")
    except Exception as e2:
        print("Error with fitz:", e2)
