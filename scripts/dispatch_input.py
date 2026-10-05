#!/usr/bin/env python3
"""Check a patch that arrived as a workflow_dispatch input, and write it to a file.

The published app saves with one call to GitHub's API instead of a commit. The
call carries the patch as plain text, and anyone holding a token for the
repository can send any text, so the workflow treats it as untrusted input. The
text is read from the PATCH environment variable and never placed on a command
line. Only lines that match the exact format survive, and everything else
aborts the run before the database is touched.

    PATCH="$text" python3 scripts/dispatch_input.py decisions --out patch.txt
    PATCH="$text" python3 scripts/dispatch_input.py hide --out ids.txt

The output holds the cleaned lines only. Comments and blank lines are dropped.
The file is then applied by `swipe.py apply` or `hide_event.py apply`, which
repeat their own validation.
"""

import argparse
import os
import re
import sys

MAX_CHARS = 20000
MAX_LINES = 1000
MAX_LINE = 200

EVENT_ID = r"[A-Za-z0-9_.-]{1,120}"
DECISION_LINE = re.compile(rf"([imrc]):({EVENT_ID})")
HIDE_LINE = re.compile(EVENT_ID)


def clean_lines(text, pattern, render):
    """Return the validated lines, or raise ValueError naming the first bad one."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("The patch is empty.")
    if len(text) > MAX_CHARS:
        raise ValueError(f"The patch is {len(text)} characters. The limit is {MAX_CHARS}.")
    rows = text.splitlines()
    if len(rows) > MAX_LINES:
        raise ValueError(f"The patch has {len(rows)} lines. The limit is {MAX_LINES}.")
    kept = []
    for number, raw in enumerate(rows, start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if len(line) > MAX_LINE:
            raise ValueError(f"Line {number} is longer than {MAX_LINE} characters.")
        match = pattern.fullmatch(line)
        if not match:
            raise ValueError(f"Line {number} is not in the expected format.")
        kept.append(render(match))
    if not kept:
        raise ValueError("The patch holds no entries.")
    return kept


def clean_decisions(text):
    """`code:event_id` lines, with the code in lower case and no spaces."""
    return clean_lines(text, DECISION_LINE, lambda match: f"{match.group(1)}:{match.group(2)}")


def clean_hide(text):
    """One exact event ID per line."""
    return clean_lines(text, HIDE_LINE, lambda match: match.group(0))


KINDS = {"decisions": clean_decisions, "hide": clean_hide}


def main(argv=None, environ=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("kind", choices=sorted(KINDS))
    parser.add_argument("--out", required=True, help="where to write the cleaned patch")
    parser.add_argument("--env", default="PATCH", help="environment variable holding the text")
    args = parser.parse_args(argv)
    environ = os.environ if environ is None else environ
    try:
        lines = KINDS[args.kind](environ.get(args.env, ""))
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    with open(args.out, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    print(f"Accepted {len(lines)} {args.kind} line(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
