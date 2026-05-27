"""Results screen for clitype."""

from core.data.constants import (
    MODE_TIME,
    MODE_WORDS,
    SPARK_CHARS,
    STATE_MENU,
)
from core.terminal.ansi import bold, fg, get_terminal_size, reset


def draw_results(renderer, app):
    """Draw the results of the completed typing test."""
    engine = app.engine
    if not engine:
        return

    r = renderer
    t = r.t
    r.fill_background()
    rows, cols = get_terminal_size()

    start_row = max(2, rows // 2 - 10)

    # Title
    r.draw_centered(start_row, "┌─── results ───┐", "border")

    # Big WPM
    wpm_str = str(engine.final_wpm)
    wpm_row = start_row + 2
    r.draw_centered(wpm_row, wpm_str, "accent", bold_on=True)
    r.draw_centered(wpm_row + 1, "wpm", "fg_dim")

    # Stats row
    stats_row = wpm_row + 3
    stats = [
        ("acc", f"{engine.final_accuracy}%", "accent2"),
        ("raw", f"{engine.final_raw_wpm}", "accent3"),
        ("time", f"{engine.final_time}s", "fg_active"),
        (
            "chars",
            f"{engine.correct_chars}/{engine.incorrect_chars}",
            "fg_correct",
        ),
        ("keys", f"{engine.total_keystrokes}", "fg_dim"),
    ]
    stat_parts = []
    for label, value, color_key in stats:
        stat_parts.append(
            fg(*t[color_key])
            + bold()
            + value
            + reset()
            + r._bg()
            + " "
            + fg(*t["fg_dim"])
            + label
            + reset()
            + r._bg()
        )
    stat_text = "    ".join(stat_parts)
    r.draw_centered(stats_row, stat_text, "fg_dim")

    # WPM Graph (sparkline)
    graph_row = stats_row + 3
    r.draw_centered(graph_row - 1, "wpm over time", "fg_dim")
    if engine.wpm_samples:
        max_wpm = max(engine.wpm_samples) if max(engine.wpm_samples) > 0 else 1
        min_wpm = min(engine.wpm_samples)
        spark = ""
        for sample in engine.wpm_samples:
            # Normalize to 0-8 index
            if max_wpm == min_wpm:
                idx = 4
            else:
                idx = int((sample - min_wpm) / (max_wpm - min_wpm) * 8)
            idx = max(0, min(8, idx))
            spark += SPARK_CHARS[idx]
        r.draw_centered(graph_row, spark, "wpm_bar", bold_on=True)
        # Min/max labels
        r.draw_centered(graph_row + 1, f"{min_wpm} ─── {max_wpm} wpm", "fg_dim")

    # Language & mode info
    info_row = graph_row + 3
    lang = app.lang_keys[app.lang_idx]
    mode_info = f"{lang}  •  {engine.mode}"
    if engine.mode == MODE_TIME:
        mode_info += f"  •  {engine.get_time_limit()}s"
    elif engine.mode == MODE_WORDS:
        mode_info += f"  •  {engine.get_word_limit()} words"
    r.draw_centered(info_row, mode_info, "fg_dim")

    # Footer
    footer_row = rows - 2
    r.draw_centered(footer_row, "enter  retry   tab  menu   q  quit", "fg_dim")

    r.flush()


def handle_results_input(key, app):
    """Handle menu keyboard navigation on the results screen."""
    if key in ("\r", "\n"):
        # Retry same config
        app.start_test()
    elif key == "\t":
        app.state = STATE_MENU
    elif key in ("q", "Q"):
        return False
    return True
