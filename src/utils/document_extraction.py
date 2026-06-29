from dataclasses import dataclass
from io import BytesIO
import os
import sys

import pytesseract
from PIL import Image

from src.utils.ocr import extract_text_from_image


@dataclass
class DocumentExtractionResult:
    text: str
    method: str
    fallback_reason: str | None = None


def _read_upload_bytes(file_storage):
    file_storage.seek(0)
    data = file_storage.read()
    file_storage.seek(0)
    return data


def _decode_text_upload(file_storage):
    return _read_upload_bytes(file_storage).decode("utf-8", errors="ignore").strip()


def extract_text_from_pdf(file_storage, max_ocr_pages=3):
    """Extract embedded PDF text with PyMuPDF, then OCR scanned pages as fallback."""
    data = _read_upload_bytes(file_storage)

    try:
        import fitz
    except ImportError:
        return DocumentExtractionResult(
            text="",
            method="pdf_text_unavailable",
            fallback_reason="PyMuPDF is not installed",
        )

    try:
        with fitz.open(stream=data, filetype="pdf") as document:
            text_chunks = []
            for page in document:
                page_text = page.get_text("text").strip()
                if page_text:
                    text_chunks.append(page_text)

            extracted_text = "\n\n".join(text_chunks).strip()
            if extracted_text:
                return DocumentExtractionResult(text=extracted_text, method="pdf_text")

            ocr_chunks = []
            for page in list(document)[:max_ocr_pages]:
                pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                image = Image.open(BytesIO(pixmap.tobytes("png"))).convert("L")
                ocr_text = pytesseract.image_to_string(image).strip()
                if ocr_text:
                    ocr_chunks.append(ocr_text)

            if ocr_chunks:
                return DocumentExtractionResult(
                    text="\n\n".join(ocr_chunks),
                    method="pdf_ocr",
                    fallback_reason="PDF did not contain readable embedded text",
                )

            return DocumentExtractionResult(
                text="",
                method="pdf_no_text",
                fallback_reason="No readable text found with embedded text extraction or OCR",
            )
    except Exception as exc:
        print(f"PDF extraction error: {exc}", file=sys.stderr)
        return DocumentExtractionResult(
            text="",
            method="pdf_error",
            fallback_reason=str(exc),
        )


def extract_text_from_document(file_storage):
    content_type = file_storage.content_type or ""
    filename = file_storage.filename or ""
    extension = os.path.splitext(filename.lower())[1]

    if content_type.startswith("image/"):
        return DocumentExtractionResult(
            text=extract_text_from_image(file_storage).strip(),
            method="image_ocr",
        )

    if content_type == "application/pdf" or extension == ".pdf":
        return extract_text_from_pdf(file_storage)

    if content_type.startswith("text/") or extension in {".txt", ".md", ".csv"}:
        return DocumentExtractionResult(
            text=_decode_text_upload(file_storage),
            method="plain_text",
        )

    return DocumentExtractionResult(
        text="",
        method="unsupported_file_type",
        fallback_reason=f"Unsupported file type: {content_type or extension or 'unknown'}",
    )
