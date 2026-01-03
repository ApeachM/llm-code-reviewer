"""
Unit tests for ChunkAnalyzer.

Tests chunk analysis, line number adjustment, and parallel processing.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock
from framework.chunk_analyzer import ChunkAnalyzer
from framework.chunker import Chunk
from framework.models import AnalysisResult, Issue, AnalysisRequest


@pytest.fixture
def mock_analyzer():
    """Create a mock ProductionAnalyzer."""
    analyzer = Mock()
    technique = Mock()

    # Mock technique.analyze() to return a result with one issue
    def mock_analyze(request):
        return AnalysisResult(
            file_path=request.file_path,
            issues=[
                Issue(
                    category='logic-errors',
                    severity='critical',
                    line=10,  # Line in chunk+context coordinates
                    description='Off-by-one error',
                    reasoning='Loop bounds incorrect'
                )
            ],
            metadata={'tokens_used': 100, 'latency': 5.0}
        )

    technique.analyze = Mock(side_effect=mock_analyze)
    analyzer.technique = technique

    return analyzer


@pytest.fixture
def sample_chunk():
    """Create a sample chunk for testing."""
    return Chunk(
        chunk_id='test.cpp:function:100-120',
        file_path=Path('test.cpp'),
        start_line=100,
        end_line=120,
        code='void foo() {\n    int* p = new int;\n    return;\n}',
        context='#include <iostream>\nusing namespace std;',
        metadata={'node_type': 'function_definition'}
    )


def test_chunk_analyzer_initialization(mock_analyzer):
    """Test ChunkAnalyzer initialization."""
    chunk_analyzer = ChunkAnalyzer(mock_analyzer)
    assert chunk_analyzer.analyzer == mock_analyzer


def test_analyze_chunk(mock_analyzer, sample_chunk):
    """Test single chunk analysis."""
    chunk_analyzer = ChunkAnalyzer(mock_analyzer)
    result = chunk_analyzer.analyze_chunk(sample_chunk)

    # Should return valid result
    assert isinstance(result, AnalysisResult)
    assert len(result.issues) > 0

    # Should have chunk metadata
    assert 'chunk_id' in result.metadata
    assert result.metadata['chunk_id'] == sample_chunk.chunk_id
    assert result.metadata['chunk_start'] == sample_chunk.start_line
    assert result.metadata['chunk_end'] == sample_chunk.end_line


def test_build_analysis_code(mock_analyzer, sample_chunk):
    """Test _build_analysis_code method."""
    chunk_analyzer = ChunkAnalyzer(mock_analyzer)
    full_code = chunk_analyzer._build_analysis_code(sample_chunk)

    # Should include context
    assert '#include <iostream>' in full_code
    assert 'using namespace std' in full_code

    # Should include chunk code
    assert 'void foo()' in full_code


def test_build_analysis_code_no_context(mock_analyzer):
    """Test _build_analysis_code with no context."""
    chunk = Chunk(
        chunk_id='test',
        file_path=Path('test.cpp'),
        start_line=1,
        end_line=5,
        code='void bar() { }',
        context='',  # No context
        metadata={}
    )

    chunk_analyzer = ChunkAnalyzer(mock_analyzer)
    full_code = chunk_analyzer._build_analysis_code(chunk)

    # Should only have code
    assert full_code == 'void bar() { }'


def test_adjust_line_numbers(mock_analyzer, sample_chunk):
    """Test _adjust_line_numbers method."""
    chunk_analyzer = ChunkAnalyzer(mock_analyzer)

    # Create result with chunk-relative line numbers
    result = AnalysisResult(
        file_path='test.cpp',
        issues=[
            Issue(
                category='logic-errors',
                severity='critical',
                line=5,  # Line in chunk+context (context=2 lines + blank)
                description='Issue at line 5 description',
                reasoning='This is a test reasoning with at least 20 characters'
            )
        ],
        metadata={}
    )

    # Adjust line numbers
    adjusted_result = chunk_analyzer._adjust_line_numbers(result, sample_chunk)

    # Line should be adjusted to file coordinates
    # Context: 2 lines, blank line: 1, so line 5 in chunk+context = line 5-2-2 = 1 relative to chunk code
    # Chunk starts at line 100, so file line = 100 + 1 = 101
    assert adjusted_result.issues[0].line >= sample_chunk.start_line
    assert adjusted_result.issues[0].line <= sample_chunk.end_line


def test_adjust_line_numbers_no_context(mock_analyzer):
    """Test line number adjustment with no context."""
    chunk = Chunk(
        chunk_id='test',
        file_path=Path('test.cpp'),
        start_line=50,
        end_line=60,
        code='void foo() { }',
        context='',  # No context
        metadata={}
    )

    result = AnalysisResult(
        file_path='test.cpp',
        issues=[
            Issue(
                category='api-misuse',
                severity='medium',
                line=3,  # Line 3 in chunk
                description='API misuse issue description',
                reasoning='This is a test reasoning with at least 20 characters'
            )
        ],
        metadata={}
    )

    chunk_analyzer = ChunkAnalyzer(mock_analyzer)
    adjusted_result = chunk_analyzer._adjust_line_numbers(result, chunk)

    # Line 3 in chunk = line 52 in file (50 + 3 - 1)
    assert adjusted_result.issues[0].line == 52


def test_adjust_line_numbers_bounds_clamping(mock_analyzer, sample_chunk):
    """Test that line numbers are clamped to chunk bounds."""
    chunk_analyzer = ChunkAnalyzer(mock_analyzer)

    # Create result with out-of-bounds line number
    result = AnalysisResult(
        file_path='test.cpp',
        issues=[
            Issue(
                category='logic-errors',
                severity='critical',
                line=1000,  # Way out of bounds
                description='Out of bounds issue description',
                reasoning='This is a test reasoning with at least 20 characters'
            )
        ],
        metadata={}
    )

    adjusted_result = chunk_analyzer._adjust_line_numbers(result, sample_chunk)

    # Should be clamped to chunk.end_line
    assert adjusted_result.issues[0].line == sample_chunk.end_line


def test_analyze_chunks_parallel(mock_analyzer):
    """Test parallel chunk analysis."""
    chunks = [
        Chunk(
            chunk_id=f'chunk_{i}',
            file_path=Path('test.cpp'),
            start_line=i * 10,
            end_line=(i + 1) * 10,
            code=f'void func{i}() {{}}',
            context='',
            metadata={}
        )
        for i in range(5)
    ]

    chunk_analyzer = ChunkAnalyzer(mock_analyzer)
    results = chunk_analyzer.analyze_chunks_parallel(chunks, max_workers=2)

    # Should have one result per chunk
    assert len(results) == 5

    # All results should be AnalysisResult objects
    assert all(isinstance(r, AnalysisResult) for r in results)


def test_analyze_chunks_parallel_with_error(mock_analyzer):
    """Test parallel analysis handles errors gracefully."""
    # Create analyzer that raises exception
    error_analyzer = Mock()
    error_technique = Mock()

    def error_analyze(request):
        raise RuntimeError("Analysis failed!")

    error_technique.analyze = Mock(side_effect=error_analyze)
    error_analyzer.technique = error_technique

    chunks = [
        Chunk(
            chunk_id='error_chunk',
            file_path=Path('test.cpp'),
            start_line=1,
            end_line=10,
            code='code',
            context='',
            metadata={}
        )
    ]

    chunk_analyzer = ChunkAnalyzer(error_analyzer)
    results = chunk_analyzer.analyze_chunks_parallel(chunks, max_workers=1)

    # Should still return results (with error metadata)
    assert len(results) == 1
    assert 'error' in results[0].metadata


def test_analyze_chunk_calls_technique(mock_analyzer, sample_chunk):
    """Test that analyze_chunk properly calls the analyzer's technique."""
    chunk_analyzer = ChunkAnalyzer(mock_analyzer)
    result = chunk_analyzer.analyze_chunk(sample_chunk)

    # Technique.analyze should have been called
    mock_analyzer.technique.analyze.assert_called_once()

    # Check that AnalysisRequest was passed with correct parameters
    call_args = mock_analyzer.technique.analyze.call_args[0][0]
    assert isinstance(call_args, AnalysisRequest)
    assert call_args.language == 'cpp'
    assert str(sample_chunk.file_path) in call_args.file_path


def test_chunk_metadata_preserved(mock_analyzer, sample_chunk):
    """Test that chunk metadata is preserved in results."""
    chunk_analyzer = ChunkAnalyzer(mock_analyzer)
    result = chunk_analyzer.analyze_chunk(sample_chunk)

    assert result.metadata['chunk_id'] == sample_chunk.chunk_id
    assert result.metadata['chunk_start'] == sample_chunk.start_line
    assert result.metadata['chunk_end'] == sample_chunk.end_line


def test_empty_chunk(mock_analyzer):
    """Test analysis of empty chunk."""
    empty_chunk = Chunk(
        chunk_id='empty',
        file_path=Path('test.cpp'),
        start_line=1,
        end_line=1,
        code='// empty',  # Minimal code to satisfy validation
        context='',
        metadata={}
    )

    chunk_analyzer = ChunkAnalyzer(mock_analyzer)
    result = chunk_analyzer.analyze_chunk(empty_chunk)

    # Should complete without errors
    assert isinstance(result, AnalysisResult)
