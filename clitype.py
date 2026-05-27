#!/usr/bin/env python3
"""clitype — A gorgeous terminal typing test inspired by Monkeytype."""

import sys

from core import CliType


def main():
    """Main entry point to launch clitype."""
    app = CliType()
    app.run()


if __name__ == "__main__":
    main()
