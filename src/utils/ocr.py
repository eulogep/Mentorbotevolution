import os
import sys

# Attempt to locate tesseract executable on Windows if not in PATH
# Common default installation paths
POSSIBLE_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    r"C:\Users\mabia\AppData\Local\Tesseract-OCR\tesseract.exe",
]


def _configure_tesseract():
    """Configures pytesseract tesseract_cmd path if found."""
    import shutil
    import pytesseract

    if shutil.which("tesseract"):
        return True

    for path in POSSIBLE_PATHS:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            return True

    return False


def extract_text_from_image(image_file):
    """
    Extracts text from an image file object using Tesseract OCR.

    Args:
        image_file: A file-like object containing the image (e.g. from Flask request.files).

    Returns:
        str: Extracted text.
    """
    try:
        import pytesseract
        from PIL import Image

        if not _configure_tesseract():
            return "[OCR unavailable: Tesseract-OCR binary not found]"

        image = Image.open(image_file)
        image = image.convert("L")
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        print(f"OCR Error: {e}", file=sys.stderr)
        return f"[OCR Failed: {str(e)}]"
