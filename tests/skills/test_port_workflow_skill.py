from pathlib import Path

SK = Path(__file__).resolve().parents[2] / "skills/port-workflow"


def test_references_exist():
    for f in ["porting-model.md", "analog-trim-walkthrough.md", "platform-call-map.md", "gap-report-template.md"]:
        assert (SK / "references" / f).is_file(), f


def test_call_map_covers_required_modules():
    text = (SK / "references/platform-call-map.md").read_text()
    for m in [
        "semi_task", "FlowContext", "get_database", "get_storage_service", "post_inbox_message",
        "create_iceberg_data_view", "wf3_lot_dataset", "product_catalog", "llm_service",
        "validate_agent_sql", "knowledge_guardrails",
    ]:
        assert m in text, m


def test_gap_template_headings():
    text = (SK / "references/gap-report-template.md").read_text()
    for h in [
        "Pinned em-semi ref", "Stand-ins", "Outside write boundary",
        "Pre-existing em-semi test failures", "Evals", "Not ported",
    ]:
        assert h in text, h


def test_porting_model_carries_anti_goals():
    text = (SK / "references/porting-model.md").read_text().lower()
    for k in ["hand-edit", "customer", "auto-merg", "pin", "rewrit", "llm.complete"]:
        assert k in text, k


def _skill():
    import yaml

    text = (SK / "SKILL.md").read_text()
    fm = yaml.safe_load(text.split("---")[1])
    return text, fm


def test_frontmatter():
    _, fm = _skill()
    assert fm["name"] == "port-workflow"
    assert fm["description"]


def test_parameters_documented():
    text, _ = _skill()
    for p in ["--jira-key", "--em-semi-ref", "--target-bundle", "--stop-after", "--no-pr",
              "--branch", "--context-file", "--provenance-file"]:
        assert p in text, p


def test_every_step_emits_provenance():
    text, _ = _skill()
    for step in ["load_context", "map_workflow", "plan_shape", "create_branch", "vendor", "shims",
                 "bundle", "parity", "gap_report", "verify", "create_pr", "jira_update"]:
        assert f'"step": "{step}"' in text, step
    assert '"event": "run_complete"' in text


def test_failure_handling_covers_review_focus():
    text, _ = _skill()
    sec = text.split("## Failure handling", 1)[1]
    for k in ["unknown workflow", "pinned ref", "pre-existing", "already exists", "partial"]:
        assert k.lower() in sec.lower(), k


def test_guardrails_present():
    text, _ = _skill()
    low = text.lower()
    for k in ["git show", "never hand-edit", "llm.complete", "nojira", "customer", "never auto-merge"]:
        assert k in low, k
    for ref in ["references/porting-model.md", "references/analog-trim-walkthrough.md",
                "references/platform-call-map.md", "references/gap-report-template.md",
                "templates/vendor_workflow.sh.tmpl", "templates/test_vendor_quarantine.py.tmpl",
                "templates/test_golden.py.tmpl"]:
        assert ref in text, ref


def test_referenced_files_exist():
    import re

    text, _ = _skill()
    for rel in set(re.findall(r"(?:references|templates)/[\w.-]+", text)):
        assert (SK / rel).is_file(), rel


def test_verify_uses_verify_and_fix_gate_names():
    text, _ = _skill()
    assert "--gates linter,tests,evals,review" in text
    assert "code-review`" not in text.split("## Step 9", 1)[1].split("## Step 10", 1)[0]


def test_generating_steps_point_existing_bundles_at_failure_handling():
    text, _ = _skill()
    for step in ["## Step 4", "## Step 5", "## Step 6", "## Step 7"]:
        body = text.split(step, 1)[1].split("\n## Step", 1)[0]
        assert "existing bundle" in body.lower(), step


def test_pre_existing_failures_need_evidence():
    text, _ = _skill()
    sec = text.split("## Failure handling", 1)[1].lower()
    assert "git archive" in sec
    assert "importerror" in sec and "collection error" in sec
    assert "in code this workflow uses" not in sec
