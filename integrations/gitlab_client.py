"""
GitLab API client for Semantic PR Review Bot.

Provides functionality to:
- Fetch merge request details
- Get changed files and diffs
- Post review comments
- Update MR discussions
"""

import json
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class MergeRequestInfo:
    """Information about a GitLab merge request."""
    iid: int
    title: str
    description: str
    source_branch: str
    target_branch: str
    author: str
    changed_files: List[str]
    diff_refs: Dict[str, str]


@dataclass
class FileDiff:
    """Diff information for a single file."""
    old_path: str
    new_path: str
    diff: str
    new_file: bool
    deleted_file: bool
    renamed_file: bool


class GitLabClient:
    """
    GitLab API client for merge request integration.

    Usage:
        client = GitLabClient(
            gitlab_url="https://gitlab.example.com",
            project_id=123,
            private_token="glpat-xxx"
        )

        # Get MR info
        mr_info = client.get_merge_request(42)

        # Get changed files
        diffs = client.get_merge_request_diffs(42)

        # Post comment
        client.post_mr_comment(42, "Found issues...")
    """

    def __init__(
        self,
        gitlab_url: str,
        project_id: int,
        private_token: str,
        api_version: str = "v4"
    ):
        """
        Initialize GitLab client.

        Args:
            gitlab_url: Base URL of GitLab instance (e.g., https://gitlab.com)
            project_id: GitLab project ID
            private_token: GitLab API token with api scope
            api_version: API version (default: v4)
        """
        self.gitlab_url = gitlab_url.rstrip('/')
        self.project_id = project_id
        self.private_token = private_token
        self.api_version = api_version

        self.base_url = f"{self.gitlab_url}/api/{api_version}"
        self.headers = {
            "PRIVATE-TOKEN": private_token,
            "Content-Type": "application/json"
        }

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make API request to GitLab."""
        url = f"{self.base_url}{endpoint}"

        response = requests.request(
            method=method,
            url=url,
            headers=self.headers,
            json=data,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        if response.text:
            return response.json()
        return {}

    def get_merge_request(self, mr_iid: int) -> MergeRequestInfo:
        """
        Get merge request information.

        Args:
            mr_iid: Merge request IID (not ID)

        Returns:
            MergeRequestInfo with MR details
        """
        endpoint = f"/projects/{self.project_id}/merge_requests/{mr_iid}"
        data = self._request("GET", endpoint)

        # Get changed files
        changes_endpoint = f"{endpoint}/changes"
        changes_data = self._request("GET", changes_endpoint)

        changed_files = [
            change['new_path']
            for change in changes_data.get('changes', [])
        ]

        return MergeRequestInfo(
            iid=data['iid'],
            title=data['title'],
            description=data.get('description', ''),
            source_branch=data['source_branch'],
            target_branch=data['target_branch'],
            author=data['author']['username'],
            changed_files=changed_files,
            diff_refs=data.get('diff_refs', {})
        )

    def get_merge_request_diffs(self, mr_iid: int) -> List[FileDiff]:
        """
        Get file diffs for a merge request.

        Args:
            mr_iid: Merge request IID

        Returns:
            List of FileDiff objects
        """
        endpoint = f"/projects/{self.project_id}/merge_requests/{mr_iid}/changes"
        data = self._request("GET", endpoint)

        diffs = []
        for change in data.get('changes', []):
            diffs.append(FileDiff(
                old_path=change.get('old_path', ''),
                new_path=change.get('new_path', ''),
                diff=change.get('diff', ''),
                new_file=change.get('new_file', False),
                deleted_file=change.get('deleted_file', False),
                renamed_file=change.get('renamed_file', False)
            ))

        return diffs

    def get_file_content(self, file_path: str, ref: str) -> str:
        """
        Get file content at a specific ref.

        Args:
            file_path: Path to file in repository
            ref: Git ref (branch, tag, commit)

        Returns:
            File content as string
        """
        import base64
        from urllib.parse import quote

        encoded_path = quote(file_path, safe='')
        endpoint = f"/projects/{self.project_id}/repository/files/{encoded_path}"

        data = self._request("GET", endpoint, params={"ref": ref})

        content = data.get('content', '')
        encoding = data.get('encoding', 'base64')

        if encoding == 'base64':
            return base64.b64decode(content).decode('utf-8')
        return content

    def post_mr_comment(self, mr_iid: int, body: str) -> Dict[str, Any]:
        """
        Post a comment on a merge request.

        Args:
            mr_iid: Merge request IID
            body: Comment body (supports Markdown)

        Returns:
            Created note data
        """
        endpoint = f"/projects/{self.project_id}/merge_requests/{mr_iid}/notes"
        return self._request("POST", endpoint, data={"body": body})

    def post_inline_comment(
        self,
        mr_iid: int,
        body: str,
        file_path: str,
        new_line: int,
        base_sha: str,
        head_sha: str,
        start_sha: str
    ) -> Dict[str, Any]:
        """
        Post an inline comment on a specific line.

        Args:
            mr_iid: Merge request IID
            body: Comment body
            file_path: Path to file
            new_line: Line number in new version
            base_sha: Base commit SHA
            head_sha: Head commit SHA
            start_sha: Start commit SHA

        Returns:
            Created discussion data
        """
        endpoint = f"/projects/{self.project_id}/merge_requests/{mr_iid}/discussions"

        position = {
            "base_sha": base_sha,
            "head_sha": head_sha,
            "start_sha": start_sha,
            "position_type": "text",
            "new_path": file_path,
            "new_line": new_line
        }

        return self._request("POST", endpoint, data={
            "body": body,
            "position": position
        })

    def format_review_comment(
        self,
        issues: List[Dict[str, Any]],
        file_path: str = None
    ) -> str:
        """
        Format issues as a Markdown comment for MR.

        Args:
            issues: List of issue dicts from analysis
            file_path: Optional file path for context

        Returns:
            Formatted Markdown string
        """
        if not issues:
            return "## Semantic Review: No Issues Found\n\nNo semantic issues detected in this merge request."

        lines = ["## Semantic Review: Issues Found\n"]

        if file_path:
            lines.append(f"**File:** `{file_path}`\n")

        # Group by severity
        by_severity = {}
        for issue in issues:
            severity = issue.get('severity', 'medium')
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(issue)

        severity_order = ['critical', 'high', 'medium', 'low']
        severity_emoji = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🔵'
        }

        for severity in severity_order:
            if severity not in by_severity:
                continue

            emoji = severity_emoji.get(severity, '⚪')
            lines.append(f"### {emoji} {severity.upper()}\n")

            for issue in by_severity[severity]:
                line_num = issue.get('line', '?')
                category = issue.get('category', 'unknown')
                description = issue.get('description', 'No description')
                reasoning = issue.get('reasoning', '')

                lines.append(f"**Line {line_num}** (`{category}`)")
                lines.append(f"> {description}")
                if reasoning:
                    lines.append(f"\n<details><summary>Details</summary>\n\n{reasoning}\n\n</details>")
                lines.append("")

        lines.append("\n---")
        lines.append("*Semantic Review Bot - Detecting issues that static analysis cannot catch*")

        return "\n".join(lines)


def create_from_env() -> GitLabClient:
    """
    Create GitLab client from environment variables.

    Expected environment variables:
    - CI_SERVER_URL: GitLab instance URL
    - CI_PROJECT_ID: Project ID
    - GITLAB_API_TOKEN: API token

    Returns:
        Configured GitLabClient
    """
    import os

    gitlab_url = os.environ.get('CI_SERVER_URL', 'https://gitlab.com')
    project_id = int(os.environ.get('CI_PROJECT_ID', 0))
    token = os.environ.get('GITLAB_API_TOKEN', '')

    if not project_id or not token:
        raise ValueError(
            "Missing required environment variables: "
            "CI_PROJECT_ID, GITLAB_API_TOKEN"
        )

    return GitLabClient(
        gitlab_url=gitlab_url,
        project_id=project_id,
        private_token=token
    )
