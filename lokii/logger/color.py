import logging

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


def style(
    text: str, fg: str = None, bg: str = None, bold: bool = False, reset: bool = True
):
    bits = []
    bit_temp = "\033[%dm"
    if fg:
        bits.append(bit_temp % _ansi_colors[fg])
    if bg:
        bits.append(bit_temp % (_ansi_colors[bg] + 10))
    bits.append(bit_temp % (1 if bold else 22))
    bits.append(text)
    if reset:
        bits.append(_ansi_reset_all)
    return "".join(bits)


default_formats = {
    logging.DEBUG: style("DEBUG | %(name)s > %(message)s", fg="bright_green"),
    logging.INFO: style("INFO  | %(name)s > %(message)s", fg="cyan"),
    logging.WARNING: style("WARN  | %(name)s > %(message)s", fg="yellow"),
    logging.ERROR: style("ERROR | %(name)s > %(message)s", fg="red"),
    logging.CRITICAL: style("FATAL", fg="bright_white", bg="red", bold=True)
    + style(" | %(message)s", fg="red", bold=True),
}
