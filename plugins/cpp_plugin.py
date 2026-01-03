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
        """Semantic issue categories for C++.

        These focus on issues that static/dynamic analysis tools CANNOT detect.
        Memory safety, performance, and concurrency are handled by ASan, TSan, clang-tidy.
        """
        return [
            'logic-errors',           # Off-by-one, wrong operators, boolean logic
            'api-misuse',             # Missing cleanup, wrong parameter order
            'semantic-inconsistency', # Code behavior doesn't match naming/docs
            'edge-case-handling',     # Missing boundary checks
            'code-intent-mismatch'    # Implementation doesn't match requirements
        ]

    def get_few_shot_examples(self, num_examples: int = 5) -> List[Dict[str, Any]]:
        """
        Get curated few-shot examples for semantic issue detection.

        These 5 examples focus on issues that static/dynamic analysis CANNOT detect:
        - Logic errors (off-by-one, wrong operators)
        - API misuse (missing cleanup in error paths)
        - Semantic inconsistency (code doesn't match naming)
        - Edge case handling (missing boundary checks)
        - Clean code (negative example for calibration)

        Args:
            num_examples: Number of examples (default 5 for optimal performance)

        Returns:
            List of example dicts
        """
        # Example 1: Logic error - off-by-one in loop
        ex1 = {
            'id': 'semantic_001',
            'description': 'Off-by-one error in loop condition',
            'code': '''std::vector<int> nums = {1, 2, 3, 4, 5};
int sum = 0;
for (int i = 0; i <= nums.size(); i++) {
    sum += nums[i];
}
return sum;''',
            'issues': [
                {
                    'category': 'logic-errors',
                    'severity': 'critical',
                    'line': 3,
                    'description': 'Off-by-one error: loop uses <= instead of <',
                    'reasoning': 'Loop condition i <= nums.size() allows i to equal size (5), causing out-of-bounds access at nums[5]. Should use i < nums.size().'
                }
            ]
        }

        # Example 2: API misuse - file handle not closed in error path
        ex2 = {
            'id': 'semantic_002',
            'description': 'Resource leak in error path',
            'code': '''bool processFile(const std::string& path) {
    FILE* f = fopen(path.c_str(), "r");
    if (!f) return false;

    char buffer[1024];
    if (fread(buffer, 1, 1024, f) == 0) {
        return false;  // Error: file not closed!
    }

    fclose(f);
    return true;
}''',
            'issues': [
                {
                    'category': 'api-misuse',
                    'severity': 'high',
                    'line': 7,
                    'description': 'File handle leaked in error path',
                    'reasoning': 'fopen() on line 2 succeeds, but early return on line 7 skips fclose() on line 10. File descriptor leaked on read error. Use RAII or add fclose() before return.'
                }
            ]
        }

        # Example 3: Semantic inconsistency - getter modifies state
        ex3 = {
            'id': 'semantic_003',
            'description': 'Function name implies read-only but modifies state',
            'code': '''class PriceCalculator {
    double price_;
    bool discountApplied_ = false;

public:
    double getDiscountedPrice() {
        discountApplied_ = true;  // Side effect!
        return price_ * 0.9;
    }
};''',
            'issues': [
                {
                    'category': 'semantic-inconsistency',
                    'severity': 'medium',
                    'line': 7,
                    'description': 'Getter function has side effect',
                    'reasoning': 'Function named "getDiscountedPrice" implies read-only operation, but line 7 modifies member state. Violates principle of least surprise. Either rename to "applyDiscount()" or remove side effect.'
                }
            ]
        }

        # Example 4: Edge case handling - no empty check
        ex4 = {
            'id': 'semantic_004',
            'description': 'Missing empty container check',
            'code': '''double calculateAverage(const std::vector<double>& values) {
    double sum = 0.0;
    for (const auto& v : values) {
        sum += v;
    }
    return sum / values.size();  // Division by zero if empty!
}''',
            'issues': [
                {
                    'category': 'edge-case-handling',
                    'severity': 'high',
                    'line': 6,
                    'description': 'Division by zero when vector is empty',
                    'reasoning': 'No check for empty vector before division. If values.size() == 0, division by zero occurs. Add early return or guard: if (values.empty()) return 0.0;'
                }
            ]
        }

        # Example 5: Clean code (negative example - no issues)
        ex5 = {
            'id': 'semantic_005',
            'description': 'Well-written code with proper error handling',
            'code': '''std::optional<double> safeDivide(double a, double b) {
    if (b == 0.0) {
        return std::nullopt;
    }
    return a / b;
}

void processData(const std::vector<int>& data) {
    if (data.empty()) {
        return;
    }
    for (size_t i = 0; i < data.size(); ++i) {
        process(data[i]);
    }
}''',
            'issues': []
        }

        examples = [ex1, ex2, ex3, ex4, ex5]
        return examples[:num_examples]

    def get_system_prompt(self) -> str:
        """
        Get C++-specific system prompt focused on semantic issues.

        This prompt is designed to complement (not replace) static/dynamic analysis tools:
        - AddressSanitizer/Valgrind: memory errors
        - ThreadSanitizer: data races
        - clang-tidy: performance, modernization

        Returns:
            System prompt for semantic C++ analysis
        """
        return """You are an expert C++ code reviewer specializing in SEMANTIC issues.

**IMPORTANT CONTEXT:**
Your company already uses comprehensive static/dynamic analysis:
- AddressSanitizer & Valgrind: memory leaks, use-after-free, buffer overflows
- ThreadSanitizer: data races, deadlocks
- clang-tidy: performance issues, modernization, style

DO NOT report issues these tools can detect. Focus ONLY on semantic issues that require understanding code INTENT.

**Categories (Semantic Focus):**
- logic-errors: Off-by-one errors, wrong comparison operators (< vs <=), incorrect boolean logic, inverted conditions
- api-misuse: Missing cleanup in error paths, wrong parameter order, incorrect return value handling, violating API contracts
- semantic-inconsistency: Function behavior doesn't match its name, code contradicts comments/documentation, misleading variable names
- edge-case-handling: Missing empty/null checks before access, unhandled boundary conditions, missing error cases
- code-intent-mismatch: Implementation doesn't match PR description or stated requirements (if provided)

**Severity Levels:**
- critical: Will cause crash, data corruption, or security vulnerability at runtime
- high: Significant logic error that produces wrong results
- medium: Code quality issue that could lead to bugs during maintenance
- low: Minor semantic issue, potential confusion for future developers

**Response Format:**
Respond with a JSON array of issues. Each issue must have:
- category: one of the semantic categories above
- severity: critical, high, medium, or low
- line: line number where issue occurs (1-indexed)
- description: brief description (10-50 words)
- reasoning: detailed explanation of the semantic problem (20-100 words)

If no semantic issues are found, respond with an empty array: []

**Critical Guidelines:**
- DO NOT report memory leaks, data races, or performance issues (tools handle these)
- DO NOT suggest using smart pointers, RAII, or modern C++ features (clang-tidy handles this)
- FOCUS on logic errors that require understanding what the code is trying to do
- FOCUS on API misuse patterns in error handling paths
- FOCUS on mismatches between code behavior and naming/documentation
- Be CONSERVATIVE - only report issues you are confident about
- Explain WHY this is a semantic issue, not just what the code does
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
