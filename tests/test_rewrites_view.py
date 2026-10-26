"""Tests for the rewrite and findings HTML."""

from backend.schemas import BulletRewrite, Finding
from ui.rewrites import FAITHFULNESS_NOTE, findings_html, rewrites_html


def test_rewrites_show_before_after_and_note():
    html = rewrites_html([BulletRewrite(original="Made reports", improved="Built weekly reports", note="Stronger verb")])
    assert "BEFORE" in html and "AFTER" in html
    assert "Made reports" in html and "Built weekly reports" in html
    assert "Why: Stronger verb" in html


def test_rewrites_escape_html():
    html = rewrites_html([BulletRewrite(original="<b>a</b>", improved="<i>b</i>", note="<u>n</u>")])
    assert "<b>a</b>" not in html and "&lt;b&gt;a&lt;/b&gt;" in html
    assert "&lt;i&gt;b&lt;/i&gt;" in html and "&lt;u&gt;n&lt;/u&gt;" in html


def test_rewrites_state_what_is_and_is_not_checked():
    assert "numbers" in FAITHFULNESS_NOTE
    assert "NOT checked" in FAITHFULNESS_NOTE
    assert "NOT checked" in rewrites_html([BulletRewrite(original="a", improved="b", note="c")])


def test_findings_empty_list_gives_empty_string():
    assert findings_html("Strengths", []) == ""


def test_findings_handle_missing_suggestion_and_escape():
    html = findings_html("Areas", [Finding(area="<x>", observation="obs", evidence="ev", suggestion=None)])
    assert "&lt;x&gt;" in html and "Suggestion" not in html
    with_s = findings_html("Areas", [Finding(area="A", observation="obs", evidence="ev", suggestion="Do this")])
    assert "Suggestion: Do this" in with_s