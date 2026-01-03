"""
GitLab CI script to post review results as MR comment.

Usage:
    python -m integrations.gitlab_post_comment \
        --project-id 123 \
        --mr-iid 42 \
        --results review_results.json \
        --gitlab-url https://gitlab.example.com \
        --token glpat-xxx
"""

import argparse
import json
import sys
from pathlib import Path

from integrations.gitlab_client import GitLabClient


def main():
    parser = argparse.ArgumentParser(
        description="Post semantic review results to GitLab MR"
    )
    parser.add_argument(
        "--project-id",
        type=int,
        required=True,
        help="GitLab project ID"
    )
    parser.add_argument(
        "--mr-iid",
        type=int,
        required=True,
        help="Merge request IID"
    )
    parser.add_argument(
        "--results",
        type=str,
        required=True,
        help="Path to JSON results file"
    )
    parser.add_argument(
        "--gitlab-url",
        type=str,
        default="https://gitlab.com",
        help="GitLab instance URL"
    )
    parser.add_argument(
        "--token",
        type=str,
        required=True,
        help="GitLab API token"
    )
    parser.add_argument(
        "--inline",
        action="store_true",
        help="Post inline comments instead of single comment"
    )

    args = parser.parse_args()

    # Load results
    results_path = Path(args.results)
    if not results_path.exists():
        print(f"Results file not found: {args.results}")
        sys.exit(1)

    with open(results_path) as f:
        results = json.load(f)

    # Check if there are issues
    issues = results.get('issues', [])
    if not issues:
        print("No issues to report")
        sys.exit(0)

    # Create client
    client = GitLabClient(
        gitlab_url=args.gitlab_url,
        project_id=args.project_id,
        private_token=args.token
    )

    if args.inline:
        # Post inline comments for each issue
        mr_info = client.get_merge_request(args.mr_iid)
        diff_refs = mr_info.diff_refs

        for issue in issues:
            file_path = issue.get('file_path', results.get('file_path', ''))
            line = issue.get('line', 1)

            body = format_inline_comment(issue)

            try:
                client.post_inline_comment(
                    mr_iid=args.mr_iid,
                    body=body,
                    file_path=file_path,
                    new_line=line,
                    base_sha=diff_refs.get('base_sha', ''),
                    head_sha=diff_refs.get('head_sha', ''),
                    start_sha=diff_refs.get('start_sha', '')
                )
                print(f"Posted inline comment for {file_path}:{line}")
            except Exception as e:
                print(f"Failed to post inline comment: {e}")

    else:
        # Post single summary comment
        comment = client.format_review_comment(
            issues=issues,
            file_path=results.get('file_path')
        )

        try:
            client.post_mr_comment(args.mr_iid, comment)
            print(f"Posted review comment with {len(issues)} issue(s)")
        except Exception as e:
            print(f"Failed to post comment: {e}")
            sys.exit(1)


def format_inline_comment(issue: dict) -> str:
    """Format a single issue as inline comment."""
    severity = issue.get('severity', 'medium')
    category = issue.get('category', 'unknown')
    description = issue.get('description', 'No description')
    reasoning = issue.get('reasoning', '')

    severity_emoji = {
        'critical': '🔴',
        'high': '🟠',
        'medium': '🟡',
        'low': '🔵'
    }
    emoji = severity_emoji.get(severity, '⚪')

    lines = [
        f"{emoji} **Semantic Issue** ({severity.upper()})",
        f"**Category:** `{category}`",
        "",
        description,
    ]

    if reasoning:
        lines.extend([
            "",
            "<details><summary>Reasoning</summary>",
            "",
            reasoning,
            "",
            "</details>"
        ])

    return "\n".join(lines)


if __name__ == "__main__":
    main()
