"""
Pydantic models for LLM framework data structures.

These models provide runtime validation and type safety for all framework components.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


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
        Validate category is one of the allowed semantic-focused values.

        These categories focus on issues that require understanding code intent
        and cannot be detected by static/dynamic analysis tools (ASan, TSan, clang-tidy).
        """
        allowed = {
            'logic-errors',           # Off-by-one, wrong operators, boolean logic mistakes
            'api-misuse',             # Wrong API usage, missing cleanup in error paths
            'semantic-inconsistency', # Code behavior doesn't match naming/docs
            'edge-case-handling',     # Missing boundary checks, unhandled edge cases
            'code-intent-mismatch'    # Code doesn't match PR description/requirements
        }
        if v not in allowed:
            raise ValueError(f"Category must be one of {allowed}, got '{v}'")
        return v

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
