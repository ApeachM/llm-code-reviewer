"""
CI/CD integrations for Semantic PR Review Bot.

Provides integration with:
- GitLab CI (via gitlab_client.py)
- GitHub Actions (future)
- Jenkins (future)
"""

from integrations.gitlab_client import GitLabClient

__all__ = ['GitLabClient']
