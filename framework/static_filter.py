"""
Static analysis integration module.

Provides clang-tidy integration to complement LLM-based semantic analysis:
1. Run clang-tidy on files to detect issues that static analysis handles
2. Filter LLM results to avoid duplicating clang-tidy findings
3. Provide AST context to help LLM understand code structure

This ensures the semantic PR reviewer focuses on issues that require
understanding code intent, not issues that tools can mechanically detect.
"""

import subprocess
import re
import json
from typing import List, Dict, Any, Optional, Set, Tuple
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class ClangTidyIssue:
    """Represents an issue found by clang-tidy."""
    file: str
    line: int
    column: int
    severity: str  # warning, error, note
    check_name: str  # e.g., "bugprone-use-after-move"
    message: str

    @property
    def category_mapping(self) -> Optional[str]:
        """Map clang-tidy check to our category (for filtering)."""
        # Memory-related checks (clang-tidy handles these)
        memory_checks = {
            'clang-analyzer-core.NullDereference',
            'clang-analyzer-cplusplus.NewDelete',
            'clang-analyzer-cplusplus.NewDeleteLeaks',
            'clang-analyzer-deadcode.DeadStores',
            'bugprone-use-after-move',
        }

        # Performance checks (clang-tidy handles these)
        performance_checks = {
            'performance-unnecessary-copy-initialization',
            'performance-for-range-copy',
            'performance-inefficient-string-concatenation',
            'performance-move-const-arg',
        }

        # Modernization checks (clang-tidy handles these)
        modernization_checks = {
            'modernize-use-nullptr',
            'modernize-use-auto',
            'modernize-use-override',
            'modernize-make-unique',
            'modernize-make-shared',
            'modernize-use-emplace',
        }

        # Concurrency checks (clang-tidy handles these)
        concurrency_checks = {
            'bugprone-thread-safety-analysis',
            'clang-analyzer-core.CallAndMessage',
        }

        if self.check_name in memory_checks:
            return 'memory-safety'
        elif self.check_name in performance_checks:
            return 'performance'
        elif self.check_name in modernization_checks:
            return 'modern-cpp'
        elif self.check_name in concurrency_checks:
            return 'concurrency'

        return None


@dataclass
class ClangTidyResult:
    """Result from running clang-tidy on a file."""
    file_path: str
    issues: List[ClangTidyIssue] = field(default_factory=list)
    success: bool = True
    error_message: Optional[str] = None

    @property
    def static_analysis_lines(self) -> Set[int]:
        """Get line numbers where clang-tidy found issues."""
        return {issue.line for issue in self.issues}

    @property
    def has_memory_issues(self) -> bool:
        """Check if clang-tidy found memory-related issues."""
        return any(
            issue.category_mapping == 'memory-safety'
            for issue in self.issues
        )

    @property
    def has_performance_issues(self) -> bool:
        """Check if clang-tidy found performance issues."""
        return any(
            issue.category_mapping == 'performance'
            for issue in self.issues
        )


class ClangTidyRunner:
    """
    Runs clang-tidy and parses output.

    Provides integration with static analysis to:
    1. Filter out issues that clang-tidy already detects
    2. Provide context about what static analysis found
    """

    # Checks that clang-tidy handles well (we should NOT duplicate)
    EXCLUDED_CHECKS = {
        # Memory safety - ASan/clang-tidy handle these
        'clang-analyzer-core.NullDereference',
        'clang-analyzer-cplusplus.NewDelete',
        'clang-analyzer-cplusplus.NewDeleteLeaks',
        'bugprone-use-after-move',

        # Performance - clang-tidy handles these
        'performance-*',

        # Modernization - clang-tidy handles these
        'modernize-*',

        # Concurrency - TSan/clang-tidy handle these
        'bugprone-data-race',
    }

    # Checks that might overlap with our semantic analysis
    SEMANTIC_ADJACENT_CHECKS = {
        'bugprone-argument-comment',  # Wrong argument order
        'bugprone-bool-pointer-implicit-conversion',
        'bugprone-incorrect-roundings',
        'bugprone-integer-division',
        'bugprone-sizeof-expression',
        'bugprone-string-integer-assignment',
        'bugprone-suspicious-enum-usage',
        'bugprone-suspicious-missing-comma',
        'bugprone-too-small-loop-variable',
        'misc-redundant-expression',
    }

    def __init__(
        self,
        clang_tidy_path: str = "clang-tidy",
        compile_commands_path: Optional[str] = None,
        extra_args: Optional[List[str]] = None
    ):
        """
        Initialize clang-tidy runner.

        Args:
            clang_tidy_path: Path to clang-tidy executable
            compile_commands_path: Path to compile_commands.json (optional)
            extra_args: Extra arguments to pass to clang-tidy
        """
        self.clang_tidy_path = clang_tidy_path
        self.compile_commands_path = compile_commands_path
        self.extra_args = extra_args or []

    def is_available(self) -> bool:
        """Check if clang-tidy is available."""
        try:
            result = subprocess.run(
                [self.clang_tidy_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def run(self, file_path: Path) -> ClangTidyResult:
        """
        Run clang-tidy on a file.

        Args:
            file_path: Path to C++ file to analyze

        Returns:
            ClangTidyResult with parsed issues
        """
        if not self.is_available():
            return ClangTidyResult(
                file_path=str(file_path),
                success=False,
                error_message="clang-tidy not available"
            )

        cmd = [self.clang_tidy_path]

        # Add compile commands if available
        if self.compile_commands_path:
            cmd.extend(["-p", self.compile_commands_path])

        # Add extra args
        cmd.extend(self.extra_args)

        # Add file
        cmd.append(str(file_path))

        # Add -- to separate from compiler args
        cmd.append("--")
        cmd.extend(["-std=c++17", "-I."])  # Basic defaults

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60  # 1 minute timeout
            )

            issues = self._parse_output(result.stdout + result.stderr, file_path)

            return ClangTidyResult(
                file_path=str(file_path),
                issues=issues,
                success=True
            )

        except subprocess.TimeoutExpired:
            return ClangTidyResult(
                file_path=str(file_path),
                success=False,
                error_message="clang-tidy timed out"
            )
        except Exception as e:
            return ClangTidyResult(
                file_path=str(file_path),
                success=False,
                error_message=str(e)
            )

    def _parse_output(self, output: str, file_path: Path) -> List[ClangTidyIssue]:
        """
        Parse clang-tidy output into structured issues.

        Output format:
        /path/to/file.cpp:10:5: warning: message [check-name]
        """
        issues = []

        # Pattern: file:line:col: severity: message [check-name]
        pattern = r"([^:]+):(\d+):(\d+): (warning|error|note): (.+?) \[([^\]]+)\]"

        for match in re.finditer(pattern, output):
            file_str, line, col, severity, message, check_name = match.groups()

            # Only include issues from the target file
            if Path(file_str).name == file_path.name:
                issues.append(ClangTidyIssue(
                    file=file_str,
                    line=int(line),
                    column=int(col),
                    severity=severity,
                    check_name=check_name,
                    message=message
                ))

        return issues


class StaticAnalysisFilter:
    """
    Filters LLM results to remove issues that static analysis already handles.

    This ensures the semantic PR reviewer adds value by focusing on issues
    that require understanding code intent, not mechanical detection.
    """

    # Issue types that clang-tidy handles - we should NOT report these
    CLANG_TIDY_HANDLED = {
        # Memory safety
        'memory leak',
        'use-after-free',
        'double free',
        'null pointer dereference',
        'uninitialized variable',
        'buffer overflow',

        # Performance
        'unnecessary copy',
        'inefficient string concatenation',
        'pass by value',
        'move semantics',

        # Modernization
        'use nullptr',
        'use auto',
        'use override',
        'use smart pointer',
        'use make_unique',
        'use make_shared',
        'use emplace',
        'range-based for',

        # Concurrency (TSan handles)
        'data race',
        'deadlock',
        'lock ordering',
    }

    def __init__(self, clang_tidy_runner: Optional[ClangTidyRunner] = None):
        """
        Initialize filter.

        Args:
            clang_tidy_runner: Optional runner for active clang-tidy integration
        """
        self.clang_tidy_runner = clang_tidy_runner

    def filter_issues(
        self,
        issues: List[Dict[str, Any]],
        clang_tidy_result: Optional[ClangTidyResult] = None
    ) -> List[Dict[str, Any]]:
        """
        Filter out issues that static analysis handles.

        Args:
            issues: List of issues from LLM analysis
            clang_tidy_result: Optional result from clang-tidy run

        Returns:
            Filtered list of semantic issues only
        """
        filtered = []

        # Get lines where clang-tidy found issues (avoid duplicates)
        clang_tidy_lines = set()
        if clang_tidy_result:
            clang_tidy_lines = clang_tidy_result.static_analysis_lines

        for issue in issues:
            # Skip if on same line as clang-tidy issue
            if issue.get('line') in clang_tidy_lines:
                continue

            # Skip if description matches clang-tidy-handled patterns
            description = issue.get('description', '').lower()
            if self._is_static_analysis_issue(description):
                continue

            # Skip if category is not semantic
            category = issue.get('category', '')
            if category in {'memory-safety', 'performance', 'concurrency', 'modern-cpp'}:
                continue

            filtered.append(issue)

        return filtered

    def _is_static_analysis_issue(self, description: str) -> bool:
        """Check if issue description matches static analysis patterns."""
        description_lower = description.lower()

        for pattern in self.CLANG_TIDY_HANDLED:
            if pattern in description_lower:
                return True

        return False

    def get_context_for_llm(
        self,
        clang_tidy_result: ClangTidyResult
    ) -> str:
        """
        Generate context string for LLM about what static analysis found.

        This helps LLM understand what NOT to report.

        Args:
            clang_tidy_result: Result from clang-tidy

        Returns:
            Context string to include in LLM prompt
        """
        if not clang_tidy_result.issues:
            return ""

        lines = ["**Static Analysis Already Found:**"]

        for issue in clang_tidy_result.issues[:10]:  # Limit to 10
            lines.append(f"- Line {issue.line}: {issue.message} [{issue.check_name}]")

        if len(clang_tidy_result.issues) > 10:
            lines.append(f"- ... and {len(clang_tidy_result.issues) - 10} more")

        lines.append("")
        lines.append("DO NOT report issues on these lines or similar issues.")
        lines.append("")

        return "\n".join(lines)


def create_default_filter() -> StaticAnalysisFilter:
    """Create default static analysis filter with clang-tidy if available."""
    runner = ClangTidyRunner()

    if runner.is_available():
        return StaticAnalysisFilter(clang_tidy_runner=runner)
    else:
        return StaticAnalysisFilter()
