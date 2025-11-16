
from pathlib import Path
from typing import Iterable
from pypdf import PdfReader
import docx2txt
import pandas as pd
from PIL import Image
import pytesseract

TEXT_EXTS = {".txt", ".md", ".log"}
DOC_EXTS = {".docx"}
PDF_EXTS = {".pdf"}
TABULAR_EXTS = {".csv", ".tsv", ".xlsx"}
IMG_EXTS = {".png", ".jpg", ".jpeg", ".tif", ".tiff"}

def extract_text(path: Path) -> Iterable[tuple[str, int]]:
    ext = path.suffix.lower()
    if ext in TEXT_EXTS:
        yield path.read_text(encoding="utf-8", errors="ignore"), 1
    elif ext in DOC_EXTS:
        text = docx2txt.process(str(path)) or ""
        yield text, 1
    elif ext in PDF_EXTS:
        reader = PdfReader(str(path))
        for i, page in enumerate(reader.pages, start=1):
            yield page.extract_text() or "", i
    elif ext in TABULAR_EXTS:
        if ext == ".xlsx":
            xls = pd.read_excel(path, sheet_name=None, header=None)
            text = "\\n\\n".join([df.to_string(index=False, header=False) for df in xls.values()])
        else:
            df = pd.read_csv(path, header=None)
            text = df.to_string(index=False, header=False)
        yield text, 1
    elif ext in IMG_EXTS:
        try:
            img = Image.open(path)
            text = pytesseract.image_to_string(img)
            yield text, 1
        except Exception:
            yield "", 1
    else:
        yield "", 1
