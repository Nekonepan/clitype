"""Theme-aware rendering primitives for clitype.

The Renderer class provides high-level drawing methods that automatically
apply the current theme's colors. All screen modules use this class
instead of writing raw ANSI sequences directly.
"""

import re
import sys

from core.terminal.ansi import fg, bg_color, reset, bold, move_to, get_terminal_size
from core.ui.themes import THEMES


class Renderer:
    """Handles all screen drawing with TrueColor support."""

    def __init__(self, theme_key="dark"):
        self.set_theme(theme_key)

    def set_theme(self, theme_key):
        """Switch to a different color theme."""
        self.theme_key = theme_key
        self.t = THEMES[theme_key]

    def _bg(self):
        """Return the background ANSI escape for the current theme."""
        return bg_color(*self.t["bg"])

    def _fg(self, key):
        """Return the foreground ANSI escape for a theme color key."""
        return fg(*self.t[key])

    def fill_background(self):
        """Fill the entire screen with the theme background color."""
        rows, cols = get_terminal_size()
        line = self._bg() + " " * cols
        for r in range(1, rows + 1):
            move_to(r, 1)
            sys.stdout.write(line)
        sys.stdout.flush()

    def draw_centered(self, row, text, fg_key="fg_active", bold_on=False):
        """Draw text horizontally centered on a row."""
        _, cols = get_terminal_size()
        visible_len = len(self._strip_ansi(text))
        col = max(1, (cols - visible_len) // 2 + 1)
        move_to(row, col)
        prefix = self._bg() + self._fg(fg_key)
        if bold_on:
            prefix += bold()
        sys.stdout.write(prefix + text + reset())

    def draw_at(self, row, col, text, fg_key="fg_active", bold_on=False):
        """Draw text at an exact row/col position."""
        move_to(row, col)
        prefix = self._bg() + self._fg(fg_key)
        if bold_on:
            prefix += bold()
        sys.stdout.write(prefix + text + reset())

    def draw_raw(self, row, col, raw_text):
        """Draw pre-formatted (already ANSI-escaped) text at a position."""
        move_to(row, col)
        sys.stdout.write(self._bg() + raw_text + reset())

    def draw_box(self, top_row, left_col, width, height, title=""):
        """Draw a rounded box with an optional title."""
        t = self.t
        border_fg = fg(*t["border"])
        bg_str = self._bg()

        # Top border
        move_to(top_row, left_col)
        sys.stdout.write(bg_str + border_fg + "╭" + "─" * (width - 2) + "╮" + reset())

        # Title
        if title:
            title_start = left_col + (width - len(title) - 2) // 2
            move_to(top_row, title_start)
            sys.stdout.write(
                bg_str + fg(*t["accent"]) + bold() + " " + title + " " + reset()
            )

        # Sides
        for r in range(1, height - 1):
            move_to(top_row + r, left_col)
            sys.stdout.write(bg_str + border_fg + "│" + " " * (width - 2) + "│" + reset())

        # Bottom border
        move_to(top_row + height - 1, left_col)
        sys.stdout.write(bg_str + border_fg + "╰" + "─" * (width - 2) + "╯" + reset())

    def draw_horizontal_line(self, row, left_col, width):
        """Draw a horizontal line with the border color."""
        move_to(row, left_col)
        sys.stdout.write(self._bg() + fg(*self.t["border"]) + "─" * width + reset())

    def flush(self):
        """Flush stdout."""
        sys.stdout.flush()

    @staticmethod
    def _strip_ansi(text):
        """Remove ANSI escape sequences for visible-length calculation."""
        return re.sub(r'\033\[[^m]*m', '', text)
