from unittest.mock import patch

import pytest

from harness import cli


def test_port_requires_jira_key():
    with pytest.raises(SystemExit):
        cli.build_parser().parse_args(["port", "cross_product_analysis"])


def test_port_launches_port_workflow_in_craft():
    args = cli.build_parser().parse_args(
        ["port", "cross_product_analysis", "--jira-key", "SEMI-9", "--stop-after", "map", "--no-pr"]
    )
    with patch.object(cli, "_run_skill_with_provenance") as run:
        args.func(args)
    assert run.call_args.args[:2] == ("SEMI-9", "craft")
    kw = run.call_args.kwargs
    assert kw["skill"] == "port-workflow"
    assert kw["skill_args"] == ["cross_product_analysis"]
    assert kw["skill_options"]["jira-key"] == "SEMI-9"
    assert kw["skill_options"]["stop-after"] == "map"
    assert kw["skill_options"]["no-pr"] == ""
    assert kw["skill_options"]["em-semi-ref"] is None


def test_port_rejects_unknown_stop_after():
    with pytest.raises(SystemExit):
        cli.build_parser().parse_args(["port", "x", "--jira-key", "SEMI-9", "--stop-after", "bogus"])


def test_implement_still_uses_autonomous_implement():
    args = cli.build_parser().parse_args(["implement", "SEMI-1", "--repo", "semi"])
    with patch.object(cli, "_run_skill_with_provenance") as run, patch.object(
        cli, "_resolve_repository", return_value="semi"
    ), patch.object(cli, "load_workspace_config", return_value={}):
        args.func(args)
    assert run.call_args.args[:2] == ("SEMI-1", "semi")
    assert run.call_args.kwargs["skill"] == "autonomous-implement"
    assert run.call_args.kwargs["skill_args"] == ["SEMI-1"]
    assert run.call_args.kwargs["skill_options"] == {"branch": None}
