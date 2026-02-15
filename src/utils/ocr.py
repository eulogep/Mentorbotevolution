import pytesseract
from PIL import Image
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
    # Check if tesseract is already in PATH (shutil.which)
    import shutil

    if shutil.which("tesseract"):
        return

    # Check common paths
    for path in POSSIBLE_PATHS:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            print(f"Tesseract found at: {path}")
            return

    # Warning if not found (will likely fail later)
    print(
        "WARNING: Tesseract-OCR binary not found in common paths or PATH. OCR functionality may fail."
    )


_configure_tesseract()


def extract_text_from_image(image_file):
    """
    Extracts text from an image file object using Tesseract OCR.

    Args:
        image_file: A file-like object containing the image (e.g. from Flask request.files).

    Returns:
        str: Extracted text.
    """
    try:
        # Open image with Pillow
        image = Image.open(image_file)

        # Convert to grayscale for better accuracy (basic preprocessing)
        image = image.convert("L")

        # Extract text
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        print(f"OCR Error: {e}", file=sys.stderr)
        # Return empty string or re-raise depending on strategy.
        # For now, return error message as text to avoid crashing flow
        return f"[OCR Failed: {str(e)}]"
