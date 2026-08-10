#!/usr/bin/env python3
"""
Harness CLI — Workspace-level orchestration for the Dark Factory.

Commands
--------
  implement   Implement a Jira issue (skill mode or harness mode)
  watch       Tail live events for an active run
  queue       Show active + queued runs
  cancel      Cancel an active run
  resume      Resume a run from its last checkpoint
  circuit-breaker  Show or reset gate circuit breaker state
  tui         Launch the terminal dashboard
  server      Start the observability server
  cost        Show cost breakdown by repo / step
  runs        List recent runs with filters
  provenance  Query provenance logs and export RL datasets
  sprint      Execute multiple issues from a sprint
  knowledge   View repository knowledge
  test        Smoke-test harness components

Usage examples
--------------
  python -m harness implement ABI-123
  python -m harness watch ABI-123
  python -m harness queue
  python -m harness cancel ABI-123
  python -m harness resume run_20240726_abc123
  python -m harness circuit-breaker status
  python -m harness circuit-breaker reset linter
  python -m harness tui
  python -m harness server
  python -m harness cost --days 7
  python -m harness runs --repo runtime --outcome failed
  python -m harness provenance stats
  python -m harness provenance export --output rl_dataset.json
"""

import json
import sys
import argparse
import time
from pathlib import Path
import yaml
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from harness.router import Router
from harness.executor import Executor
from harness.knowledge import KnowledgeEngine
from harness import jira_mcp

_FACTORY_ROOT   = Path(__file__).parent.parent
_PROVENANCE_DIR = _FACTORY_ROOT / "provenance"


def load_workspace_config() -> dict:
    """Load workspace.yaml configuration."""
    workspace_file = Path(__file__).parent.parent / 'workspace.yaml'

    if not workspace_file.exists():
        print(f"❌ Error: workspace.yaml not found at {workspace_file}")
        print("   Create workspace.yaml with repository configuration first.")
        sys.exit(1)

    with open(workspace_file) as f:
        return yaml.safe_load(f)


def _resolve_repository(args, workspace_config) -> str:
    """Route issue to a repository unless --repo was specified explicitly."""
    if args.repo:
        return args.repo

    router = Router(workspace_config)
    component = jira_mcp.get_issue_component(args.issue_key)
    repository = jira_mcp.get_repository_for_issue(
        args.issue_key,
        workspace_config.get('jira', {}).get('component_mapping', {}),
    )
    if not repository:
        repository = 'runtime'
        print(f"🎯 Repository: {repository} (default — unknown component)")
    else:
        print(f"🎯 Repository: {repository} (routed from {component})")
    return repository


def cmd_implement(args):
    """Implement a single Jira issue with workspace-level orchestration."""

    print(f"\n{'='*60}")
    print(f"AI Software Factory - Workspace Harness")
    skill_mode = True  # always skill mode — harness mode removed in this branch
    mode = "skill"
    print(f"Mode: {mode}")
    print(f"{'='*60}\n")

    workspace_config = load_workspace_config()
    factory_root = Path(__file__).parent.parent

    print(f"📋 Issue: {args.issue_key}")
    repository = _resolve_repository(args, workspace_config)
    print()

    if True:
        # ── Skill mode with provenance monitoring ─────────────────────────
        executor = Executor(factory_root, workspace_config)
        result = executor.execute_single_repo(
            issue_key=args.issue_key,
            repository=repository,
        )
        print(result.summary() if hasattr(result, 'summary') else str(result))
        sys.exit(0 if result.success else 1)


def cmd_multi_repo(args):
    """Implement issue across multiple repositories."""

    print(f"\n{'='*60}")
    print(f"AI Software Factory - Multi-Repo Orchestrator")
    print(f"{'='*60}\n")

    # Load configuration
    workspace_config = load_workspace_config()
    factory_root = Path(__file__).parent.parent

    # Fetch Jira issue
    print(f"📋 Fetching issue: {args.issue_key}")
    issue = get_jira_issue(args.issue_key)
    print(f"   Summary: {issue['summary']}\n")

    # Determine affected repositories
    if args.repos:
        repositories = args.repos.split(',')
        print(f"🎯 Repositories: {', '.join(repositories)} (explicit)")
    else:
        router = Router(workspace_config)
        repositories = router.get_affected_repositories(issue)
        print(f"🎯 Repositories: {', '.join(repositories)} (auto-detected)")

    print()

    # Initialize executor
    executor = Executor(factory_root, workspace_config)

    # Execute across repositories
    result = executor.execute_multi_repo(
        issue_key=args.issue_key,
        repositories=repositories
    )

    # Print summary
    print(result.summary())

    # Exit with appropriate code
    sys.exit(0 if result.overall_success else 1)


def cmd_provenance(args):
    """Query provenance logs and export RL datasets."""
    from harness.provenance import ProvenanceLogger

    factory_root = Path(__file__).parent.parent
    prov_dir = factory_root / "provenance"

    if not prov_dir.exists():
        print("No provenance data found. Harness mode is the default; no --harness flag needed.")
        sys.exit(1)

    logger = ProvenanceLogger(prov_dir)

    if args.sub == "stats":
        print(f"\n{'='*60}")
        print("Provenance Statistics")
        print(f"{'='*60}\n")

        success_rate = logger.success_rate()
        avg_attempts = logger.avg_attempts_to_pass()
        gate_failures = logger.gate_failure_rates()

        print(f"  Success rate    : {success_rate*100:.1f}%")
        print(f"  Avg gate attempts: {avg_attempts:.2f}")
        print()
        print("  Gate failure rates:")
        for gate, rate in sorted(gate_failures.items(), key=lambda x: -x[1]):
            bar = "█" * int(rate * 20)
            print(f"    {gate:<14} {rate*100:5.1f}%  {bar}")
        print()

    elif args.sub == "export":
        output = Path(args.output)
        n = logger.export_rl_dataset(output)
        print(f"✅ Exported {n} trajectories → {output}")

    elif args.sub == "runs":
        runs_dir = prov_dir / "runs"
        summaries = sorted(runs_dir.glob("*.summary.json"), reverse=True)
        print(f"\n{'='*60}")
        print(f"Recent Runs ({len(summaries)} total)")
        print(f"{'='*60}\n")
        import json
        for f in summaries[:20]:
            s = json.loads(f.read_text())
            icon = {"success": "✅", "partial": "⚠️ ", "failed": "❌"}.get(s["overall_outcome"], "?")
            print(f"  {icon}  {s['run_id']}  {s['issue_key']:<12}  {s['repository']:<14}  "
                  f"gates:{s['gate_attempts']}  reward:{s['reward']:.1f}")
        print()


def cmd_sprint(args):
    """Execute multiple issues from a sprint (delegates to /autonomous-sprint)."""

    print(f"\n{'='*60}")
    print(f"AI Software Factory - Sprint Orchestrator")
    print(f"{'='*60}\n")

    print("🔄 Delegating to /autonomous-sprint skill...")
    print(f"   JQL: {args.jql}\n")

    # TODO: This should invoke /autonomous-sprint skill with JQL
    # For now, just show what would happen

    print("⚠️  Sprint orchestration via CLI not yet implemented.")
    print("   Use /autonomous-sprint skill directly instead:")
    print(f"   /autonomous-sprint --jql \"{args.jql}\"")

    sys.exit(1)


def cmd_knowledge(args):
    """Display repository knowledge."""

    workspace_config = load_workspace_config()
    factory_root = Path(__file__).parent.parent

    # Initialize knowledge engine
    knowledge_root = factory_root / 'knowledge'
    knowledge_engine = KnowledgeEngine(str(knowledge_root))

    if args.list:
        # List available repositories
        repos = workspace_config.get('repositories', [])
        print(f"\n{'='*60}")
        print("Available Repositories")
        print(f"{'='*60}\n")
        for repo in repos:
            print(f"  - {repo['name']}: {repo.get('display_name', repo['name'])}")
        print()
        return

    if not args.repo:
        print("❌ Error: --repo required (or use --list to see available repos)")
        sys.exit(1)

    # Load knowledge for repository
    print(f"\n{'='*60}")
    print(f"Repository Knowledge: {args.repo}")
    print(f"{'='*60}\n")

    knowledge = knowledge_engine.get_repository_knowledge(args.repo)

    for category, content in knowledge.items():
        print(f"\n## {category.upper()}")
        print(f"{'-'*60}")
        if content:
            # Show first 500 chars
            preview = content[:500] + ('...' if len(content) > 500 else '')
            print(preview)
        else:
            print("(No content available)")

    print()


def cmd_test(args):
    """Test harness components without execution."""

    print(f"\n{'='*60}")
    print(f"Orchestrator Component Test")
    print(f"{'='*60}\n")

    workspace_config = load_workspace_config()
    factory_root = Path(__file__).parent.parent

    # Test router
    print("Testing Router...")
    router = Router(workspace_config)
    component = jira_mcp.get_issue_component(args.issue_key)
    test_issue = {
        'key': args.issue_key,
        'components': [component] if component else [],
        'description': '',
        'labels': [],
    }
    repo = router.route_issue(test_issue)
    print(f"  ✅ Routed {args.issue_key} → {repo}\n")

    # Test knowledge engine
    print("Testing Knowledge Engine...")
    knowledge_root = factory_root / 'knowledge'
    knowledge_engine = KnowledgeEngine(str(knowledge_root))
    knowledge = knowledge_engine.get_repository_knowledge(repo)
    print(f"  ✅ Loaded knowledge for {repo}:")
    for category in knowledge.keys():
        length = len(knowledge[category])
        print(f"     - {category}: {length} chars")
    print()

    # Test foundations
    print("Testing Foundations Standards...")
    foundations = knowledge_engine.get_foundations_guidance('standards')
    if foundations:
        print(f"  ✅ Loaded foundations standards: {len(foundations.get('standards', ''))} chars")
    else:
        print(f"  ⚠️  No foundations standards found")
    print()

    print("✅ All component tests passed!\n")


def _find_run_id(query: str) -> Optional[str]:
    """
    Resolve a run_id or issue_key to a concrete run_id from the provenance index.
    Returns the most recent matching run_id, or None.
    """
    index = _PROVENANCE_DIR / "index.jsonl"
    if not index.exists():
        return None
    matches = []
    for line in index.read_text().splitlines():
        try:
            s = json.loads(line)
        except json.JSONDecodeError:
            continue
        if s.get("run_id") == query or s.get("issue_key") == query:
            matches.append(s)
    if not matches:
        return None
    return matches[-1]["run_id"]  # most recent


def cmd_watch(args):
    """Tail live events for an active run (by run_id or issue_key)."""
    run_id = _find_run_id(args.target)
    if not run_id:
        print(f"❌  No run found for '{args.target}'")
        sys.exit(1)

    run_file = _PROVENANCE_DIR / "runs" / f"{run_id}.jsonl"
    if not run_file.exists():
        print(f"❌  Provenance file not found: {run_file}")
        sys.exit(1)

    print(f"👀  Watching {run_id}  (Ctrl-C to stop)\n")
    with open(run_file) as fh:
        # Print history
        for line in fh:
            _print_event(line)
        # Tail
        while True:
            line = fh.readline()
            if line:
                _print_event(line)
                if '"event": "run_end"' in line or '"event": "error"' in line:
                    print("\n✅  Run finished.")
                    break
            else:
                try:
                    time.sleep(0.5)
                except KeyboardInterrupt:
                    break


def _print_event(line: str) -> None:
    """Pretty-print a single provenance JSONL line."""
    try:
        e = json.loads(line.strip())
    except json.JSONDecodeError:
        return
    ev = e.get("event", "?")
    ts = e.get("timestamp", "")[:19].replace("T", " ")
    if ev == "step":
        icon = "✅" if e.get("success") else "❌"
        cost = f"  ${e.get('cost_usd', 0):.4f}" if e.get("cost_usd") else ""
        print(f"  {icon} [{ts}] step:{e.get('step')}  {e.get('duration_ms', 0)/1000:.1f}s{cost}")
    elif ev == "gate":
        icon = "✅" if e.get("passed") else "❌"
        flaky = "  ⚡flaky" if e.get("flaky") else ""
        print(f"  {icon} [{ts}] gate:{e.get('gate')} att#{e.get('attempt')}{flaky}")
    elif ev == "gate_loop_complete":
        icon = "✅" if e.get("passed") else "⚠️ "
        print(f"  {icon} [{ts}] gate_loop: passed={e.get('passed')} attempts={e.get('attempts')}")
    elif ev == "run_end":
        print(f"\n  🏁 [{ts}] run_end: outcome={e.get('overall_outcome')}  cost=${e.get('cost_usd',0):.4f}")
    elif ev == "error":
        print(f"  ❌ [{ts}] error: {e.get('error', '')[:120]}")


def cmd_queue(args):
    """Show active and queued runs."""
    # Try server API first
    try:
        import urllib.request
        port = 8089
        with urllib.request.urlopen(f"http://localhost:{port}/api/queue", timeout=2) as r:
            data = json.loads(r.read())
        active  = data.get("active", [])
        waiting = data.get("waiting", [])
    except Exception:
        active, waiting = [], []

    if not active and not waiting:
        print("No active or queued runs.")
        return

    print(f"\n{'='*50}")
    print(f"Active ({len(active)}):")
    for r in active:
        print(f"  🔄  {r.get('run_id','?')[:20]}  {r.get('issue_key','?')}  {r.get('repository','?')}")

    if waiting:
        print(f"\nWaiting ({len(waiting)}):")
        for r in waiting:
            print(f"  ⏳  {r.get('run_id','?')[:20]}  {r.get('issue_key','?')}  {r.get('repository','?')}")
    print()


def cmd_cancel(args):
    """Cancel an active run."""
    run_id = _find_run_id(args.target) or args.target
    try:
        import urllib.request
        req = urllib.request.Request(
            f"http://localhost:8089/api/runs/{run_id}/cancel",
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=3) as r:
            result = json.loads(r.read())
        print(f"✅  Cancelled: {result}")
    except Exception as e:
        print(f"❌  Could not cancel via server ({e}). Is the server running?")
        print("    Start it with: python -m harness server")


def cmd_resume(args):
    """Resume a run from its checkpoint."""
    run_id = args.run_id
    index  = _PROVENANCE_DIR / "index.jsonl"
    if not index.exists():
        print("❌  No provenance data found.")
        sys.exit(1)

    # Find the run in the index to get issue_key + repo
    match = None
    for line in index.read_text().splitlines():
        try:
            s = json.loads(line)
            if s.get("run_id") == run_id:
                match = s
        except json.JSONDecodeError:
            continue

    if not match:
        print(f"❌  Run '{run_id}' not found in provenance index.")
        sys.exit(1)

    issue_key  = match["issue_key"]
    repository = match["repository"]
    print(f"♻️   Resuming {run_id}  ({issue_key} → {repository})")

    workspace_config = load_workspace_config()
    h = Harness(
        _FACTORY_ROOT,
        workspace_config,
        max_gate_attempts=getattr(args, "max_gate_attempts", 3),
    )
    result = h.implement(issue_key, repository)
    print(result.summary())
    sys.exit(0 if result.overall_outcome in ("success", "partial") else 1)


def cmd_circuit_breaker(args):
    """Show or reset circuit breaker state."""
    from harness.circuit_breaker import CircuitBreaker
    cb = CircuitBreaker(_PROVENANCE_DIR)

    if args.cb_action == "status":
        states = cb.all_states()
        print(f"\n{'='*48}")
        print("Circuit Breaker Status")
        print(f"{'='*48}")
        for gate, st in states.items():
            state   = st.get("state", "closed")
            fails   = st.get("consecutive_failures", 0)
            icon    = "🔴 OPEN  " if state == "open" else "🟢 closed"
            opened  = st.get("opened_at", "")[:19] if state == "open" else ""
            print(f"  {icon}  {gate:<14} failures={fails}  {opened}")
        print()

    elif args.cb_action == "reset":
        gate = args.gate
        cb.reset(gate)
        print(f"✅  Circuit breaker reset: {gate} → closed (0 failures)")


def cmd_tui(args):
    """Launch the terminal dashboard."""
    try:
        from harness.tui import main as tui_main
        tui_main()
    except ImportError:
        print("❌  rich is required for the TUI. Install with: pip install rich")
        sys.exit(1)


def cmd_server(args):
    """Start the observability server (foreground)."""
    try:
        import uvicorn
        from harness.server import app
        port = int(__import__("os").environ.get("HARNESS_SERVER_PORT", "8089"))
        print(f"🌐  Dark Factory server  →  http://localhost:{port}")
        print(f"    Dashboard: http://localhost:{port}/")
        print(f"    Metrics:   http://localhost:{port}/metrics")
        uvicorn.run(app, host="0.0.0.0", port=port)
    except ImportError:
        print("❌  fastapi and uvicorn required: pip install fastapi uvicorn[standard]")
        sys.exit(1)


def cmd_cost(args):
    """Show cost breakdown by repo and step."""
    from harness.provenance import ProvenanceLogger
    import datetime

    logger   = ProvenanceLogger(_PROVENANCE_DIR)
    days     = getattr(args, "days", 7)
    cutoff   = datetime.datetime.utcnow() - datetime.timedelta(days=days)
    index    = _PROVENANCE_DIR / "index.jsonl"

    if not index.exists():
        print("No provenance data found.")
        return

    by_repo:  dict = {}
    by_step:  dict = {}
    total_cost = 0.0

    for line in index.read_text().splitlines():
        try:
            s = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts = s.get("timestamp", "")
        try:
            run_ts = datetime.datetime.fromisoformat(ts.rstrip("Z"))
        except ValueError:
            continue
        if run_ts < cutoff:
            continue

        run_cost = s.get("cost_usd", 0.0)
        repo     = s.get("repository", "unknown")
        by_repo[repo] = by_repo.get(repo, 0.0) + run_cost
        total_cost   += run_cost

        # Per-step breakdown from run events
        for event in logger.read_run(s["run_id"]):
            if event.get("event") not in ("step", "gate"):
                continue
            step_name = event.get("step") or event.get("gate") or "?"
            step_cost = event.get("cost_usd", 0.0)
            by_step[step_name] = by_step.get(step_name, 0.0) + step_cost

    print(f"\n{'='*50}")
    print(f"Cost breakdown — last {days} day(s)")
    print(f"{'='*50}")
    print(f"\nTotal: ${total_cost:.4f}\n")
    print("By repository:")
    for repo, cost in sorted(by_repo.items(), key=lambda x: -x[1]):
        print(f"  {repo:<20} ${cost:.4f}")
    print("\nBy step:")
    for step, cost in sorted(by_step.items(), key=lambda x: -x[1])[:15]:
        print(f"  {step:<30} ${cost:.4f}")
    print()


def cmd_runs(args):
    """List recent runs with optional filters."""
    index = _PROVENANCE_DIR / "index.jsonl"
    if not index.exists():
        print("No provenance data found.")
        return

    repo_filter    = getattr(args, "repo", None)
    outcome_filter = getattr(args, "outcome", None)
    limit          = getattr(args, "limit", 20)

    summaries = []
    for line in index.read_text().splitlines():
        try:
            s = json.loads(line)
        except json.JSONDecodeError:
            continue
        if repo_filter and s.get("repository") != repo_filter:
            continue
        if outcome_filter and s.get("overall_outcome") != outcome_filter:
            continue
        summaries.append(s)

    summaries = summaries[-limit:]  # most recent N

    print(f"\n{'='*80}")
    print(f"{'Run ID':<24} {'Issue':<12} {'Repo':<16} {'Outcome':<8} {'Gates':<6} {'Cost':>8}  {'Timestamp'}")
    print(f"{'='*80}")
    for s in reversed(summaries):
        icon    = {"success": "✅", "partial": "⚠️ ", "failed": "❌"}.get(s.get("overall_outcome", ""), "?")
        run_id  = s.get("run_id", "?")[:22]
        issue   = s.get("issue_key", "?")[:10]
        repo    = s.get("repository", "?")[:14]
        gates   = s.get("gate_attempts", 0)
        cost    = s.get("cost_usd", 0.0)
        ts      = s.get("timestamp", "")[:16].replace("T", " ")
        print(f"{icon} {run_id:<22} {issue:<12} {repo:<16} {gates:<6} ${cost:>7.4f}  {ts}")
    print()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='AI Software Factory - Workspace-level harness',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Implement single issue (auto-route to repository)
  python -m harness.cli implement ABI-123

  # Implement in specific repository
  python -m harness.cli implement ABI-123 --repo runtime

  # Implement across multiple repositories
  python -m harness.cli multi-repo SDK-456 --repos sdk,runtime,runtime-ui

  # Execute sprint (delegates to /autonomous-sprint)
  python -m harness.cli sprint --jql "sprint in openSprints()"

  # View repository knowledge
  python -m harness.cli knowledge --repo runtime
  python -m harness.cli knowledge --list

  # Test harness components
  python -m harness.cli test ABI-123
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # implement command
    implement = subparsers.add_parser(
        'implement',
        help='Implement single Jira issue in one repository'
    )
    implement.add_argument('issue_key', help='Jira issue key (e.g., ABI-123)')
    implement.add_argument(
        '--repo',
        help='Explicit repository name (default: auto-route)'
    )
    implement.add_argument(
        '--skill',
        action='store_true',
        default=False,
        help=(
            'Use skill mode: delegate everything to /autonomous-implement '
            'with no provenance logging. Default: harness mode.'
        ),
    )
    implement.add_argument(
        '--max-gate-attempts',
        type=int,
        default=2,
        metavar='N',
        help='Max gate loop retries in harness mode (default: 2)',
    )
    implement.add_argument(
        '--auto-merge',
        action='store_true',
        default=False,
        help='Auto-merge PR via gh CLI when all gates pass (harness mode only)',
    )
    implement.set_defaults(func=cmd_implement)

    # multi-repo command
    multi = subparsers.add_parser(
        'multi-repo',
        help='Implement issue across multiple repositories'
    )
    multi.add_argument('issue_key', help='Jira issue key')
    multi.add_argument(
        '--repos',
        help='Comma-separated repository names (default: auto-detect)'
    )
    multi.set_defaults(func=cmd_multi_repo)

    # sprint command
    sprint = subparsers.add_parser(
        'sprint',
        help='Execute multiple issues from sprint'
    )
    sprint.add_argument(
        '--jql',
        required=True,
        help='JQL query for issues'
    )
    sprint.set_defaults(func=cmd_sprint)

    # knowledge command
    knowledge = subparsers.add_parser(
        'knowledge',
        help='View repository knowledge'
    )
    knowledge.add_argument('--repo', help='Repository name')
    knowledge.add_argument('--list', action='store_true', help='List all repositories')
    knowledge.set_defaults(func=cmd_knowledge)

    # test command
    test = subparsers.add_parser(
        'test',
        help='Test harness components'
    )
    test.add_argument('issue_key', help='Jira issue key for testing')
    test.set_defaults(func=cmd_test)

    # provenance command
    prov = subparsers.add_parser(
        'provenance',
        help='Query provenance logs and export RL datasets',
    )
    prov_sub = prov.add_subparsers(dest='sub', help='Provenance sub-commands')

    prov_sub.add_parser('stats', help='Show aggregate statistics (success rate, gate failure rates)')
    prov_sub.add_parser('runs',  help='List recent runs with outcomes and rewards')

    prov_export = prov_sub.add_parser('export', help='Export RL training dataset (JSON)')
    prov_export.add_argument(
        '--output',
        default='provenance/rl_dataset.json',
        help='Output file path (default: provenance/rl_dataset.json)',
    )
    prov.set_defaults(func=cmd_provenance)

    # watch command
    watch = subparsers.add_parser('watch', help='Tail live events for a run')
    watch.add_argument('target', help='run_id or issue_key (e.g. ABI-123 or run_20240726_abc)')
    watch.set_defaults(func=cmd_watch)

    # queue command
    subparsers.add_parser('queue', help='Show active and queued runs').set_defaults(func=cmd_queue)

    # cancel command
    cancel = subparsers.add_parser('cancel', help='Cancel an active run')
    cancel.add_argument('target', help='run_id or issue_key')
    cancel.set_defaults(func=cmd_cancel)

    # resume command
    resume = subparsers.add_parser('resume', help='Resume a run from its last checkpoint')
    resume.add_argument('run_id', help='run_id to resume (e.g. run_20240726_abc123)')
    resume.set_defaults(func=cmd_resume)

    # circuit-breaker command
    cb = subparsers.add_parser('circuit-breaker', help='Show or reset gate circuit breaker state')
    cb_sub = cb.add_subparsers(dest='cb_action')
    cb_sub.add_parser('status', help='Show all circuit breaker states')
    cb_reset = cb_sub.add_parser('reset', help='Manually reset a tripped circuit breaker')
    cb_reset.add_argument('gate', choices=['linter', 'tests', 'evals', 'code-review'])
    cb.set_defaults(func=cmd_circuit_breaker)

    # tui command
    subparsers.add_parser('tui', help='Launch the terminal dashboard').set_defaults(func=cmd_tui)

    # server command
    subparsers.add_parser('server', help='Start the observability server (foreground)').set_defaults(func=cmd_server)

    # cost command
    cost_cmd = subparsers.add_parser('cost', help='Show cost breakdown by repo and step')
    cost_cmd.add_argument('--days', type=int, default=7, help='Look-back window in days (default: 7)')
    cost_cmd.set_defaults(func=cmd_cost)

    # runs command
    runs_cmd = subparsers.add_parser('runs', help='List recent runs with optional filters')
    runs_cmd.add_argument('--repo', help='Filter by repository name')
    runs_cmd.add_argument('--outcome', choices=['success', 'partial', 'failed'], help='Filter by outcome')
    runs_cmd.add_argument('--limit', type=int, default=20, help='Maximum rows to show (default: 20)')
    runs_cmd.set_defaults(func=cmd_runs)

    # Parse and execute
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    args.func(args)


if __name__ == '__main__':
    main()
