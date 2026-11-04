from pathlib import Path

from harness.executor import build_skill_prompt

CTX = Path("/r/.ctx.md")
EV = Path("/r/.harness-results/provenance-events.jsonl")


def test_implement_prompt_unchanged():
    assert build_skill_prompt("autonomous-implement", ["SEMI-1"], {"branch": None}, CTX, EV) == (
        "/autonomous-implement SEMI-1 --context-file /r/.ctx.md "
        "--provenance-file /r/.harness-results/provenance-events.jsonl"
    )


def test_implement_prompt_with_branch_keeps_old_order():
    # The old hard-coded prompt appended --branch after --provenance-file.
    p = build_skill_prompt("autonomous-implement", ["SEMI-1"], {"branch": "b1"}, CTX, EV)
    assert p.endswith("--provenance-file /r/.harness-results/provenance-events.jsonl --branch b1")


def test_port_prompt():
    p = build_skill_prompt(
        "port-workflow", ["cross_product_analysis"], {"jira-key": "SEMI-9", "em-semi-ref": None}, CTX, EV
    )
    assert p.startswith("/port-workflow cross_product_analysis --jira-key SEMI-9")
    assert "--em-semi-ref" not in p
