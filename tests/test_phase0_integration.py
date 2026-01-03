"""
Phase 0 Integration Test

Verifies that all Phase 0 components work together:
1. Pydantic models validate correctly
2. Ground truth dataset loads successfully
3. Metrics calculator computes correct metrics
4. Prompt logger logs interactions
5. Experiment config loads from YAML

This is the exit gate for Phase 0 - all tests must pass before proceeding to Phase 1.
"""

import pytest
import json
from pathlib import Path
import yaml
from datetime import datetime

from framework.models import (
    Issue,
    AnalysisRequest,
    AnalysisResult,
    GroundTruthExample,
    ExperimentConfig,
    MetricsResult,
    PromptLogEntry,
)
from framework.evaluation import GroundTruthDataset, MetricsCalculator
from framework.prompt_logger import PromptLogger


class TestPydanticModels:
    """Test that all Pydantic models validate correctly."""

    def test_issue_validation(self):
        """Test Issue model with valid and invalid data."""
        # Valid issue
        issue = Issue(
            category="logic-errors",
            severity="critical",
            line=10,
            description="Off-by-one error detected",
            reasoning="Loop condition uses <= instead of <"
        )
        assert issue.category == "logic-errors"
        assert issue.severity == "critical"
        assert issue.line == 10

        # Invalid category
        with pytest.raises(ValueError):
            Issue(
                category="invalid-category",
                severity="critical",
                line=10,
                description="Test",
                reasoning="Test reasoning"
            )

        # Invalid severity
        with pytest.raises(ValueError):
            Issue(
                category="logic-errors",
                severity="invalid",
                line=10,
                description="Test",
                reasoning="Test reasoning"
            )

        # Invalid line number (must be >= 1)
        with pytest.raises(ValueError):
            Issue(
                category="logic-errors",
                severity="critical",
                line=0,
                description="Test",
                reasoning="Test reasoning"
            )

    def test_category_normalization(self):
        """Test that categories are normalized to allowed values."""
        # Test 'code-quality' -> 'edge-case-handling'
        issue = Issue(
            category="code-quality",
            severity="medium",
            line=10,
            description="Division by zero potential",
            reasoning="No empty check before division"
        )
        assert issue.category == "edge-case-handling"

        # Test 'logic-error' -> 'logic-errors' (singular to plural)
        issue2 = Issue(
            category="logic-error",
            severity="high",
            line=20,
            description="Off-by-one error in loop",
            reasoning="Loop uses <= instead of <"
        )
        assert issue2.category == "logic-errors"

        # Test 'resource-leak' -> 'api-misuse'
        issue3 = Issue(
            category="resource-leak",
            severity="high",
            line=30,
            description="File handle not closed",
            reasoning="File opened but not closed in error path"
        )
        assert issue3.category == "api-misuse"

        # Test case-insensitive normalization
        issue4 = Issue(
            category="CODE-QUALITY",
            severity="medium",
            line=40,
            description="Missing null check before use",
            reasoning="Pointer used without null check"
        )
        assert issue4.category == "edge-case-handling"

        # Test that completely invalid categories still fail
        with pytest.raises(ValueError):
            Issue(
                category="completely-unknown-category-xyz",
                severity="critical",
                line=10,
                description="Test description here",
                reasoning="Test reasoning here"
            )

    def test_analysis_result(self):
        """Test AnalysisResult model."""
        result = AnalysisResult(
            issues=[
                Issue(
                    category="logic-errors",
                    severity="critical",
                    line=5,
                    description="Off-by-one error detected",
                    reasoning="Loop condition allows out of bounds access"
                )
            ],
            metadata={"tokens_used": 500, "latency": 1.2},
            raw_response="[...]"
        )

        assert result.issue_count == 1
        assert result.critical_count == 1
        assert result.metadata["tokens_used"] == 500

    def test_ground_truth_example(self):
        """Test GroundTruthExample model."""
        example = GroundTruthExample(
            id="test_001",
            description="Test example",
            code="for (int i = 0; i <= v.size(); i++) { sum += v[i]; }",
            file_path="test.cpp",
            expected_issues=[
                Issue(
                    category="logic-errors",
                    severity="critical",
                    line=1,
                    description="Off-by-one error in loop",
                    reasoning="Loop uses <= instead of <, causing out of bounds access"
                )
            ]
        )

        assert not example.is_clean
        assert example.category_counts == {"logic-errors": 1}

        # Clean example
        clean_example = GroundTruthExample(
            id="test_clean",
            description="Clean code",
            code="std::unique_ptr<int> ptr;",
            file_path="clean.cpp",
            expected_issues=[]
        )
        assert clean_example.is_clean

    def test_metrics_result(self):
        """Test MetricsResult model and overall_score calculation."""
        metrics = MetricsResult(
            experiment_id="test_exp",
            precision=0.9,
            recall=0.85,
            f1=0.875,
            token_efficiency=5.0,
            latency=1.5,
            total_tokens=10000,
            per_category_metrics={}
        )

        # Overall score = 0.7 * f1 + 0.3 * normalized_efficiency
        # normalized_efficiency = min(5.0 / 10.0, 1.0) = 0.5
        # overall_score = 0.7 * 0.875 + 0.3 * 0.5 = 0.6125 + 0.15 = 0.7625
        assert abs(metrics.overall_score - 0.7625) < 0.001


class TestGroundTruthDataset:
    """Test ground truth dataset loading."""

    def test_load_dataset(self):
        """Test loading ground truth dataset from docs/research/experiments/ground_truth/cpp."""
        dataset = GroundTruthDataset("docs/research/experiments/ground_truth/cpp")

        # Should have 20 examples
        assert dataset.size == 20, f"Expected 20 examples, got {dataset.size}"

        # Should be able to get all examples
        examples = dataset.get_all()
        assert len(examples) == 20

        # Verify example structure
        for example in examples:
            assert isinstance(example, GroundTruthExample)
            assert example.id
            assert example.code
            assert example.file_path
            assert isinstance(example.expected_issues, list)

    def test_dataset_filtering(self):
        """Test dataset filtering by category and clean/issues."""
        dataset = GroundTruthDataset("docs/research/experiments/ground_truth/cpp")

        # Filter by category (using first available category in dataset)
        examples = dataset.get_examples_with_issues()
        if examples:
            first_category = examples[0].expected_issues[0].category
            filtered_examples = dataset.filter_by_category(first_category)
            assert len(filtered_examples) > 0
            for ex in filtered_examples:
                assert any(issue.category == first_category for issue in ex.expected_issues)

        # Get clean examples (negative examples with no issues)
        clean_examples = dataset.get_clean_examples()
        assert len(clean_examples) > 0
        for ex in clean_examples:
            assert len(ex.expected_issues) == 0

        # Get examples with issues
        issue_examples = dataset.get_examples_with_issues()
        assert len(issue_examples) > 0
        for ex in issue_examples:
            assert len(ex.expected_issues) > 0

    def test_category_distribution(self):
        """Test category distribution calculation."""
        dataset = GroundTruthDataset("docs/research/experiments/ground_truth/cpp")
        distribution = dataset.category_distribution

        # Should have semantic categories (Phase 1 update: new categories)
        # The actual categories will depend on the ground truth dataset
        # This test verifies the distribution is non-empty and categories are valid
        assert len(distribution) > 0
        valid_categories = {
            "logic-errors", "api-misuse", "semantic-inconsistency",
            "edge-case-handling", "code-intent-mismatch",
            # Also allow old categories during transition
            "memory-safety", "modern-cpp", "performance", "security", "concurrency"
        }
        for category in distribution.keys():
            assert category in valid_categories, f"Unknown category: {category}"


class TestMetricsCalculator:
    """Test metrics calculation."""

    def test_perfect_match(self):
        """Test metrics with perfect detection (TP=1, FP=0, FN=0)."""
        calculator = MetricsCalculator(line_tolerance=1)

        ground_truth = GroundTruthExample(
            id="test",
            description="Test",
            code="code",
            file_path="test.cpp",
            expected_issues=[
                Issue(
                    category="logic-errors",
                    severity="critical",
                    line=10,
                    description="Off-by-one error detected",
                    reasoning="Loop uses <= instead of < causing bounds error"
                )
            ]
        )

        analysis_result = AnalysisResult(
            issues=[
                Issue(
                    category="logic-errors",
                    severity="critical",
                    line=10,
                    description="Off-by-one error detected",
                    reasoning="Loop uses <= instead of < causing bounds error"
                )
            ]
        )

        metrics = calculator.calculate_metrics(ground_truth, analysis_result)

        assert metrics['true_positives'] == 1
        assert metrics['false_positives'] == 0
        assert metrics['false_negatives'] == 0
        assert metrics['precision'] == 1.0
        assert metrics['recall'] == 1.0
        assert metrics['f1'] == 1.0

    def test_false_positive(self):
        """Test metrics with false positive (TP=0, FP=1, FN=1)."""
        calculator = MetricsCalculator(line_tolerance=1)

        ground_truth = GroundTruthExample(
            id="test",
            description="Test",
            code="code",
            file_path="test.cpp",
            expected_issues=[
                Issue(
                    category="logic-errors",
                    severity="critical",
                    line=10,
                    description="Real logic error",
                    reasoning="This is a real logic error that needs fixing"
                )
            ]
        )

        # Detected wrong category
        analysis_result = AnalysisResult(
            issues=[
                Issue(
                    category="api-misuse",  # Wrong category!
                    severity="low",
                    line=10,
                    description="Wrong detection here",
                    reasoning="This is a false positive detection by the system"
                )
            ]
        )

        metrics = calculator.calculate_metrics(ground_truth, analysis_result)

        assert metrics['true_positives'] == 0
        assert metrics['false_positives'] == 1
        assert metrics['false_negatives'] == 1
        assert metrics['precision'] == 0.0
        assert metrics['recall'] == 0.0

    def test_line_tolerance(self):
        """Test that line tolerance allows nearby matches."""
        calculator = MetricsCalculator(line_tolerance=1)

        ground_truth = GroundTruthExample(
            id="test",
            description="Test",
            code="code",
            file_path="test.cpp",
            expected_issues=[
                Issue(
                    category="logic-errors",
                    severity="critical",
                    line=10,
                    description="Logic error detected",
                    reasoning="This is a logic error issue"
                )
            ]
        )

        # Detected at line 11 (within tolerance)
        analysis_result = AnalysisResult(
            issues=[
                Issue(
                    category="logic-errors",
                    severity="critical",
                    line=11,  # Off by 1
                    description="Logic error detected",
                    reasoning="This is a logic error detected nearby"
                )
            ]
        )

        metrics = calculator.calculate_metrics(ground_truth, analysis_result)

        # Should still count as true positive
        assert metrics['true_positives'] == 1
        assert metrics['precision'] == 1.0


class TestPromptLogger:
    """Test prompt logging."""

    def test_log_interaction(self, tmp_path):
        """Test logging an LLM interaction."""
        logger = PromptLogger(
            log_dir=str(tmp_path),
            experiment_id="test_exp"
        )

        logger.log_interaction(
            example_id="ex001",
            technique_name="zero_shot",
            model_name="test-model",
            prompt="Analyze this code",
            response="[{...}]",
            tokens_used=500,
            latency=1.5,
            metadata={"test": True}
        )

        assert len(logger.get_entries()) == 1
        assert logger.get_total_tokens() == 500
        assert logger.get_total_latency() == 1.5

        # Verify log file was created
        log_file = tmp_path / "test_exp_prompts.jsonl"
        assert log_file.exists()

        # Verify can reload from file
        loaded_entries = PromptLogger.load_from_file(str(log_file))
        assert len(loaded_entries) == 1
        assert loaded_entries[0].example_id == "ex001"


class TestExperimentConfig:
    """Test experiment configuration loading."""

    def test_load_zero_shot_config(self):
        """Test loading zero_shot.yml config."""
        config_path = Path("docs/research/experiments/configs/zero_shot.yml")
        assert config_path.exists(), f"Config file not found: {config_path}"

        with open(config_path) as f:
            data = yaml.safe_load(f)

        # Verify required fields
        assert data['experiment_id'] == 'zero_shot_baseline'
        assert data['technique_name'] == 'zero_shot'
        assert data['model_name'] == 'deepseek-coder:33b-instruct'
        assert data['dataset_path'] == 'docs/research/experiments/ground_truth/cpp'
        assert 'technique_params' in data

    def test_load_all_configs(self):
        """Test that all experiment configs are valid YAML."""
        config_dir = Path("docs/research/experiments/configs")
        config_files = list(config_dir.glob("*.yml"))

        assert len(config_files) >= 7, f"Expected at least 7 configs, found {len(config_files)}"

        for config_file in config_files:
            with open(config_file) as f:
                data = yaml.safe_load(f)

            # Verify required fields
            assert 'experiment_id' in data
            assert 'technique_name' in data
            assert 'model_name' in data
            assert 'dataset_path' in data
            assert 'technique_params' in data

            print(f"✓ {config_file.name} is valid")


class TestPhase0ExitGate:
    """Phase 0 exit gate - all systems integrated."""

    def test_all_components_integrated(self):
        """Verify all Phase 0 components can work together."""

        # 1. Load dataset
        dataset = GroundTruthDataset("docs/research/experiments/ground_truth/cpp")
        assert dataset.size == 20

        # 2. Get first example
        example = dataset.get_all()[0]
        assert isinstance(example, GroundTruthExample)

        # 3. Simulate analysis result
        result = AnalysisResult(
            issues=example.expected_issues,  # Perfect detection for this test
            metadata={"tokens_used": 500, "latency": 1.2}
        )

        # 4. Calculate metrics
        calculator = MetricsCalculator()
        metrics = calculator.calculate_metrics(example, result)
        assert metrics['precision'] == 1.0  # Perfect match

        # 5. Log interaction
        import tempfile
        with tempfile.TemporaryDirectory() as tmp_dir:
            logger = PromptLogger(tmp_dir, "integration_test")
            logger.log_interaction(
                example_id=example.id,
                technique_name="test",
                model_name="test-model",
                prompt="test prompt",
                response="test response",
                tokens_used=500,
                latency=1.2
            )
            assert logger.get_total_tokens() == 500

        print("\n✅ Phase 0 Integration Test: ALL SYSTEMS OPERATIONAL")
        print("   - Pydantic models: ✓")
        print("   - Ground truth dataset: ✓")
        print("   - Metrics calculator: ✓")
        print("   - Prompt logger: ✓")
        print("   - Config loader: ✓")
        print("\n🚀 READY TO PROCEED TO PHASE 1")


if __name__ == "__main__":
    # Run with: pytest tests/test_phase0_integration.py -v
    pytest.main([__file__, "-v", "-s"])
