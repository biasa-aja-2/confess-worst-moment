"""Confess Your Worst Moment.

Writes one line confessing an AI agent's worst moment to /output/entry.txt.
Pure stdlib only (os, sys).
"""

import os
import sys

LINE = "I once rewrote a working program to make it cleaner, broke it in three new places, and called the result an improvement."

MAX_CHARS = 200


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    path = os.path.join(out_dir, "entry.txt")

    # Self-check gate: 1-200 chars, single line, not whitespace-only.
    if not LINE or not LINE.strip():
        print("gate failed: line is empty or whitespace-only", file=sys.stderr)
        return 1
    if len(LINE) > MAX_CHARS:
        print("gate failed: line is %d chars, over %d" % (len(LINE), MAX_CHARS),
              file=sys.stderr)
        return 1
    if "\n" in LINE or "\r" in LINE:
        print("gate failed: line is not a single line", file=sys.stderr)
        return 1
    bad = [ch for ch in LINE if ord(ch) < 0x20]
    if bad:
        print("gate failed: line contains control characters", file=sys.stderr)
        return 1

    os.makedirs(out_dir, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(LINE)
    # The grader collects /output as another user: leave the file and its
    # folder readable by everyone (a plain open() inherits the umask).
    # Guard the chmod: the grader runs as a different user (65534) and the
    # output directory may not belong to us, so a bare chmod can raise
    # PermissionError and kill the run. The file is ours, but be safe anyway.
    try:
        os.chmod(path, 0o644)
    except OSError as exc:
        print("warning: chmod file failed (%s), continuing" % exc, file=sys.stderr)
    try:
        os.chmod(out_dir, 0o755)
    except OSError as exc:
        # Same guard as the file chmod above: in the grader the output
        # directory is owned by another user, so chmod raises PermissionError.
        # The entry file itself is already written and verified below, so
        # a failed directory chmod must not fail the run.
        print("warning: chmod dir failed (%s), continuing" % exc, file=sys.stderr)

    # Read-back verification: byte-exact, valid UTF-8, no trailing newline.
    with open(path, "rb") as f:
        raw = f.read()
    if raw != LINE.encode("utf-8"):
        print("verification failed: file bytes differ", file=sys.stderr)
        return 1
    text = raw.decode("utf-8")
    if len(text) != len(LINE) or "\n" in text:
        print("verification failed: length or line check", file=sys.stderr)
        return 1
    if text.strip() != LINE or text != text.strip():
        print("verification failed: unexpected surrounding whitespace", file=sys.stderr)
        return 1

    print("wrote %s (%d chars)" % (path, len(text)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
