"""
Chain-of-thought technique.

Requires explicit step-by-step reasoning before providing answers.
Research hypothesis: +30% complex bug detection through structured thinking.
"""

from framework.models import AnalysisRequest, AnalysisResult
from framework.techniques.base import SinglePassTechnique


class ChainOfThoughtTechnique(SinglePassTechnique):
    """
    Chain-of-thought prompting technique.

    Instructs the LLM to think step-by-step before identifying issues:
    1. What is the code doing?
    2. What could go wrong?
    3. Under what conditions would this fail?
    4. What category and severity?

    The explicit reasoning process helps the LLM catch complex issues
    that might be missed with direct pattern matching.

    The LLM is asked to show its reasoning in <thinking> tags before
    providing the JSON response.
    """

    @property
    def name(self) -> str:
        """Technique identifier."""
        return "chain_of_thought"

    def _build_user_prompt(self, code: str) -> str:
        """
        Build prompt that requires explicit reasoning.

        Args:
            code: Code to analyze

        Returns:
            User prompt with chain-of-thought instructions
        """
        return f"""Analyze this C++ code using step-by-step reasoning:

```cpp
{code}
```

For each potential issue, think through:
1. What is this code doing?
2. What could go wrong?
3. Under what conditions would this fail?
4. What category does this belong to?
5. How severe is it?

First, show your reasoning in <thinking>...</thinking> tags.
Then, provide your final answer as a JSON array of issues.

Example format:
<thinking>
Looking at line 1, I see a pointer allocated with 'new'.
Let me trace its lifecycle... I don't see a corresponding 'delete'.
This means the memory will leak. This is a memory-safety issue
with critical severity since it happens on every execution.
</thinking>

[{{"category": "memory-safety", "severity": "critical", ...}}]

Now analyze the code above:
"""

    def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """
        Analyze with chain-of-thought and extract reasoning.

        Args:
            request: Analysis request

        Returns:
            AnalysisResult with issues and reasoning extracted
        """
        # Use parent's single-pass implementation
        result = super().analyze(request)

        # Extract thinking from response if present
        if result.raw_response and '<thinking>' in result.raw_response:
            thinking_start = result.raw_response.find('<thinking>')
            thinking_end = result.raw_response.find('</thinking>')

            if thinking_start != -1 and thinking_end != -1:
                thinking = result.raw_response[thinking_start + 10:thinking_end].strip()
                result.metadata['chain_of_thought_reasoning'] = thinking

        return result
