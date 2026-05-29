"""Typing test engine for clitype.

This module encapsulates all core typing test logic, statistics calculation,
keystroke handling, and state variables for an active typing session.
"""

import random
import time

from core.data.constants import (
    LANGUAGES,
    LANG_KEYS,
    MODE_CODE,
    MODE_TIME,
    MODE_WORDS,
    TIME_OPTIONS,
    WORD_OPTIONS,
)


class TypingEngine:
    """Core engine managing the state of an active typing test."""

    def __init__(self, mode, lang_idx, time_idx, word_idx):
        self.mode = mode
        self.lang_idx = lang_idx
        self.time_idx = time_idx
        self.word_idx = word_idx

        self.words = []
        self.target_text = ""
        self.input_chars = []  # list of typed chars (including corrections)
        self.char_idx = 0
        self.correct_chars = 0
        self.incorrect_chars = 0
        self.total_keystrokes = 0
        self.start_time = None
        self.wpm_samples = []
        self.test_finished = False

        self._last_sample_time = 0
        self._last_sample_correct = 0

        # Final calculated statistics
        self.final_wpm = 0
        self.final_accuracy = 0
        self.final_raw_wpm = 0
        self.final_time = 0

        self.start_test()

    def get_time_limit(self):
        """Return the time limit in seconds for the current session."""
        return TIME_OPTIONS[self.time_idx]

    def get_word_limit(self):
        """Return the target word limit for the current session."""
        return WORD_OPTIONS[self.word_idx]

    def _get_word_list(self):
        lang = LANG_KEYS[self.lang_idx]
        return LANGUAGES.get(lang, LANGUAGES["english"])

    def _generate_words(self, count):
        word_list = self._get_word_list()
        return random.choices(word_list, k=count)

    def start_test(self):
        """Initialize or reset the typing test state."""
        self.test_finished = False
        self.input_chars = []
        self.char_idx = 0
        self.correct_chars = 0
        self.incorrect_chars = 0
        self.total_keystrokes = 0
        self.start_time = None
        self.wpm_samples = []
        self._last_sample_time = 0
        self._last_sample_correct = 0

        if self.mode == MODE_CODE:
            self.words = self._generate_words(30)
        elif self.mode == MODE_WORDS:
            self.words = self._generate_words(self.get_word_limit())
        else:
            # For time mode, generate plenty of words
            self.words = self._generate_words(200)

        # Build the flat target string — flatten newlines to spaces
        # so code snippets don't break word-wrapping
        cleaned = [w.replace("\n", " ") for w in self.words]
        if self.mode == MODE_CODE:
            self.target_text = "  ".join(cleaned)
        else:
            self.target_text = " ".join(cleaned)

    def count_completed_words(self):
        """Count how many fully completed words have been typed.

        A word is only considered complete when the space after it has been typed.
        This prevents the test from ending before the last word is finished.
        """
        typed_text = "".join(self.input_chars[:self.char_idx])
        return typed_text.count(" ")

    def handle_input(self, key):
        """Process a single keystroke during the test.

        Returns True if the test is still running, or False if the test finished
        or was canceled.
        """
        if key == "ESC":
            return False

        if key is None:
            # Timeout tick — check time limit
            if self.mode == MODE_TIME and self.start_time:
                elapsed = time.time() - self.start_time
                if elapsed >= self.get_time_limit():
                    self.finish_test()
                    return False
            return True

        # Ignore arrow keys and other special keys
        if key.startswith("ESC") or key in ("UP", "DOWN", "LEFT", "RIGHT"):
            return True

        # Start timer on first real keystroke
        if self.start_time is None:
            self.start_time = time.time()
            self._last_sample_time = self.start_time
            self._last_sample_correct = 0

        self.total_keystrokes += 1

        if key in ("\x7f", "\x08"):
            # Backspace
            if self.char_idx > 0:
                self.char_idx -= 1
                if self.char_idx < len(self.input_chars):
                    # Re-evaluate correct/incorrect
                    removed = self.input_chars[self.char_idx]
                    target_ch = (
                        self.target_text[self.char_idx]
                        if self.char_idx < len(self.target_text)
                        else ""
                    )
                    if removed == target_ch:
                        self.correct_chars -= 1
                    else:
                        self.incorrect_chars -= 1
                    self.input_chars.pop(self.char_idx)
        elif len(key) == 1 and (key.isprintable() or key == "\t"):
            # Normal character
            if self.char_idx < len(self.target_text):
                target_ch = self.target_text[self.char_idx]
                if key == target_ch:
                    self.correct_chars += 1
                else:
                    self.incorrect_chars += 1

                # Insert or replace
                if self.char_idx < len(self.input_chars):
                    self.input_chars[self.char_idx] = key
                else:
                    self.input_chars.append(key)
                self.char_idx += 1

                # Sample WPM every second
                now = time.time()
                if now - self._last_sample_time >= 1.0:
                    elapsed_since_start = now - self.start_time
                    if elapsed_since_start > 0:
                        sample_wpm = int(
                            (self.correct_chars / 5) / (elapsed_since_start / 60)
                        )
                        self.wpm_samples.append(sample_wpm)
                    self._last_sample_time = now

                # Check completion
                if self.char_idx >= len(self.target_text):
                    self.finish_test()
                    return False
                elif self.mode == MODE_WORDS:
                    done_w = self.count_completed_words()
                    if done_w >= self.get_word_limit():
                        self.finish_test()
                        return False

        # Check time limit
        if self.mode == MODE_TIME and self.start_time:
            elapsed = time.time() - self.start_time
            if elapsed >= self.get_time_limit():
                self.finish_test()
                return False

        return True

    def finish_test(self):
        """Calculate final statistics and mark test as finished."""
        self.test_finished = True
        elapsed = time.time() - self.start_time if self.start_time else 1
        self.final_time = round(elapsed, 1)
        total_typed = self.correct_chars + self.incorrect_chars
        self.final_wpm = int((self.correct_chars / 5) / (elapsed / 60)) if elapsed > 0 else 0
        self.final_raw_wpm = int((total_typed / 5) / (elapsed / 60)) if elapsed > 0 else 0
        self.final_accuracy = round(
            (self.correct_chars / total_typed * 100) if total_typed > 0 else 0,
            1,
        )

        # Add final sample
        if self.wpm_samples:
            self.wpm_samples.append(self.final_wpm)
        else:
            self.wpm_samples = [self.final_wpm]
