import logging
from typing import Union, Tuple, Optional, Any

_ansi_colors = {
    "black": 30,
    "red": 31,
    "green": 32,
    "yellow": 33,
    "blue": 34,
    "magenta": 35,
    "cyan": 36,
    "white": 37,
    "reset": 39,
    "bright_black": 90,
    "bright_red": 91,
    "bright_green": 92,
    "bright_yellow": 93,
    "bright_blue": 94,
    "bright_magenta": 95,
    "bright_cyan": 96,
    "bright_white": 97,
}
_ansi_reset_all = "\033[0m"

Color = Union[int, Tuple[int, int, int], str]


def _interpret_color(color: Color, offset: int = 0) -> str:
    if isinstance(color, int):
        return f"{38 + offset};5;{color:d}"

    if isinstance(color, (tuple, list)):
        r, g, b = color
        return f"{38 + offset};2;{r:d};{g:d};{b:d}"

    return str(_ansi_colors[color] + offset)


def style(
    text: Any,
    fg: Optional[Color] = None,
    bg: Optional[Color] = None,
    bold: Optional[bool] = None,
    dim: Optional[bool] = None,
    underline: Optional[bool] = None,
    overline: Optional[bool] = None,
    italic: Optional[bool] = None,
    blink: Optional[bool] = None,
    reverse: Optional[bool] = None,
    strikethrough: Optional[bool] = None,
    reset: bool = True,
):
    if not isinstance(text, str):
        text = str(text)

    bits = []

    if fg:
        try:
            bits.append(f"\033[{_interpret_color(fg)}m")
        except KeyError:
            raise TypeError(f"Unknown color {fg!r}") from None

    if bg:
        try:
            bits.append(f"\033[{_interpret_color(bg, 10)}m")
        except KeyError:
            raise TypeError(f"Unknown color {bg!r}") from None

    if bold is not None:
        bits.append(f"\033[{1 if bold else 22}m")
    if dim is not None:
        bits.append(f"\033[{2 if dim else 22}m")
    if underline is not None:
        bits.append(f"\033[{4 if underline else 24}m")
    if overline is not None:
        bits.append(f"\033[{53 if overline else 55}m")
    if italic is not None:
        bits.append(f"\033[{3 if italic else 23}m")
    if blink is not None:
        bits.append(f"\033[{5 if blink else 25}m")
    if reverse is not None:
        bits.append(f"\033[{7 if reverse else 27}m")
    if strikethrough is not None:
        bits.append(f"\033[{9 if strikethrough else 29}m")
    bits.append(text)
    if reset:
        bits.append(_ansi_reset_all)
    return "".join(bits)


lokii_prefix = style("Lokii - ", fg="bright_green", italic=True, dim=True)
default_formats = {
    logging.DEBUG: style("DEBUG | %(name)s > %(message)s", fg="bright_green"),
    logging.INFO: style("INFO  | %(name)s > %(message)s", fg="cyan"),
    logging.WARNING: style("WARN  | %(name)s > %(message)s", fg="yellow"),
    logging.ERROR: style("ERROR | %(name)s > %(message)s", fg="red"),
    logging.CRITICAL: style("FATAL", fg="bright_white", bg="red", bold=True)
    + style(" | %(message)s", fg="red", bold=True),
}
