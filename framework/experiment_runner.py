"""
Experiment runner for A/B testing LLM techniques.

Orchestrates running experiments, collecting results, and computing metrics.
"""

from typing import List, Dict, Any, Optional, Protocol
from pathlib import Path
import time
from datetime import datetime

from framework.models import (
    ExperimentConfig,
    GroundTruthExample,
    AnalysisResult,
    MetricsResult,
    AnalysisRequest
)
from framework.evaluation import GroundTruthDataset, MetricsCalculator
from framework.prompt_logger import PromptLogger


class TechniqueProtocol(Protocol):
    """
    Protocol (interface) that all LLM techniques must implement.

    This enables modular technique development and testing.
    """

    def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """
        Analyze code and return detected issues.

        Args:
            request: Analysis request with code and configuration

        Returns:
            AnalysisResult with detected issues and metadata
        """
        ...

    @property
    def name(self) -> str:
        """Technique name (e.g., 'few_shot_5', 'multi_pass')."""
        ...


class ExperimentRunner:
    """
    Runs experiments to evaluate LLM techniques against ground truth.

    Orchestrates:
    1. Loading ground truth dataset
    2. Running technique on all examples
    3. Logging all prompts/responses
    4. Calculating metrics
    5. Saving results
    """

    def __init__(
        self,
        config: ExperimentConfig,
        technique: TechniqueProtocol,
        output_dir: str = "experiments/runs"
    ):
        """
        Initialize experiment runner.

        Args:
            config: Experiment configuration
            technique: Technique implementation to test
            output_dir: Directory to save experiment results
        """
        self.config = config
        self.technique = technique
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.dataset = GroundTruthDataset(config.dataset_path)
        self.calculator = MetricsCalculator(line_tolerance=1)
        self.logger = PromptLogger(
            log_dir=str(self.output_dir / config.run_id),
            experiment_id=config.experiment_id
        )

        # Results storage
        self.analysis_results: List[AnalysisResult] = []
        self.ground_truth_examples: List[GroundTruthExample] = []

    def run(self) -> MetricsResult:
        """
        Run the experiment on all examples in the dataset.

        Returns:
            MetricsResult with overall and per-category metrics
        """
        print(f"Starting experiment: {self.config.experiment_id}")
        print(f"Technique: {self.config.technique_name}")
        print(f"Model: {self.config.model_name}")
        print(f"Dataset: {self.config.dataset_path} ({self.dataset.size} examples)")
        print("-" * 60)

        start_time = time.time()

        # Run technique on each example
        for i, example in enumerate(self.dataset.get_all(), 1):
            print(f"[{i}/{self.dataset.size}] Analyzing {example.id}...")

            # Create analysis request
            request = AnalysisRequest(
                code=example.code,
                file_path=example.file_path,
                language="cpp",
                technique_config=self.config.technique_params
            )

            # Run technique and time it
            example_start = time.time()
            result = self.technique.analyze(request)
            example_latency = time.time() - example_start

            # Log the interaction (extract from result metadata)
            self.logger.log_interaction(
                example_id=example.id,
                technique_name=self.config.technique_name,
                model_name=self.config.model_name,
                prompt=result.metadata.get('prompt', ''),
                response=result.raw_response or '',
                tokens_used=result.metadata.get('tokens_used', 0),
                latency=example_latency,
                metadata={
                    'expected_issues': len(example.expected_issues),
                    'detected_issues': len(result.issues)
                }
            )

            # Store results
            self.analysis_results.append(result)
            self.ground_truth_examples.append(example)

            # Print quick summary
            print(f"  Expected: {len(example.expected_issues)} issues")
            print(f"  Detected: {len(result.issues)} issues")
            print(f"  Latency: {example_latency:.2f}s")

        total_time = time.time() - start_time

        # Calculate metrics
        print("-" * 60)
        print("Calculating metrics...")
        metrics = self.calculator.calculate_aggregate_metrics(
            experiment_id=self.config.experiment_id,
            ground_truth_examples=self.ground_truth_examples,
            analysis_results=self.analysis_results,
            total_tokens=self.logger.get_total_tokens(),
            total_latency=self.logger.get_total_latency()
        )

        # Print results
        print("\n" + "=" * 60)
        print("EXPERIMENT RESULTS")
        print("=" * 60)
        print(f"Precision: {metrics.precision:.3f}")
        print(f"Recall:    {metrics.recall:.3f}")
        print(f"F1 Score:  {metrics.f1:.3f}")
        print(f"Token Efficiency: {metrics.token_efficiency:.2f} issues/1K tokens")
        print(f"Avg Latency: {metrics.latency:.2f}s")
        print(f"Total Tokens: {metrics.total_tokens}")
        print(f"Total Time: {total_time:.2f}s")
        print("\nPer-Category Metrics:")
        for category, cat_metrics in metrics.per_category_metrics.items():
            print(f"  {category}:")
            print(f"    Precision: {cat_metrics['precision']:.3f}")
            print(f"    Recall:    {cat_metrics['recall']:.3f}")
            print(f"    F1:        {cat_metrics['f1']:.3f}")

        # Save results
        self._save_results(metrics)

        print(f"\nResults saved to: {self.output_dir / self.config.run_id}")
        print("=" * 60)

        return metrics

    def _save_results(self, metrics: MetricsResult) -> None:
        """Save experiment results to JSON file."""
        import json

        run_dir = self.output_dir / self.config.run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        # Save metrics
        metrics_file = run_dir / "metrics.json"
        with open(metrics_file, 'w', encoding='utf-8') as f:
            json.dump(metrics.model_dump(), f, indent=2, default=str)

        # Save config
        config_file = run_dir / "config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config.model_dump(), f, indent=2, default=str)

        # Save summary
        summary_file = run_dir / "summary.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"Experiment: {self.config.experiment_id}\n")
            f.write(f"Technique: {self.config.technique_name}\n")
            f.write(f"Model: {self.config.model_name}\n")
            f.write(f"Timestamp: {self.config.timestamp}\n")
            f.write(f"\nMetrics:\n")
            f.write(f"  Precision: {metrics.precision:.3f}\n")
            f.write(f"  Recall: {metrics.recall:.3f}\n")
            f.write(f"  F1: {metrics.f1:.3f}\n")
            f.write(f"  Token Efficiency: {metrics.token_efficiency:.2f}\n")
            f.write(f"  Latency: {metrics.latency:.2f}s\n")
            f.write(f"  Total Tokens: {metrics.total_tokens}\n")

    def get_results(self) -> List[AnalysisResult]:
        """Get analysis results for all examples."""
        return self.analysis_results

    def get_ground_truth(self) -> List[GroundTruthExample]:
        """Get ground truth examples used in this experiment."""
        return self.ground_truth_examples
