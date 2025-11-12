"""
Unit tests for ResultMerger.

Tests result merging, deduplication, and metadata combination.
"""

import pytest
from framework.result_merger import ResultMerger
from framework.models import AnalysisResult, Issue


def create_issue(line: int, category: str = 'memory-safety', description: str = None, reasoning: str = None):
    """Helper function to create an Issue."""
    return Issue(
        category=category,
        severity='critical',
        line=line,
        description=description or f'Issue at line {line} description',
        reasoning=reasoning or f'This is reasoning for issue at line {line} with enough characters'
    )


def create_result(file_path: str, issues: list, **metadata):
    """Helper function to create an AnalysisResult."""
    # Add file_path to metadata
    metadata['file_path'] = file_path
    return AnalysisResult(
        issues=issues,
        metadata=metadata
    )


def test_merger_initialization():
    """Test ResultMerger initialization."""
    merger = ResultMerger(similarity_threshold=0.8)
    assert merger.similarity_threshold == 0.8


def test_merge_single_result():
    """Test merging a single result."""
    issue = create_issue(10)
    result = create_result('test.cpp', [issue], tokens_used=100, latency=5.0, chunk_id='chunk1')

    merger = ResultMerger()
    merged = merger.merge([result])

    assert isinstance(merged, AnalysisResult)
    assert len(merged.issues) == 1
    assert merged.issues[0].line == 10


def test_merge_multiple_results():
    """Test merging multiple results."""
    result1 = create_result('test.cpp', [create_issue(10), create_issue(20)],
                           tokens_used=100, latency=5.0, chunk_id='chunk1')
    result2 = create_result('test.cpp', [create_issue(30), create_issue(40)],
                           tokens_used=150, latency=6.0, chunk_id='chunk2')

    merger = ResultMerger()
    merged = merger.merge([result1, result2])

    # Should have all 4 issues
    assert len(merged.issues) == 4

    # Should be sorted by line number
    assert merged.issues[0].line == 10
    assert merged.issues[1].line == 20
    assert merged.issues[2].line == 30
    assert merged.issues[3].line == 40


def test_merge_deduplicates_issues():
    """Test that duplicate issues are removed."""
    # Same issue reported from two chunks
    issue1 = create_issue(15, category='memory-safety',
                         description='Memory leak description',
                         reasoning='Short reasoning for memory leak issue')
    issue2 = create_issue(15, category='memory-safety',
                         description='Memory leak description',
                         reasoning='Much longer and more detailed reasoning for the memory leak issue with lots of explanation')

    result1 = create_result('test.cpp', [issue1], chunk_id='chunk1')
    result2 = create_result('test.cpp', [issue2], chunk_id='chunk2')

    merger = ResultMerger()
    merged = merger.merge([result1, result2])

    # Should have only 1 issue (deduplicated)
    assert len(merged.issues) == 1

    # Should keep the one with longer reasoning
    assert len(merged.issues[0].reasoning) > 30


def test_merge_empty_results():
    """Test merging when results is empty."""
    merger = ResultMerger()

    with pytest.raises(ValueError, match="No chunk results to merge"):
        merger.merge([])


def test_combine_metadata():
    """Test metadata combination."""
    result1 = create_result('test.cpp', [],
                           tokens_used=100, latency=5.0, chunk_id='chunk1')
    result2 = create_result('test.cpp', [],
                           tokens_used=150, latency=6.5, chunk_id='chunk2')
    result3 = create_result('test.cpp', [],
                           tokens_used=120, latency=5.5, chunk_id='chunk3')

    merger = ResultMerger()
    merged = merger.merge([result1, result2, result3])

    # Check combined metadata
    assert merged.metadata['num_chunks'] == 3
    assert merged.metadata['total_tokens'] == 370  # 100 + 150 + 120
    assert merged.metadata['total_latency'] == 17.0  # 5.0 + 6.5 + 5.5
    assert merged.metadata['avg_latency_per_chunk'] == pytest.approx(5.67, rel=0.1)
    assert merged.metadata['technique'] == 'chunked_analysis'


def test_combine_metadata_with_errors():
    """Test metadata combination when some chunks failed."""
    result1 = create_result('test.cpp', [], tokens_used=100, latency=5.0, chunk_id='chunk1')
    result2 = create_result('test.cpp', [], error='Parse error', chunk_id='chunk2')
    result3 = create_result('test.cpp', [], tokens_used=120, latency=5.5, chunk_id='chunk3')

    merger = ResultMerger()
    merged = merger.merge([result1, result2, result3])

    assert merged.metadata['num_chunks'] == 3
    assert merged.metadata['failed_chunks'] == 1


def test_deduplicate_same_line_different_category():
    """Test that issues on same line but different categories are kept."""
    issue1 = create_issue(25, category='memory-safety')
    issue2 = create_issue(25, category='performance')

    result = create_result('test.cpp', [issue1, issue2])

    merger = ResultMerger()
    merged = merger.merge([result])

    # Should keep both (different categories)
    assert len(merged.issues) == 2


def test_deduplicate_different_lines_same_category():
    """Test that issues on different lines are kept."""
    issue1 = create_issue(10, category='memory-safety')
    issue2 = create_issue(20, category='memory-safety')

    result = create_result('test.cpp', [issue1, issue2])

    merger = ResultMerger()
    merged = merger.merge([result])

    # Should keep both (different lines)
    assert len(merged.issues) == 2


def test_sort_by_line_number():
    """Test that merged issues are sorted by line number."""
    # Create issues in random order
    issues = [
        create_issue(50),
        create_issue(10),
        create_issue(30),
        create_issue(20),
        create_issue(40)
    ]

    result = create_result('test.cpp', issues)

    merger = ResultMerger()
    merged = merger.merge([result])

    # Should be sorted
    lines = [issue.line for issue in merged.issues]
    assert lines == [10, 20, 30, 40, 50]


def test_chunk_ids_preserved():
    """Test that chunk IDs are preserved in metadata."""
    result1 = create_result('test.cpp', [], chunk_id='chunk_a')
    result2 = create_result('test.cpp', [], chunk_id='chunk_b')
    result3 = create_result('test.cpp', [], chunk_id='chunk_c')

    merger = ResultMerger()
    merged = merger.merge([result1, result2, result3])

    assert 'chunk_ids' in merged.metadata
    assert merged.metadata['chunk_ids'] == ['chunk_a', 'chunk_b', 'chunk_c']


def test_file_path_from_first_result():
    """Test that file path is taken from first result."""
    result1 = create_result('test.cpp', [])
    result2 = create_result('other.cpp', [])  # Different file path (shouldn't happen)

    merger = ResultMerger()
    merged = merger.merge([result1, result2])

    # Should use file path from first result (stored in metadata)
    assert merged.metadata['file_path'] == 'test.cpp'


def test_merge_with_no_issues():
    """Test merging results with no issues."""
    result1 = create_result('test.cpp', [], chunk_id='chunk1')
    result2 = create_result('test.cpp', [], chunk_id='chunk2')

    merger = ResultMerger()
    merged = merger.merge([result1, result2])

    assert len(merged.issues) == 0
    assert merged.metadata['num_chunks'] == 2


def test_deduplicate_prefers_longer_reasoning():
    """Test that deduplication prefers issues with longer reasoning."""
    issue_short = create_issue(100, reasoning='Short reasoning text here for testing purposes')
    issue_long = create_issue(100, reasoning='This is a much longer and more detailed reasoning that explains the issue in great depth with multiple sentences')

    result1 = create_result('test.cpp', [issue_short])
    result2 = create_result('test.cpp', [issue_long])

    merger = ResultMerger()
    merged = merger.merge([result1, result2])

    # Should keep the one with longer reasoning
    assert len(merged.issues) == 1
    assert len(merged.issues[0].reasoning) > 50


def test_multiple_duplicate_groups():
    """Test deduplication with multiple groups of duplicates."""
    # Line 10: 2 duplicates
    issues_line10 = [
        create_issue(10, reasoning='Short reasoning text with enough characters'),
        create_issue(10, reasoning='Long reasoning with many words and detailed explanation')
    ]

    # Line 20: 3 duplicates
    issues_line20 = [
        create_issue(20, reasoning='Shortest reasoning text here for testing'),
        create_issue(20, reasoning='Medium length reasoning with some detail'),
        create_issue(20, reasoning='Very long and detailed reasoning with lots of explanation and multiple points')
    ]

    # Line 30: 1 unique
    issues_line30 = [create_issue(30)]

    all_issues = issues_line10 + issues_line20 + issues_line30

    result = create_result('test.cpp', all_issues)

    merger = ResultMerger()
    merged = merger.merge([result])

    # Should have 3 issues (1 per line)
    assert len(merged.issues) == 3

    # Should be sorted by line
    assert merged.issues[0].line == 10
    assert merged.issues[1].line == 20
    assert merged.issues[2].line == 30
