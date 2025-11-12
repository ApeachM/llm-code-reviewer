"""
LLM analysis techniques.

This package contains modular technique implementations for different
prompting strategies.
"""

from framework.techniques.base import BaseTechnique, SinglePassTechnique, MultiPassTechnique
from framework.techniques.zero_shot import ZeroShotTechnique
from framework.techniques.few_shot import FewShotTechnique
from framework.techniques.chain_of_thought import ChainOfThoughtTechnique
from framework.techniques.multi_pass import MultiPassSelfCritiqueTechnique
from framework.techniques.hybrid import HybridTechnique, SpecializedHybridTechnique, CategorySpecializedHybrid
from framework.ollama_client import OllamaClient, OllamaClientFactory
from typing import Dict, Any


class TechniqueFactory:
    """
    Factory for creating technique instances.

    Maps technique names to their implementation classes.
    """

    _TECHNIQUE_MAP = {
        'zero_shot': ZeroShotTechnique,
        'few_shot_3': FewShotTechnique,
        'few_shot_5': FewShotTechnique,
        'few_shot': FewShotTechnique,  # Generic few-shot
        'chain_of_thought': ChainOfThoughtTechnique,
        'multi_pass': MultiPassSelfCritiqueTechnique,
        'combined_best': FewShotTechnique,  # Uses few-shot as base
        'diff_focused': ZeroShotTechnique,  # Simplified for now
        # Phase 4: Hybrid techniques
        'hybrid': HybridTechnique,
        'hybrid_high_precision': SpecializedHybridTechnique,
        'hybrid_category_specialized': CategorySpecializedHybrid,
    }

    @classmethod
    def create(cls, technique_name: str, client: OllamaClient, config: Dict[str, Any]) -> BaseTechnique:
        """
        Create a technique instance.

        Args:
            technique_name: Name of the technique (from config)
            client: OllamaClient for LLM interactions
            config: Full experiment configuration

        Returns:
            Initialized technique instance

        Raises:
            ValueError: If technique name is not recognized
        """
        technique_class = cls._TECHNIQUE_MAP.get(technique_name)

        if technique_class is None:
            raise ValueError(
                f"Unknown technique: {technique_name}. "
                f"Available: {list(cls._TECHNIQUE_MAP.keys())}"
            )

        return technique_class(client, config)

    @classmethod
    def available_techniques(cls) -> list[str]:
        """
        Get list of available technique names.

        Returns:
            List of technique names
        """
        return list(cls._TECHNIQUE_MAP.keys())


__all__ = [
    'BaseTechnique',
    'SinglePassTechnique',
    'MultiPassTechnique',
    'ZeroShotTechnique',
    'FewShotTechnique',
    'ChainOfThoughtTechnique',
    'MultiPassSelfCritiqueTechnique',
    'HybridTechnique',
    'SpecializedHybridTechnique',
    'CategorySpecializedHybrid',
    'TechniqueFactory',
    'OllamaClient',
    'OllamaClientFactory',
]
