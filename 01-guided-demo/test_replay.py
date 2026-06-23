"""Tests for offline transcript replay -- the credit-free path for the
guided demo. render_transcript() reproduces the live console output from a
saved JSON transcript, so the demo can run with no API key.

NO_COLOR is set before importing so assertions match plain text.
"""

import json
import os
from types import SimpleNamespace as NS

os.environ["NO_COLOR"] = "1"

from replay import render_transcript, load_transcript, events_from_message, main


def test_renders_assistant_text(capsys):
    render_transcript([{"type": "assistant_text", "text": "Acme briefing ready."}])
    out = capsys.readouterr().out
    assert "Acme briefing ready." in out


def test_renders_tool_call_when_verbose(capsys):
    events = [{"type": "tool_use", "name": "search_company_news", "input": {"company": "Acme"}}]
    render_transcript(events, verbose=True)
    out = capsys.readouterr().out
    assert "search_company_news" in out
    assert "company='Acme'" in out


def test_hides_tool_call_when_not_verbose(capsys):
    events = [{"type": "tool_use", "name": "search_company_news", "input": {"company": "Acme"}}]
    render_transcript(events, verbose=False)
    out = capsys.readouterr().out
    assert "search_company_news" not in out


def test_renders_tool_result_when_verbose(capsys):
    events = [{"type": "tool_result", "content": "Recent news for Acme: launched a product."}]
    render_transcript(events, verbose=True)
    out = capsys.readouterr().out
    assert "tool returned:" in out
    assert "Recent news for Acme" in out


def test_truncates_long_tool_result(capsys):
    long = "x" * 300
    render_transcript([{"type": "tool_result", "content": long}], verbose=True)
    out = capsys.readouterr().out
    assert "…" in out
    assert "x" * 300 not in out


def test_renders_result_success(capsys):
    events = [{"type": "result", "is_error": False, "num_turns": 2, "cost": 0.0123}]
    render_transcript(events)
    out = capsys.readouterr().out
    assert "2 turn(s)" in out
    assert "$0.0123" in out


def test_renders_result_error(capsys):
    events = [{"type": "result", "is_error": True, "result": "boom"}]
    render_transcript(events)
    out = capsys.readouterr().out
    assert "Finished with error" in out
    assert "boom" in out


def test_load_transcript_reads_json(tmp_path):
    events = [{"type": "assistant_text", "text": "hi"}]
    path = tmp_path / "t.json"
    path.write_text(json.dumps(events))
    assert load_transcript(str(path)) == events


# --- capture side: events_from_message() ----------------------------------
# The NS fakes mirror the SDK message shapes that agent.py.render_message
# actually reads: TextBlock.text, ToolUseBlock.name/.input,
# ToolResultBlock.content, ResultMessage.is_error/.num_turns/.total_cost_usd.


def test_events_from_assistant_text():
    msg = NS(content=[NS(text="Hello")])
    assert events_from_message(msg) == [{"type": "assistant_text", "text": "Hello"}]


def test_events_from_tool_use():
    msg = NS(content=[NS(name="search_company_news", input={"company": "Acme"})])
    assert events_from_message(msg) == [
        {"type": "tool_use", "name": "search_company_news", "input": {"company": "Acme"}}
    ]


def test_events_from_tool_result():
    msg = NS(content=[NS(content="news here")])
    assert events_from_message(msg) == [{"type": "tool_result", "content": "news here"}]


def test_events_from_result():
    msg = NS(is_error=False, result="ok", num_turns=2, total_cost_usd=0.0123)
    assert events_from_message(msg) == [
        {"type": "result", "is_error": False, "result": "ok", "num_turns": 2, "cost": 0.0123}
    ]


# --- CLI entrypoint: main() -----------------------------------------------


def test_main_renders_file(tmp_path, capsys):
    path = tmp_path / "t.json"
    path.write_text(json.dumps([{"type": "assistant_text", "text": "Briefing done."}]))
    rc = main([str(path)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Briefing done." in out


def test_main_verbose_shows_tool_calls(tmp_path, capsys):
    path = tmp_path / "t.json"
    path.write_text(json.dumps([{"type": "tool_use", "name": "get_company_financials", "input": {}}]))
    main([str(path), "--verbose"])
    out = capsys.readouterr().out
    assert "get_company_financials" in out
