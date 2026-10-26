"""OCR engine: real Tesseract via pytesseract + pdf2image."""
import io
import os
from typing import Optional

import pytesseract
from PIL import Image

try:
    from pdf2image import convert_from_bytes
    _PDF2IMAGE = True
except Exception:
    _PDF2IMAGE = False


class OCREngine:
    @classmethod
    def extract_text_from_file(cls, file_path: str, mime_type: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        with open(file_path, "rb") as f:
            data = f.read()

        is_pdf = (mime_type == "application/pdf") or file_path.lower().endswith(".pdf")
        if is_pdf and _PDF2IMAGE:
            try:
                pages = convert_from_bytes(data)
                texts = []
                for img in pages:
                    texts.append(pytesseract.image_to_string(img))
                return "\n\n".join(texts)
            except Exception:
                pass
        # image
        try:
            img = Image.open(io.BytesIO(data))
            return pytesseract.image_to_string(img)
        except Exception:
            pass
        # last resort
        try:
            return data.decode("utf-8", errors="ignore")
        except Exception:
            return ""
