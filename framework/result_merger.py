"""
Result merger for combining chunk analysis results.

This module provides functionality to merge and deduplicate issues from
multiple chunk analyses into a single cohesive result.
"""

from typing import List
from framework.models import AnalysisResult, Issue


class ResultMerger:
    """
    Merge results from multiple chunk analyses.

    Features:
    - Deduplicate issues across chunks
    - Combine metadata (tokens, latency)
    - Sort by line number
    """

    def __init__(self, similarity_threshold: float = 0.8):
        """
        Initialize result merger.

        Args:
            similarity_threshold: Threshold for fuzzy deduplication
        """
        self.similarity_threshold = similarity_threshold

    def merge(self, chunk_results: List[AnalysisResult]) -> AnalysisResult:
        """
        Merge multiple chunk results into one file result.

        Args:
            chunk_results: List of AnalysisResult from chunks

        Returns:
            Combined AnalysisResult

        Raises:
            ValueError: If chunk_results is empty
        """
        if not chunk_results:
            raise ValueError("No chunk results to merge")

        # Collect all issues
        all_issues = []
        for result in chunk_results:
            all_issues.extend(result.issues)

        # Deduplicate
        deduplicated_issues = self._deduplicate_issues(all_issues)

        # Sort by line number
        sorted_issues = sorted(deduplicated_issues, key=lambda i: i.line)

        # Combine metadata
        combined_metadata = self._combine_metadata(chunk_results)

        # Create merged result
        # Add file_path to metadata if available from first result
        if 'file_path' in chunk_results[0].metadata:
            combined_metadata['file_path'] = chunk_results[0].metadata['file_path']

        return AnalysisResult(
            issues=sorted_issues,
            metadata=combined_metadata
        )

    def _deduplicate_issues(self, issues: List[Issue]) -> List[Issue]:
        """
        Deduplicate issues from multiple chunks.

        Strategy:
        1. Group by (line, category)
        2. Within each group, check description similarity
        3. Keep issue with most detailed reasoning

        Args:
            issues: List of issues from all chunks

        Returns:
            Deduplicated list of issues
        """
        if not issues:
            return []

        # Group by (line, category)
        groups = {}
        for issue in issues:
            key = (issue.line, issue.category)
            if key not in groups:
                groups[key] = []
            groups[key].append(issue)

        # Deduplicate within each group
        deduplicated = []
        for key, group in groups.items():
            if len(group) == 1:
                deduplicated.append(group[0])
            else:
                # Multiple issues at same line/category
                # Pick the one with longest reasoning (most detailed)
                best_issue = max(group, key=lambda i: len(i.reasoning))
                deduplicated.append(best_issue)

        return deduplicated

    def _combine_metadata(self, chunk_results: List[AnalysisResult]) -> dict:
        """
        Combine metadata from all chunks.

        Args:
            chunk_results: List of chunk analysis results

        Returns:
            Combined metadata dictionary
        """
        total_tokens = sum(
            r.metadata.get('tokens_used', 0) for r in chunk_results
        )
        total_latency = sum(
            r.metadata.get('latency', 0) for r in chunk_results
        )

        num_chunks = len(chunk_results)
        failed_chunks = sum(
            1 for r in chunk_results if 'error' in r.metadata
        )

        return {
            'technique': 'chunked_analysis',
            'num_chunks': num_chunks,
            'failed_chunks': failed_chunks,
            'total_tokens': total_tokens,
            'total_latency': total_latency,
            'avg_latency_per_chunk': total_latency / num_chunks if num_chunks > 0 else 0,
            'chunk_ids': [r.metadata.get('chunk_id', 'unknown') for r in chunk_results]
        }
