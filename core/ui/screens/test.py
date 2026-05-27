"""Typing test screen for clitype."""

import sys
import time

from core.data.constants import (
    MODE_TIME,
    MODE_WORDS,
    STATE_MENU,
    STATE_RESULTS,
)
from core.data.history import save_history
from core.terminal.ansi import (
    bg_color,
    bold,
    fg,
    get_terminal_size,
    move_to,
    reset,
    underline,
)
from core.ui.themes import THEME_KEYS


def _wrap_text(text, width):
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


def draw_test(renderer, app):
    """Draw the live typing test screen."""
    engine = app.engine
    if not engine:
        return

    r = renderer
    t = r.t
    r.fill_background()
    rows, cols = get_terminal_size()
    text_width = min(70, cols - 6)
    text_col = max(1, (cols - text_width) // 2 + 1)

    # Header: live stats
    header_row = max(2, rows // 2 - 8)
    elapsed = 0
    if engine.start_time:
        elapsed = time.time() - engine.start_time

    # Calculate live WPM
    if elapsed > 0 and engine.correct_chars > 0:
        live_wpm = int((engine.correct_chars / 5) / (elapsed / 60))
    else:
        live_wpm = 0

    # Time or word counter
    if engine.mode == MODE_TIME:
        remaining = max(0, engine.get_time_limit() - elapsed)
        counter_text = f"{int(remaining)}s"
    elif engine.mode == MODE_WORDS:
        total_w = engine.get_word_limit()
        done_w = engine.count_completed_words()
        counter_text = f"{done_w}/{total_w}"
    else:
        counter_text = "code"

    # Draw header
    stats_line = (
        fg(*t["accent"])
        + bold()
        + str(live_wpm)
        + reset()
        + r._bg()
        + fg(*t["fg_dim"])
        + " wpm"
        + reset()
        + r._bg()
        + "    "
        + fg(*t["accent2"])
        + bold()
        + counter_text
        + reset()
        + r._bg()
    )
    r.draw_centered(header_row, stats_line, "fg_dim")

    # Separator
    r.draw_horizontal_line(header_row + 1, text_col, text_width)

    # Draw the text with coloring
    text_start_row = header_row + 3
    lines = _wrap_text(engine.target_text, text_width)

    # Find which line the cursor is on
    char_offset = 0
    cursor_line = 0
    for i, line in enumerate(lines):
        if char_offset + len(line) > engine.char_idx:
            cursor_line = i
            break
        char_offset += len(line) + 1  # +1 for the space that was split
    else:
        cursor_line = len(lines) - 1

    # Show up to 3 lines around cursor
    start_line_display = max(0, cursor_line - 1)
    display_lines = lines[start_line_display : start_line_display + 3]

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
            if abs_idx < engine.char_idx:
                # Already typed
                if (
                    abs_idx < len(engine.input_chars)
                    and engine.input_chars[abs_idx] == ch
                ):
                    rendered += fg(*t["fg_correct"]) + ch
                else:
                    rendered += (
                        fg(*t["fg_incorrect"])
                        + bg_color(*t["surface"])
                        + ch
                        + r._bg()
                    )
            elif abs_idx == engine.char_idx:
                # Cursor position — draw with underline effect
                rendered += (
                    fg(*t["fg_cursor"]) + underline() + ch + reset() + r._bg()
                )
            else:
                # Not yet typed
                rendered += fg(*t["fg_dim"]) + ch
        sys.stdout.write(r._bg() + rendered + reset())
        display_char_offset += len(line) + 1

    # Footer hints
    footer_row = rows - 2
    r.draw_centered(footer_row, "esc  restart   ctrl+c  quit", "fg_dim")

    r.flush()


def handle_test_input(key, app):
    """Handle input during the test session."""
    engine = app.engine
    if not engine:
        return True

    # If user hits ESC, go back to menu
    if key == "ESC":
        app.state = STATE_MENU
        return True

    # Feed input to typing engine
    is_running = engine.handle_input(key)

    # If typing test finished, compile history and transition
    if not is_running and engine.test_finished:
        entry = {
            "date": time.strftime("%Y-%m-%d %H:%M"),
            "wpm": engine.final_wpm,
            "raw_wpm": engine.final_raw_wpm,
            "accuracy": engine.final_accuracy,
            "mode": engine.mode,
            "time": engine.final_time,
            "language": app.lang_keys[app.lang_idx],
            "theme": THEME_KEYS[app.theme_idx],
            "correct": engine.correct_chars,
            "incorrect": engine.incorrect_chars,
            "keystrokes": engine.total_keystrokes,
            "wpm_graph": engine.wpm_samples,
        }
        save_history(entry)
        app.state = STATE_RESULTS

    return True
