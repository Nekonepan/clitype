"""Application constants, configuration, and static data for clitype."""

import json
from pathlib import Path

# ---------------------------------------------------------------------------
# Directories
# ---------------------------------------------------------------------------
CORE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = CORE_DIR.parent
LANGUAGES_DIR = PROJECT_DIR / "languages"

# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------
VERSION = "1.0.0"
APP_NAME = "clitype"

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
CONFIG_DIR = Path.home() / ".config" / "clitype"
HISTORY_FILE = CONFIG_DIR / "history.json"

# ---------------------------------------------------------------------------
# States
# ---------------------------------------------------------------------------
STATE_MENU = "menu"
STATE_TEST = "test"
STATE_RESULTS = "results"
STATE_HISTORY = "history"

# ---------------------------------------------------------------------------
# Modes
# ---------------------------------------------------------------------------
MODE_TIME = "time"
MODE_WORDS = "words"
MODE_CODE = "code"

# ---------------------------------------------------------------------------
# Options
# ---------------------------------------------------------------------------
TIME_OPTIONS = [15, 30, 60]
WORD_OPTIONS = [10, 25, 50]

# ---------------------------------------------------------------------------
# Dynamic Language Loader
# Loads any .json files from languages/ (mocked/forked from Monkeytype static repo)
# ---------------------------------------------------------------------------
LANGUAGES = {}
LANG_KEYS = []
LANG_LABELS = []

if LANGUAGES_DIR.exists() and LANGUAGES_DIR.is_dir():
    # Sort files consistently: English first, Indonesian second, Code last, others alphabetical
    json_paths = list(LANGUAGES_DIR.glob("*.json"))

    def sort_key(p):
        name = p.stem.lower()
        if name == "english":
            return (0, name)
        elif name == "indonesian":
            return (1, name)
        elif name == "code":
            return (9, name)
        return (2, name)

    json_paths.sort(key=sort_key)

    for path in json_paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                name = data.get("name", path.stem).lower()
                words = data.get("words", [])
                if words:
                    LANGUAGES[name] = words
                    LANG_KEYS.append(name)
                    LANG_LABELS.append(name.capitalize())
        except Exception:
            pass

# Fallback in case no languages are loaded
if not LANGUAGES:
    LANGUAGES = {
        "english": [
            "the", "be", "to", "of", "and", "a", "in", "that", "have", "i"
        ],
        "indonesian": [
            "dan", "yang", "di", "ini", "itu", "dengan", "untuk", "tidak"
        ],
        "code": [
            "const x = 42;", "def hello(): pass", "print('hello')"
        ],
    }
    LANG_KEYS = ["english", "indonesian", "code"]
    LANG_LABELS = ["English", "Indonesian", "Code"]

# ---------------------------------------------------------------------------
# Sparkline characters for WPM graph
# ---------------------------------------------------------------------------
SPARK_CHARS = " ▁▂▃▄▅▆▇█"

# ---------------------------------------------------------------------------
# ASCII Art Logo
# ---------------------------------------------------------------------------
LOGO = [
"  ██████╗██╗     ██╗████████╗██╗   ██╗██████╗ ███████╗ ",
" ██╔════╝██║     ██║╚══██╔══╝╚██╗ ██╔╝██╔══██╗██╔════╝ ",
" ██║     ██║     ██║   ██║    ╚████╔╝ ██████╔╝█████╗   ",
" ██║     ██║     ██║   ██║     ╚██╔╝  ██╔═══╝ ██╔══╝   ",
" ╚██████╗███████╗██║   ██║      ██║   ██║     ███████╗ ",
"  ╚═════╝╚══════╝╚═╝   ╚═╝      ╚═╝   ╚═╝     ╚══════╝ ",
]
