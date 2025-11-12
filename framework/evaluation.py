"""
Evaluation infrastructure for measuring LLM technique effectiveness.

This module provides ground truth dataset loading and metrics calculation.
"""

import json
from pathlib import Path
from typing import List, Dict, Set, Tuple
from framework.models import GroundTruthExample, Issue, AnalysisResult, MetricsResult


class GroundTruthDataset:
    """
    Loads and manages ground truth annotated examples for evaluation.

    Ground truth examples are JSON files with expected issues annotated by humans.
    This class provides methods to load, filter, and access these examples.
    """

    def __init__(self, dataset_path: str):
        """
        Initialize dataset from a directory of JSON files.

        Args:
            dataset_path: Path to directory containing ground truth JSON files
        """
        self.dataset_path = Path(dataset_path)
        self.examples: List[GroundTruthExample] = []
        self._load_examples()

    def _load_examples(self) -> None:
        """Load all JSON files from dataset directory."""
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Dataset path not found: {self.dataset_path}")

        json_files = list(self.dataset_path.glob("*.json"))
        if not json_files:
            raise ValueError(f"No JSON files found in {self.dataset_path}")

        for json_file in sorted(json_files):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    example = GroundTruthExample(**data)
                    self.examples.append(example)
            except Exception as e:
                raise ValueError(f"Failed to load {json_file}: {e}")

    def get_all(self) -> List[GroundTruthExample]:
        """Get all examples in the dataset."""
        return self.examples

    def get_by_id(self, example_id: str) -> GroundTruthExample:
        """Get a specific example by ID."""
        for example in self.examples:
            if example.id == example_id:
                return example
        raise KeyError(f"Example not found: {example_id}")

    def filter_by_category(self, category: str) -> List[GroundTruthExample]:
        """Get all examples that contain at least one issue of the given category."""
        return [
            ex for ex in self.examples
            if any(issue.category == category for issue in ex.expected_issues)
        ]

    def get_clean_examples(self) -> List[GroundTruthExample]:
        """Get all examples with no expected issues (negative examples)."""
        return [ex for ex in self.examples if ex.is_clean]

    def get_examples_with_issues(self) -> List[GroundTruthExample]:
        """Get all examples with at least one expected issue."""
        return [ex for ex in self.examples if not ex.is_clean]

    @property
    def size(self) -> int:
        """Total number of examples in dataset."""
        return len(self.examples)

    @property
    def category_distribution(self) -> Dict[str, int]:
        """Count of examples per category."""
        counts: Dict[str, int] = {}
        for example in self.examples:
            for category in example.category_counts.keys():
                counts[category] = counts.get(category, 0) + 1
        return counts


class MetricsCalculator:
    """
    Calculates precision, recall, F1, and token efficiency metrics.

    Compares LLM-detected issues against ground truth expected issues to compute
    evaluation metrics. Uses fuzzy matching for line numbers (±1 tolerance) and
    exact matching for categories.
    """

    def __init__(self, line_tolerance: int = 1):
        """
        Initialize metrics calculator.

        Args:
            line_tolerance: Allow line number to differ by this amount for matching
        """
        self.line_tolerance = line_tolerance

    def calculate_metrics(
        self,
        ground_truth: GroundTruthExample,
        analysis_result: AnalysisResult
    ) -> Dict[str, any]:
        """
        Calculate metrics for a single example.

        Args:
            ground_truth: Expected issues
            analysis_result: LLM-detected issues

        Returns:
            Dictionary with TP, FP, FN counts and metrics
        """
        expected = ground_truth.expected_issues
        detected = analysis_result.issues

        # Match detected issues to expected issues
        tp, fp, fn = self._match_issues(expected, detected)

        # Calculate metrics
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        return {
            'true_positives': tp,
            'false_positives': fp,
            'false_negatives': fn,
            'precision': precision,
            'recall': recall,
            'f1': f1
        }

    def calculate_aggregate_metrics(
        self,
        experiment_id: str,
        ground_truth_examples: List[GroundTruthExample],
        analysis_results: List[AnalysisResult],
        total_tokens: int,
        total_latency: float
    ) -> MetricsResult:
        """
        Calculate aggregate metrics across all examples in an experiment.

        Args:
            experiment_id: Unique experiment identifier
            ground_truth_examples: List of ground truth examples
            analysis_results: List of corresponding analysis results
            total_tokens: Total tokens consumed across all examples
            total_latency: Total time spent across all examples

        Returns:
            MetricsResult with overall and per-category metrics
        """
        if len(ground_truth_examples) != len(analysis_results):
            raise ValueError("Ground truth and results must have same length")

        # Aggregate counts
        total_tp = 0
        total_fp = 0
        total_fn = 0
        category_stats: Dict[str, Dict[str, int]] = {}

        for gt, result in zip(ground_truth_examples, analysis_results):
            metrics = self.calculate_metrics(gt, result)
            total_tp += metrics['true_positives']
            total_fp += metrics['false_positives']
            total_fn += metrics['false_negatives']

            # Per-category tracking
            for issue in gt.expected_issues:
                cat = issue.category
                if cat not in category_stats:
                    category_stats[cat] = {'tp': 0, 'fp': 0, 'fn': 0}

            # Match issues by category for per-category metrics
            for expected in gt.expected_issues:
                matched = False
                for detected in result.issues:
                    if self._issues_match(expected, detected):
                        category_stats[expected.category]['tp'] += 1
                        matched = True
                        break
                if not matched:
                    category_stats[expected.category]['fn'] += 1

            # Count FP by category
            for detected in result.issues:
                matched = False
                for expected in gt.expected_issues:
                    if self._issues_match(expected, detected):
                        matched = True
                        break
                if not matched:
                    cat = detected.category
                    if cat not in category_stats:
                        category_stats[cat] = {'tp': 0, 'fp': 0, 'fn': 0}
                    category_stats[cat]['fp'] += 1

        # Calculate overall metrics
        precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
        recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        # Calculate per-category metrics
        per_category_metrics: Dict[str, Dict[str, float]] = {}
        for cat, stats in category_stats.items():
            tp, fp, fn = stats['tp'], stats['fp'], stats['fn']
            cat_precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            cat_recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            cat_f1 = (2 * cat_precision * cat_recall) / (cat_precision + cat_recall) if (cat_precision + cat_recall) > 0 else 0.0
            per_category_metrics[cat] = {
                'precision': cat_precision,
                'recall': cat_recall,
                'f1': cat_f1
            }

        # Token efficiency: issues found per 1K tokens
        total_issues_found = total_tp  # Only count true positives
        token_efficiency = (total_issues_found / (total_tokens / 1000.0)) if total_tokens > 0 else 0.0

        # Average latency
        avg_latency = total_latency / len(ground_truth_examples) if len(ground_truth_examples) > 0 else 0.0

        return MetricsResult(
            experiment_id=experiment_id,
            precision=precision,
            recall=recall,
            f1=f1,
            token_efficiency=token_efficiency,
            latency=avg_latency,
            total_tokens=total_tokens,
            per_category_metrics=per_category_metrics,
            confusion_matrix={
                'true_positives': total_tp,
                'false_positives': total_fp,
                'false_negatives': total_fn
            }
        )

    def _match_issues(
        self,
        expected: List[Issue],
        detected: List[Issue]
    ) -> Tuple[int, int, int]:
        """
        Match detected issues to expected issues and count TP, FP, FN.

        Returns:
            Tuple of (true_positives, false_positives, false_negatives)
        """
        expected_matched: Set[int] = set()
        detected_matched: Set[int] = set()

        # Find true positives
        for i, exp_issue in enumerate(expected):
            for j, det_issue in enumerate(detected):
                if j in detected_matched:
                    continue
                if self._issues_match(exp_issue, det_issue):
                    expected_matched.add(i)
                    detected_matched.add(j)
                    break

        tp = len(expected_matched)
        fp = len(detected) - len(detected_matched)
        fn = len(expected) - len(expected_matched)

        return tp, fp, fn

    def _issues_match(self, expected: Issue, detected: Issue) -> bool:
        """
        Check if two issues match (same category and nearby line number).

        Args:
            expected: Ground truth issue
            detected: LLM-detected issue

        Returns:
            True if issues match within tolerance
        """
        # Must have same category
        if expected.category != detected.category:
            return False

        # Line number must be within tolerance
        line_diff = abs(expected.line - detected.line)
        if line_diff <= self.line_tolerance:
            return True

        return False
