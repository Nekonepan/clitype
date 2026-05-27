"""Application constants, configuration, and static data for clitype."""

from pathlib import Path

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
# Languages
# ---------------------------------------------------------------------------
LANGUAGES = {
    "english": WORDS_ENGLISH,
    "indonesian": WORDS_INDONESIAN,
    "code": CODE_SNIPPETS,
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
    "        ██  ██            ██",
    "        ██                ██",
    " ▄████▄ ██  ██  ██   ██  ██▄▄██  ▄███▄",
    "██▀  ▀▀ ██  ██  ▀█▄ ██▀ ██▀▀██  ██▀ ▀██",
    "██   ▄▄ ██  ██   ▀███▀  ██  ██  ██   ██",
    " ▀███▀  ██  ██    ██    ██  ██  ▀████▀",
    "                  ██",
    "                 ██",
]
