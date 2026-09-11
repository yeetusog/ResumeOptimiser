from __future__ import annotations


LATEX_REPLACEMENTS = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
    "\n": " ",
    "\r": " ",
    "\t": " ",
}


def escape_latex_chars(text: str) -> str:
    """Escape user or model text before it is inserted into a LaTeX template."""
    if text is None:
        return ""

    return "".join(LATEX_REPLACEMENTS.get(char, char) for char in str(text))
