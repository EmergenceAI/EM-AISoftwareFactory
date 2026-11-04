from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_craft_registered():
    cfg = yaml.safe_load((ROOT / "workspace.yaml").read_text())
    craft = next(r for r in cfg["repositories"] if r["name"] == "craft")
    assert craft["path"] == "craft"
    assert craft["github"] == "EmergenceAI/craft"
    assert cfg["jira"]["component_mapping"]["Craft"] == "craft"


def test_craft_in_knowledge_sync():
    assert '"craft:$HOME/Documents/Development/craft"' in (ROOT / "sync_knowledge.sh").read_text()


def test_craft_knowledge_pack_exists():
    pack = ROOT / "knowledge/repositories/craft"
    assert {p.name for p in pack.glob("*.md")} >= {
        "architecture.md", "conventions.md", "dependencies.md", "patterns.md"
    }
