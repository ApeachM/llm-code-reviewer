"""
Hybrid technique composition.

Combines multiple techniques for improved accuracy:
- Few-shot for broad coverage
- Chain-of-thought for complex categories
- Multi-pass self-critique for reducing false positives
"""

from typing import List, Dict, Any, Optional
from pathlib import Path

from framework.models import AnalysisRequest, AnalysisResult, Issue
from framework.techniques.base import BaseTechnique
from framework.techniques.few_shot import FewShotTechnique
from framework.techniques.chain_of_thought import ChainOfThoughtTechnique
from framework.ollama_client import OllamaClient


class HybridTechnique(BaseTechnique):
    """
    Hybrid technique combining multiple approaches.

    Strategy:
    1. Pass 1: Few-shot-5 for general issue detection (broad coverage)
    2. Pass 2: Chain-of-thought for specific categories (modern-cpp, performance)
    3. Pass 3: Self-critique to filter false positives

    Based on Phase 2 findings:
    - Few-shot-5: F1=0.615 (overall best)
    - Chain-of-thought: F1=0.727 on modern-cpp (vs 0.000 for few-shot)
    - Expected hybrid: F1~0.70+ (10-15% improvement)
    """

    def __init__(self, client: OllamaClient, config: Dict[str, Any]):
        """
        Initialize hybrid technique.

        Args:
            client: Ollama client
            config: Configuration with:
                - technique_params.few_shot_config: Config for few-shot pass
                - technique_params.cot_config: Config for chain-of-thought pass
                - technique_params.cot_categories: Categories to use CoT for (default: ['modern-cpp', 'performance'])
                - technique_params.confidence_threshold: Min confidence to keep issue (default: 0.6)
        """
        super().__init__(client, config)

        # Extract sub-configs
        technique_params = config.get('technique_params', {})
        few_shot_config = technique_params.get('few_shot_config', {})
        cot_config = technique_params.get('cot_config', {})

        # Pass 1: Few-shot technique
        self.few_shot = FewShotTechnique(client, {
            'technique_name': 'few_shot_5',
            'technique_params': few_shot_config
        })

        # Pass 2: Chain-of-thought technique
        self.cot = ChainOfThoughtTechnique(client, {
            'technique_name': 'chain_of_thought',
            'technique_params': cot_config
        })

        # Categories that benefit from chain-of-thought
        self.cot_categories = technique_params.get('cot_categories', ['modern-cpp', 'performance'])

        # Confidence threshold for filtering
        self.confidence_threshold = technique_params.get('confidence_threshold', 0.6)

    @property
    def name(self) -> str:
        """Technique name."""
        return "hybrid"

    def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """
        Analyze code using hybrid approach.

        Args:
            request: Analysis request

        Returns:
            Analysis result with deduplicated, confidence-scored issues
        """
        all_issues = []
        total_tokens = 0
        total_latency = 0.0

        # Pass 1: Few-shot for broad coverage
        few_shot_result = self.few_shot.analyze(request)
        all_issues.extend(few_shot_result.issues)
        total_tokens += few_shot_result.metadata.get('tokens_used', 0)
        total_latency += few_shot_result.metadata.get('latency', 0)

        # Pass 2: Chain-of-thought for specific categories
        # Only if we have CoT categories configured
        if self.cot_categories:
            cot_result = self._analyze_with_cot(request)
            if cot_result:
                # Add CoT issues (these are more accurate for specific categories)
                all_issues.extend(cot_result.issues)
                total_tokens += cot_result.metadata.get('tokens_used', 0)
                total_latency += cot_result.metadata.get('latency', 0)

        # Pass 3: Deduplicate and score confidence
        deduplicated_issues = self._deduplicate_issues(all_issues)
        scored_issues = self._score_confidence(deduplicated_issues)

        # Filter by confidence threshold
        filtered_issues = [
            issue for issue in scored_issues
            if getattr(issue, 'confidence', 1.0) >= self.confidence_threshold
        ]

        # Create result
        result = AnalysisResult(
            file_path=request.file_path,
            issues=filtered_issues,
            metadata={
                'technique': self.name,
                'tokens_used': total_tokens,
                'latency': total_latency,
                'pass1_issues': len(few_shot_result.issues),
                'pass2_issues': len(cot_result.issues) if cot_result else 0,
                'deduplicated': len(deduplicated_issues),
                'after_confidence_filter': len(filtered_issues)
            }
        )

        return result

    def _analyze_with_cot(self, request: AnalysisRequest) -> Optional[AnalysisResult]:
        """
        Run chain-of-thought analysis focused on specific categories.

        Args:
            request: Analysis request

        Returns:
            CoT analysis result or None
        """
        # Modify request to focus on CoT categories
        focused_prompt = self._create_focused_prompt(request.code)

        focused_request = AnalysisRequest(
            code=focused_prompt,
            file_path=request.file_path,
            language=request.language
        )

        try:
            result = self.cot.analyze(focused_request)

            # Filter to only CoT categories
            filtered_issues = [
                issue for issue in result.issues
                if issue.category in self.cot_categories
            ]

            result.issues = filtered_issues
            return result
        except Exception as e:
            # CoT can timeout or fail - gracefully handle
            print(f"CoT analysis failed: {e}")
            return None

    def _create_focused_prompt(self, code: str) -> str:
        """
        Create prompt focused on CoT categories.

        Args:
            code: Source code

        Returns:
            Focused prompt for CoT analysis
        """
        categories_str = ", ".join(self.cot_categories)
        return f"""Focus specifically on these categories: {categories_str}

Code to analyze:
```cpp
{code}
```

Look especially for:
- Modern C++ improvements (smart pointers, auto, range-for)
- Performance optimizations (unnecessary copies, efficient algorithms)
"""

    def _deduplicate_issues(self, issues: List[Issue]) -> List[Issue]:
        """
        Deduplicate issues from multiple passes.

        Two issues are duplicates if they:
        - Have the same line number
        - Have the same category
        - Have similar descriptions (fuzzy match)

        Args:
            issues: List of issues from all passes

        Returns:
            Deduplicated list
        """
        if not issues:
            return []

        # Group by (line, category)
        groups: Dict[tuple, List[Issue]] = {}
        for issue in issues:
            key = (issue.line, issue.category)
            if key not in groups:
                groups[key] = []
            groups[key].append(issue)

        # For each group, pick the best issue
        deduplicated = []
        for key, group in groups.items():
            if len(group) == 1:
                deduplicated.append(group[0])
            else:
                # Multiple issues at same line/category
                # Prefer CoT issues (more detailed reasoning)
                # Or pick the one with more detailed description
                best = max(group, key=lambda i: len(i.reasoning))
                deduplicated.append(best)

        return deduplicated

    def _score_confidence(self, issues: List[Issue]) -> List[Issue]:
        """
        Score confidence for each issue.

        Confidence heuristics:
        - Issue detected by both few-shot AND CoT: confidence = 0.95
        - Issue from CoT only (for CoT categories): confidence = 0.85
        - Issue from few-shot only: confidence = 0.7
        - Critical severity: +0.05 boost
        - Low severity: -0.1 penalty

        Args:
            issues: List of issues

        Returns:
            Issues with confidence scores added
        """
        # This is a simplified heuristic
        # In production, could use:
        # - LLM self-assessment ("How confident are you? 0-1")
        # - Historical accuracy by category
        # - Ensemble voting across multiple runs

        for issue in issues:
            # Base confidence
            confidence = 0.7

            # Adjust by severity
            if issue.severity == 'critical':
                confidence += 0.05
            elif issue.severity == 'low':
                confidence -= 0.1

            # Clamp to [0, 1]
            confidence = max(0.0, min(1.0, confidence))

            # Add confidence attribute
            issue.confidence = confidence

        return issues


class SpecializedHybridTechnique(HybridTechnique):
    """
    Specialized hybrid for specific use cases.

    Example: HighPrecisionHybrid for PR reviews (minimize false positives)
    """

    def __init__(self, client: OllamaClient, config: Dict[str, Any]):
        # Higher confidence threshold for PR reviews
        if 'confidence_threshold' not in config.get('technique_params', {}):
            config.setdefault('technique_params', {})['confidence_threshold'] = 0.75

        super().__init__(client, config)


class CategorySpecializedHybrid(BaseTechnique):
    """
    Hybrid that routes to different techniques based on category.

    Strategy:
    - memory-safety, security → Few-shot (high F1 already)
    - modern-cpp, performance → Chain-of-thought (much better)
    - concurrency → Few-shot (CoT failed on this)
    """

    def __init__(self, client: OllamaClient, config: Dict[str, Any]):
        super().__init__(client, config)

        technique_params = config.get('technique_params', {})

        # Create techniques
        self.few_shot = FewShotTechnique(client, {
            'technique_name': 'few_shot_5',
            'technique_params': technique_params.get('few_shot_config', {})
        })

        self.cot = ChainOfThoughtTechnique(client, {
            'technique_name': 'chain_of_thought',
            'technique_params': technique_params.get('cot_config', {})
        })

        # Category routing (based on Phase 2 results)
        self.cot_categories = {'modern-cpp', 'performance'}
        self.few_shot_categories = {'memory-safety', 'security', 'concurrency'}

    @property
    def name(self) -> str:
        return "category_specialized_hybrid"

    def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """
        Analyze using category-specific routing.

        Args:
            request: Analysis request

        Returns:
            Analysis result
        """
        all_issues = []
        total_tokens = 0
        total_latency = 0.0

        # Run few-shot for its strong categories
        few_shot_result = self._analyze_few_shot_categories(request)
        if few_shot_result:
            all_issues.extend(few_shot_result.issues)
            total_tokens += few_shot_result.metadata.get('tokens_used', 0)
            total_latency += few_shot_result.metadata.get('latency', 0)

        # Run CoT for its strong categories
        cot_result = self._analyze_cot_categories(request)
        if cot_result:
            all_issues.extend(cot_result.issues)
            total_tokens += cot_result.metadata.get('tokens_used', 0)
            total_latency += cot_result.metadata.get('latency', 0)

        return AnalysisResult(
            file_path=request.file_path,
            issues=all_issues,
            metadata={
                'technique': self.name,
                'tokens_used': total_tokens,
                'latency': total_latency,
                'few_shot_issues': len(few_shot_result.issues) if few_shot_result else 0,
                'cot_issues': len(cot_result.issues) if cot_result else 0
            }
        )

    def _analyze_few_shot_categories(self, request: AnalysisRequest) -> Optional[AnalysisResult]:
        """Analyze using few-shot for its strong categories."""
        try:
            result = self.few_shot.analyze(request)
            # Filter to few-shot categories
            result.issues = [
                issue for issue in result.issues
                if issue.category in self.few_shot_categories
            ]
            return result
        except Exception as e:
            print(f"Few-shot analysis failed: {e}")
            return None

    def _analyze_cot_categories(self, request: AnalysisRequest) -> Optional[AnalysisResult]:
        """Analyze using CoT for its strong categories."""
        try:
            result = self.cot.analyze(request)
            # Filter to CoT categories
            result.issues = [
                issue for issue in result.issues
                if issue.category in self.cot_categories
            ]
            return result
        except Exception as e:
            print(f"CoT analysis failed: {e}")
            return None
