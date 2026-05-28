#!/usr/bin/env python3
"""
Generic helper script to create Jira bugs from dogfood report.

This is a GENERIC, portable script that works with any dogfood report.
Part of the em-semi-tools plugin - can be used across any project.

Called automatically by dogfood skill at the end of session.
Parses any dogfood report and invokes create-bug skill for each issue.

Usage:
    # From any project using the plugin
    python .claude/plugins/em-semi-tools/skills/dogfood/create-bugs-helper.py <report-path>

    # Example
    python .claude/plugins/em-semi-tools/skills/dogfood/create-bugs-helper.py dogfood-output/report.md
    python .claude/plugins/em-semi-tools/skills/dogfood/create-bugs-helper.py qa-reports/sprint-qa.md
"""

import re
import subprocess
import sys
from pathlib import Path


def parse_issue_from_report(content, issue_number):
    """Extract issue details from report markdown."""

    # Find issue section
    pattern = rf"### ISSUE-{issue_number:03d}: (.+?)\n.*?\n(.*?)(?=### ISSUE-|\Z)"
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        return None

    title = match.group(1).strip()
    body = match.group(2)

    # Extract table fields
    severity_match = re.search(r"\| \*\*Severity\*\* \| (.+?) \|", body)
    category_match = re.search(r"\| \*\*Category\*\* \| (.+?) \|", body)
    ticket_match = re.search(r"\| \*\*Sprint Ticket\*\* \| (.+?) \|", body)
    url_match = re.search(r"\| \*\*URL\*\* \| (.+?) \|", body)
    video_match = re.search(r"\| \*\*Repro Video\*\* \| (.+?) \|", body)

    # Extract description sections
    desc_match = re.search(
        r"\*\*Description\*\*\s*\n\n(.+?)\n\n\*\*Expected", body, re.DOTALL
    )
    expected_match = re.search(
        r"\*\*Expected Behavior\*\*\s*\n\n(.+?)\n\n\*\*Actual", body, re.DOTALL
    )
    actual_match = re.search(
        r"\*\*Actual Behavior\*\*\s*\n\n(.+?)\n\n\*\*Repro", body, re.DOTALL
    )
    steps_match = re.search(
        r"\*\*Repro Steps\*\*\s*\n\n(.+?)\n\n\*\*Impact", body, re.DOTALL
    )
    impact_match = re.search(
        r"\*\*Impact\*\*\s*\n\n(.+?)(\n\n\*\*Related|\Z)", body, re.DOTALL
    )

    # Find screenshot paths
    screenshots = re.findall(r"!\[.*?\]\((screenshots/[^)]+)\)", body)

    return {
        "number": issue_number,
        "title": title,
        "severity": severity_match.group(1).strip() if severity_match else "medium",
        "category": category_match.group(1).strip() if category_match else "functional",
        "sprint_ticket": ticket_match.group(1).strip() if ticket_match else "",
        "url": url_match.group(1).strip() if url_match else "",
        "video": video_match.group(1).strip() if video_match else "N/A",
        "description": desc_match.group(1).strip() if desc_match else "",
        "expected": expected_match.group(1).strip() if expected_match else "",
        "actual": actual_match.group(1).strip() if actual_match else "",
        "steps": steps_match.group(1).strip() if steps_match else "",
        "impact": impact_match.group(1).strip() if impact_match else "",
        "screenshots": screenshots,
    }


def format_for_create_bug(issue):
    """Format issue data for create-bug skill invocation."""

    # Build the bug description for create-bug
    bug_info = f"""Bug Summary: {issue["title"]}

Severity: {issue["severity"]}
Category: {issue["category"]}
Related Sprint Tickets: {issue["sprint_ticket"]}

Description:
{issue["description"]}

Expected Behavior:
{issue["expected"]}

Actual Behavior:
{issue["actual"]}

Steps to Reproduce:
{issue["steps"]}

Impact:
{issue["impact"]}

URL: {issue["url"]}
Screenshots: {", ".join(issue["screenshots"])}
Repro Video: {issue["video"]}

Source: Dogfood Report ISSUE-{issue["number"]:03d}
"""

    return bug_info


def invoke_create_bug_skill(issue, report_dir, dry_run=False):
    """
    Invoke create-bug skill for an issue.

    GENERIC - works with any dogfood report from any project.
    """

    if dry_run:
        print(f"\n{'=' * 80}")
        print(f"Would create bug: ISSUE-{issue['number']:03d}: {issue['title']}")
        print(f"Severity: {issue['severity']}")
        print(f"Related: {issue.get('sprint_ticket', 'N/A')}")
        print(f"{'=' * 80}")
        return None

    print(f"\n🐛 Creating Jira bug for ISSUE-{issue['number']:03d}")
    print(f"Title: {issue['title']}")
    print(f"Severity: {issue['severity']}")

    # Format the data for create-bug skill
    bug_description = format_for_create_bug(issue)

    # Save to temp file (generic temp location)
    temp_file = f"/tmp/dogfood-bug-{issue['number']:03d}.txt"
    with open(temp_file, "w") as f:
        f.write(bug_description)

    print(f"Bug details saved to: {temp_file}")
    print(f"Screenshot: {issue['screenshots'][0] if issue['screenshots'] else 'N/A'}")

    # Build screenshot path (relative to report directory)
    screenshot_arg = ""
    if issue["screenshots"]:
        # Screenshot path is relative to report, so prepend report directory
        screenshot_path = Path(report_dir) / issue["screenshots"][0]
        if screenshot_path.exists():
            screenshot_arg = str(screenshot_path)
        else:
            print(f"⚠️  Screenshot not found: {screenshot_path}")

    try:
        # Call create-bug skill with summary and screenshot
        # GENERIC - calls the create-bug skill from the same plugin
        result = subprocess.run(
            ["claude", "run", "create-bug", issue["title"], screenshot_arg]
            if screenshot_arg
            else ["claude", "run", "create-bug", issue["title"]],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        if result.returncode == 0:
            print("✅ Bug created successfully")

            # Try to extract Jira ticket ID from output (generic pattern)
            # Matches: SEMI-1234, PROJ-456, ABC-789, etc.
            jira_match = re.search(r"([A-Z]+-\d+)", result.stdout)
            if jira_match:
                jira_key = jira_match.group(1)
                print(f"✅ Jira ticket: {jira_key}")
                return jira_key

            return "Created (ID not parsed)"
        else:
            print(f"⚠️  create-bug failed: {result.stderr}")
            return None

    except Exception as e:
        print(f"⚠️  Error invoking create-bug: {e}")
        return None


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Create Jira bugs from dogfood report")
    parser.add_argument("report", help="Path to dogfood report (report.md)")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument(
        "--auto", action="store_true", help="Auto-create without confirmation"
    )

    args = parser.parse_args()

    if not Path(args.report).exists():
        print(f"❌ Report not found: {args.report}")
        sys.exit(1)

    content = Path(args.report).read_text()

    # Find all issues
    issue_count = len(re.findall(r"^### ISSUE-", content, re.MULTILINE))

    if issue_count == 0:
        print("No issues found in report")
        return

    print(f"📋 Found {issue_count} issue(s) in dogfood report")

    # Show preview
    for i in range(1, issue_count + 1):
        issue = parse_issue_from_report(content, i)
        if issue:
            print(f"  ISSUE-{i:03d}: {issue['title']} ({issue['severity']})")

    print()

    if not args.auto and not args.dry_run:
        response = input(f"Create {issue_count} Jira bug(s)? [Y/n] ")
        if response.lower() == "n":
            print("Cancelled")
            return

    # Process each issue
    created_bugs = {}

    # Get report directory for resolving screenshot paths
    report_dir = Path(args.report).parent

    for i in range(1, issue_count + 1):
        issue = parse_issue_from_report(content, i)

        if issue:
            jira_key = invoke_create_bug_skill(issue, report_dir, dry_run=args.dry_run)
            if jira_key:
                created_bugs[f"ISSUE-{i:03d}"] = jira_key

    # Update report with Jira ticket references
    if not args.dry_run and created_bugs:
        print(f"\n✅ Created {len(created_bugs)} Jira bug(s)")
        print("\nJira tickets created:")
        for issue_id, jira_key in created_bugs.items():
            print(f"  {issue_id} → {jira_key}")

        # TODO: Update report.md with Jira ticket references
        print(f"\n💡 Update {args.report} to add Jira ticket references")

    if args.dry_run:
        print("\n✅ Dry run complete (no bugs created)")


if __name__ == "__main__":
    main()
