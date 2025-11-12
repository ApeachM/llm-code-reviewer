"""
Base technique abstract class.

All LLM techniques must inherit from BaseTechnique and implement the analyze() method.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from framework.models import AnalysisRequest, AnalysisResult
from framework.ollama_client import OllamaClient


class BaseTechnique(ABC):
    """
    Abstract base class for all LLM analysis techniques.

    Each technique represents a different prompting strategy:
    - Zero-shot: No examples
    - Few-shot: Include examples in prompt
    - Chain-of-thought: Require explicit reasoning
    - Multi-pass: Self-critique for confidence scoring
    - Diff-focused: Focus on changed lines only

    All techniques share the same interface but differ in prompt construction.
    """

    def __init__(self, client: OllamaClient, config: Dict[str, Any]):
        """
        Initialize technique.

        Args:
            client: OllamaClient for LLM interactions
            config: Technique-specific configuration parameters
        """
        self.client = client
        self.config = config
        self.technique_params = config.get('technique_params', {})

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Technique name (e.g., 'zero_shot', 'few_shot_5').

        Returns:
            String identifier for this technique
        """
        pass

    @abstractmethod
    def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """
        Analyze code and return detected issues.

        This is the main entry point for all techniques. Each technique
        implements its own prompt construction strategy.

        Args:
            request: Analysis request with code and metadata

        Returns:
            AnalysisResult with detected issues and metadata
        """
        pass

    def _get_system_prompt(self) -> str:
        """
        Get system prompt from config.

        Returns:
            System prompt string
        """
        return self.technique_params.get('system_prompt', '')

    def _build_user_prompt(self, code: str) -> str:
        """
        Build user prompt with code.

        Default implementation just returns the code.
        Subclasses can override for more complex prompt construction.

        Args:
            code: Code to analyze

        Returns:
            User prompt string
        """
        return f"Analyze this code:\n\n```cpp\n{code}\n```"

    def _extract_metadata(self) -> Dict[str, Any]:
        """
        Extract technique-specific metadata.

        Returns:
            Dictionary of metadata
        """
        return {
            'technique_name': self.name,
            'technique_params': self.technique_params
        }


class SinglePassTechnique(BaseTechnique):
    """
    Base class for single-pass techniques (zero-shot, few-shot, chain-of-thought).

    These techniques make a single LLM call and parse the response.
    """

    def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """
        Single-pass analysis.

        Args:
            request: Analysis request

        Returns:
            AnalysisResult with detected issues
        """
        # Build prompts
        system_prompt = self._get_system_prompt()
        user_prompt = self._build_user_prompt(request.code)

        # Call LLM
        result = self.client.analyze_code(
            request=request,
            system_prompt=system_prompt,
            user_prompt_template=user_prompt
        )

        # Add technique metadata
        result.metadata.update(self._extract_metadata())

        return result


class MultiPassTechnique(BaseTechnique):
    """
    Base class for multi-pass techniques (self-critique, ensemble).

    These techniques make multiple LLM calls and combine results.
    """

    @abstractmethod
    def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """
        Multi-pass analysis with multiple LLM calls.

        Subclasses implement specific multi-pass strategies.

        Args:
            request: Analysis request

        Returns:
            AnalysisResult with detected issues
        """
        pass
