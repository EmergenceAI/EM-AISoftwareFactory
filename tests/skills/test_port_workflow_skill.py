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
