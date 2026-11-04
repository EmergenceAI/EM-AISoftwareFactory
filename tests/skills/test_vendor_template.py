"""Fills templates/vendor_workflow.sh.tmpl against a throwaway em-semi repo and runs it."""

import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest

TEMPLATE = Path(__file__).resolve().parents[2] / "skills/port-workflow/templates/vendor_workflow.sh.tmpl"


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True, text=True).stdout.strip()


@dataclass
class Run:
    returncode: int
    stderr: str
    vendor: Path
    vendor_tests: Path


@pytest.fixture
def em_semi(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "em-semi"
    (repo / "workflow/app/demo").mkdir(parents=True)
    (repo / "workflow/tests/demo").mkdir(parents=True)
    (repo / "workflow/app/demo/flow.py").write_text("from app.flows.base import semi_flow\n")
    (repo / "workflow/app/demo/calc.py").write_text(
        "from common_semi.observe import get_logger\nfrom app.demo.util import f\n"
    )
    (repo / "workflow/app/demo/util.py").write_text("def f():\n    return 1\n")
    (repo / "workflow/tests/demo/test_calc.py").write_text("from app.demo.calc import f\n")
    (repo / "workflow/tests/demo/__init__.py").write_text("")
    (repo / "workflow/tests/demo/test_more.py").write_text("from tests.demo.test_calc import f\n")
    _git(tmp_path, "init", "-q", str(repo))
    _git(repo, "add", ".")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "init")
    return repo, _git(repo, "rev-parse", "HEAD")


@pytest.fixture
def render_vendor(tmp_path: Path, em_semi):
    repo, sha = em_semi
    bundle = tmp_path / "craft/bundles/demo"
    (bundle / "job/scripts").mkdir(parents=True)
    _git(tmp_path, "init", "-q", str(tmp_path / "craft"))

    def run(*, ref: str | None = None, em_semi_path: Path | None = None,
            rewrites: list[str] | None = None, excluded: str = r"/flow\.py$",
            src_roots: str = "workflow/app/demo", test_roots: str = "workflow/tests/demo",
            vendor_pkg: str = "craft_demo.vendor") -> Run:
        script = TEMPLATE.read_text()
        for token, value in {
            "{{EM_SEMI_REF}}": ref or sha,
            "{{SRC_ROOTS}}": src_roots,
            "{{TEST_ROOTS}}": test_roots,
            "{{EXCLUDED_REGEX}}": excluded,
            "{{VENDOR_PKG}}": vendor_pkg,
            "{{IMPORT_REWRITES}}": "\n".join(rewrites or []),
        }.items():
            script = script.replace(token, value)
        path = bundle / "job/scripts/vendor_workflow.sh"
        path.write_text(script)
        proc = subprocess.run(
            ["bash", str(path)], capture_output=True, text=True,
            env={"EM_SEMI": str(em_semi_path or repo), "PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin"},
        )
        return Run(proc.returncode, proc.stderr, bundle / "job/src/craft_demo/vendor", bundle / "job/tests/vendor")

    return run


def test_template_has_no_unfilled_tokens_after_render(render_vendor):
    out = render_vendor()
    assert out.returncode == 0, out.stderr
    assert "{{" not in (out.vendor.parents[2] / "scripts/vendor_workflow.sh").read_text()


def test_vendor_copies_pinned_tree_and_excludes_flow(render_vendor):
    out = render_vendor()
    assert out.returncode == 0, out.stderr
    assert (out.vendor / "demo/calc.py").is_file()
    assert (out.vendor / "demo/util.py").is_file()
    assert not (out.vendor / "demo/flow.py").exists()
    assert (out.vendor_tests / "demo/test_calc.py").is_file()


def test_vendor_rewrites_app_imports_into_vendor_package(render_vendor):
    out = render_vendor()
    text = (out.vendor / "demo/calc.py").read_text()
    assert "from craft_demo.vendor.demo.util import f" in text


def test_vendor_applies_platform_rewrites_first(render_vendor):
    out = render_vendor(rewrites=[r"s{^from common_semi\.observe import }{from craft_demo.vendor._observe import };"])
    assert out.returncode == 0, out.stderr
    assert "from craft_demo.vendor._observe import get_logger" in (out.vendor / "demo/calc.py").read_text()


def test_vendor_keeps_shims_on_rerun(render_vendor):
    assert render_vendor().returncode == 0
    out = render_vendor()
    (out.vendor / "_observe.py").write_text("# shim\n")
    (out.vendor / "demo/stale.py").write_text("# removed upstream\n")
    out = render_vendor()
    assert out.returncode == 0, out.stderr
    assert (out.vendor / "_observe.py").read_text() == "# shim\n"
    assert not (out.vendor / "demo/stale.py").exists()


def test_vendor_fails_on_bad_ref_without_writing(render_vendor):
    out = render_vendor(ref="deadbeef")
    assert out.returncode != 0
    assert "deadbeef" in out.stderr
    assert not out.vendor.exists()


def test_vendor_fails_without_em_semi_checkout(render_vendor, tmp_path):
    out = render_vendor(em_semi_path=tmp_path / "missing")
    assert out.returncode != 0
    assert not out.vendor.exists()


def test_vendor_fails_on_missing_test_root_without_writing(render_vendor):
    out = render_vendor(test_roots="workflow/tests/nope")
    assert out.returncode != 0
    assert "workflow/tests/nope" in out.stderr
    assert not out.vendor.exists()


def test_vendor_fails_on_missing_src_root_among_several(render_vendor):
    out = render_vendor(src_roots="workflow/app/demo workflow/app/gone")
    assert out.returncode != 0
    assert "workflow/app/gone" in out.stderr
    assert not out.vendor.exists()


def test_vendor_with_no_test_roots_warns_and_vendors_only_sources(render_vendor):
    out = render_vendor(test_roots="")
    assert out.returncode == 0, out.stderr
    assert "0 test files" in out.stderr
    assert (out.vendor / "demo/calc.py").is_file()
    assert not any(out.vendor_tests.rglob("*.py"))
    assert not (out.vendor / "workflow").exists()


def test_vendor_with_empty_excluded_regex_excludes_nothing(render_vendor):
    out = render_vendor(excluded="")
    assert out.returncode == 0, out.stderr
    assert (out.vendor / "demo/flow.py").is_file()


def test_vendor_refuses_package_not_ending_in_vendor(render_vendor):
    first = render_vendor()
    (first.vendor.parent / "nodes.py").write_text("# hand-written\n")
    out = render_vendor(vendor_pkg="craft_demo")
    assert out.returncode != 0
    assert (first.vendor.parent / "nodes.py").is_file()


def test_vendor_rewrites_test_tree_imports_and_drops_test_inits(render_vendor):
    out = render_vendor()
    assert out.returncode == 0, out.stderr
    assert "from vendor.demo.test_calc import f" in (out.vendor_tests / "demo/test_more.py").read_text()
    assert not (out.vendor_tests / "demo/__init__.py").exists()


def test_quarantine_skeleton_finds_runner_requirements(tmp_path):
    import runpy

    craft = tmp_path / "craft"
    req = craft / "compute-plane-python/python-runner/requirements.txt"
    req.parent.mkdir(parents=True)
    req.write_text("numpy==2.0\nscikit-learn==1.5\n")
    tests_dir = craft / "bundles/demo/job/tests"
    tests_dir.mkdir(parents=True)
    rendered = tests_dir / "test_vendor_is_self_contained.py"
    rendered.write_text((TEMPLATE.parent / "test_vendor_quarantine.py.tmpl").read_text().replace("{{PKG}}", "craft_demo"))
    module = runpy.run_path(str(rendered))
    assert module["_REQUIREMENTS"] == req
    assert {"numpy", "sklearn", "craft_demo"} <= module["PERMITTED_ROOTS"]


@pytest.mark.parametrize("name", ["test_vendor_quarantine.py.tmpl", "test_golden.py.tmpl"])
def test_test_skeletons_compile_once_filled(name):
    text = (TEMPLATE.parent / name).read_text()
    for token, value in {"{{PKG}}": "craft_demo", "{{NODES}}": '"ingest", "report"'}.items():
        text = text.replace(token, value)
    assert "{{" not in text
    compile(text, name, "exec")
