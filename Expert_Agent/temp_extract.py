import pypdf
import os

pdf_path = '/home/lxmix/Downloads/projetiia/projet/docs/Internal Bank Account Opening.pdf'
if not os.path.exists(pdf_path):
    print(f"File not found: {pdf_path}")
    exit(1)

try:
    reader = pypdf.PdfReader(pdf_path)
    print(f"Extracting {len(reader.pages)} pages...")
    for i, page in enumerate(reader.pages):
        print(f"--- Page {i+1} ---")
        text = page.extract_text()
        print(text if text else "[Empty Page]")
except Exception as e:
    print(f"Error: {e}")
