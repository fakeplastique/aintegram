import logging
import matplotlib.pyplot as plt
from sympy.parsing.latex import parse_latex
from pix2tex.cli import LatexOCR
from aiogram.types import FSInputFile
from PIL import Image
from config import MATPLOTLIB_CONFIG

logger = logging.getLogger(__name__)

# Configure matplotlib for LaTeX rendering
plt.rcParams.update(MATPLOTLIB_CONFIG)

# Initialize LaTeX OCR model
model = LatexOCR()


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
        fig, ax = plt.subplots()
        ax.axis('off')
        latex_expr = ''.join([char for char in latex_expr if char not in ["\n"]])
        ax.text(0.5, 0.5, latex_expr, fontsize=20, ha='center', va='center', transform=ax.transAxes)

        img_name = f'out{message_id}_{img_index}.jpg'
        plt.savefig(img_name, dpi=300, bbox_inches='tight', pad_inches=0)
        plt.close('all')

        return FSInputFile(img_name)
    except Exception as e:
        logger.error(f"Error rendering LaTeX to image: {e}")
        raise


async def process_image_with_latex_ocr(image_path: str) -> str:
    """
    Process image with LaTeX OCR.

    Args:
        image_path: Path to the image

    Returns:
        LaTeX representation of the content
    """
    try:
        img = Image.open(image_path)
        return model(img)
    except Exception as e:
        logger.error(f"Error processing image with LaTeX OCR: {e}")
        raise