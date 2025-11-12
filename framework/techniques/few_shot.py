"""
Few-shot learning technique.

Provides high-quality annotated examples to guide the LLM.
Research hypothesis: +30-40% accuracy improvement over zero-shot.
"""

import json
from framework.models import AnalysisRequest, AnalysisResult
from framework.techniques.base import SinglePassTechnique


class FewShotTechnique(SinglePassTechnique):
    """
    Few-shot learning technique.

    Includes 3-5 high-quality examples in the prompt to demonstrate:
    - What issues look like
    - How to format responses
    - What level of detail is expected
    - Both positive (issues found) and negative (clean code) examples

    The number of examples is configurable via technique_params['few_shot_examples'].
    """

    @property
    def name(self) -> str:
        """Technique identifier."""
        examples = self.technique_params.get('few_shot_examples', [])
        return f"few_shot_{len(examples)}"

    def _build_user_prompt(self, code: str) -> str:
        """
        Build prompt with few-shot examples followed by target code.

        Args:
            code: Code to analyze

        Returns:
            User prompt with examples and target code
        """
        examples = self.technique_params.get('few_shot_examples', [])

        if not examples:
            # Fallback to zero-shot if no examples provided
            return f"Analyze this code:\n\n```cpp\n{code}\n```"

        # Build examples section
        examples_text = "Here are some examples:\n\n"

        for i, example in enumerate(examples, 1):
            ex_code = example.get('code', '')
            ex_issues = example.get('issues', [])
            ex_id = example.get('id', f'example_{i}')
            ex_desc = example.get('description', '')

            examples_text += f"Example {i} ({ex_id}):\n"
            if ex_desc:
                examples_text += f"Description: {ex_desc}\n"

            examples_text += f"```cpp\n{ex_code}\n```\n\n"

            if ex_issues:
                examples_text += f"Issues found:\n{json.dumps(ex_issues, indent=2)}\n\n"
            else:
                examples_text += "Issues found: [] (clean code)\n\n"

            examples_text += "---\n\n"

        # Build target code section
        target_text = f"""Now analyze this target code:

```cpp
{code}
```

Respond with a JSON array of issues found. If no issues, respond with [].
"""

        return examples_text + target_text

    def _extract_metadata(self):
        """Add example count to metadata."""
        metadata = super()._extract_metadata()
        examples = self.technique_params.get('few_shot_examples', [])
        metadata['num_examples'] = len(examples)
        return metadata
