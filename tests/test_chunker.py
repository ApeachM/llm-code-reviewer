"""
Unit tests for FileChunker.

Tests chunking logic, context extraction, and edge cases.
"""

import pytest
from pathlib import Path
from framework.chunker import FileChunker, Chunk


@pytest.fixture
def sample_cpp_file(tmp_path):
    """Create a sample C++ file for testing."""
    file_path = tmp_path / "test.cpp"
    code = """#include <iostream>
#include <vector>
using namespace std;

class MyClass {
public:
    void method1() {
        int x = 10;
        cout << x << endl;
    }

    void method2() {
        vector<int> v = {1, 2, 3};
        for (int i : v) {
            cout << i << endl;
        }
    }
};

void globalFunction() {
    int* ptr = new int(42);
    delete ptr;
}

int main() {
    MyClass obj;
    obj.method1();
    return 0;
}
"""
    file_path.write_text(code)
    return file_path


@pytest.fixture
def large_cpp_file(tmp_path):
    """Create a large C++ file (300+ lines) for testing."""
    file_path = tmp_path / "large.cpp"
    lines = []
    lines.append("#include <iostream>")
    lines.append("#include <vector>")
    lines.append("using namespace std;")
    lines.append("")

    # Generate multiple functions
    for i in range(20):
        lines.append(f"void function{i}() {{")
        for j in range(15):
            lines.append(f"    int x{j} = {j};")
            lines.append(f"    cout << x{j} << endl;")
        lines.append("}")
        lines.append("")

    file_path.write_text('\n'.join(lines))
    return file_path


def test_chunker_initialization():
    """Test FileChunker initialization."""
    chunker = FileChunker(language='cpp', max_chunk_lines=200)
    assert chunker.language == 'cpp'
    assert chunker.max_chunk_lines == 200
    assert chunker.parser is not None


def test_chunk_small_file(sample_cpp_file):
    """Small file should produce a few chunks (functions/classes)."""
    chunker = FileChunker(max_chunk_lines=200)
    chunks = chunker.chunk_file(sample_cpp_file)

    # Should have chunks for: MyClass, globalFunction, main
    assert len(chunks) >= 3
    assert all(isinstance(chunk, Chunk) for chunk in chunks)


def test_chunk_includes_context(sample_cpp_file):
    """Each chunk should include file-level context (includes, usings)."""
    chunker = FileChunker()
    chunks = chunker.chunk_file(sample_cpp_file)

    for chunk in chunks:
        # Context should include includes or be empty
        if chunk.context:
            assert '#include' in chunk.context or 'using' in chunk.context


def test_chunk_ids_unique(sample_cpp_file):
    """Each chunk should have a unique ID."""
    chunker = FileChunker()
    chunks = chunker.chunk_file(sample_cpp_file)

    chunk_ids = [chunk.chunk_id for chunk in chunks]
    assert len(chunk_ids) == len(set(chunk_ids)), "Chunk IDs must be unique"


def test_line_numbers_valid(sample_cpp_file):
    """Chunk line numbers should be valid and non-overlapping."""
    chunker = FileChunker()
    chunks = chunker.chunk_file(sample_cpp_file)

    # Check no overlap
    for i in range(len(chunks) - 1):
        # Next chunk should start after current chunk ends
        assert chunks[i].end_line <= chunks[i+1].start_line, \
            f"Chunks overlap: {chunks[i].chunk_id} and {chunks[i+1].chunk_id}"

    # Check line numbers are positive
    for chunk in chunks:
        assert chunk.start_line > 0, "Line numbers must be 1-indexed"
        assert chunk.end_line >= chunk.start_line, "End line must be >= start line"


def test_chunk_large_file(large_cpp_file):
    """Large file (300+ lines) should produce multiple chunks."""
    chunker = FileChunker(max_chunk_lines=200)
    chunks = chunker.chunk_file(large_cpp_file)

    # Should have multiple chunks (20 functions)
    assert len(chunks) >= 15, f"Expected at least 15 chunks, got {len(chunks)}"


def test_chunk_respects_max_lines(large_cpp_file):
    """Chunks should respect max_chunk_lines limit."""
    max_lines = 50
    chunker = FileChunker(max_chunk_lines=max_lines)
    chunks = chunker.chunk_file(large_cpp_file)

    for chunk in chunks:
        chunk_lines = chunker._get_chunk_line_count(chunk)
        # Allow some tolerance for very small chunks
        if chunk_lines > max_lines:
            # Should only exceed for split chunks
            assert chunk.metadata.get('is_split', False), \
                f"Chunk {chunk.chunk_id} exceeds max lines without being split"


def test_chunk_code_extraction(sample_cpp_file):
    """Extracted code should be valid C++ snippets."""
    chunker = FileChunker()
    chunks = chunker.chunk_file(sample_cpp_file)

    for chunk in chunks:
        assert chunk.code.strip(), "Chunk code should not be empty"
        # Should contain valid C++ syntax elements
        assert any(keyword in chunk.code for keyword in
                   ['void', 'int', 'class', '{', '}']), \
            f"Chunk {chunk.chunk_id} doesn't look like valid C++ code"


def test_nonexistent_file():
    """Should raise FileNotFoundError for nonexistent file."""
    chunker = FileChunker()
    with pytest.raises(FileNotFoundError):
        chunker.chunk_file(Path("/nonexistent/file.cpp"))


def test_fallback_line_chunking(tmp_path):
    """Should fallback to line-based chunking for unparseable files."""
    # Create a malformed C++ file
    file_path = tmp_path / "malformed.cpp"
    file_path.write_text("This is not valid C++ code { { { ]")

    chunker = FileChunker(max_chunk_lines=10)
    chunks = chunker.chunk_file(file_path)

    # Should still produce chunks via fallback
    assert len(chunks) > 0
    # Fallback chunks should have is_fallback metadata
    assert any(chunk.metadata.get('is_fallback', False) for chunk in chunks)


def test_empty_file(tmp_path):
    """Should handle empty files gracefully."""
    file_path = tmp_path / "empty.cpp"
    file_path.write_text("")

    chunker = FileChunker()
    chunks = chunker.chunk_file(file_path)

    # Empty file should produce at least one empty chunk or no chunks
    assert len(chunks) >= 0


def test_chunk_metadata(sample_cpp_file):
    """Chunks should include useful metadata."""
    chunker = FileChunker()
    chunks = chunker.chunk_file(sample_cpp_file)

    for chunk in chunks:
        assert 'node_type' in chunk.metadata or 'is_fallback' in chunk.metadata
        assert chunk.file_path == sample_cpp_file


def test_get_chunk_line_count():
    """Test _get_chunk_line_count method."""
    chunker = FileChunker()

    chunk = Chunk(
        chunk_id="test",
        file_path=Path("test.cpp"),
        start_line=1,
        end_line=10,
        code="void foo() {\n    int x = 10;\n}",
        context="#include <iostream>",
        metadata={}
    )

    line_count = chunker._get_chunk_line_count(chunk)
    # Context: 1 line, Code: 3 lines = 4 total
    assert line_count == 4


def test_split_large_chunk():
    """Test _split_large_chunk method."""
    chunker = FileChunker(max_chunk_lines=10)

    # Create a large chunk
    large_code = '\n'.join([f"line {i}" for i in range(50)])
    chunk = Chunk(
        chunk_id="large_chunk",
        file_path=Path("test.cpp"),
        start_line=100,
        end_line=150,
        code=large_code,
        context="",
        metadata={'node_type': 'function'}
    )

    sub_chunks = chunker._split_large_chunk(chunk)

    # Should have multiple sub-chunks
    assert len(sub_chunks) >= 5

    # Sub-chunks should have continuous line numbers
    for i in range(len(sub_chunks) - 1):
        assert sub_chunks[i].end_line < sub_chunks[i+1].start_line

    # All sub-chunks should have is_split metadata
    assert all(sc.metadata.get('is_split', False) for sc in sub_chunks)


def test_extract_file_context(sample_cpp_file):
    """Test _extract_file_context method."""
    chunker = FileChunker()
    code_bytes = sample_cpp_file.read_bytes()
    code_text = code_bytes.decode('utf-8')
    tree = chunker.parser.parse(code_bytes)

    context = chunker._extract_file_context(tree, code_text)

    # Should include includes and usings
    assert '#include' in context
    assert 'using namespace std' in context


def test_get_node_name():
    """Test _get_node_name method (integration with tree-sitter)."""
    chunker = FileChunker()
    code = "void myFunction() { return; }"
    tree = chunker.parser.parse(code.encode('utf-8'))

    # Get function node
    func_node = None
    for node in tree.root_node.children:
        if node.type == 'function_definition':
            func_node = node
            break

    assert func_node is not None
    name = chunker._get_node_name(func_node)
    assert name == "myFunction"
