"""
Domain-Agnostic LLM Engineering Framework.

A research platform for discovering which LLM techniques work best for code analysis.
"""

from framework.models import (
    Issue,
    AnalysisRequest,
    AnalysisResult,
    GroundTruthExample,
    ExperimentConfig,
    MetricsResult,
    PromptLogEntry,
    ComparisonResult,
)

__version__ = "0.1.0"

__all__ = [
    "Issue",
    "AnalysisRequest",
    "AnalysisResult",
    "GroundTruthExample",
    "ExperimentConfig",
    "MetricsResult",
    "PromptLogEntry",
    "ComparisonResult",
]
