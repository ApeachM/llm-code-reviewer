"""
Prompt logging infrastructure for complete reproducibility.

Logs all LLM interactions with full prompts, responses, and metadata.
This enables debugging, prompt engineering, and full experiment reproducibility.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from framework.models import PromptLogEntry


class PromptLogger:
    """
    Logs all LLM prompts and responses for reproducibility and analysis.

    Creates timestamped log files with complete prompt history, enabling:
    - Full experiment reproducibility
    - Prompt engineering and debugging
    - Token usage analysis
    - Response time profiling
    """

    def __init__(self, log_dir: str, experiment_id: str):
        """
        Initialize prompt logger.

        Args:
            log_dir: Directory to store log files
            experiment_id: Unique experiment identifier
        """
        self.log_dir = Path(log_dir)
        self.experiment_id = experiment_id
        self.log_file = self.log_dir / f"{experiment_id}_prompts.jsonl"
        self.entries: List[PromptLogEntry] = []

        # Create log directory if it doesn't exist
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def log_interaction(
        self,
        example_id: str,
        technique_name: str,
        model_name: str,
        prompt: str,
        response: str,
        tokens_used: int,
        latency: float,
        metadata: Optional[dict] = None
    ) -> None:
        """
        Log a single LLM interaction.

        Args:
            example_id: ID of the example being analyzed
            technique_name: Name of the technique (e.g., "few_shot_5")
            model_name: LLM model name (e.g., "deepseek-coder:33b")
            prompt: Full prompt sent to the LLM
            response: Raw LLM response
            tokens_used: Number of tokens consumed
            latency: Response time in seconds
            metadata: Optional additional metadata
        """
        entry = PromptLogEntry(
            timestamp=datetime.now(),
            experiment_id=self.experiment_id,
            example_id=example_id,
            technique_name=technique_name,
            model_name=model_name,
            prompt=prompt,
            response=response,
            tokens_used=tokens_used,
            latency=latency,
            metadata=metadata or {}
        )

        self.entries.append(entry)
        self._write_entry(entry)

    def _write_entry(self, entry: PromptLogEntry) -> None:
        """Write a single entry to the log file (JSONL format)."""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(entry.model_dump_json() + '\n')

    def get_entries(self) -> List[PromptLogEntry]:
        """Get all logged entries for this session."""
        return self.entries

    def get_entries_for_example(self, example_id: str) -> List[PromptLogEntry]:
        """Get all entries for a specific example."""
        return [e for e in self.entries if e.example_id == example_id]

    def get_total_tokens(self) -> int:
        """Calculate total tokens used in this experiment."""
        return sum(e.tokens_used for e in self.entries)

    def get_total_latency(self) -> float:
        """Calculate total latency (seconds) for this experiment."""
        return sum(e.latency for e in self.entries)

    def get_average_latency(self) -> float:
        """Calculate average latency per interaction."""
        if not self.entries:
            return 0.0
        return self.get_total_latency() / len(self.entries)

    @staticmethod
    def load_from_file(log_file: str) -> List[PromptLogEntry]:
        """
        Load prompt log entries from a JSONL file.

        Args:
            log_file: Path to the log file

        Returns:
            List of PromptLogEntry objects
        """
        entries = []
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    entries.append(PromptLogEntry(**data))
        return entries

    def summary(self) -> dict:
        """Generate a summary of logged interactions."""
        if not self.entries:
            return {
                'total_interactions': 0,
                'total_tokens': 0,
                'total_latency': 0.0,
                'average_latency': 0.0
            }

        return {
            'experiment_id': self.experiment_id,
            'total_interactions': len(self.entries),
            'total_tokens': self.get_total_tokens(),
            'total_latency': self.get_total_latency(),
            'average_latency': self.get_average_latency(),
            'unique_examples': len(set(e.example_id for e in self.entries)),
            'log_file': str(self.log_file)
        }
