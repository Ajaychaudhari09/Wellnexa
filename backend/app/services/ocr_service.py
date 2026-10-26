"""OCR via pytesseract + pdf2image."""
import io
from dataclasses import dataclass
from typing import List, Tuple
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes


@dataclass
class PageOCR:
    page_number: int
    text: str
    confidence: float


def ocr_image_bytes(data: bytes) -> Tuple[str, float]:
    img = Image.open(io.BytesIO(data))
    text = pytesseract.image_to_string(img)
    try:
        d = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        confs = [int(c) for c in d["conf"] if str(c).isdigit() and int(c) >= 0]
        conf = sum(confs) / len(confs) if confs else 0.0
    except Exception:
        conf = 0.0
    return text, conf


def ocr_pdf_bytes(data: bytes) -> List[PageOCR]:
    pages = convert_from_bytes(data)
    out = []
    for i, img in enumerate(pages, start=1):
        text = pytesseract.image_to_string(img)
        try:
            d = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            confs = [int(c) for c in d["conf"] if str(c).isdigit() and int(c) >= 0]
            conf = sum(confs) / len(confs) if confs else 0.0
        except Exception:
            conf = 0.0
        out.append(PageOCR(page_number=i, text=text, confidence=conf))
    return out
