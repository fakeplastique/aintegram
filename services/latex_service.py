import asyncio
import logging
import os
import threading

import matplotlib
matplotlib.use("Agg")  # non-interactive backend, safe for headless/threaded rendering
import matplotlib.pyplot as plt
from sympy.parsing.latex import parse_latex
from pix2tex.cli import LatexOCR
from aiogram.types import FSInputFile
from PIL import Image
from config import MATPLOTLIB_CONFIG, GENERATED_DIR

logger = logging.getLogger(__name__)

# Configure matplotlib for LaTeX rendering
plt.rcParams.update(MATPLOTLIB_CONFIG)

# Initialize LaTeX OCR model
model = LatexOCR()

# matplotlib's pyplot state machine and the pix2tex model are not thread-safe;
# serialize access since blocking work runs in worker threads.
_render_lock = threading.Lock()
_ocr_lock = threading.Lock()


def latex_to_math(expr: str) -> str:
    """Convert LaTeX expression to mathematical notation."""
    try:
        return str(parse_latex(expr))
    except Exception as e:
        logger.error(f"Error parsing LaTeX: {e}")
        return expr


def preprocess_response(tex: str) -> str:
    """Preprocess LaTeX in the response for proper rendering."""
    text = list(tex)
    i = 0
    length = len(text)
    while i < length:
        if text[i:i + 2] in [['\\', '('], ['\\', '[']]:
            if text[i + 5:i + 7] in [['\\', ')'], ['\\', ']']]:
                text[i:i + 2] = ['', '*']
                text[i + 5:i + 7] = ['', '*']
            else:
                text[i:i + 2] = ['$', '$']
        elif text[i:i + 2] in [['\\', ')'], ['\\', ']']]:
            text[i:i + 2] = ['$', '$']
        elif text[i] == '$' and i + 2 < length and text[i + 2] == '$':
            text[i] = '*'
            text[i + 2] = '*'
        i += 1
    return "".join(text)


def _render_latex_to_image(latex_expr: str, message_id: int, img_index: int) -> str:
    """Render a LaTeX expression to an image file and return its path."""
    with _render_lock:
        fig, ax = plt.subplots()
        try:
            ax.axis('off')
            latex_expr = ''.join([char for char in latex_expr if char not in ["\n"]])
            ax.text(0.5, 0.5, latex_expr, fontsize=20, ha='center', va='center', transform=ax.transAxes)

            os.makedirs(GENERATED_DIR, exist_ok=True)
            img_name = os.path.join(GENERATED_DIR, f'out{message_id}_{img_index}.jpg')
            fig.savefig(img_name, dpi=300, bbox_inches='tight', pad_inches=0)
            return img_name
        finally:
            plt.close(fig)


async def render_latex_to_image(latex_expr: str, message_id: int, img_index: int) -> FSInputFile:
    """
    Render LaTeX expression to an image.

    Args:
        latex_expr: LaTeX expression to render
        message_id: Message ID for file naming
        img_index: Index for file naming when multiple images

    Returns:
        FSInputFile object for the image
    """
    try:
        # matplotlib rendering is CPU-bound; run it off the event loop.
        img_name = await asyncio.to_thread(
            _render_latex_to_image, latex_expr, message_id, img_index
        )
        return FSInputFile(img_name)
    except Exception as e:
        logger.error(f"Error rendering LaTeX to image: {e}")
        raise


def _process_image_with_latex_ocr(image_path: str) -> str:
    """Run the pix2tex OCR model on an image and return the LaTeX string."""
    with _ocr_lock:
        img = Image.open(image_path)
        return model(img)


async def process_image_with_latex_ocr(image_path: str) -> str:
    """
    Process image with LaTeX OCR.

    Args:
        image_path: Path to the image

    Returns:
        LaTeX representation of the content
    """
    try:
        # The OCR model inference is CPU/GPU-bound; run it off the event loop.
        return await asyncio.to_thread(_process_image_with_latex_ocr, image_path)
    except Exception as e:
        logger.error(f"Error processing image with LaTeX OCR: {e}")
        raise