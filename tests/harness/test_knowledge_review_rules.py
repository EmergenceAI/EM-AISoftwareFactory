"""Review rules: knowledge pack generation, loading, and context-file injection."""

import shutil
import subprocess
from pathlib import Path

import pytest

from harness.executor import Executor
from harness.harness import Harness
from harness.knowledge import NO_REVIEW_RULES, KnowledgeEngine

FACTORY_ROOT = Path(__file__).resolve().parents[2]
REPO_CFG = {"name": "demo", "language": "python", "build_system": "uv"}
KNOWLEDGE_KEYS = {"architecture", "patterns", "conventions", "dependencies", "review_rules"}


def _pack(root: Path, files: dict) -> Path:
    d = root / "repositories" / "demo"
    d.mkdir(parents=True)
    for name, text in files.items():
        (d / name).write_text(text)
    return root


# --- KnowledgeEngine ---------------------------------------------------------

def test_loads_review_rules_when_present(tmp_path):
    root = _pack(tmp_path, {"architecture.md": "arch", "review-rules.md": "1. **I** - add a changeset"})
    k = KnowledgeEngine(str(root)).get_repository_knowledge("demo")
    assert set(k) == KNOWLEDGE_KEYS
    assert k["review_rules"] == "1. **I** - add a changeset"


def test_review_rules_empty_when_file_absent(tmp_path):
    root = _pack(tmp_path, {"architecture.md": "arch"})
    assert KnowledgeEngine(str(root)).get_repository_knowledge("demo")["review_rules"] == ""


def test_no_pack_default_includes_empty_review_rules(tmp_path):
    k = KnowledgeEngine(str(tmp_path)).get_repository_knowledge("missing")
    assert set(k) == KNOWLEDGE_KEYS
    assert k["review_rules"] == ""


def test_committed_craft_review_rules_load():
    k = KnowledgeEngine(str(FACTORY_ROOT / "knowledge")).get_repository_knowledge("craft")
    rules = k["review_rules"]
    assert rules.startswith("<!--\nAUTO-GENERATED from craft")
    assert ".changeset" in rules
    assert "## Severity (from .claude/skills/craft-review/contract.md)" in rules


# --- Context files -----------------------------------------------------------

def _harness_ctx(tmp_path, knowledge):
    h = object.__new__(Harness)  # _write_knowledge_context uses no instance state
    path = h._write_knowledge_context(knowledge, {"standards": "std"}, REPO_CFG, tmp_path)
    return path.read_text()


def _executor_ctx(tmp_path, knowledge):
    ex = Executor(tmp_path, {"workspace": {"root": str(tmp_path)}}, knowledge_engine=object())
    path = ex._create_knowledge_context_file(knowledge, "std", REPO_CFG, tmp_path)
    return path.read_text()


@pytest.mark.parametrize("write", [_harness_ctx, _executor_ctx])
def test_context_file_includes_review_rules(tmp_path, write):
    text = write(tmp_path, {"architecture": "arch", "review_rules": "RULE-I-CHANGESET"})
    assert "## Review Rules" in text
    section = text.split("## Review Rules", 1)[1].split("## Foundations Standards", 1)[0]
    assert "RULE-I-CHANGESET" in section


@pytest.mark.parametrize("write", [_harness_ctx, _executor_ctx])
@pytest.mark.parametrize("knowledge", [{"review_rules": ""}, {}])
def test_context_file_placeholder_when_no_review_rules(tmp_path, write, knowledge):
    text = write(tmp_path, knowledge)
    section = text.split("## Review Rules", 1)[1].split("## Foundations Standards", 1)[0]
    assert NO_REVIEW_RULES in section


# --- extract_knowledge.sh ----------------------------------------------------

def _git_repo(path: Path, files: dict) -> Path:
    for name, text in files.items():
        f = path / name
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text)
    git = ["git", "-c", "user.email=t@t", "-c", "user.name=t"]
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    subprocess.run(["git", "add", "-A"], cwd=path, check=True)
    subprocess.run([*git, "commit", "-qm", "init"], cwd=path, check=True)
    return path


def _extract(tmp_path: Path, src: Path, name: str) -> Path:
    factory = tmp_path / "factory"
    factory.mkdir(exist_ok=True)
    shutil.copy(FACTORY_ROOT / "extract_knowledge.sh", factory)
    subprocess.run(["bash", "extract_knowledge.sh", str(src), name], cwd=factory, check=True,
                   capture_output=True)
    return factory / "knowledge" / "repositories" / name


@pytest.mark.skipif(shutil.which("git") is None, reason="git required")
def test_extract_generates_review_rules(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    _git_repo(src, {
        "README.md": "# demo\n\n## Overview\n\ntext\n",
        "REVIEW.md": "# Review instructions\n\nBe kind.\n",
        ".claude/skills/demo-review/contract.md":
            "# Contract\n\n## Severity\n\n- `important`: breaks behaviour\n\n## Output\n\nlist\n",
        ".claude/skills/demo-review/units/api.md": "# Review rules: api\n\n1. **I** - per-row checks\n",
        ".claude/skills/demo-review/units/repo-wide.md": "# Review rules: repo-wide\n\n1. **I** - changeset\n",
    })
    out = (_extract(tmp_path, src, "demo") / "review-rules.md").read_text()
    assert out.startswith("<!--\nAUTO-GENERATED from demo")
    assert "Source commit: unknown" not in out
    assert "Be kind." in out
    assert "- `important`: breaks behaviour" in out
    assert "## Output" not in out  # only the contract's Severity section
    assert out.index("units/repo-wide.md") < out.index("units/api.md")
    assert "per-row checks" in out and "changeset" in out


@pytest.mark.skipif(shutil.which("git") is None, reason="git required")
def test_extract_without_review_sources_writes_no_review_rules(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    _git_repo(src, {"README.md": "# demo\n\n## Overview\n\ntext\n"})
    pack = _extract(tmp_path, src, "demo")
    assert (pack / "architecture.md").exists()
    assert not (pack / "review-rules.md").exists()
