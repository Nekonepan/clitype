"""Main application controller and event loop for clitype."""

import sys

from core.data.constants import (
    LANG_KEYS,
    LANG_LABELS,
    MODE_TIME,
    STATE_HISTORY,
    STATE_MENU,
    STATE_RESULTS,
    STATE_TEST,
)
from core.engine.typing_engine import TypingEngine
from core.terminal.ansi import reset, show_cursor, hide_cursor
from core.terminal.input import RawTerminal
from core.ui.renderer import Renderer
from core.ui.screens import (
    draw_history,
    draw_menu,
    draw_results,
    draw_test,
    handle_history_input,
    handle_menu_input,
    handle_results_input,
    handle_test_input,
)


class CliType:
    """Main application controller managing state transitions and event loops."""

    def __init__(self):
        self.state = STATE_MENU
        self.renderer = Renderer("dark")
        self.theme_idx = 0
        self.mode = MODE_TIME
        self.time_idx = 1  # default 30s
        self.word_idx = 1  # default 25 words
        self.lang_idx = 0
        self.lang_keys = LANG_KEYS
        self.lang_labels = LANG_LABELS

        # Menu navigation
        self.menu_row = 0
        self.menu_items = 5
        self.in_option_select = False

        # Typing session engine
        self.engine = None

    def start_test(self):
        """Initialize a new typing test session and transition state."""
        self.engine = TypingEngine(
            self.mode, self.lang_idx, self.time_idx, self.word_idx
        )
        self.state = STATE_TEST

    def run(self):
        """Start the main execution loop."""
        try:
            with RawTerminal() as term:
                running = True
                while running:
                    if self.state == STATE_MENU:
                        hide_cursor()
                        draw_menu(self.renderer, self)
                        key = term.read_key()
                        running = handle_menu_input(key, self)

                    elif self.state == STATE_TEST:
                        draw_test(self.renderer, self)
                        # Short timeout to allow WPM and countdown updates
                        key = term.read_key(timeout=0.1)
                        running = handle_test_input(key, self)

                    elif self.state == STATE_RESULTS:
                        hide_cursor()
                        draw_results(self.renderer, self)
                        key = term.read_key()
                        running = handle_results_input(key, self)

                    elif self.state == STATE_HISTORY:
                        hide_cursor()
                        draw_history(self.renderer, self)
                        key = term.read_key()
                        running = handle_history_input(key, self)

        except KeyboardInterrupt:
            pass
        finally:
            show_cursor()
            sys.stdout.write(reset())
            sys.stdout.flush()
