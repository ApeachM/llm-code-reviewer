"""
Pydantic models for LLM framework data structures.

These models provide runtime validation and type safety for all framework components.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


# Category normalization mapping: maps common LLM category variations to allowed categories
CATEGORY_NORMALIZATION_MAP: Dict[str, str] = {
    # Direct mappings (allowed categories)
    'logic-errors': 'logic-errors',
    'api-misuse': 'api-misuse',
    'semantic-inconsistency': 'semantic-inconsistency',
    'edge-case-handling': 'edge-case-handling',
    'code-intent-mismatch': 'code-intent-mismatch',

    # Common variations -> edge-case-handling
    'code-quality': 'edge-case-handling',
    'error-handling': 'edge-case-handling',
    'null-check': 'edge-case-handling',
    'boundary-check': 'edge-case-handling',
    'division-by-zero': 'edge-case-handling',
    'empty-check': 'edge-case-handling',
    'input-validation': 'edge-case-handling',

    # Common variations -> logic-errors
    'logic-error': 'logic-errors',
    'logical-error': 'logic-errors',
    'off-by-one': 'logic-errors',
    'boolean-logic': 'logic-errors',
    'integer-division': 'logic-errors',
    'arithmetic-error': 'logic-errors',
    'operator-error': 'logic-errors',

    # Common variations -> api-misuse
    'resource-leak': 'api-misuse',
    'memory-leak': 'api-misuse',
    'file-leak': 'api-misuse',
    'api-usage': 'api-misuse',
    'cleanup-missing': 'api-misuse',

    # Common variations -> semantic-inconsistency
    'naming-issue': 'semantic-inconsistency',
    'side-effect': 'semantic-inconsistency',
    'documentation-mismatch': 'semantic-inconsistency',
    'misleading-name': 'semantic-inconsistency',

    # Common variations -> code-intent-mismatch
    'requirement-mismatch': 'code-intent-mismatch',
    'specification-mismatch': 'code-intent-mismatch',
}

ALLOWED_CATEGORIES = {
    'logic-errors',           # Off-by-one, wrong operators, boolean logic mistakes
    'api-misuse',             # Wrong API usage, missing cleanup in error paths
    'semantic-inconsistency', # Code behavior doesn't match naming/docs
    'edge-case-handling',     # Missing boundary checks, unhandled edge cases
    'code-intent-mismatch'    # Code doesn't match PR description/requirements
}


def normalize_category(category: str) -> str:
    """
    Normalize a category string to one of the allowed categories.

    Args:
        category: Raw category string from LLM

    Returns:
        Normalized category string

    Raises:
        ValueError: If category cannot be normalized
    """
    # Lowercase and strip whitespace
    normalized = category.lower().strip()

    # Direct lookup
    if normalized in CATEGORY_NORMALIZATION_MAP:
        return CATEGORY_NORMALIZATION_MAP[normalized]

    # Try with hyphens replaced by underscores and vice versa
    alt_normalized = normalized.replace('_', '-')
    if alt_normalized in CATEGORY_NORMALIZATION_MAP:
        return CATEGORY_NORMALIZATION_MAP[alt_normalized]

    alt_normalized = normalized.replace('-', '_')
    if alt_normalized in CATEGORY_NORMALIZATION_MAP:
        return CATEGORY_NORMALIZATION_MAP[alt_normalized]

    # Fuzzy matching based on keywords
    if 'logic' in normalized or 'boolean' in normalized or 'operator' in normalized:
        return 'logic-errors'
    if 'api' in normalized or 'resource' in normalized or 'leak' in normalized:
        return 'api-misuse'
    if 'semantic' in normalized or 'naming' in normalized or 'side' in normalized:
        return 'semantic-inconsistency'
    if 'edge' in normalized or 'boundary' in normalized or 'empty' in normalized or 'null' in normalized:
        return 'edge-case-handling'
    if 'intent' in normalized or 'requirement' in normalized or 'mismatch' in normalized:
        return 'code-intent-mismatch'

    # Default fallback for quality-related terms
    if 'quality' in normalized or 'check' in normalized or 'validation' in normalized:
        return 'edge-case-handling'

    raise ValueError(f"Cannot normalize category '{category}' to allowed categories: {ALLOWED_CATEGORIES}")


class Issue(BaseModel):
    """Represents a code issue detected by LLM analysis."""

    category: str = Field(
        ...,
        description="Issue category: logic-errors, api-misuse, semantic-inconsistency, edge-case-handling, code-intent-mismatch"
    )
    severity: str = Field(
        ...,
        description="Severity level: critical, high, medium, low"
    )
    line: int = Field(..., ge=1, description="Line number where issue occurs (1-indexed)")
    description: str = Field(..., min_length=10, description="Brief description of the issue")
    reasoning: str = Field(..., min_length=20, description="Detailed explanation of why this is an issue")
    suggested_fix: Optional[str] = Field(None, description="Optional suggestion for fixing the issue")
    confidence: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Confidence score from self-critique (0.0-1.0)"
    )

    @field_validator('category')
    @classmethod
    def validate_category(cls, v: str) -> str:
        """
        Validate and normalize category to one of the allowed semantic-focused values.

        These categories focus on issues that require understanding code intent
        and cannot be detected by static/dynamic analysis tools (ASan, TSan, clang-tidy).

        Category normalization is applied to handle common LLM variations:
        - 'code-quality' -> 'edge-case-handling'
        - 'logic-error' -> 'logic-errors'
        - etc.
        """
        try:
            return normalize_category(v)
        except ValueError:
            raise ValueError(f"Category must be one of {ALLOWED_CATEGORIES}, got '{v}'")

    @field_validator('severity')
    @classmethod
    def validate_severity(cls, v: str) -> str:
        """Validate severity is one of the allowed values."""
        allowed = {'critical', 'high', 'medium', 'low'}
        if v not in allowed:
            raise ValueError(f"Severity must be one of {allowed}, got '{v}'")
        return v


class AnalysisRequest(BaseModel):
    """Request for LLM code analysis."""

    code: str = Field(..., min_length=1, description="Code to analyze")
    file_path: str = Field(..., description="Path to the file being analyzed")
    language: str = Field(default="cpp", description="Programming language (cpp, rtl, etc.)")
    context: Optional[str] = Field(None, description="Additional context (e.g., diff, surrounding code)")
    technique_config: Optional[Dict[str, Any]] = Field(
        None,
        description="Configuration for the technique being used (e.g., few_shot examples)"
    )


class AnalysisResult(BaseModel):
    """Result of LLM code analysis."""

    issues: List[Issue] = Field(default_factory=list, description="List of detected issues")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata about the analysis (tokens, latency, model, etc.)"
    )
    raw_response: Optional[str] = Field(None, description="Raw LLM response for debugging")

    @property
    def issue_count(self) -> int:
        """Total number of issues detected."""
        return len(self.issues)

    @property
    def critical_count(self) -> int:
        """Number of critical severity issues."""
        return sum(1 for issue in self.issues if issue.severity == 'critical')


class GroundTruthExample(BaseModel):
    """Annotated example for evaluation."""

    id: str = Field(..., description="Unique identifier for the example")
    description: str = Field(..., description="Human-readable description")
    code: str = Field(..., min_length=1, description="Code snippet")
    file_path: str = Field(..., description="Virtual file path")
    expected_issues: List[Issue] = Field(
        default_factory=list,
        description="List of expected issues (empty for clean code)"
    )

    @property
    def is_clean(self) -> bool:
        """Returns True if this is a negative example (no issues expected)."""
        return len(self.expected_issues) == 0

    @property
    def category_counts(self) -> Dict[str, int]:
        """Count issues by category."""
        counts: Dict[str, int] = {}
        for issue in self.expected_issues:
            counts[issue.category] = counts.get(issue.category, 0) + 1
        return counts


class ExperimentConfig(BaseModel):
    """Configuration for an experiment run."""

    experiment_id: str = Field(..., description="Unique experiment identifier")
    technique_name: str = Field(
        ...,
        description="Technique being tested (few_shot_3, multi_pass, chain_of_thought, etc.)"
    )
    model_name: str = Field(..., description="LLM model name (e.g., deepseek-coder:33b)")
    technique_params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters for the technique"
    )
    dataset_path: str = Field(..., description="Path to ground truth dataset")
    seed: Optional[int] = Field(None, description="Random seed for reproducibility")
    timestamp: datetime = Field(default_factory=datetime.now, description="Experiment start time")

    @property
    def run_id(self) -> str:
        """Generate unique run ID from experiment_id and timestamp."""
        return f"{self.experiment_id}_{self.timestamp.strftime('%Y%m%d_%H%M%S')}"


class MetricsResult(BaseModel):
    """Evaluation metrics for an experiment."""

    experiment_id: str = Field(..., description="Experiment identifier")
    precision: float = Field(..., ge=0.0, le=1.0, description="Precision score")
    recall: float = Field(..., ge=0.0, le=1.0, description="Recall score")
    f1: float = Field(..., ge=0.0, le=1.0, description="F1 score")
    token_efficiency: float = Field(
        ...,
        ge=0.0,
        description="Issues found per 1K tokens consumed"
    )
    latency: float = Field(..., ge=0.0, description="Average latency per example (seconds)")
    total_tokens: int = Field(..., ge=0, description="Total tokens consumed")
    per_category_metrics: Dict[str, Dict[str, float]] = Field(
        default_factory=dict,
        description="Metrics broken down by category (precision, recall, f1 per category)"
    )
    confusion_matrix: Optional[Dict[str, Any]] = Field(
        None,
        description="Confusion matrix data (TP, FP, TN, FN)"
    )

    @property
    def overall_score(self) -> float:
        """Weighted overall score: F1 (70%) + token_efficiency (30%)."""
        # Normalize token_efficiency to 0-1 scale (assume max 10 issues per 1K tokens)
        normalized_efficiency = min(self.token_efficiency / 10.0, 1.0)
        return (0.7 * self.f1) + (0.3 * normalized_efficiency)


class PromptLogEntry(BaseModel):
    """Log entry for a single LLM interaction."""

    timestamp: datetime = Field(default_factory=datetime.now)
    experiment_id: str
    example_id: str
    technique_name: str
    model_name: str
    prompt: str = Field(..., description="Full prompt sent to LLM")
    response: str = Field(..., description="Raw LLM response")
    tokens_used: int = Field(..., ge=0)
    latency: float = Field(..., ge=0.0, description="Response time in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ComparisonResult(BaseModel):
    """Result of comparing two techniques."""

    technique_a: str
    technique_b: str
    metrics_a: MetricsResult
    metrics_b: MetricsResult
    statistical_significance: Dict[str, Any] = Field(
        default_factory=dict,
        description="Statistical test results (t-test, p-value, effect size)"
    )
    winner: Optional[str] = Field(
        None,
        description="Which technique performed better (or 'tie' if no significant difference)"
    )

    @property
    def f1_improvement(self) -> float:
        """Percentage improvement in F1 score (positive if B better, negative if A better)."""
        if self.metrics_a.f1 == 0:
            return 0.0
        return ((self.metrics_b.f1 - self.metrics_a.f1) / self.metrics_a.f1) * 100

    @property
    def token_efficiency_improvement(self) -> float:
        """Percentage improvement in token efficiency."""
        if self.metrics_a.token_efficiency == 0:
            return 0.0
        return ((self.metrics_b.token_efficiency - self.metrics_a.token_efficiency) /
                self.metrics_a.token_efficiency) * 100
