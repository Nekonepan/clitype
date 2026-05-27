"""ANSI escape code helpers for TrueColor terminal rendering."""

import sys
import os


def fg(r, g, b):
    """Return ANSI escape for 24-bit foreground color."""
    return f"\033[38;2;{r};{g};{b}m"


def bg_color(r, g, b):
    """Return ANSI escape for 24-bit background color."""
    return f"\033[48;2;{r};{g};{b}m"


def reset():
    """Return ANSI reset escape."""
    return "\033[0m"


def bold():
    """Return ANSI bold escape."""
    return "\033[1m"


def dim():
    """Return ANSI dim escape."""
    return "\033[2m"


def italic():
    """Return ANSI italic escape."""
    return "\033[3m"


def underline():
    """Return ANSI underline escape."""
    return "\033[4m"


def hide_cursor():
    """Hide the terminal cursor."""
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()


def show_cursor():
    """Show the terminal cursor."""
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()


def clear_screen():
    """Clear the entire terminal screen and move cursor to top-left."""
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def move_to(row, col):
    """Move cursor to the given row and column (1-indexed)."""
    sys.stdout.write(f"\033[{row};{col}H")


def get_terminal_size():
    """Return (rows, cols) of the current terminal."""
    try:
        cols, rows = os.get_terminal_size()
        return rows, cols
    except OSError:
        return 24, 80
