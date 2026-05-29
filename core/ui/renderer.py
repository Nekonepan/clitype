"""Theme-aware rendering primitives for clitype.

The Renderer class provides high-level drawing methods that automatically
apply the current theme's colors. All screen modules use this class
instead of writing raw ANSI sequences directly.
"""

import re
import sys

from core.terminal.ansi import fg, bg_color, reset, bold, move_to, get_terminal_size
from core.ui.themes import THEMES

# Compiled regex matching any ANSI escape sequence (CSI sequences).
# Uses \x1b to match the actual ESC byte (0x1B).
_ANSI_RE = re.compile(r'\x1b\[[^m]*m')

# The raw reset sequence for string replacement.
_RESET_SEQ = "\033[0m"


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

    def _patch_resets(self, text):
        """Replace every embedded reset with reset + bg restore.

        This ensures the theme background is maintained even when the
        text contains internal reset() calls between styled segments.
        Without this, each reset drops the bg to the terminal default,
        causing visible gaps on non-default themes (e.g. light themes).
        """
        bg_str = self._bg()
        return text.replace(_RESET_SEQ, _RESET_SEQ + bg_str)

    def fill_background(self):
        """Fill the entire screen with the theme background color."""
        # Use standard ANSI sequence to clear screen with current background color
        # Do not flush here; let the caller flush after drawing the full frame to prevent flickering.
        sys.stdout.write(self._bg() + "\033[2J\033[H")

    def draw_centered(self, row, text, fg_key="fg_active", bold_on=False):
        """Draw text horizontally centered on a row, padded to full width."""
        _, cols = get_terminal_size()
        bg_str = self._bg()
        text = self._patch_resets(text)
        visible_len = len(self._strip_ansi(text))
        col = max(1, (cols - visible_len) // 2 + 1)
        pad_left = col - 1
        pad_right = max(0, cols - pad_left - visible_len)
        move_to(row, 1)
        prefix = bg_str + self._fg(fg_key)
        if bold_on:
            prefix += bold()
        sys.stdout.write(
            bg_str + " " * pad_left
            + prefix + text + reset()
            + bg_str + " " * pad_right + reset()
        )

    def draw_rainbow_centered(self, row, text, time_offset):
        """Draw text centered with a smooth horizontal rainbow wave effect."""
        import colorsys
        
        _, cols = get_terminal_size()
        bg_str = self._bg()
        
        # Calculate padding based on visible length (for raw text)
        visible_len = len(text)  # Assuming no ANSI codes in rainbow input
        col = max(1, (cols - visible_len) // 2 + 1)
        pad_left = col - 1
        pad_right = max(0, cols - pad_left - visible_len)
        
        move_to(row, 1)
        sys.stdout.write(bg_str + " " * pad_left)
        
        # Wave parameters (slow and smooth horizontal wave)
        wave_freq = 0.015  # How wide the color bands are
        speed = 0.15       # Animation speed (hue cycles per second)

        for i, char in enumerate(text):
            if char.isspace():
                sys.stdout.write(bg_str + char)
                continue
                
            hue = (i * wave_freq - time_offset * speed) % 1.0
            r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            r_int, g_int, b_int = int(r * 255), int(g * 255), int(b * 255)
            
            # Combine background, rainbow foreground, and bold text
            sys.stdout.write(bg_str + fg(r_int, g_int, b_int) + bold() + char + reset() + bg_str)
            
        sys.stdout.write(bg_str + " " * pad_right + reset())

    def draw_at(self, row, col, text, fg_key="fg_active", bold_on=False):
        """Draw text at an exact row/col position."""
        text = self._patch_resets(text)
        move_to(row, col)
        prefix = self._bg() + self._fg(fg_key)
        if bold_on:
            prefix += bold()
        sys.stdout.write(prefix + text + reset() + self._bg())

    def draw_raw(self, row, col, raw_text):
        """Draw pre-formatted (already ANSI-escaped) text at a position."""
        raw_text = self._patch_resets(raw_text)
        move_to(row, col)
        sys.stdout.write(self._bg() + raw_text + reset() + self._bg())

    def draw_box(self, top_row, left_col, width, height, title=""):
        """Draw a rounded box with an optional title."""
        t = self.t
        border_fg = fg(*t["border"])
        bg_str = self._bg()

        # Top border
        move_to(top_row, left_col)
        sys.stdout.write(bg_str + border_fg + "╭" + "─" * (width - 2) + "╮" + reset() + bg_str)

        # Title
        if title:
            title_start = left_col + (width - len(title) - 2) // 2
            move_to(top_row, title_start)
            sys.stdout.write(
                bg_str + fg(*t["accent"]) + bold() + " " + title + " " + reset() + bg_str
            )

        # Sides
        for r in range(1, height - 1):
            move_to(top_row + r, left_col)
            sys.stdout.write(bg_str + border_fg + "│" + " " * (width - 2) + "│" + reset() + bg_str)

        # Bottom border
        move_to(top_row + height - 1, left_col)
        sys.stdout.write(bg_str + border_fg + "╰" + "─" * (width - 2) + "╯" + reset() + bg_str)

    def draw_horizontal_line(self, row, left_col, width):
        """Draw a horizontal line with the border color."""
        move_to(row, left_col)
        sys.stdout.write(self._bg() + fg(*self.t["border"]) + "─" * width + reset() + self._bg())

    def flush(self):
        """Flush stdout."""
        sys.stdout.flush()

    @staticmethod
    def _strip_ansi(text):
        """Remove ANSI escape sequences for visible-length calculation."""
        return _ANSI_RE.sub('', text)
