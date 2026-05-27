"""History screen for clitype."""

from core.data.constants import STATE_MENU
from core.data.history import load_history
from core.terminal.ansi import get_terminal_size


def draw_history(renderer, app):
    """Draw the score history screen with a table of recent tests."""
    r = renderer
    t = r.t
    r.fill_background()
    rows, cols = get_terminal_size()

    start_row = 2
    r.draw_centered(start_row, "┌─── history ───┐", "border")

    history = load_history()
    if not history:
        r.draw_centered(
            start_row + 3, "no records yet — go type something!", "fg_dim"
        )
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


def handle_history_input(key, app):
    """Handle keyboard navigation on the history screen."""
    if key in ("ESC", "q", "Q", "\r", "\n"):
        app.state = STATE_MENU
    return True
