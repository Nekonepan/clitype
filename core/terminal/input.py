"""Raw terminal input handling for clitype."""

import os
import sys
import tty
import termios
import select

from core.terminal.ansi import hide_cursor, show_cursor, clear_screen, reset


class RawTerminal:
    """Context manager for raw terminal input.

    Saves terminal settings on entry, sets cbreak mode for character-by-
    character input, and restores the original settings on exit — even if
    the program crashes.
    """

    def __init__(self):
        self.fd = sys.stdin.fileno()
        self.old_settings = None

    def __enter__(self):
        self.old_settings = termios.tcgetattr(self.fd)
        tty.setcbreak(self.fd)
        hide_cursor()
        return self

    def __exit__(self, *args):
        if self.old_settings:
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)
        show_cursor()
        clear_screen()
        sys.stdout.write(reset())
        sys.stdout.flush()

    def read_key(self, timeout=None):
        """Read a single keypress or escape sequence with zero-buffering.

        Returns a string representing the key pressed, or None on timeout.
        Arrow keys are returned as "UP", "DOWN", "LEFT", "RIGHT".
        Escape is returned as "ESC".
        """
        ready, _, _ = select.select([self.fd], [], [], timeout if timeout is not None else None)
        if not ready:
            return None

        try:
            # Read exactly 1 byte to see if it's the start of an escape sequence
            first_byte = os.read(self.fd, 1)
        except OSError:
            return None

        if not first_byte:
            return None

        if first_byte == b"\x1b":
            # It's an escape sequence. Check if more bytes are immediately available.
            ready, _, _ = select.select([self.fd], [], [], 0.05)
            if ready:
                try:
                    # Read the rest of the escape sequence
                    seq = os.read(self.fd, 7)
                    full_seq = first_byte + seq
                    if full_seq == b"\x1b[A":
                        return "UP"
                    elif full_seq == b"\x1b[B":
                        return "DOWN"
                    elif full_seq == b"\x1b[C":
                        return "RIGHT"
                    elif full_seq == b"\x1b[D":
                        return "LEFT"
                    return full_seq.decode("utf-8", errors="ignore")
                except OSError:
                    pass
            return "ESC"

        try:
            return first_byte.decode("utf-8", errors="ignore")
        except Exception:
            return None
