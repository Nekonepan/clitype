"""Menu screen for clitype with selection sub-menus."""

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
    bold,
    fg,
    bg_color,
    get_terminal_size,
    move_to,
    reset,
)
from core.ui.themes import THEME_KEYS, THEMES


def draw_menu(renderer, app):
    """Draw the new hierarchical master-detail menu on the terminal."""
    renderer.fill_background()
    rows, cols = get_terminal_size()
    t = renderer.t

    # Draw logo
    logo_start_row = max(2, rows // 2 - 12)
    for i, line in enumerate(LOGO):
        renderer.draw_centered(logo_start_row + i, line, "accent", bold_on=True)

    # Version
    ver_row = logo_start_row + len(LOGO) + 1
    renderer.draw_centered(ver_row, f"v{VERSION}", "fg_dim")

    # Current Selection Status Bar
    lang_label = app.lang_labels[app.lang_idx]
    theme_label = THEMES[THEME_KEYS[app.theme_idx]]["name"]
    if app.mode == MODE_TIME:
        limit_label = f"time : {TIME_OPTIONS[app.time_idx]}s"
    elif app.mode == MODE_WORDS:
        limit_label = f"count : {WORD_OPTIONS[app.word_idx]}"
    else:
        limit_label = "type : code"

    status_text = (
        f"mode : {app.mode}  │  {limit_label}  │  "
        f"language : {lang_label}  │  theme : {theme_label}"
    )

    status_row = ver_row + 2
    renderer.draw_centered(status_row - 1, "═" * min(70, cols - 4), "border")
    renderer.draw_centered(status_row, status_text, "accent2", bold_on=True)
    renderer.draw_centered(status_row + 1, "═" * min(70, cols - 4), "border")

    # Start drawing options
    menu_start_row = status_row + 3

    # Define menu rows:
    # 0: Mode, 1: Time/Count, 2: Language, 3: Theme, 4: Start Test
    for row_idx in range(5):
        # We calculate the row's terminal position dynamically.
        # If we have entered an option submenu (app.in_option_select is True)
        # and that row is row_idx, it takes an extra line for option list.
        draw_row = menu_start_row + row_idx * 2
        if app.in_option_select and row_idx > app.menu_row:
            draw_row += 1

        is_active = app.menu_row == row_idx
        is_editing = is_active and app.in_option_select

        if row_idx == 4:
            # Row 4: Start Test Row
            if is_active:
                header_str = (
                    fg(*t["accent"]) + bold() + "▸ [ START TEST ]" + reset()
                )
            else:
                header_str = fg(*t["fg_dim"]) + "  [ START TEST ]" + reset()
            renderer.draw_centered(draw_row, header_str)
            continue

        # Get Category Label & Value
        if row_idx == 0:
            label = "mode"
            val = app.mode
        elif row_idx == 1:
            label = (
                "count"
                if app.mode == MODE_WORDS
                else "time"
                if app.mode == MODE_TIME
                else "type"
            )
            val = (
                f"{WORD_OPTIONS[app.word_idx]} words"
                if app.mode == MODE_WORDS
                else f"{TIME_OPTIONS[app.time_idx]}s"
                if app.mode == MODE_TIME
                else "snippets"
            )
        elif row_idx == 2:
            label = "language"
            val = lang_label.lower()
        else:
            label = "theme"
            val = theme_label.lower()

        # Draw Category Row
        # Format: Category Name ...... Value
        label_col_w = 12
        padded_label = f"{label:<{label_col_w}}"

        if is_editing:
            # Editing state: Header expanded with focus color
            header_str = (
                fg(*t["accent"])
                + bold()
                + f"▸ {padded_label}   ( select value below )"
                + reset()
            )
            renderer.draw_centered(draw_row, header_str)

            # Draw the submenu option items directly below it
            options_str = ""
            if row_idx == 0:
                # Mode Options
                modes = ["time", "words", "code"]
                parts = []
                for m in modes:
                    if app.mode == m:
                        parts.append(
                            fg(*t["accent"]) + bold() + f"[ {m} ]" + reset() + bg_color(*t["surface"])
                        )
                    else:
                        parts.append(fg(*t["fg_dim"]) + f"  {m}  " + reset() + bg_color(*t["surface"]))
                # Wrap the whole block in surface background with padding
                options_str = bg_color(*t["surface"]) + "  " + "   ".join(parts) + "  " + reset()

            elif row_idx == 1:
                # Time / Count Options
                if app.mode == MODE_TIME:
                    sub_labels = [f"{s}s" for s in TIME_OPTIONS]
                    sub_idx = app.time_idx
                elif app.mode == MODE_WORDS:
                    sub_labels = [str(w) for w in WORD_OPTIONS]
                    sub_idx = app.word_idx
                else:
                    sub_labels = ["snippets"]
                    sub_idx = 0

                parts = []
                for i, s in enumerate(sub_labels):
                    if i == sub_idx:
                        parts.append(
                            fg(*t["accent2"]) + bold() + f"[ {s} ]" + reset() + bg_color(*t["surface"])
                        )
                    else:
                        parts.append(fg(*t["fg_dim"]) + f"  {s}  " + reset() + bg_color(*t["surface"]))
                options_str = bg_color(*t["surface"]) + "  " + "   ".join(parts) + "  " + reset()

            elif row_idx == 2:
                parts = []
                for i, lang in enumerate(app.lang_labels):
                    if i == app.lang_idx:
                        parts.append(
                            fg(*t["accent3"])
                            + bold()
                            + f"[ {lang.lower()} ]"
                            + reset() + bg_color(*t["surface"])
                        )
                    else:
                        parts.append(
                            fg(*t["fg_dim"]) + f"  {lang.lower()}  " + reset() + bg_color(*t["surface"])
                        )
                options_str = bg_color(*t["surface"]) + "  " + "   ".join(parts) + "  " + reset()

            elif row_idx == 3:
                # Theme Options
                parts = []
                for i, tk in enumerate(THEME_KEYS):
                    tn = THEMES[tk]["name"].lower()
                    if i == app.theme_idx:
                        parts.append(
                            fg(*t["accent"]) + bold() + f"[ {tn} ]" + reset() + bg_color(*t["surface"])
                        )
                    else:
                        parts.append(fg(*t["fg_dim"]) + f"  {tn}  " + reset() + bg_color(*t["surface"]))
                options_str = bg_color(*t["surface"]) + "  " + "  ".join(parts) + "  " + reset()

            renderer.draw_centered(draw_row + 1, options_str)

        else:
            # Standard View (Collapsed):
            # Show "Category Name   value"
            if is_active:
                line_str = (
                    fg(*t["accent"])
                    + bold()
                    + f"▸ {padded_label}   "
                    + fg(*t["accent2"])
                    + f" {val} "
                    + reset()
                )
            else:
                line_str = (
                    fg(*t["fg_dim"])
                    + f"  {padded_label}   "
                    + fg(*t["fg_dim"])
                    + f" {val} "
                    + reset()
                )
            renderer.draw_centered(draw_row, line_str)

    # Footer hints
    footer_row = rows - 2
    if app.in_option_select:
        hints = [
            ("←→", "change option"),
            ("enter", "confirm & return"),
            ("esc", "go back"),
        ]
    else:
        hints = [
            ("↑↓", "navigate categories"),
            ("enter", "select / edit category"),
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
    """Handle keyboard navigation on the hierarchical select menu."""
    if app.in_option_select:
        # State: Submenu Active (Selecting Option Value)
        if key in ("\r", "\n", "ESC"):
            # Confirm and collapse
            app.in_option_select = False
        elif key in ("LEFT", "RIGHT"):
            delta = 1 if key == "RIGHT" else -1
            if app.menu_row == 0:
                # Mode
                modes = [MODE_TIME, MODE_WORDS, MODE_CODE]
                idx = modes.index(app.mode)
                idx = (idx + delta) % len(modes)
                app.mode = modes[idx]
                code_idx = app.lang_keys.index("code") if "code" in app.lang_keys else -1
                if app.mode == MODE_CODE and code_idx >= 0:
                    app.lang_idx = code_idx
                elif app.lang_keys[app.lang_idx] == "code":
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
                if app.lang_keys[app.lang_idx] == "code":
                    app.mode = MODE_CODE
                elif app.mode == MODE_CODE:
                    app.mode = MODE_TIME
            elif app.menu_row == 3:
                # Theme
                app.theme_idx = (app.theme_idx + delta) % len(THEME_KEYS)
                app.renderer.set_theme(THEME_KEYS[app.theme_idx])
    else:
        # State: Navigating Menu Row categories
        if key == "UP":
            app.menu_row = (app.menu_row - 1) % app.menu_items
        elif key == "DOWN":
            app.menu_row = (app.menu_row + 1) % app.menu_items
        elif key in ("\r", "\n", "RIGHT"):
            if app.menu_row == 4:
                # Start Test
                app.start_test()
            else:
                # Enter options select submenu
                app.in_option_select = True
        elif key in ("h", "H"):
            app.state = STATE_HISTORY
        elif key in ("q", "Q"):
            return False
    return True
