"""Menu screen for clitype."""

import sys

from core.data.constants import (
    LANG_KEYS,
    LANG_LABELS,
    LOGO,
    MODE_CODE,
    MODE_TIME,
    MODE_WORDS,
    STATE_HISTORY,
    TIME_OPTIONS,
    VERSION,
    WORD_OPTIONS,
)
from core.terminal.ansi import (
    bg_color,
    bold,
    fg,
    get_terminal_size,
    move_to,
    reset,
)
from core.ui.themes import THEME_KEYS, THEMES


def draw_menu(renderer, app):
    """Draw the configurations menu on the terminal."""
    renderer.fill_background()
    rows, cols = get_terminal_size()

    # Draw logo
    logo_start_row = max(2, rows // 2 - 12)
    for i, line in enumerate(LOGO):
        renderer.draw_centered(logo_start_row + i, line, "accent", bold_on=True)

    # Version
    ver_row = logo_start_row + len(LOGO) + 1
    renderer.draw_centered(ver_row, f"v{VERSION}", "fg_dim")

    # Separator
    sep_row = ver_row + 1
    sep_w = min(60, cols - 4)
    sep_col = (cols - sep_w) // 2 + 1
    renderer.draw_horizontal_line(sep_row, sep_col, sep_w)

    # Menu options
    menu_start = sep_row + 2
    t = renderer.t

    # Mode row
    mode_labels = ["time", "words", "code"]
    mode_parts = []
    for i, m in enumerate(mode_labels):
        if (
            (app.mode == MODE_TIME and i == 0)
            or (app.mode == MODE_WORDS and i == 1)
            or (app.mode == MODE_CODE and i == 2)
        ):
            mode_parts.append(
                fg(*t["accent"]) + bold() + m + reset() + renderer._bg()
            )
        else:
            mode_parts.append(fg(*t["fg_dim"]) + m + reset() + renderer._bg())
    mode_text = "  mode   " + "  │  ".join(mode_parts)

    indicator = (
        fg(*t["accent"]) + "▸ "
        if app.menu_row == 0
        else fg(*t["fg_dim"]) + "  "
    )
    move_to(menu_start, max(1, (cols - 50) // 2))
    sys.stdout.write(renderer._bg() + indicator + mode_text + reset())

    # Sub-option row (time or word count)
    sub_row = menu_start + 2
    if app.mode == MODE_TIME:
        sub_labels = [f"{s}s" for s in TIME_OPTIONS]
        sub_idx = app.time_idx
    elif app.mode == MODE_WORDS:
        sub_labels = [str(w) for w in WORD_OPTIONS]
        sub_idx = app.word_idx
    else:
        sub_labels = ["snippets"]
        sub_idx = 0

    sub_parts = []
    for i, s in enumerate(sub_labels):
        if i == sub_idx:
            sub_parts.append(
                fg(*t["accent2"]) + bold() + s + reset() + renderer._bg()
            )
        else:
            sub_parts.append(fg(*t["fg_dim"]) + s + reset() + renderer._bg())
    sub_prefix = (
        "  count  "
        if app.mode == MODE_WORDS
        else "  time   "
        if app.mode == MODE_TIME
        else "  type   "
    )
    sub_text = sub_prefix + "  │  ".join(sub_parts)
    indicator2 = (
        fg(*t["accent"]) + "▸ "
        if app.menu_row == 1
        else fg(*t["fg_dim"]) + "  "
    )
    move_to(sub_row, max(1, (cols - 50) // 2))
    sys.stdout.write(renderer._bg() + indicator2 + sub_text + reset())

    # Language row
    lang_row = sub_row + 2
    lang_parts = []
    for i, label in enumerate(app.lang_labels):
        if i == app.lang_idx:
            lang_parts.append(
                fg(*t["accent3"])
                + bold()
                + label.lower()
                + reset()
                + renderer._bg()
            )
        else:
            lang_parts.append(
                fg(*t["fg_dim"]) + label.lower() + reset() + renderer._bg()
            )
    lang_text = "  lang   " + "  │  ".join(lang_parts)
    indicator3 = (
        fg(*t["accent"]) + "▸ "
        if app.menu_row == 2
        else fg(*t["fg_dim"]) + "  "
    )
    move_to(lang_row, max(1, (cols - 50) // 2))
    sys.stdout.write(renderer._bg() + indicator3 + lang_text + reset())

    # Theme row
    theme_row = lang_row + 2
    theme_parts = []
    for i, tk in enumerate(THEME_KEYS):
        tn = THEMES[tk]["name"].lower()
        if i == app.theme_idx:
            theme_parts.append(
                fg(*t["accent"]) + bold() + tn + reset() + renderer._bg()
            )
        else:
            theme_parts.append(fg(*t["fg_dim"]) + tn + reset() + renderer._bg())
    theme_text = "  theme  " + "  │  ".join(theme_parts)
    indicator4 = (
        fg(*t["accent"]) + "▸ "
        if app.menu_row == 3
        else fg(*t["fg_dim"]) + "  "
    )
    move_to(theme_row, max(1, (cols - 50) // 2))
    sys.stdout.write(renderer._bg() + indicator4 + theme_text + reset())

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
            fg(*t["accent"])
            + bold()
            + key
            + reset()
            + renderer._bg()
            + " "
            + fg(*t["fg_dim"])
            + desc
            + reset()
            + renderer._bg()
        )
    hint_text = "   ".join(hint_parts)
    renderer.draw_centered(footer_row, hint_text, "fg_dim")

    renderer.flush()


def handle_menu_input(key, app):
    """Handle keyboard input on the menu screen."""
    if key == "UP":
        app.menu_row = (app.menu_row - 1) % app.menu_items
    elif key == "DOWN":
        app.menu_row = (app.menu_row + 1) % app.menu_items
    elif key in ("LEFT", "RIGHT"):
        delta = 1 if key == "RIGHT" else -1
        if app.menu_row == 0:
            # Mode
            modes = [MODE_TIME, MODE_WORDS, MODE_CODE]
            idx = modes.index(app.mode)
            idx = (idx + delta) % len(modes)
            app.mode = modes[idx]
            if app.mode == MODE_CODE:
                app.lang_idx = 2
            elif app.lang_idx == 2:
                app.lang_idx = 0
        elif app.menu_row == 1:
            # Sub-option
            if app.mode == MODE_TIME:
                app.time_idx = (app.time_idx + delta) % len(TIME_OPTIONS)
            elif app.mode == MODE_WORDS:
                app.word_idx = (app.word_idx + delta) % len(WORD_OPTIONS)
        elif app.menu_row == 2:
            # Language
            app.lang_idx = (app.lang_idx + delta) % len(app.lang_keys)
            if app.lang_idx == 2:
                app.mode = MODE_CODE
            elif app.mode == MODE_CODE:
                app.mode = MODE_TIME
        elif app.menu_row == 3:
            # Theme
            app.theme_idx = (app.theme_idx + delta) % len(THEME_KEYS)
            app.renderer.set_theme(THEME_KEYS[app.theme_idx])
    elif key in ("\r", "\n"):
        app.start_test()
    elif key in ("h", "H"):
        app.state = STATE_HISTORY
    elif key in ("q", "Q"):
        return False
    return True
