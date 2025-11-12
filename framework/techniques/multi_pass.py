"""
Multi-pass self-critique technique.

Makes two LLM calls: first to detect issues, second to review and filter false positives.
Research hypothesis: -20% false positives through self-critique.
"""

import json
from typing import List
from framework.models import AnalysisRequest, AnalysisResult, Issue
from framework.techniques.base import MultiPassTechnique


class MultiPassSelfCritiqueTechnique(MultiPassTechnique):
    """
    Multi-pass technique with self-critique.

    Pass 1: Initial detection (be thorough, err on side of finding issues)
    Pass 2: Self-critique (review findings, assign confidence, filter low confidence)

    This reduces false positives by having the LLM critique its own work.
    Only issues with confidence >= threshold are kept.
    """

    @property
    def name(self) -> str:
        """Technique identifier."""
        return "multi_pass"

    def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """
        Two-pass analysis with self-critique.

        Args:
            request: Analysis request

        Returns:
            AnalysisResult with filtered issues and confidence scores
        """
        # Pass 1: Initial detection
        pass1_result = self._pass1_detect(request)

        # If no issues found in pass 1, return empty result
        if not pass1_result.issues:
            return pass1_result

        # Pass 2: Self-critique
        pass2_result = self._pass2_critique(request, pass1_result.issues)

        # Combine metadata from both passes
        metadata = {
            **pass2_result.metadata,
            'pass1_issues': len(pass1_result.issues),
            'pass2_issues': len(pass2_result.issues),
            'pass1_tokens': pass1_result.metadata.get('tokens_used', 0),
            'pass2_tokens': pass2_result.metadata.get('tokens_used', 0),
            'total_tokens': (
                pass1_result.metadata.get('tokens_used', 0) +
                pass2_result.metadata.get('tokens_used', 0)
            ),
            'pass1_latency': pass1_result.metadata.get('latency', 0),
            'pass2_latency': pass2_result.metadata.get('latency', 0),
            'total_latency': (
                pass1_result.metadata.get('latency', 0) +
                pass2_result.metadata.get('latency', 0)
            ),
            'confidence_threshold': self.technique_params.get('confidence_threshold', 0.6),
            'technique_name': self.name
        }

        return AnalysisResult(
            issues=pass2_result.issues,
            metadata=metadata,
            raw_response=f"PASS 1:\n{pass1_result.raw_response}\n\nPASS 2:\n{pass2_result.raw_response}"
        )

    def _pass1_detect(self, request: AnalysisRequest) -> AnalysisResult:
        """
        Pass 1: Initial thorough detection.

        Args:
            request: Analysis request

        Returns:
            AnalysisResult from first pass
        """
        system_prompt = self.technique_params.get(
            'pass1_prompt',
            self.technique_params.get('system_prompt', '')
        )

        user_prompt = f"""Analyze this C++ code for potential issues:

```cpp
{request.code}
```

Be thorough - look for any potential issues, even if you're not 100% certain.
Respond with a JSON array of issues.
"""

        return self.client.analyze_code(
            request=request,
            system_prompt=system_prompt,
            user_prompt_template=user_prompt
        )

    def _pass2_critique(self, request: AnalysisRequest, pass1_issues: List[Issue]) -> AnalysisResult:
        """
        Pass 2: Self-critique and confidence scoring.

        Args:
            request: Original analysis request
            pass1_issues: Issues from first pass

        Returns:
            AnalysisResult with filtered issues and confidence scores
        """
        # Format pass1 issues as JSON for the prompt
        issues_json = json.dumps(
            [issue.model_dump() for issue in pass1_issues],
            indent=2
        )

        system_prompt = self.technique_params.get(
            'pass2_prompt',
            self.technique_params.get('system_prompt', '')
        )

        # Replace placeholder with pass1 issues
        system_prompt = system_prompt.replace('{PASS1_ISSUES}', issues_json)

        user_prompt = f"""Original code:
```cpp
{request.code}
```

Review each issue critically and assign confidence scores (0.0-1.0).
Remove false positives. Keep only high-confidence issues.
"""

        # Get critique result
        critique_response = self.client.generate(
            prompt=user_prompt,
            system_prompt=system_prompt
        )

        # Parse issues with confidence scores
        issues_with_confidence = self.client.parse_issues_from_response(
            critique_response['response']
        )

        # Filter by confidence threshold
        threshold = self.technique_params.get('confidence_threshold', 0.6)
        filtered_issues = [
            issue for issue in issues_with_confidence
            if issue.confidence is None or issue.confidence >= threshold
        ]

        metadata = {
            'model': critique_response['model'],
            'tokens_used': critique_response['tokens_used'],
            'latency': critique_response['latency']
        }

        return AnalysisResult(
            issues=filtered_issues,
            metadata=metadata,
            raw_response=critique_response['response']
        )
