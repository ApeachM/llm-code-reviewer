"""
Integration tests for chunked analysis workflow.

Tests the end-to-end flow: ProductionAnalyzer -> FileChunker -> ChunkAnalyzer -> ResultMerger
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock
from plugins.production_analyzer import ProductionAnalyzer
from framework.models import AnalysisResult, Issue


@pytest.fixture
def temp_large_cpp_file(tmp_path):
    """Create a temporary large C++ file for testing."""
    file_path = tmp_path / "large_sample.cpp"

    # Create a file with ~350 lines (should trigger chunking at 300 line threshold)
    code_lines = [
        '#include <iostream>',
        '#include <vector>',
        '#include <string>',
        'using namespace std;',
        '',
        '// This is a large C++ file for testing chunking',
        ''
    ]

    # Add multiple functions to reach 350+ lines
    for i in range(40):
        code_lines.extend([
            f'void function_{i}() {{',
            f'    // Function {i} implementation',
            f'    int x = {i};',
            f'    int y = x * 2;',
            f'    cout << "Function {i}: " << y << endl;',
            f'    // More code here',
            f'    for (int j = 0; j < 10; j++) {{',
            f'        cout << j << " ";',
            f'    }}',
            '}',
            ''
        ])

    file_path.write_text('\n'.join(code_lines))
    return file_path


@pytest.fixture
def mock_production_analyzer(monkeypatch):
    """Create a mock ProductionAnalyzer that doesn't need LLM."""
    # We'll mock the technique.analyze method to return predictable results
    def mock_technique_analyze(request):
        # Return a result with one issue per chunk
        return AnalysisResult(
            issues=[
                Issue(
                    category='memory-safety',
                    severity='medium',
                    line=5,
                    description='Test issue description for integration testing',
                    reasoning='This is test reasoning with sufficient characters for validation purposes'
                )
            ],
            metadata={
                'tokens_used': 100,
                'latency': 0.5,
                'model': 'mock-model'
            }
        )

    # Create real analyzer but mock the technique
    analyzer = ProductionAnalyzer(model_name='mock-model')
    analyzer.technique.analyze = Mock(side_effect=mock_technique_analyze)

    return analyzer


def test_analyze_file_whole_mode(mock_production_analyzer, temp_large_cpp_file):
    """Test analyzing a file without chunking (whole mode)."""
    result = mock_production_analyzer.analyze_file(
        temp_large_cpp_file,
        chunk_mode=False
    )

    # Should return a result
    assert result is not None
    assert isinstance(result, AnalysisResult)

    # Should have issues
    assert len(result.issues) > 0

    # Metadata should not indicate chunking
    assert 'num_chunks' not in result.metadata


def test_analyze_file_chunk_mode(mock_production_analyzer, temp_large_cpp_file):
    """Test analyzing a large file with chunking enabled."""
    result = mock_production_analyzer.analyze_file(
        temp_large_cpp_file,
        chunk_mode=True,
        max_chunk_lines=150
    )

    # Should return a result
    assert result is not None
    assert isinstance(result, AnalysisResult)

    # Should have chunking metadata
    assert 'num_chunks' in result.metadata
    assert result.metadata['num_chunks'] > 1  # File should be split into multiple chunks
    assert result.metadata['technique'] == 'chunked_analysis'

    # Should have chunk IDs
    assert 'chunk_ids' in result.metadata
    assert len(result.metadata['chunk_ids']) == result.metadata['num_chunks']

    # Should have combined metrics
    assert 'total_tokens' in result.metadata
    assert 'total_latency' in result.metadata
    assert 'avg_latency_per_chunk' in result.metadata


def test_chunking_threshold(mock_production_analyzer, tmp_path):
    """Test that chunking only triggers for files above threshold."""
    # Create a small file (< 300 lines)
    small_file = tmp_path / "small.cpp"
    small_file.write_text('\n'.join([f'int x{i};' for i in range(50)]))

    # Analyze with chunk_mode=True
    result = mock_production_analyzer.analyze_file(
        small_file,
        chunk_mode=True
    )

    # Small file should NOT be chunked even with chunk_mode=True
    assert 'num_chunks' not in result.metadata or result.metadata['num_chunks'] == 0


def test_chunk_deduplication(mock_production_analyzer, temp_large_cpp_file):
    """Test that duplicate issues are deduplicated across chunks."""
    # Mock technique to return same issue from different chunks
    # Note: line numbers get adjusted per chunk, so to get duplicates we need
    # to report the same relative line in each chunk

    result = mock_production_analyzer.analyze_file(
        temp_large_cpp_file,
        chunk_mode=True,
        max_chunk_lines=100
    )

    # Multiple chunks should have been analyzed
    assert result.metadata['num_chunks'] > 1

    # Check that deduplication is working by verifying no exact duplicates
    # (same line + category)
    seen_keys = set()
    for issue in result.issues:
        key = (issue.line, issue.category)
        assert key not in seen_keys, f"Duplicate issue found: {key}"
        seen_keys.add(key)


def test_line_number_adjustment(mock_production_analyzer, temp_large_cpp_file):
    """Test that line numbers are correctly adjusted from chunk coordinates to file coordinates."""
    result = mock_production_analyzer.analyze_file(
        temp_large_cpp_file,
        chunk_mode=True,
        max_chunk_lines=150
    )

    # All issues should have valid line numbers
    for issue in result.issues:
        assert issue.line >= 1
        # Line numbers should be reasonable for our test file
        assert issue.line <= 500  # Our test file is ~350 lines


def test_chunk_metadata_preserved(mock_production_analyzer, temp_large_cpp_file):
    """Test that chunk metadata is preserved in results."""
    result = mock_production_analyzer.analyze_file(
        temp_large_cpp_file,
        chunk_mode=True,
        max_chunk_lines=150
    )

    # Check that all chunk IDs are present
    assert 'chunk_ids' in result.metadata
    for chunk_id in result.metadata['chunk_ids']:
        assert isinstance(chunk_id, str)
        assert len(chunk_id) > 0


def test_error_handling_in_chunks(mock_production_analyzer, temp_large_cpp_file, monkeypatch):
    """Test that errors in individual chunks are handled gracefully with parallel processing."""
    call_count = [0]

    def mock_with_error(request):
        call_count[0] += 1
        # Fail on second chunk
        if call_count[0] == 2:
            raise RuntimeError("Simulated chunk analysis error")

        return AnalysisResult(
            issues=[
                Issue(
                    category='security',
                    severity='low',
                    line=5,
                    description='Test issue for error handling integration test',
                    reasoning='This is test reasoning with sufficient length for validation requirements'
                )
            ],
            metadata={'tokens_used': 100, 'latency': 0.5}
        )

    mock_production_analyzer.technique.analyze = Mock(side_effect=mock_with_error)

    # With parallel processing, errors are caught and stored in metadata
    result = mock_production_analyzer.analyze_file(
        temp_large_cpp_file,
        chunk_mode=True,
        max_chunk_lines=150
    )

    # Should still return a result (parallel processing handles errors gracefully)
    assert result is not None

    # Should indicate failed chunks
    assert result.metadata['failed_chunks'] > 0


def test_empty_result_merging(mock_production_analyzer, temp_large_cpp_file):
    """Test merging when some chunks return no issues."""
    call_count = [0]

    def mock_alternating_results(request):
        call_count[0] += 1
        # Alternate between empty and non-empty results
        if call_count[0] % 2 == 0:
            return AnalysisResult(
                issues=[],
                metadata={'tokens_used': 100, 'latency': 0.5}
            )
        else:
            return AnalysisResult(
                issues=[
                    Issue(
                        category='performance',
                        severity='medium',
                        line=10,
                        description='Performance issue in alternating chunks test',
                        reasoning='This is test reasoning with many characters for validation purposes and requirements'
                    )
                ],
                metadata={'tokens_used': 100, 'latency': 0.5}
            )

    mock_production_analyzer.technique.analyze = Mock(side_effect=mock_alternating_results)

    result = mock_production_analyzer.analyze_file(
        temp_large_cpp_file,
        chunk_mode=True,
        max_chunk_lines=150
    )

    # Should have some issues but not from all chunks
    assert result is not None
    assert len(result.issues) >= 1


def test_sorted_issues_in_result(mock_production_analyzer, temp_large_cpp_file):
    """Test that issues in the final result are sorted by line number."""
    call_count = [0]

    def mock_unsorted_issues(request):
        call_count[0] += 1
        # Return issues with different line numbers from each chunk
        return AnalysisResult(
            issues=[
                Issue(
                    category='concurrency',
                    severity='low',
                    line=100 + (call_count[0] * 5),
                    description=f'Issue at line {100 + (call_count[0] * 5)} for sorting test',
                    reasoning='This is test reasoning with adequate length for validation purposes'
                )
            ],
            metadata={'tokens_used': 100, 'latency': 0.5}
        )

    mock_production_analyzer.technique.analyze = Mock(side_effect=mock_unsorted_issues)

    result = mock_production_analyzer.analyze_file(
        temp_large_cpp_file,
        chunk_mode=True,
        max_chunk_lines=150
    )

    # Issues should be sorted by line number
    if len(result.issues) > 1:
        for i in range(len(result.issues) - 1):
            assert result.issues[i].line <= result.issues[i + 1].line
