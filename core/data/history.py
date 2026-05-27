"""Score history persistence for clitype."""

import json

from core.data.constants import CONFIG_DIR, HISTORY_FILE


def load_history():
    """Load score history from the JSON file.

    Returns a list of score entry dicts, or an empty list if the file
    doesn't exist or is corrupted.
    """
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_history(entry):
    """Append a score entry to the history file.

    Keeps at most the 500 most recent entries.
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    history = load_history()
    history.append(entry)
    history = history[-500:]
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)
