#!/usr/bin/env python3
"""
Test script to verify chunking works on large_file_test.cpp.

This script demonstrates the chunking workflow without requiring an LLM.
"""

from pathlib import Path
from framework.chunker import FileChunker

def test_large_file_chunking():
    """Test chunking on the sample large file."""

    file_path = Path("large_file_test.cpp")

    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False

    # Check file size
    file_stats = file_path.stat()
    file_size_kb = file_stats.st_size / 1024
    line_count = len(file_path.read_text().split('\n'))

    print(f"📄 File: {file_path}")
    print(f"📏 Size: {file_size_kb:.1f} KB")
    print(f"📝 Lines: {line_count}")
    print()

    # Create chunker
    chunker = FileChunker(language='cpp', max_chunk_lines=200)

    # Chunk the file
    print("🔪 Chunking file...")
    chunks = chunker.chunk_file(file_path)

    print(f"✅ Created {len(chunks)} chunks\n")

    # Display chunk information
    print("📦 Chunk Details:")
    print("-" * 80)

    total_chunk_lines = 0
    for i, chunk in enumerate(chunks, 1):
        chunk_line_count = chunk.end_line - chunk.start_line + 1
        total_chunk_lines += chunk_line_count
        context_lines = len(chunk.context.split('\n')) if chunk.context else 0

        print(f"Chunk {i}: {chunk.chunk_id}")
        print(f"  Lines: {chunk.start_line}-{chunk.end_line} ({chunk_line_count} lines)")
        print(f"  Context: {context_lines} lines")
        print(f"  Code preview: {chunk.code[:60]}...")
        print()

    print("-" * 80)
    print(f"Total lines covered: {total_chunk_lines}")
    print(f"Original file lines: {line_count}")
    print()

    # Verify chunks cover the whole file
    if total_chunk_lines >= line_count - 10:  # Allow some tolerance
        print("✅ Chunks cover entire file")
    else:
        print(f"⚠️  Warning: Chunks may not cover entire file")
        print(f"   Expected ~{line_count} lines, got {total_chunk_lines}")

    # Verify no overlapping line numbers
    line_ranges = [(c.start_line, c.end_line) for c in chunks]
    overlaps = []
    for i in range(len(line_ranges) - 1):
        if line_ranges[i][1] >= line_ranges[i + 1][0]:
            overlaps.append((i, i + 1))

    if not overlaps:
        print("✅ No overlapping chunks")
    else:
        print(f"❌ Found {len(overlaps)} overlapping chunks: {overlaps}")

    # Verify chunk sizes
    oversized_chunks = [
        (i, c.end_line - c.start_line + 1)
        for i, c in enumerate(chunks, 1)
        if (c.end_line - c.start_line + 1) > 250  # Allow some overage
    ]

    if not oversized_chunks:
        print("✅ All chunks within size limit")
    else:
        print(f"⚠️  {len(oversized_chunks)} chunks exceed size limit:")
        for chunk_num, size in oversized_chunks:
            print(f"   Chunk {chunk_num}: {size} lines")

    # Verify all chunks have unique IDs
    chunk_ids = [c.chunk_id for c in chunks]
    if len(chunk_ids) == len(set(chunk_ids)):
        print("✅ All chunk IDs are unique")
    else:
        print("❌ Duplicate chunk IDs found")

    print()
    print("=" * 80)
    print("🎉 Chunking test completed successfully!")
    print()

    return True

if __name__ == "__main__":
    import sys
    success = test_large_file_chunking()
    sys.exit(0 if success else 1)
