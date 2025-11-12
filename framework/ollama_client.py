"""
Ollama client for LLM interactions.

Provides a clean interface to Ollama with token counting, timing, and error handling.
"""

import time
import json
from typing import Dict, Any, Optional
import ollama
from framework.models import AnalysisRequest, AnalysisResult, Issue


class OllamaClient:
    """
    Client for interacting with Ollama LLMs.

    Handles:
    - Model availability checking
    - Prompt generation
    - Response parsing
    - Token counting (estimated)
    - Timing/latency tracking
    - Error handling
    """

    def __init__(self, model_name: str, temperature: float = 0.1, max_tokens: int = 2000):
        """
        Initialize Ollama client.

        Args:
            model_name: Name of the Ollama model (e.g., "deepseek-coder:33b")
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens in response
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = ollama.Client()

    def check_model_available(self) -> bool:
        """
        Check if the model is available in Ollama.

        Returns:
            True if model is available, False otherwise
        """
        try:
            models = self.client.list()
            available_models = [model.model for model in models.get('models', [])]
            return self.model_name in available_models
        except Exception as e:
            print(f"Error checking model availability: {e}")
            return False

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate a response from the LLM.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Override default temperature
            max_tokens: Override default max_tokens

        Returns:
            Dictionary with:
                - response: Raw text response
                - tokens_used: Estimated tokens (prompt + completion)
                - latency: Time taken in seconds
                - model: Model name
        """
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens

        # Build messages
        messages = []
        if system_prompt:
            messages.append({
                'role': 'system',
                'content': system_prompt
            })
        messages.append({
            'role': 'user',
            'content': prompt
        })

        # Time the request
        start_time = time.time()

        try:
            response = self.client.chat(
                model=self.model_name,
                messages=messages,
                options={
                    'temperature': temp,
                    'num_predict': max_tok
                }
            )

            latency = time.time() - start_time

            # Extract response text
            response_text = response.get('message', {}).get('content', '')

            # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
            prompt_tokens = self._estimate_tokens(prompt)
            if system_prompt:
                prompt_tokens += self._estimate_tokens(system_prompt)
            completion_tokens = self._estimate_tokens(response_text)
            total_tokens = prompt_tokens + completion_tokens

            return {
                'response': response_text,
                'tokens_used': total_tokens,
                'latency': latency,
                'model': self.model_name,
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens
            }

        except Exception as e:
            latency = time.time() - start_time
            return {
                'response': '',
                'tokens_used': 0,
                'latency': latency,
                'model': self.model_name,
                'error': str(e)
            }

    def parse_json_response(self, response_text: str) -> list:
        """
        Parse JSON array from LLM response.

        Handles responses with extra text around the JSON.

        Args:
            response_text: Raw LLM response

        Returns:
            Parsed JSON array (list of dicts) or empty list if parsing fails
        """
        # Try to find JSON array in the response
        response_text = response_text.strip()

        # Look for JSON array markers
        start_idx = response_text.find('[')
        end_idx = response_text.rfind(']')

        if start_idx == -1 or end_idx == -1:
            # No JSON array found
            return []

        json_str = response_text[start_idx:end_idx + 1]

        try:
            issues_data = json.loads(json_str)
            if isinstance(issues_data, list):
                return issues_data
            return []
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response text: {response_text[:200]}...")
            return []

    def parse_issues_from_response(self, response_text: str) -> list[Issue]:
        """
        Parse Issue objects from JSON response.

        Args:
            response_text: Raw LLM response containing JSON array

        Returns:
            List of Issue objects
        """
        issues_data = self.parse_json_response(response_text)
        issues = []

        for issue_dict in issues_data:
            try:
                # Validate required fields
                required_fields = ['category', 'severity', 'line', 'description', 'reasoning']
                if not all(field in issue_dict for field in required_fields):
                    print(f"Skipping issue with missing fields: {issue_dict}")
                    continue

                # Create Issue object (Pydantic will validate)
                issue = Issue(**issue_dict)
                issues.append(issue)

            except Exception as e:
                print(f"Error parsing issue: {e}")
                print(f"Issue data: {issue_dict}")
                continue

        return issues

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count from text.

        Uses rough approximation: 1 token ≈ 4 characters.
        This is conservative and tends to overestimate.

        Args:
            text: Input text

        Returns:
            Estimated token count
        """
        return len(text) // 4

    def analyze_code(
        self,
        request: AnalysisRequest,
        system_prompt: str,
        user_prompt_template: str
    ) -> AnalysisResult:
        """
        Analyze code and return structured result.

        Args:
            request: Analysis request with code and metadata
            system_prompt: System prompt for the LLM
            user_prompt_template: Template for user prompt (with {CODE} placeholder)

        Returns:
            AnalysisResult with detected issues and metadata
        """
        # Build user prompt
        user_prompt = user_prompt_template.replace('{CODE}', request.code)

        # Generate response
        result = self.generate(
            prompt=user_prompt,
            system_prompt=system_prompt
        )

        # Parse issues
        issues = []
        if 'error' not in result:
            issues = self.parse_issues_from_response(result['response'])

        # Build metadata
        metadata = {
            'model': result['model'],
            'tokens_used': result['tokens_used'],
            'prompt_tokens': result.get('prompt_tokens', 0),
            'completion_tokens': result.get('completion_tokens', 0),
            'latency': result['latency'],
            'temperature': self.temperature,
            'prompt': system_prompt + '\n\n' + user_prompt
        }

        if 'error' in result:
            metadata['error'] = result['error']

        return AnalysisResult(
            issues=issues,
            metadata=metadata,
            raw_response=result['response']
        )


class OllamaClientFactory:
    """Factory for creating Ollama clients with proper configuration."""

    @staticmethod
    def create_from_config(config: dict) -> OllamaClient:
        """
        Create OllamaClient from experiment config.

        Args:
            config: Experiment configuration dict

        Returns:
            Configured OllamaClient
        """
        model_name = config.get('model_name', 'deepseek-coder:33b')
        params = config.get('technique_params', {})
        temperature = params.get('temperature', 0.1)
        max_tokens = params.get('max_tokens', 2000)

        return OllamaClient(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens
        )

    @staticmethod
    def check_all_models_available(model_names: list[str]) -> Dict[str, bool]:
        """
        Check availability of multiple models.

        Args:
            model_names: List of model names to check

        Returns:
            Dictionary mapping model name to availability
        """
        results = {}
        client = ollama.Client()

        try:
            models = client.list()
            available_models = [model.model for model in models.get('models', [])]

            for model_name in model_names:
                results[model_name] = model_name in available_models

        except Exception as e:
            print(f"Error checking models: {e}")
            for model_name in model_names:
                results[model_name] = False

        return results
