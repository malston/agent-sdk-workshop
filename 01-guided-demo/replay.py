"""Offline transcript replay for the guided demo.

The live demo runs the agent through the Agent SDK, which owns the loop and
calls the model -- so it needs an API key. render_transcript() re-renders a
previously captured run from a plain JSON transcript, reproducing the same
console output with no API key. Self-contained: imports no SDK, so it runs
anywhere.
"""

import json
import os
import sys

_COLOR = os.environ.get("NO_COLOR") != "1"


def load_transcript(path: str) -> list[dict]:
    """Read a captured transcript (a JSON list of events) from disk."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def events_from_message(message) -> list[dict]:
    """Convert one SDK message into transcript events for recording.

    Reads the same fields agent.py.render_message reads, so a captured
    transcript replays identically. A ResultMessage (the only one carrying
    num_turns) becomes a single result event; assistant/user messages expand
    their content blocks into text / tool_use / tool_result events.
    """
    if hasattr(message, "num_turns"):
        return [
            {
                "type": "result",
                "is_error": getattr(message, "is_error", False),
                "result": getattr(message, "result", None),
                "num_turns": message.num_turns,
                "cost": getattr(message, "total_cost_usd", None),
            }
        ]

    events: list[dict] = []
    for block in getattr(message, "content", None) or []:
        if hasattr(block, "text"):
            events.append({"type": "assistant_text", "text": block.text})
        elif hasattr(block, "name") and hasattr(block, "input"):
            events.append({"type": "tool_use", "name": block.name, "input": block.input})
        elif hasattr(block, "content"):
            events.append({"type": "tool_result", "content": block.content})
    return events


def _c(code: str) -> str:
    return code if _COLOR else ""


RESET = _c("\033[0m")
DIM = _c("\033[2m")
CYAN = _c("\033[96m")
YELLOW = _c("\033[93m")
GRAY = _c("\033[90m")


def render_transcript(events: list[dict], verbose: bool = False) -> None:
    """Render a captured transcript to the console, in order."""
    for ev in events:
        kind = ev["type"]
        if kind == "assistant_text":
            print(f"{CYAN}{ev['text']}{RESET}")
        elif kind == "tool_use" and verbose:
            inputs = ", ".join(f"{k}={v!r}" for k, v in (ev.get("input") or {}).items())
            print(f"{DIM}{YELLOW}  → calling {ev['name']}({inputs}){RESET}")
        elif kind == "tool_result" and verbose:
            text = str(ev.get("content", ""))
            if len(text) > 200:
                text = text[:200] + "…"
            print(f"{DIM}  ← tool returned: {text}{RESET}")
        elif kind == "result":
            print()
            if ev.get("is_error"):
                print(f"{YELLOW}⚠ Finished with error: {ev.get('result')}{RESET}")
            else:
                cost = ev.get("cost") or 0.0
                print(f"{GRAY}[done — {ev.get('num_turns')} turn(s), ${cost:.4f}]{RESET}")


def main(argv: list[str]) -> int:
    """Render a saved transcript file. Usage: replay.py <file.json> [--verbose]"""
    args = list(argv)
    verbose = False
    for flag in ("--verbose", "-v"):
        if flag in args:
            verbose = True
            args.remove(flag)
    if not args:
        print("usage: replay.py <transcript.json> [--verbose]")
        return 2
    render_transcript(load_transcript(args[0]), verbose=verbose)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
