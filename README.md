# clitype

A gorgeous, highly-polished terminal typing test inspired by [Monkeytype](https://monkeytype.com). Built entirely in Python with zero dependencies.

![Python](https://img.shields.io/badge/python-3.6%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS-lightgrey)

---

## ✨ Features

- **TrueColor themes** - 6 hand-crafted color palettes (Dark, Nord, One Dark, Neon Cyan, Matrix, Retro Sepia)
- **Multiple modes** - Timed tests (15s / 30s / 60s), word-count tests (10 / 25 / 50 words), and code snippet practice
- **Multilingual** - English, French, Spanish, Indonesian, and Code snippet support
- **Live stats** - Real-time WPM counter and progress indicator as you type
- **Results dashboard** - Final WPM, accuracy, raw WPM, keystroke breakdown, and a sparkline WPM-over-time graph
- **Score history** - All your runs are saved locally; view your personal bests and track your progress
- **Zero dependencies** - Uses only the Python standard library (termios, tty, select, json)
- **Instant launch** - No pip install, no virtual environments, just run it

---

## 🚀 Quick Start

```bash
git clone https://github.com/Nekonepan/clitype.git
cd clitype
make run
```

That's it. No setup, no install.

Alternatively, run directly with Python:
```bash
python3 clitype.py
```

---

## 🛠 Make Commands

```bash
make run      # Run the typing test application
make help     # Show available commands
make clean    # Remove Python cache files
```

---

### Menu

| Key       | Action                |
|-----------|-----------------------|
| `↑` `↓`  | Navigate menu rows    |
| `←` `→`  | Cycle through options |
| `Enter`  | Start typing test     |
| `h`      | View score history    |
| `q`      | Quit                  |

### During Test

| Key         | Action                          |
|-------------|---------------------------------|
| *any key*   | Type (test starts on first key) |
| `Backspace` | Delete last character           |
| `Esc`       | Abort & return to menu          |
| `Ctrl+C`    | Force quit                      |

### Results Screen

| Key     | Action                       |
|---------|------------------------------|
| `Enter` | Retry with same settings     |
| `Tab`   | Return to menu               |
| `q`     | Quit                         |

---

## 🎨 Themes

| Theme        | Vibe                             |
|--------------|----------------------------------|
| Dark         | Catppuccin-inspired, easy on eyes |
| Nord         | Cool arctic blues & greens       |
| One Dark     | Atom editor classic              |
| Neon Cyan    | GitHub dark + cyberpunk accents  |
| Matrix       | Terminal green rain aesthetic    |
| Retro Sepia  | Warm, vintage paper tones        |

---

## 📊 Score History

Your results are automatically saved to:
```
~/.config/clitype/history.json
```

Press `h` in the menu to view your recent runs, personal best WPM, and accuracy stats.

---

## 🌐 Languages

- **English** - Common words for everyday typing
- **French** - French vocabulary for bilingual practice
- **Spanish** - Spanish words for polyglots
- **Indonesian** - Indonesian words for local speakers
- **Code** - Programming snippets (Python, JavaScript, C, HTML, CSS)

New languages can be added by creating JSON files in the `languages/` directory.

---

## 📋 Requirements

- Python 3.6+
- A terminal with TrueColor (24-bit) support (most modern terminals: kitty, alacritty, wezterm, GNOME Terminal, etc.)
- Linux or macOS (uses `termios`/`tty` - not compatible with native Windows CMD)

---

## 📁 Project Structure

```
clitype/
├── clitype.py           # Main entry point
├── core/
│   ├── app.py          # Main application controller
│   ├── data/           # Constants and local history storage
│   ├── engine/         # Typing test engine logic
│   ├── terminal/       # Terminal I/O and ANSI control
│   └── ui/             # UI components (renderer, screens, themes)
├── languages/          # Language definitions (JSON format)
├── README.md           # You are here
└── LICENSE             # MIT License
```

---

## 🤝 Contributing

This is an open-source personal project! Feel free to:
1. Fork the repository
2. Add new languages by creating JSON files in the `languages/` directory
3. Create new themes in the `THEMES` dict in `core/ui/themes.py`
4. Improve the engine or UI components in the `core/` directory
5. Submit a pull request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

Copyright (c) 2026 Lutfan Alaudin Naja