"""
Statistical analysis for comparing LLM techniques.

Provides A/B testing with t-tests, p-values, and effect sizes to determine
if differences between techniques are statistically significant.
"""

from typing import List, Dict, Any, Tuple
import numpy as np
from scipy import stats

from framework.models import MetricsResult, ComparisonResult


class StatisticalAnalyzer:
    """
    Performs statistical significance testing for technique comparisons.

    Uses t-tests to determine if performance differences are statistically
    significant (p < 0.05) or just random variation.
    """

    def __init__(self, significance_level: float = 0.05):
        """
        Initialize statistical analyzer.

        Args:
            significance_level: p-value threshold for significance (default 0.05)
        """
        self.significance_level = significance_level

    def compare_techniques(
        self,
        technique_a_name: str,
        technique_b_name: str,
        metrics_a: MetricsResult,
        metrics_b: MetricsResult,
        sample_scores_a: List[float],
        sample_scores_b: List[float]
    ) -> ComparisonResult:
        """
        Compare two techniques with statistical testing.

        Args:
            technique_a_name: Name of first technique
            technique_b_name: Name of second technique
            metrics_a: Aggregate metrics for technique A
            metrics_b: Aggregate metrics for technique B
            sample_scores_a: Per-example F1 scores for technique A
            sample_scores_b: Per-example F1 scores for technique B

        Returns:
            ComparisonResult with winner and statistical significance
        """
        # Perform t-test
        t_statistic, p_value = self._paired_t_test(sample_scores_a, sample_scores_b)

        # Calculate effect size (Cohen's d)
        effect_size = self._cohens_d(sample_scores_a, sample_scores_b)

        # Determine winner
        is_significant = p_value < self.significance_level
        if not is_significant:
            winner = "tie"
        elif metrics_b.f1 > metrics_a.f1:
            winner = technique_b_name
        else:
            winner = technique_a_name

        # Build statistical significance dict
        statistical_significance = {
            't_statistic': float(t_statistic),
            'p_value': float(p_value),
            'effect_size': float(effect_size),
            'is_significant': is_significant,
            'significance_level': self.significance_level,
            'interpretation': self._interpret_results(
                p_value,
                effect_size,
                metrics_a.f1,
                metrics_b.f1
            )
        }

        return ComparisonResult(
            technique_a=technique_a_name,
            technique_b=technique_b_name,
            metrics_a=metrics_a,
            metrics_b=metrics_b,
            statistical_significance=statistical_significance,
            winner=winner
        )

    def _paired_t_test(
        self,
        samples_a: List[float],
        samples_b: List[float]
    ) -> Tuple[float, float]:
        """
        Perform paired t-test (assumes samples are from same examples).

        Args:
            samples_a: Scores for technique A
            samples_b: Scores for technique B

        Returns:
            Tuple of (t_statistic, p_value)
        """
        if len(samples_a) != len(samples_b):
            raise ValueError("Sample sizes must match for paired t-test")

        if len(samples_a) < 2:
            # Not enough data for meaningful test
            return 0.0, 1.0

        t_stat, p_val = stats.ttest_rel(samples_a, samples_b)
        return t_stat, p_val

    def _cohens_d(
        self,
        samples_a: List[float],
        samples_b: List[float]
    ) -> float:
        """
        Calculate Cohen's d effect size.

        Effect size interpretation:
        - Small: 0.2
        - Medium: 0.5
        - Large: 0.8+

        Args:
            samples_a: Scores for technique A
            samples_b: Scores for technique B

        Returns:
            Cohen's d effect size
        """
        if len(samples_a) < 2 or len(samples_b) < 2:
            return 0.0

        mean_a = np.mean(samples_a)
        mean_b = np.mean(samples_b)
        std_a = np.std(samples_a, ddof=1)
        std_b = np.std(samples_b, ddof=1)

        # Pooled standard deviation
        n_a = len(samples_a)
        n_b = len(samples_b)
        pooled_std = np.sqrt(((n_a - 1) * std_a**2 + (n_b - 1) * std_b**2) / (n_a + n_b - 2))

        if pooled_std == 0:
            return 0.0

        cohens_d = (mean_b - mean_a) / pooled_std
        return cohens_d

    def _interpret_results(
        self,
        p_value: float,
        effect_size: float,
        f1_a: float,
        f1_b: float
    ) -> str:
        """
        Generate human-readable interpretation of statistical results.

        Args:
            p_value: Statistical significance
            effect_size: Cohen's d
            f1_a: F1 score for technique A
            f1_b: F1 score for technique B

        Returns:
            Human-readable interpretation string
        """
        # Effect size interpretation
        abs_effect = abs(effect_size)
        if abs_effect < 0.2:
            effect_desc = "negligible"
        elif abs_effect < 0.5:
            effect_desc = "small"
        elif abs_effect < 0.8:
            effect_desc = "medium"
        else:
            effect_desc = "large"

        # Statistical significance
        if p_value >= self.significance_level:
            return (
                f"No statistically significant difference (p={p_value:.3f}). "
                f"The {abs(f1_b - f1_a):.1%} difference in F1 scores "
                f"could be due to random variation."
            )

        # Determine which technique is better
        better = "B" if f1_b > f1_a else "A"
        improvement = abs(f1_b - f1_a) / f1_a * 100 if f1_a > 0 else 0

        return (
            f"Technique {better} is statistically significantly better "
            f"(p={p_value:.3f}, {effect_desc} effect size). "
            f"Performance improvement: {improvement:.1f}%."
        )

    def bootstrap_confidence_interval(
        self,
        samples: List[float],
        n_bootstrap: int = 1000,
        confidence_level: float = 0.95
    ) -> Tuple[float, float]:
        """
        Calculate bootstrap confidence interval for mean.

        Args:
            samples: Sample scores
            n_bootstrap: Number of bootstrap iterations
            confidence_level: Confidence level (default 0.95 for 95% CI)

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        if len(samples) < 2:
            return (0.0, 0.0)

        bootstrap_means = []
        for _ in range(n_bootstrap):
            resample = np.random.choice(samples, size=len(samples), replace=True)
            bootstrap_means.append(np.mean(resample))

        alpha = 1 - confidence_level
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100

        lower = np.percentile(bootstrap_means, lower_percentile)
        upper = np.percentile(bootstrap_means, upper_percentile)

        return lower, upper

    def generate_comparison_report(
        self,
        comparison: ComparisonResult
    ) -> str:
        """
        Generate a formatted report for a technique comparison.

        Args:
            comparison: ComparisonResult from compare_techniques

        Returns:
            Formatted string report
        """
        report = []
        report.append("=" * 70)
        report.append("TECHNIQUE COMPARISON REPORT")
        report.append("=" * 70)
        report.append(f"\nTechnique A: {comparison.technique_a}")
        report.append(f"Technique B: {comparison.technique_b}")
        report.append(f"\n{'-' * 70}")
        report.append("PERFORMANCE METRICS")
        report.append(f"{'-' * 70}")

        # Metrics table
        report.append(f"{'Metric':<20} {'Technique A':>15} {'Technique B':>15} {'Difference':>15}")
        report.append(f"{'-' * 70}")

        metrics_pairs = [
            ("Precision", comparison.metrics_a.precision, comparison.metrics_b.precision),
            ("Recall", comparison.metrics_a.recall, comparison.metrics_b.recall),
            ("F1 Score", comparison.metrics_a.f1, comparison.metrics_b.f1),
            ("Token Efficiency", comparison.metrics_a.token_efficiency, comparison.metrics_b.token_efficiency),
            ("Latency (s)", comparison.metrics_a.latency, comparison.metrics_b.latency),
        ]

        for name, val_a, val_b in metrics_pairs:
            diff = val_b - val_a
            diff_pct = (diff / val_a * 100) if val_a > 0 else 0
            sign = "+" if diff > 0 else ""
            report.append(
                f"{name:<20} {val_a:>15.3f} {val_b:>15.3f} "
                f"{sign}{diff:>10.3f} ({sign}{diff_pct:.1f}%)"
            )

        # Statistical significance
        report.append(f"\n{'-' * 70}")
        report.append("STATISTICAL SIGNIFICANCE")
        report.append(f"{'-' * 70}")
        sig = comparison.statistical_significance
        report.append(f"p-value: {sig['p_value']:.4f}")
        report.append(f"Effect size (Cohen's d): {sig['effect_size']:.3f}")
        report.append(f"Statistically significant: {sig['is_significant']}")
        report.append(f"\nInterpretation:")
        report.append(f"{sig['interpretation']}")

        # Winner
        report.append(f"\n{'-' * 70}")
        report.append("CONCLUSION")
        report.append(f"{'-' * 70}")
        if comparison.winner == "tie":
            report.append("Result: TIE (no significant difference)")
        else:
            report.append(f"Winner: {comparison.winner}")
            report.append(f"F1 Improvement: {comparison.f1_improvement:+.1f}%")
            report.append(f"Token Efficiency Improvement: {comparison.token_efficiency_improvement:+.1f}%")

        report.append("=" * 70)

        return "\n".join(report)
