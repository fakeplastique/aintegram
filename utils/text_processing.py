from typing import List


def split_response(text: str, max_length: int = 4096) -> List[str]:
    """
    Split a response into chunks, preserving LaTeX expressions.

    Args:
        text: The text to split
        max_length: Maximum length of each chunk

    Returns:
        List of text chunks
    """
    result = []
    buffer = ""
    inside_latex = False
    delimiter = None
    in_code_block = False
    i = 0

    while i < len(text):
        if text[i:i + 3] == "```":
            in_code_block = not in_code_block
            buffer += text[i:i + 3]
            i += 3
            continue

        if not in_code_block:
            if text[i:i + 2] == "$$":
                if inside_latex and delimiter == "$$":
                    result.append("$$" + buffer + "$$")
                    buffer = ""
                    inside_latex = False
                    delimiter = None
                    i += 2
                else:
                    if buffer:
                        result.extend(split_non_latex(buffer, max_length))
                    buffer = ""
                    inside_latex = True
                    delimiter = "$$"
                    i += 2
            elif text[i] == "$":
                if inside_latex and delimiter == "$":
                    result.append("$" + buffer + "$")
                    buffer = ""
                    inside_latex = False
                    delimiter = None
                    i += 1
                else:
                    if buffer:
                        result.extend(split_non_latex(buffer, max_length))
                    buffer = ""
                    inside_latex = True
                    delimiter = "$"
                    i += 1
            else:
                buffer += text[i]
                i += 1
        else:
            buffer += text[i]
            i += 1

    # Add remaining buffer
    if buffer:
        result.extend(split_non_latex(buffer, max_length))

    return result


def split_non_latex(text: str, max_length: int) -> List[str]:
    """
    Split non-LaTeX text into chunks of a specified length.

    Args:
        text: The text to split
        max_length: Maximum length of each chunk

    Returns:
        List of text chunks
    """
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]


def clear_splitted_response(text: str) -> str:
    """
    Clean up a split response by removing leading whitespace and punctuation.

    Args:
        text: The text to clean

    Returns:
        Cleaned text
    """
    to_remove = " !.,:-\n"
    text = text.lstrip()
    for ch in text:
        if ch in to_remove:
            text = text[1:]
        else:
            break
    return text