"""
Domain plugin interface.

This abstract base class defines the interface that all domain-specific plugins
must implement. The framework handles LLM techniques, while plugins provide
domain knowledge.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path


class DomainPlugin(ABC):
    """
    Abstract base class for domain-specific plugins.

    Plugins provide:
    - Language-specific parsing
    - Few-shot examples for the domain
    - Category definitions
    - Validation rules
    - File filtering
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Plugin name (e.g., 'cpp', 'rtl', 'power').

        Returns:
            String identifier for this plugin
        """
        pass

    @property
    @abstractmethod
    def supported_extensions(self) -> List[str]:
        """
        File extensions this plugin handles.

        Returns:
            List of extensions (e.g., ['.cpp', '.h', '.hpp'])
        """
        pass

    @property
    @abstractmethod
    def categories(self) -> List[str]:
        """
        Issue categories this plugin detects.

        Returns:
            List of category names (e.g., ['memory-safety', 'modern-cpp'])
        """
        pass

    @abstractmethod
    def get_few_shot_examples(self, num_examples: int = 5) -> List[Dict[str, Any]]:
        """
        Get few-shot examples for this domain.

        Based on Phase 2 findings, 5 examples is optimal.

        Args:
            num_examples: Number of examples to return (default 5)

        Returns:
            List of example dicts with 'id', 'code', 'issues'
        """
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get domain-specific system prompt.

        Returns:
            System prompt text describing the analysis task
        """
        pass

    def should_analyze_file(self, file_path: Path) -> bool:
        """
        Check if this file should be analyzed.

        Default implementation checks file extension.
        Can be overridden for more complex logic.

        Args:
            file_path: Path to file

        Returns:
            True if file should be analyzed
        """
        return file_path.suffix in self.supported_extensions

    def preprocess_code(self, code: str, file_path: Path) -> str:
        """
        Preprocess code before analysis.

        Optional hook for domain-specific preprocessing.
        Default implementation returns code unchanged.

        Args:
            code: Source code
            file_path: Path to file

        Returns:
            Preprocessed code
        """
        return code

    def postprocess_issues(self, issues: List[Any]) -> List[Any]:
        """
        Postprocess detected issues.

        Optional hook for domain-specific filtering or enhancement.
        Default implementation returns issues unchanged.

        Args:
            issues: List of Issue objects

        Returns:
            Filtered/enhanced issues
        """
        return issues

    def validate_issue(self, issue: Any) -> bool:
        """
        Validate that an issue is appropriate for this domain.

        Args:
            issue: Issue object

        Returns:
            True if issue is valid
        """
        return issue.category in self.categories
