"""
Zero-shot technique - baseline with no examples.

This is the control group for measuring the effectiveness of other techniques.
"""

from framework.models import AnalysisRequest, AnalysisResult
from framework.techniques.base import SinglePassTechnique


class ZeroShotTechnique(SinglePassTechnique):
    """
    Zero-shot technique - no examples provided.

    The LLM receives only:
    - System prompt with task description
    - The code to analyze

    This establishes the baseline performance against which other
    techniques (few-shot, chain-of-thought, etc.) are measured.
    """

    @property
    def name(self) -> str:
        """Technique identifier."""
        return "zero_shot"

    def _build_user_prompt(self, code: str) -> str:
        """
        Build simple user prompt with just the code.

        Args:
            code: Code to analyze

        Returns:
            User prompt with code
        """
        return f"""Analyze this C++ code for issues:

```cpp
{code}
```

Respond with a JSON array of issues found. If no issues, respond with [].
"""
