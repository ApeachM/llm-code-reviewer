"""
Chunk analyzer for analyzing code chunks independently.

This module provides functionality to analyze individual chunks with proper
context and line number adjustment.
"""

from pathlib import Path
from typing import List
from framework.models import AnalysisRequest, AnalysisResult, Issue
from framework.chunker import Chunk


class ChunkAnalyzer:
    """
    Analyze code chunks independently.

    Features:
    - Adds context to each chunk
    - Adjusts line numbers back to file coordinates
    - Supports parallel processing
    """

    def __init__(self, analyzer):
        """
        Initialize chunk analyzer.

        Args:
            analyzer: ProductionAnalyzer instance to use for analysis
        """
        self.analyzer = analyzer

    def analyze_chunk(self, chunk: Chunk) -> AnalysisResult:
        """
        Analyze a single chunk.

        Args:
            chunk: Chunk to analyze

        Returns:
            AnalysisResult with adjusted line numbers
        """
        # Combine context and code
        full_code = self._build_analysis_code(chunk)

        # Create analysis request
        request = AnalysisRequest(
            code=full_code,
            file_path=str(chunk.file_path),
            language='cpp'
        )

        # Analyze using existing technique
        result = self.analyzer.technique.analyze(request)

        # Adjust line numbers
        result = self._adjust_line_numbers(result, chunk)

        # Add chunk metadata
        result.metadata['chunk_id'] = chunk.chunk_id
        result.metadata['chunk_start'] = chunk.start_line
        result.metadata['chunk_end'] = chunk.end_line

        return result

    def _build_analysis_code(self, chunk: Chunk) -> str:
        """
        Build code for analysis (context + chunk code).

        Format:
        ```cpp
        // File-level context (includes, usings)
        #include <iostream>
        using namespace std;

        // Chunk code
        void myFunction() {
            ...
        }
        ```
        """
        if chunk.context:
            return f"{chunk.context}\n\n{chunk.code}"
        else:
            return chunk.code

    def _adjust_line_numbers(
        self, result: AnalysisResult, chunk: Chunk
    ) -> AnalysisResult:
        """
        Adjust issue line numbers from chunk coordinates to file coordinates.

        Example:
        - Context has 5 lines
        - Chunk starts at file line 100
        - Issue reported at line 8 (in chunk+context)
        - Adjusted line: 100 + (8 - 5 - 1) = 102

        Args:
            result: Analysis result with chunk-relative line numbers
            chunk: Chunk being analyzed

        Returns:
            AnalysisResult with file-relative line numbers
        """
        context_lines = len(chunk.context.split('\n')) if chunk.context else 0

        for issue in result.issues:
            # Line number in chunk+context
            chunk_line = issue.line

            # Adjust to file coordinates
            # Subtract context lines and blank line, add chunk start offset
            if chunk.context:
                # Account for context + blank line separator
                file_line = chunk.start_line + (chunk_line - context_lines - 2)
            else:
                # No context, direct mapping
                file_line = chunk.start_line + chunk_line - 1

            # Ensure line is within chunk bounds
            if file_line < chunk.start_line:
                file_line = chunk.start_line
            elif file_line > chunk.end_line:
                file_line = chunk.end_line

            issue.line = file_line

        return result

    def analyze_chunks_parallel(
        self, chunks: List[Chunk], max_workers: int = 4
    ) -> List[AnalysisResult]:
        """
        Analyze multiple chunks in parallel.

        Args:
            chunks: List of chunks to analyze
            max_workers: Maximum parallel workers

        Returns:
            List of AnalysisResult objects (one per chunk)
        """
        import concurrent.futures

        results = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all chunks
            futures = {
                executor.submit(self.analyze_chunk, chunk): chunk
                for chunk in chunks
            }

            # Collect results as they complete
            for future in concurrent.futures.as_completed(futures):
                chunk = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"Error analyzing chunk {chunk.chunk_id}: {e}")
                    # Create empty result for failed chunk
                    results.append(AnalysisResult(
                        file_path=str(chunk.file_path),
                        issues=[],
                        metadata={'error': str(e), 'chunk_id': chunk.chunk_id}
                    ))

        return results
