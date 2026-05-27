#!/usr/bin/env python3
"""clitype — A gorgeous terminal typing test inspired by Monkeytype."""

import sys
import os
import tty
import termios
import select
import time
import random
import json
import signal
import math
from pathlib import Path

# ---------------------------------------------------------------------------
# Word lists (imported from companion module)
# ---------------------------------------------------------------------------
try:
    from wordlists import WORDS_ENGLISH, WORDS_INDONESIAN, CODE_SNIPPETS
except ImportError:
    # Fallback if wordlists.py is not found — minimal built-in set
    WORDS_ENGLISH = [
        "the", "be", "to", "of", "and", "a", "in", "that", "have", "i",
        "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
        "this", "but", "his", "by", "from", "they", "we", "her", "she", "or",
    ]
    WORDS_INDONESIAN = [
        "dan", "yang", "di", "ini", "itu", "dengan", "untuk", "tidak",
        "dari", "pada", "ada", "akan", "saya", "anda", "kita", "mereka",
    ]
    CODE_SNIPPETS = [
        'const x = 42;',
        'def hello(): pass',
        'print("hello world")',
    ]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
VERSION = "1.0.0"
APP_NAME = "clitype"
CONFIG_DIR = Path.home() / ".config" / "clitype"
HISTORY_FILE = CONFIG_DIR / "history.json"

# States
STATE_MENU = "menu"
STATE_TEST = "test"
STATE_RESULTS = "results"
STATE_HISTORY = "history"

# Modes
MODE_TIME = "time"
MODE_WORDS = "words"
MODE_CODE = "code"

# Time options (seconds)
TIME_OPTIONS = [15, 30, 60]
# Word count options
WORD_OPTIONS = [10, 25, 50]

# Languages
LANGUAGES = {
    "english": WORDS_ENGLISH,
    "indonesian": WORDS_INDONESIAN,
    "code": CODE_SNIPPETS,
}

# Sparkline characters for WPM graph
SPARK_CHARS = " ▁▂▃▄▅▆▇█"

# ---------------------------------------------------------------------------
# TrueColor Themes
# ---------------------------------------------------------------------------
THEMES = {
    "dark": {
        "name": "Dark",
        "bg": (30, 30, 46),
        "fg_dim": (88, 91, 112),
        "fg_active": (205, 214, 244),
        "fg_correct": (166, 227, 161),
        "fg_incorrect": (243, 139, 168),
        "fg_cursor": (245, 224, 220),
        "accent": (137, 180, 250),
        "accent2": (180, 190, 254),
        "accent3": (203, 166, 247),
        "border": (69, 71, 90),
        "surface": (49, 50, 68),
        "wpm_bar": (137, 180, 250),
    },
    "nord": {
        "name": "Nord",
        "bg": (46, 52, 64),
        "fg_dim": (76, 86, 106),
        "fg_active": (216, 222, 233),
        "fg_correct": (163, 190, 140),
        "fg_incorrect": (191, 97, 106),
        "fg_cursor": (236, 239, 244),
        "accent": (136, 192, 208),
        "accent2": (129, 161, 193),
        "accent3": (94, 129, 172),
        "border": (59, 66, 82),
        "surface": (59, 66, 82),
        "wpm_bar": (136, 192, 208),
    },
    "onedark": {
        "name": "One Dark",
        "bg": (40, 44, 52),
        "fg_dim": (92, 99, 112),
        "fg_active": (171, 178, 191),
        "fg_correct": (152, 195, 121),
        "fg_incorrect": (224, 108, 117),
        "fg_cursor": (220, 223, 228),
        "accent": (97, 175, 239),
        "accent2": (198, 120, 221),
        "accent3": (229, 192, 123),
        "border": (62, 68, 81),
        "surface": (53, 59, 69),
        "wpm_bar": (97, 175, 239),
    },
    "neon": {
        "name": "Neon Cyan",
        "bg": (13, 17, 23),
        "fg_dim": (48, 54, 61),
        "fg_active": (201, 209, 217),
        "fg_correct": (63, 185, 80),
        "fg_incorrect": (248, 81, 73),
        "fg_cursor": (255, 255, 255),
        "accent": (0, 255, 255),
        "accent2": (121, 192, 255),
        "accent3": (210, 153, 255),
        "border": (33, 38, 45),
        "surface": (22, 27, 34),
        "wpm_bar": (0, 255, 255),
    },
    "matrix": {
        "name": "Matrix",
        "bg": (0, 10, 2),
        "fg_dim": (0, 60, 15),
        "fg_active": (0, 200, 50),
        "fg_correct": (0, 255, 65),
        "fg_incorrect": (255, 50, 50),
        "fg_cursor": (180, 255, 180),
        "accent": (0, 255, 65),
        "accent2": (0, 200, 50),
        "accent3": (0, 150, 35),
        "border": (0, 40, 10),
        "surface": (0, 20, 5),
        "wpm_bar": (0, 255, 65),
    },
    "sepia": {
        "name": "Retro Sepia",
        "bg": (50, 40, 30),
        "fg_dim": (120, 100, 80),
        "fg_active": (230, 210, 180),
        "fg_correct": (180, 200, 120),
        "fg_incorrect": (220, 100, 80),
        "fg_cursor": (255, 240, 220),
        "accent": (220, 180, 120),
        "accent2": (200, 160, 100),
        "accent3": (180, 140, 90),
        "border": (80, 65, 50),
        "surface": (65, 52, 40),
        "wpm_bar": (220, 180, 120),
    },
}

THEME_KEYS = list(THEMES.keys())

# ---------------------------------------------------------------------------
# ANSI Helpers
# ---------------------------------------------------------------------------

def fg(r, g, b):
    """Return ANSI escape for 24-bit foreground color."""
    return f"\033[38;2;{r};{g};{b}m"

def bg_color(r, g, b):
    """Return ANSI escape for 24-bit background color."""
    return f"\033[48;2;{r};{g};{b}m"

def reset():
    return "\033[0m"

def bold():
    return "\033[1m"

def dim():
    return "\033[2m"

def italic():
    return "\033[3m"

def underline():
    return "\033[4m"

def hide_cursor():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

def show_cursor():
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()

def clear_screen():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()

def move_to(row, col):
    sys.stdout.write(f"\033[{row};{col}H")

def get_terminal_size():
    try:
        cols, rows = os.get_terminal_size()
        return rows, cols
    except OSError:
        return 24, 80

# ---------------------------------------------------------------------------
# History Manager
# ---------------------------------------------------------------------------

def load_history():
    """Load score history from JSON file."""
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def save_history(entry):
    """Append a score entry to history."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    history = load_history()
    history.append(entry)
    # Keep last 500 entries
    history = history[-500:]
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

# ---------------------------------------------------------------------------
# Terminal raw mode context manager
# ---------------------------------------------------------------------------

class RawTerminal:
    """Context manager for raw terminal input."""

    def __init__(self):
        self.fd = sys.stdin.fileno()
        self.old_settings = None

    def __enter__(self):
        self.old_settings = termios.tcgetattr(self.fd)
        tty.setcbreak(self.fd)
        hide_cursor()
        return self

    def __exit__(self, *args):
        if self.old_settings:
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)
        show_cursor()
        clear_screen()
        sys.stdout.write(reset())
        sys.stdout.flush()

    def read_key(self, timeout=None):
        """Read a single keypress. Returns string or None on timeout."""
        if timeout is not None:
            ready, _, _ = select.select([sys.stdin], [], [], timeout)
            if not ready:
                return None
        ch = sys.stdin.read(1)
        if ch == "\033":
            # Escape sequence
            ready, _, _ = select.select([sys.stdin], [], [], 0.05)
            if ready:
                ch2 = sys.stdin.read(1)
                if ch2 == "[":
                    ch3 = sys.stdin.read(1)
                    if ch3 == "A":
                        return "UP"
                    elif ch3 == "B":
                        return "DOWN"
                    elif ch3 == "C":
                        return "RIGHT"
                    elif ch3 == "D":
                        return "LEFT"
                    return f"ESC[{ch3}"
                return f"ESC{ch2}"
            return "ESC"
        return ch

# ---------------------------------------------------------------------------
# ASCII Art Logo
# ---------------------------------------------------------------------------

LOGO = [
    "        ██  ██            ██",
    "        ██                ██",
    " ▄████▄ ██  ██  ██   ██  ██▄▄██  ▄███▄",
    "██▀  ▀▀ ██  ██  ▀█▄ ██▀ ██▀▀██  ██▀ ▀██",
    "██   ▄▄ ██  ██   ▀███▀  ██  ██  ██   ██",
    " ▀███▀  ██  ██    ██    ██  ██  ▀████▀",
    "                  ██",
    "                 ██",
]

# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------

class Renderer:
    """Handles all screen drawing with TrueColor support."""

    def __init__(self, theme_key="dark"):
        self.set_theme(theme_key)

    def set_theme(self, theme_key):
        self.theme_key = theme_key
        self.t = THEMES[theme_key]

    def _bg(self):
        return bg_color(*self.t["bg"])

    def _fg(self, key):
        return fg(*self.t[key])

    def fill_background(self):
        """Fill entire screen with background color."""
        rows, cols = get_terminal_size()
        line = self._bg() + " " * cols
        for r in range(1, rows + 1):
            move_to(r, 1)
            sys.stdout.write(line)
        sys.stdout.flush()

    def draw_centered(self, row, text, fg_key="fg_active", bold_on=False):
        """Draw text centered on a row."""
        _, cols = get_terminal_size()
        # Strip ANSI for length calculation
        visible_len = len(self._strip_ansi(text))
        col = max(1, (cols - visible_len) // 2 + 1)
        move_to(row, col)
        prefix = self._bg() + self._fg(fg_key)
        if bold_on:
            prefix += bold()
        sys.stdout.write(prefix + text + reset())

    def draw_at(self, row, col, text, fg_key="fg_active", bold_on=False):
        """Draw text at an exact position."""
        move_to(row, col)
        prefix = self._bg() + self._fg(fg_key)
        if bold_on:
            prefix += bold()
        sys.stdout.write(prefix + text + reset())

    def draw_raw(self, row, col, raw_text):
        """Draw pre-formatted text at a position."""
        move_to(row, col)
        sys.stdout.write(self._bg() + raw_text + reset())

    def _strip_ansi(self, text):
        """Remove ANSI escape sequences for length calculation."""
        import re
        return re.sub(r'\033\[[^m]*m', '', text)

    def draw_box(self, top_row, left_col, width, height, title=""):
        """Draw a rounded box with optional title."""
        t = self.t
        border_fg = fg(*t["border"])
        bg_str = self._bg()
        # Top border
        move_to(top_row, left_col)
        top_line = "╭" + "─" * (width - 2) + "╮"
        sys.stdout.write(bg_str + border_fg + top_line + reset())
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
        bot_line = "╰" + "─" * (width - 2) + "╯"
        sys.stdout.write(bg_str + border_fg + bot_line + reset())

    def draw_horizontal_line(self, row, left_col, width):
        """Draw a dim horizontal line."""
        t = self.t
        move_to(row, left_col)
        sys.stdout.write(self._bg() + fg(*t["border"]) + "─" * width + reset())

    def flush(self):
        sys.stdout.flush()


# ---------------------------------------------------------------------------
# The App
# ---------------------------------------------------------------------------

class CliType:
    """Main application state machine."""

    def __init__(self):
        self.state = STATE_MENU
        self.renderer = Renderer("dark")
        self.theme_idx = 0
        self.mode = MODE_TIME
        self.time_idx = 1     # default 30s
        self.word_idx = 1     # default 25 words
        self.lang_idx = 0     # 0=english, 1=indonesian, 2=code
        self.lang_keys = ["english", "indonesian", "code"]
        self.lang_labels = ["English", "Indonesian", "Code"]

        # Menu navigation
        self.menu_row = 0     # 0=mode, 1=sub-option, 2=language, 3=theme
        self.menu_items = 4   # total selectable rows

        # Test state
        self.words = []
        self.typed = ""
        self.word_idx_test = 0
        self.char_idx = 0
        self.correct_chars = 0
        self.incorrect_chars = 0
        self.total_keystrokes = 0
        self.start_time = None
        self.wpm_samples = []
        self.test_finished = False

        # Results
        self.final_wpm = 0
        self.final_accuracy = 0
        self.final_raw_wpm = 0
        self.final_time = 0

    # -- Helpers --

    def _get_word_list(self):
        lang = self.lang_keys[self.lang_idx]
        return LANGUAGES.get(lang, WORDS_ENGLISH)

    def _generate_words(self, count):
        word_list = self._get_word_list()
        if self.lang_keys[self.lang_idx] == "code":
            return random.choices(word_list, k=count)
        return random.choices(word_list, k=count)

    def _get_time_limit(self):
        return TIME_OPTIONS[self.time_idx]

    def _get_word_limit(self):
        return WORD_OPTIONS[self.word_idx]

    # -- Menu Screen --

    def draw_menu(self):
        r = self.renderer
        r.fill_background()
        rows, cols = get_terminal_size()

        # Draw logo
        logo_start_row = max(2, rows // 2 - 12)
        for i, line in enumerate(LOGO):
            r.draw_centered(logo_start_row + i, line, "accent", bold_on=True)

        # Version
        ver_row = logo_start_row + len(LOGO) + 1
        r.draw_centered(ver_row, f"v{VERSION}", "fg_dim")

        # Separator
        sep_row = ver_row + 1
        sep_w = min(60, cols - 4)
        sep_col = (cols - sep_w) // 2 + 1
        r.draw_horizontal_line(sep_row, sep_col, sep_w)

        # Menu options
        menu_start = sep_row + 2
        t = r.t

        # Mode row
        mode_labels = ["time", "words", "code"]
        mode_parts = []
        for i, m in enumerate(mode_labels):
            if (self.mode == MODE_TIME and i == 0) or \
               (self.mode == MODE_WORDS and i == 1) or \
               (self.mode == MODE_CODE and i == 2):
                mode_parts.append(fg(*t["accent"]) + bold() + m + reset() + r._bg())
            else:
                mode_parts.append(fg(*t["fg_dim"]) + m + reset() + r._bg())
        mode_text = "  mode   " + "  │  ".join(mode_parts)
        row_fg = "accent" if self.menu_row == 0 else "fg_dim"
        indicator = fg(*t["accent"]) + "▸ " if self.menu_row == 0 else fg(*t["fg_dim"]) + "  "
        move_to(menu_start, max(1, (cols - 50) // 2))
        sys.stdout.write(r._bg() + indicator + mode_text + reset())

        # Sub-option row (time or word count)
        sub_row = menu_start + 2
        if self.mode == MODE_TIME:
            sub_labels = [f"{s}s" for s in TIME_OPTIONS]
            sub_idx = self.time_idx
        elif self.mode == MODE_WORDS:
            sub_labels = [str(w) for w in WORD_OPTIONS]
            sub_idx = self.word_idx
        else:
            sub_labels = ["snippets"]
            sub_idx = 0

        sub_parts = []
        for i, s in enumerate(sub_labels):
            if i == sub_idx:
                sub_parts.append(fg(*t["accent2"]) + bold() + s + reset() + r._bg())
            else:
                sub_parts.append(fg(*t["fg_dim"]) + s + reset() + r._bg())
        sub_prefix = "  count  " if self.mode == MODE_WORDS else "  time   " if self.mode == MODE_TIME else "  type   "
        sub_text = sub_prefix + "  │  ".join(sub_parts)
        indicator2 = fg(*t["accent"]) + "▸ " if self.menu_row == 1 else fg(*t["fg_dim"]) + "  "
        move_to(sub_row, max(1, (cols - 50) // 2))
        sys.stdout.write(r._bg() + indicator2 + sub_text + reset())

        # Language row
        lang_row = sub_row + 2
        lang_parts = []
        for i, label in enumerate(self.lang_labels):
            if i == self.lang_idx:
                lang_parts.append(fg(*t["accent3"]) + bold() + label.lower() + reset() + r._bg())
            else:
                lang_parts.append(fg(*t["fg_dim"]) + label.lower() + reset() + r._bg())
        lang_text = "  lang   " + "  │  ".join(lang_parts)
        indicator3 = fg(*t["accent"]) + "▸ " if self.menu_row == 2 else fg(*t["fg_dim"]) + "  "
        move_to(lang_row, max(1, (cols - 50) // 2))
        sys.stdout.write(r._bg() + indicator3 + lang_text + reset())

        # Theme row
        theme_row = lang_row + 2
        theme_parts = []
        for i, tk in enumerate(THEME_KEYS):
            tn = THEMES[tk]["name"].lower()
            if i == self.theme_idx:
                theme_parts.append(fg(*t["accent"]) + bold() + tn + reset() + r._bg())
            else:
                theme_parts.append(fg(*t["fg_dim"]) + tn + reset() + r._bg())
        theme_text = "  theme  " + "  │  ".join(theme_parts)
        indicator4 = fg(*t["accent"]) + "▸ " if self.menu_row == 3 else fg(*t["fg_dim"]) + "  "
        move_to(theme_row, max(1, (cols - 50) // 2))
        sys.stdout.write(r._bg() + indicator4 + theme_text + reset())

        # Footer hints
        footer_row = rows - 2
        hints = [
            ("↑↓", "navigate"),
            ("←→", "select"),
            ("enter", "start"),
            ("h", "history"),
            ("q", "quit"),
        ]
        hint_parts = []
        for key, desc in hints:
            hint_parts.append(
                fg(*t["accent"]) + bold() + key + reset() + r._bg() + " " +
                fg(*t["fg_dim"]) + desc + reset() + r._bg()
            )
        hint_text = "   ".join(hint_parts)
        r.draw_centered(footer_row, hint_text, "fg_dim")

        r.flush()

    def handle_menu_input(self, key):
        if key == "UP":
            self.menu_row = (self.menu_row - 1) % self.menu_items
        elif key == "DOWN":
            self.menu_row = (self.menu_row + 1) % self.menu_items
        elif key == "LEFT" or key == "RIGHT":
            delta = 1 if key == "RIGHT" else -1
            if self.menu_row == 0:
                # Mode
                modes = [MODE_TIME, MODE_WORDS, MODE_CODE]
                idx = modes.index(self.mode)
                idx = (idx + delta) % len(modes)
                self.mode = modes[idx]
                if self.mode == MODE_CODE:
                    self.lang_idx = 2
                elif self.lang_idx == 2:
                    self.lang_idx = 0
            elif self.menu_row == 1:
                # Sub-option
                if self.mode == MODE_TIME:
                    self.time_idx = (self.time_idx + delta) % len(TIME_OPTIONS)
                elif self.mode == MODE_WORDS:
                    self.word_idx = (self.word_idx + delta) % len(WORD_OPTIONS)
            elif self.menu_row == 2:
                # Language
                self.lang_idx = (self.lang_idx + delta) % len(self.lang_keys)
                if self.lang_idx == 2:
                    self.mode = MODE_CODE
                elif self.mode == MODE_CODE:
                    self.mode = MODE_TIME
            elif self.menu_row == 3:
                # Theme
                self.theme_idx = (self.theme_idx + delta) % len(THEME_KEYS)
                self.renderer.set_theme(THEME_KEYS[self.theme_idx])
        elif key == "\r" or key == "\n":
            self._start_test()
        elif key == "h" or key == "H":
            self.state = STATE_HISTORY
        elif key == "q" or key == "Q":
            return False
        return True

    # -- Test Screen --

    def _start_test(self):
        """Initialize and switch to the typing test."""
        self.state = STATE_TEST
        self.test_finished = False
        self.typed = ""
        self.word_idx_test = 0
        self.char_idx = 0
        self.correct_chars = 0
        self.incorrect_chars = 0
        self.total_keystrokes = 0
        self.start_time = None
        self.wpm_samples = []
        self._last_sample_time = 0
        self._last_sample_correct = 0

        if self.mode == MODE_CODE:
            self.words = self._generate_words(30)
        elif self.mode == MODE_WORDS:
            self.words = self._generate_words(self._get_word_limit())
        else:
            # For time mode, generate plenty of words
            self.words = self._generate_words(200)

        # Build the flat target string
        if self.mode == MODE_CODE:
            self.target_text = "  ".join(self.words)
        else:
            self.target_text = " ".join(self.words)

        self.input_chars = []  # list of typed chars (including corrections)

    def _wrap_text(self, text, width):
        """Word-wrap text into lines of at most `width` characters."""
        lines = []
        words_iter = text.split(" ")
        current_line = ""
        for w in words_iter:
            if current_line and len(current_line) + 1 + len(w) > width:
                lines.append(current_line)
                current_line = w
            elif current_line:
                current_line += " " + w
            else:
                current_line = w
        if current_line:
            lines.append(current_line)
        return lines

    def draw_test(self):
        r = self.renderer
        t = r.t
        r.fill_background()
        rows, cols = get_terminal_size()
        text_width = min(70, cols - 6)
        text_col = max(1, (cols - text_width) // 2 + 1)

        # Header: live stats
        header_row = max(2, rows // 2 - 8)
        elapsed = 0
        if self.start_time:
            elapsed = time.time() - self.start_time

        # Calculate live WPM
        if elapsed > 0 and self.correct_chars > 0:
            live_wpm = int((self.correct_chars / 5) / (elapsed / 60))
        else:
            live_wpm = 0

        # Time or word counter
        if self.mode == MODE_TIME:
            remaining = max(0, self._get_time_limit() - elapsed)
            counter_text = f"{int(remaining)}s"
        elif self.mode == MODE_WORDS:
            total_w = self._get_word_limit()
            done_w = self._count_completed_words()
            counter_text = f"{done_w}/{total_w}"
        else:
            counter_text = "code"

        # Draw header
        stats_line = (
            fg(*t["accent"]) + bold() + str(live_wpm) + reset() + r._bg() +
            fg(*t["fg_dim"]) + " wpm" + reset() + r._bg() +
            "    " +
            fg(*t["accent2"]) + bold() + counter_text + reset() + r._bg()
        )
        r.draw_centered(header_row, stats_line, "fg_dim")

        # Separator
        r.draw_horizontal_line(header_row + 1, text_col, text_width)

        # Draw the text with coloring
        text_start_row = header_row + 3
        lines = self._wrap_text(self.target_text, text_width)

        # Find which line the cursor is on
        char_offset = 0
        cursor_line = 0
        cursor_char_in_line = 0
        for i, line in enumerate(lines):
            if char_offset + len(line) > self.char_idx:
                cursor_line = i
                cursor_char_in_line = self.char_idx - char_offset
                break
            char_offset += len(line) + 1  # +1 for the space that was split
        else:
            cursor_line = len(lines) - 1
            cursor_char_in_line = self.char_idx - char_offset

        # Show up to 3 lines around cursor
        start_line_display = max(0, cursor_line - 1)
        display_lines = lines[start_line_display:start_line_display + 3]

        # Calculate char offset for start_line_display
        display_char_offset = 0
        for i in range(start_line_display):
            display_char_offset += len(lines[i]) + 1

        for li, line in enumerate(display_lines):
            row = text_start_row + li * 2  # spacing between lines
            move_to(row, text_col)
            rendered = ""
            for ci, ch in enumerate(line):
                abs_idx = display_char_offset + ci
                if abs_idx < self.char_idx:
                    # Already typed
                    if abs_idx < len(self.input_chars) and self.input_chars[abs_idx] == ch:
                        rendered += fg(*t["fg_correct"]) + ch
                    else:
                        rendered += fg(*t["fg_incorrect"]) + bg_color(*t["surface"]) + ch + r._bg()
                elif abs_idx == self.char_idx:
                    # Cursor position — draw with underline effect
                    rendered += fg(*t["fg_cursor"]) + underline() + ch + reset() + r._bg()
                else:
                    # Not yet typed
                    rendered += fg(*t["fg_dim"]) + ch
            sys.stdout.write(r._bg() + rendered + reset())
            display_char_offset += len(line) + 1

        # Footer hints
        footer_row = rows - 2
        r.draw_centered(footer_row, "esc  restart   ctrl+c  quit", "fg_dim")

        r.flush()

    def _count_completed_words(self):
        """Count how many complete words have been typed."""
        typed_text = "".join(self.input_chars[:self.char_idx])
        return typed_text.count(" ") + (1 if self.char_idx > 0 else 0)

    def handle_test_input(self, key, term):
        """Process a keystroke during the test. Returns True to continue."""
        if key == "ESC":
            # Restart — go back to menu
            self.state = STATE_MENU
            return True

        if key is None:
            # Timeout tick — check time limit
            if self.mode == MODE_TIME and self.start_time:
                elapsed = time.time() - self.start_time
                if elapsed >= self._get_time_limit():
                    self._finish_test()
            return True

        # Ignore arrow keys and other special keys
        if key.startswith("ESC") or key in ("UP", "DOWN", "LEFT", "RIGHT"):
            return True

        # Start timer on first real keystroke
        if self.start_time is None:
            self.start_time = time.time()
            self._last_sample_time = self.start_time
            self._last_sample_correct = 0

        self.total_keystrokes += 1

        if key == "\x7f" or key == "\x08":
            # Backspace
            if self.char_idx > 0:
                self.char_idx -= 1
                if self.char_idx < len(self.input_chars):
                    # Re-evaluate correct/incorrect
                    removed = self.input_chars[self.char_idx]
                    target_ch = self.target_text[self.char_idx] if self.char_idx < len(self.target_text) else ""
                    if removed == target_ch:
                        self.correct_chars -= 1
                    else:
                        self.incorrect_chars -= 1
                    self.input_chars.pop(self.char_idx)
        elif len(key) == 1 and (key.isprintable() or key == "\t"):
            # Normal character
            if self.char_idx < len(self.target_text):
                target_ch = self.target_text[self.char_idx]
                if key == target_ch:
                    self.correct_chars += 1
                else:
                    self.incorrect_chars += 1
                # Insert or replace
                if self.char_idx < len(self.input_chars):
                    self.input_chars[self.char_idx] = key
                else:
                    self.input_chars.append(key)
                self.char_idx += 1

                # Sample WPM every second
                now = time.time()
                if now - self._last_sample_time >= 1.0:
                    elapsed_since_start = now - self.start_time
                    if elapsed_since_start > 0:
                        sample_wpm = int((self.correct_chars / 5) / (elapsed_since_start / 60))
                        self.wpm_samples.append(sample_wpm)
                    self._last_sample_time = now

                # Check completion
                if self.char_idx >= len(self.target_text):
                    self._finish_test()
                elif self.mode == MODE_WORDS:
                    done_w = self._count_completed_words()
                    if done_w >= self._get_word_limit():
                        self._finish_test()

        # Check time limit
        if self.mode == MODE_TIME and self.start_time:
            elapsed = time.time() - self.start_time
            if elapsed >= self._get_time_limit():
                self._finish_test()

        return True

    def _finish_test(self):
        """Calculate final stats and switch to results."""
        self.test_finished = True
        elapsed = time.time() - self.start_time if self.start_time else 1
        self.final_time = round(elapsed, 1)
        total_typed = self.correct_chars + self.incorrect_chars
        self.final_wpm = int((self.correct_chars / 5) / (elapsed / 60)) if elapsed > 0 else 0
        self.final_raw_wpm = int((total_typed / 5) / (elapsed / 60)) if elapsed > 0 else 0
        self.final_accuracy = round(
            (self.correct_chars / total_typed * 100) if total_typed > 0 else 0, 1
        )

        # Add final sample
        if self.wpm_samples:
            self.wpm_samples.append(self.final_wpm)
        else:
            self.wpm_samples = [self.final_wpm]

        # Save to history
        entry = {
            "date": time.strftime("%Y-%m-%d %H:%M"),
            "wpm": self.final_wpm,
            "raw_wpm": self.final_raw_wpm,
            "accuracy": self.final_accuracy,
            "mode": self.mode,
            "time": self.final_time,
            "language": self.lang_keys[self.lang_idx],
            "theme": THEME_KEYS[self.theme_idx],
            "correct": self.correct_chars,
            "incorrect": self.incorrect_chars,
            "keystrokes": self.total_keystrokes,
            "wpm_graph": self.wpm_samples,
        }
        save_history(entry)

        self.state = STATE_RESULTS

    # -- Results Screen --

    def draw_results(self):
        r = self.renderer
        t = r.t
        r.fill_background()
        rows, cols = get_terminal_size()

        start_row = max(2, rows // 2 - 10)

        # Title
        r.draw_centered(start_row, "┌─── results ───┐", "border")

        # Big WPM
        wpm_str = str(self.final_wpm)
        wpm_row = start_row + 2
        r.draw_centered(wpm_row, wpm_str, "accent", bold_on=True)
        r.draw_centered(wpm_row + 1, "wpm", "fg_dim")

        # Stats row
        stats_row = wpm_row + 3
        stats = [
            ("acc", f"{self.final_accuracy}%", "accent2"),
            ("raw", f"{self.final_raw_wpm}", "accent3"),
            ("time", f"{self.final_time}s", "fg_active"),
            ("chars", f"{self.correct_chars}/{self.incorrect_chars}", "fg_correct"),
            ("keys", f"{self.total_keystrokes}", "fg_dim"),
        ]
        stat_parts = []
        for label, value, color_key in stats:
            stat_parts.append(
                fg(*t[color_key]) + bold() + value + reset() + r._bg() + " " +
                fg(*t["fg_dim"]) + label + reset() + r._bg()
            )
        stat_text = "    ".join(stat_parts)
        r.draw_centered(stats_row, stat_text, "fg_dim")

        # WPM Graph (sparkline)
        graph_row = stats_row + 3
        r.draw_centered(graph_row - 1, "wpm over time", "fg_dim")
        if self.wpm_samples:
            max_wpm = max(self.wpm_samples) if max(self.wpm_samples) > 0 else 1
            min_wpm = min(self.wpm_samples)
            spark = ""
            for sample in self.wpm_samples:
                # Normalize to 0-8 index
                if max_wpm == min_wpm:
                    idx = 4
                else:
                    idx = int((sample - min_wpm) / (max_wpm - min_wpm) * 8)
                idx = max(0, min(8, idx))
                spark += SPARK_CHARS[idx]
            r.draw_centered(graph_row, spark, "wpm_bar", bold_on=True)
            # Min/max labels
            r.draw_centered(graph_row + 1,
                            f"{min_wpm} ─── {max_wpm} wpm", "fg_dim")

        # Language & mode info
        info_row = graph_row + 3
        lang = self.lang_keys[self.lang_idx]
        mode_info = f"{lang}  •  {self.mode}"
        if self.mode == MODE_TIME:
            mode_info += f"  •  {self._get_time_limit()}s"
        elif self.mode == MODE_WORDS:
            mode_info += f"  •  {self._get_word_limit()} words"
        r.draw_centered(info_row, mode_info, "fg_dim")

        # Footer
        footer_row = rows - 2
        r.draw_centered(footer_row, "enter  retry   tab  menu   q  quit", "fg_dim")

        r.flush()

    def handle_results_input(self, key):
        if key == "\r" or key == "\n":
            # Retry same config
            self._start_test()
        elif key == "\t":
            self.state = STATE_MENU
        elif key == "q" or key == "Q":
            return False
        return True

    # -- History Screen --

    def draw_history(self):
        r = self.renderer
        t = r.t
        r.fill_background()
        rows, cols = get_terminal_size()

        start_row = 2
        r.draw_centered(start_row, "┌─── history ───┐", "border")

        history = load_history()
        if not history:
            r.draw_centered(start_row + 3, "no records yet — go type something!", "fg_dim")
        else:
            # Show last 15 entries
            recent = history[-15:]
            recent.reverse()

            # Header row
            header_row = start_row + 2
            header = f"{'date':<17}{'wpm':>6}{'acc':>8}{'mode':>8}{'lang':>12}"
            r.draw_centered(header_row, header, "accent", bold_on=True)
            hdr_len = len(header)
            hdr_col = max(1, (cols - hdr_len) // 2 + 1)
            r.draw_horizontal_line(header_row + 1, hdr_col, hdr_len)

            for i, entry in enumerate(recent):
                row = header_row + 2 + i
                if row >= rows - 3:
                    break
                line = (
                    f"{entry.get('date', '?'):<17}"
                    f"{entry.get('wpm', 0):>6}"
                    f"{str(entry.get('accuracy', 0)) + '%':>8}"
                    f"{entry.get('mode', '?'):>8}"
                    f"{entry.get('language', '?'):>12}"
                )
                r.draw_centered(row, line, "fg_active")

            # Best WPM highlight
            best = max(history, key=lambda e: e.get("wpm", 0))
            best_row = min(rows - 4, header_row + 2 + len(recent) + 1)
            r.draw_horizontal_line(best_row, hdr_col, hdr_len)
            best_text = f"personal best: {best.get('wpm', 0)} wpm ({best.get('accuracy', 0)}% acc)"
            r.draw_centered(best_row + 1, best_text, "accent", bold_on=True)

        # Footer
        footer_row = rows - 2
        r.draw_centered(footer_row, "esc  back to menu", "fg_dim")
        r.flush()

    def handle_history_input(self, key):
        if key == "ESC" or key == "q" or key == "Q" or key == "\r" or key == "\n":
            self.state = STATE_MENU
        return True

    # -- Main Loop --

    def run(self):
        """Main event loop."""
        try:
            with RawTerminal() as term:
                running = True
                while running:
                    if self.state == STATE_MENU:
                        self.draw_menu()
                        key = term.read_key()
                        running = self.handle_menu_input(key)

                    elif self.state == STATE_TEST:
                        self.draw_test()
                        # Use short timeout so we can update timer
                        key = term.read_key(timeout=0.1)
                        running = self.handle_test_input(key, term)

                    elif self.state == STATE_RESULTS:
                        self.draw_results()
                        key = term.read_key()
                        running = self.handle_results_input(key)

                    elif self.state == STATE_HISTORY:
                        self.draw_history()
                        key = term.read_key()
                        running = self.handle_history_input(key)

        except KeyboardInterrupt:
            pass
        finally:
            show_cursor()
            sys.stdout.write(reset())
            sys.stdout.flush()


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

def main():
    app = CliType()
    app.run()


if __name__ == "__main__":
    main()
