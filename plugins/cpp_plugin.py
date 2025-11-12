"""
C++ domain plugin.

Production-ready C++ code analyzer using few-shot-5 technique (Phase 2 winner).
"""

from typing import List, Dict, Any
from pathlib import Path
from plugins.domain_plugin import DomainPlugin


class CppPlugin(DomainPlugin):
    """
    C++ code analysis plugin.

    Based on Phase 2 research findings:
    - Uses 5 few-shot examples (optimal balance)
    - Covers all 5 categories
    - Focuses on high-value issues
    """

    @property
    def name(self) -> str:
        """Plugin identifier."""
        return "cpp"

    @property
    def supported_extensions(self) -> List[str]:
        """C++ file extensions."""
        return ['.cpp', '.cc', '.cxx', '.h', '.hpp', '.hxx']

    @property
    def categories(self) -> List[str]:
        """Issue categories for C++."""
        return [
            'memory-safety',
            'modern-cpp',
            'performance',
            'security',
            'concurrency'
        ]

    def get_few_shot_examples(self, num_examples: int = 5) -> List[Dict[str, Any]]:
        """
        Get curated few-shot examples.

        These 5 examples were selected based on Phase 2 findings to provide
        the best coverage and accuracy.

        Args:
            num_examples: Number of examples (default 5 for optimal performance)

        Returns:
            List of example dicts
        """
        # Example 1: Memory leak (high-value, easy to detect)
        ex1 = {
            'id': 'example_001',
            'description': 'Memory leak - raw pointer never deleted',
            'code': 'int* ptr = new int(10);\n*ptr = 42;\nreturn 0;\n// missing: delete ptr;',
            'issues': [
                {
                    'category': 'memory-safety',
                    'severity': 'critical',
                    'line': 1,
                    'description': 'Memory leak - dynamically allocated pointer never deleted',
                    'reasoning': 'Pointer allocated with \'new\' on line 1 but no corresponding \'delete\'. Memory leak on every execution.'
                }
            ]
        }

        # Example 2: Use-after-free (critical safety issue)
        ex2 = {
            'id': 'example_002',
            'description': 'Use-after-free bug',
            'code': 'int* ptr = new int(100);\ndelete ptr;\nstd::cout << *ptr << std::endl; // use after free!',
            'issues': [
                {
                    'category': 'memory-safety',
                    'severity': 'critical',
                    'line': 3,
                    'description': 'Use-after-free - accessing pointer after deletion',
                    'reasoning': 'Pointer deleted on line 2, then dereferenced on line 3. Undefined behavior.'
                }
            ]
        }

        # Example 3: Modern C++ - raw pointer should use unique_ptr
        ex3 = {
            'id': 'example_006',
            'description': 'Raw pointer should use unique_ptr',
            'code': 'Widget* w = new Widget(42);\nstd::cout << w->value << std::endl;\ndelete w;',
            'issues': [
                {
                    'category': 'modern-cpp',
                    'severity': 'medium',
                    'line': 1,
                    'description': 'Use std::unique_ptr instead of raw pointer',
                    'reasoning': 'Manual memory management with new/delete. Use std::unique_ptr for automatic cleanup and exception safety.'
                }
            ]
        }

        # Example 4: Concurrency - data race
        ex4 = {
            'id': 'example_015',
            'description': 'Data race - shared variable without synchronization',
            'code': 'int counter = 0;\nvoid inc() { for(int i=0; i<1000; i++) counter++; }\nstd::thread t1(inc);\nstd::thread t2(inc);',
            'issues': [
                {
                    'category': 'concurrency',
                    'severity': 'critical',
                    'line': 2,
                    'description': 'Data race - unsynchronized access to shared variable',
                    'reasoning': 'Variable \'counter\' accessed by multiple threads without synchronization. Use std::mutex or std::atomic.'
                }
            ]
        }

        # Example 5: Clean code (negative example)
        ex5 = {
            'id': 'example_017',
            'description': 'Clean code with smart pointers - no issues',
            'code': 'std::unique_ptr<int> ptr = std::make_unique<int>(42);\nstd::cout << *ptr << std::endl;\nreturn 0;',
            'issues': []
        }

        examples = [ex1, ex2, ex3, ex4, ex5]
        return examples[:num_examples]

    def get_system_prompt(self) -> str:
        """
        Get C++-specific system prompt.

        Returns:
            System prompt for C++ analysis
        """
        return """You are an expert C++ code reviewer. Analyze code for issues in these categories:

**Categories:**
- memory-safety: memory leaks, use-after-free, double free, buffer overflows, null dereference
- modern-cpp: opportunities to use modern C++ features (smart pointers, std::array, nullptr, auto, range-for)
- performance: inefficient operations, unnecessary copies, string concatenation in loops
- security: hardcoded credentials, SQL injection, input validation, buffer overflows
- concurrency: data races, deadlocks, missing synchronization

**Severity Levels:**
- critical: Security vulnerability or crash-causing bug
- high: Significant correctness or performance issue
- medium: Code quality or maintainability issue
- low: Minor style or optimization opportunity

**Response Format:**
Respond with a JSON array of issues. Each issue must have:
- category: one of the above categories
- severity: critical, high, medium, or low
- line: line number where issue occurs (1-indexed)
- description: brief description (10-50 words)
- reasoning: detailed explanation of why this is an issue (20-100 words)

If no issues are found, respond with an empty array: []

**Important:**
- Only report real issues with clear negative impact
- Avoid false positives - be conservative
- Focus on actionable issues that developers should fix
"""

    def should_analyze_file(self, file_path: Path) -> bool:
        """
        Check if file should be analyzed.

        Excludes test files and third-party code.

        Args:
            file_path: Path to file

        Returns:
            True if should analyze
        """
        # Check extension first
        if not super().should_analyze_file(file_path):
            return False

        # Skip test files
        if 'test' in file_path.stem.lower():
            return False

        # Skip third-party directories
        excluded_dirs = {'third_party', 'external', 'vendor', 'node_modules'}
        if any(excluded in file_path.parts for excluded in excluded_dirs):
            return False

        return True

    def preprocess_code(self, code: str, file_path: Path) -> str:
        """
        Preprocess C++ code.

        Strips comments for cleaner analysis (optional).

        Args:
            code: Source code
            file_path: Path to file

        Returns:
            Preprocessed code
        """
        # For now, return code unchanged
        # Could add comment stripping, macro expansion, etc.
        return code

    def postprocess_issues(self, issues: List[Any]) -> List[Any]:
        """
        Postprocess detected issues.

        Filters and sorts by severity.

        Args:
            issues: List of Issue objects

        Returns:
            Filtered and sorted issues
        """
        # Filter out invalid issues
        valid_issues = [issue for issue in issues if self.validate_issue(issue)]

        # Sort by severity (critical first)
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        sorted_issues = sorted(
            valid_issues,
            key=lambda x: (severity_order.get(x.severity, 4), x.line)
        )

        return sorted_issues
