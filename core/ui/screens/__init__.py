"""UI Screens for clitype."""

from core.ui.screens.history import draw_history, handle_history_input
from core.ui.screens.menu import draw_menu, handle_menu_input
from core.ui.screens.results import draw_results, handle_results_input
from core.ui.screens.test import draw_test, handle_test_input

__all__ = [
    "draw_menu",
    "handle_menu_input",
    "draw_test",
    "handle_test_input",
    "draw_results",
    "handle_results_input",
    "draw_history",
    "handle_history_input",
]
