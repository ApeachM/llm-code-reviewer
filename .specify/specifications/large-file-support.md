# Specification: Large File Support

**Status**: Draft
**Constitution**: large-file-support.md
**Target**: Phase 5 implementation
**Estimated Effort**: 4 days

---

## Overview

Implement function-level chunking to enable analysis of 700+ line C++ files by splitting them into manageable chunks, analyzing each independently, and merging results.

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     User Input (CLI)                         │
│   python -m cli.main analyze file large.cpp --chunk         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              ProductionAnalyzer (Modified)                   │
│  - Check if chunking needed (file size + --chunk flag)      │
│  - Route to chunked or whole-file analysis                  │
└─────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
┌──────────────────────┐    ┌──────────────────────┐
│  Whole File Analysis │    │  Chunked Analysis    │
│  (Existing Logic)    │    │  (New Pipeline)      │
└──────────────────────┘    └──────────────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
         ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
         │  FileChunker     │ │ ChunkAnalyzer    │ │  ResultMerger    │
         │  - Parse AST     │ │ - Analyze chunks │ │ - Deduplicate    │
         │  - Extract funcs │ │ - Add context    │ │ - Adjust lines   │
         │  - Create chunks │ │ - Parallel exec  │ │ - Combine stats  │
         └──────────────────┘ └──────────────────┘ └──────────────────┘
                    │                  │                  │
                    └──────────────────┴──────────────────┘
                                       │
                                       ▼
                         ┌──────────────────────────┐
                         │   Final AnalysisResult   │
                         │  - Merged issues         │
                         │  - Adjusted line numbers │
                         │  - Combined metadata     │
                         └──────────────────────────┘
```

---

## Component Specifications

### 1. FileChunker

**Purpose**: Parse C++ file and split into analyzable chunks

**Location**: `framework/chunker.py`

**Class Definition**:

```python
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import tree_sitter_cpp as ts_cpp
from tree_sitter import Language, Parser

@dataclass
class Chunk:
    """Represents a chunk of code to be analyzed."""
    chunk_id: str          # e.g., "large.cpp:MyClass::process:45-120"
    file_path: Path        # Original file path
    start_line: int        # Starting line in original file (1-indexed)
    end_line: int          # Ending line in original file (inclusive)
    code: str              # The actual code chunk
    context: str           # Necessary context (imports, class def, etc.)
    metadata: dict         # Additional metadata

class FileChunker:
    """
    Chunk large files into analyzable pieces.

    Strategy:
    1. Parse file with tree-sitter to get AST
    2. Extract top-level functions and class methods
    3. Create chunks with appropriate context
    4. Handle edge cases (templates, macros, nested classes)
    """

    def __init__(self, language: str = 'cpp', max_chunk_lines: int = 200):
        """
        Initialize chunker.

        Args:
            language: Programming language ('cpp', 'python', etc.)
            max_chunk_lines: Maximum lines per chunk
        """
        self.language = language
        self.max_chunk_lines = max_chunk_lines

        # Initialize tree-sitter parser
        CPP_LANGUAGE = Language(ts_cpp.language())
        self.parser = Parser(CPP_LANGUAGE)

    def chunk_file(self, file_path: Path) -> List[Chunk]:
        """
        Split file into chunks.

        Args:
            file_path: Path to file

        Returns:
            List of Chunk objects

        Raises:
            FileNotFoundError: If file doesn't exist
            ParseError: If file cannot be parsed
        """
        # Read file
        code_bytes = file_path.read_bytes()
        code_text = code_bytes.decode('utf-8')

        # Parse with tree-sitter
        tree = self.parser.parse(code_bytes)

        # Extract chunks
        chunks = []

        # Get file-level context (includes, namespaces)
        file_context = self._extract_file_context(tree, code_text)

        # Extract functions and classes
        for node in tree.root_node.children:
            if node.type in ['function_definition', 'class_specifier',
                            'struct_specifier', 'namespace_definition']:
                chunk = self._create_chunk_from_node(
                    node, file_path, code_text, file_context
                )

                if chunk:
                    # Check size
                    if self._get_chunk_line_count(chunk) <= self.max_chunk_lines:
                        chunks.append(chunk)
                    else:
                        # Split large chunk
                        sub_chunks = self._split_large_chunk(chunk)
                        chunks.extend(sub_chunks)

        return chunks

    def _extract_file_context(self, tree, code_text: str) -> str:
        """
        Extract file-level context (includes, using statements, etc.).

        Returns:
            String containing necessary context
        """
        context_lines = []

        for node in tree.root_node.children:
            if node.type in ['preproc_include', 'using_declaration',
                            'namespace_alias_definition']:
                # Extract line
                start_byte = node.start_byte
                end_byte = node.end_byte
                context_lines.append(code_text[start_byte:end_byte])

        return '\n'.join(context_lines)

    def _create_chunk_from_node(
        self, node, file_path: Path, code_text: str, file_context: str
    ) -> Optional[Chunk]:
        """Create Chunk from AST node."""
        start_line = node.start_point[0] + 1  # tree-sitter is 0-indexed
        end_line = node.end_point[0] + 1

        # Extract code
        start_byte = node.start_byte
        end_byte = node.end_byte
        code = code_text[start_byte:end_byte]

        # Generate chunk ID
        chunk_id = f"{file_path.name}:{self._get_node_name(node)}:{start_line}-{end_line}"

        return Chunk(
            chunk_id=chunk_id,
            file_path=file_path,
            start_line=start_line,
            end_line=end_line,
            code=code,
            context=file_context,
            metadata={'node_type': node.type}
        )

    def _get_node_name(self, node) -> str:
        """Extract function/class name from node."""
        # Look for declarator or identifier child
        for child in node.children:
            if child.type == 'function_declarator':
                for subchild in child.children:
                    if subchild.type == 'identifier':
                        return subchild.text.decode('utf-8')
            elif child.type == 'type_identifier' or child.type == 'identifier':
                return child.text.decode('utf-8')

        return "unknown"

    def _get_chunk_line_count(self, chunk: Chunk) -> int:
        """Count lines in chunk (code + context)."""
        return len(chunk.context.split('\n')) + len(chunk.code.split('\n'))

    def _split_large_chunk(self, chunk: Chunk) -> List[Chunk]:
        """
        Split a chunk that exceeds max_chunk_lines.

        Strategy: Split at statement boundaries (every N statements)
        Fallback: Split at line boundaries
        """
        # For now, simple line-based splitting
        lines = chunk.code.split('\n')
        sub_chunks = []

        for i in range(0, len(lines), self.max_chunk_lines):
            sub_code = '\n'.join(lines[i:i + self.max_chunk_lines])
            sub_start = chunk.start_line + i
            sub_end = min(chunk.start_line + i + self.max_chunk_lines - 1, chunk.end_line)

            sub_chunk = Chunk(
                chunk_id=f"{chunk.chunk_id}_part{i // self.max_chunk_lines + 1}",
                file_path=chunk.file_path,
                start_line=sub_start,
                end_line=sub_end,
                code=sub_code,
                context=chunk.context,
                metadata={**chunk.metadata, 'is_split': True}
            )
            sub_chunks.append(sub_chunk)

        return sub_chunks
```

---

### 2. ChunkAnalyzer

**Purpose**: Analyze individual chunks with context

**Location**: `framework/chunk_analyzer.py`

**Class Definition**:

```python
from pathlib import Path
from typing import List
from framework.models import AnalysisRequest, AnalysisResult, Issue
from framework.chunker import Chunk
from plugins.production_analyzer import ProductionAnalyzer

class ChunkAnalyzer:
    """
    Analyze code chunks independently.

    Features:
    - Adds context to each chunk
    - Adjusts line numbers back to file coordinates
    - Supports parallel processing
    """

    def __init__(self, analyzer: ProductionAnalyzer):
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
        """
        context_lines = len(chunk.context.split('\n')) if chunk.context else 0

        for issue in result.issues:
            # Line number in chunk+context
            chunk_line = issue.line

            # Adjust to file coordinates
            # Subtract context lines, add chunk start offset
            file_line = chunk.start_line + (chunk_line - context_lines - 1)

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
```

---

### 3. ResultMerger

**Purpose**: Merge and deduplicate results from multiple chunks

**Location**: `framework/result_merger.py`

**Class Definition**:

```python
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
        return AnalysisResult(
            file_path=chunk_results[0].file_path,
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
        """Combine metadata from all chunks."""
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
```

---

### 4. ProductionAnalyzer Modifications

**Purpose**: Route to chunked or whole-file analysis

**Location**: `plugins/production_analyzer.py` (modify existing)

**Changes**:

```python
class ProductionAnalyzer:
    # ... existing code ...

    def analyze_file(
        self,
        file_path: Path,
        chunk_mode: bool = False,
        max_chunk_lines: int = 200
    ) -> Optional[AnalysisResult]:
        """
        Analyze a single file.

        Args:
            file_path: Path to file
            chunk_mode: Enable chunking for large files
            max_chunk_lines: Maximum lines per chunk

        Returns:
            AnalysisResult or None if file should not be analyzed
        """
        # Check if file should be analyzed
        if not self.plugin.should_analyze_file(file_path):
            return None

        # Decide: chunked or whole-file analysis
        if chunk_mode and self._should_use_chunking(file_path):
            return self._analyze_chunked(file_path, max_chunk_lines)
        else:
            return self._analyze_whole(file_path)

    def _should_use_chunking(self, file_path: Path) -> bool:
        """
        Determine if file should be chunked.

        Criteria: file > 300 lines
        """
        try:
            line_count = len(file_path.read_text(encoding='utf-8').split('\n'))
            return line_count > 300
        except Exception:
            return False

    def _analyze_whole(self, file_path: Path) -> AnalysisResult:
        """
        Analyze file as a whole (existing logic).

        This is the existing implementation, unchanged.
        """
        # ... existing analyze_file logic ...
        pass

    def _analyze_chunked(
        self, file_path: Path, max_chunk_lines: int
    ) -> AnalysisResult:
        """
        Analyze file using chunking strategy.

        Steps:
        1. Chunk file with FileChunker
        2. Analyze each chunk with ChunkAnalyzer
        3. Merge results with ResultMerger
        """
        from framework.chunker import FileChunker
        from framework.chunk_analyzer import ChunkAnalyzer
        from framework.result_merger import ResultMerger

        # Chunk file
        chunker = FileChunker(
            language=self.plugin.name,
            max_chunk_lines=max_chunk_lines
        )
        chunks = chunker.chunk_file(file_path)

        print(f"Chunked file into {len(chunks)} chunks")

        # Analyze chunks
        chunk_analyzer = ChunkAnalyzer(analyzer=self)
        chunk_results = []

        for i, chunk in enumerate(chunks, 1):
            print(f"Analyzing chunk {i}/{len(chunks)}: {chunk.chunk_id}")
            result = chunk_analyzer.analyze_chunk(chunk)
            chunk_results.append(result)

        # Merge results
        merger = ResultMerger()
        merged_result = merger.merge(chunk_results)

        # Postprocess (existing plugin logic)
        merged_result.issues = self.plugin.postprocess_issues(merged_result.issues)

        return merged_result
```

---

### 5. CLI Changes

**Purpose**: Add `--chunk` flag

**Location**: `cli/main.py` (modify existing)

**Changes**:

```python
@analyze.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--model', '-m', default='deepseek-coder:33b-instruct',
              help='Ollama model to use')
@click.option('--output', '-o', type=click.Path(), help='Output file (markdown)')
@click.option('--chunk/--no-chunk', default=False,
              help='Enable chunking for large files (default: disabled)')
@click.option('--chunk-size', default=200, type=int,
              help='Maximum lines per chunk (default: 200)')
def file(file_path: str, model: str, output: Optional[str], chunk: bool, chunk_size: int):
    """
    Analyze a single file.

    Example:
        llm-framework analyze file src/main.cpp
        llm-framework analyze file large.cpp --chunk
        llm-framework analyze file large.cpp --chunk --chunk-size 150
    """
    from plugins.production_analyzer import ProductionAnalyzer

    console.print(f"\n[bold cyan]Analyzing file:[/bold cyan] {file_path}")
    console.print(f"[bold]Model:[/bold] {model}")
    if chunk:
        console.print(f"[bold]Chunk mode:[/bold] Enabled (max {chunk_size} lines per chunk)")
    console.print()

    # Create analyzer
    analyzer = ProductionAnalyzer(model_name=model)

    # Analyze
    file_path_obj = Path(file_path)
    result = analyzer.analyze_file(
        file_path_obj,
        chunk_mode=chunk,
        max_chunk_lines=chunk_size
    )

    # ... rest of existing display logic ...
```

---

## Data Structures

### Chunk

```python
@dataclass
class Chunk:
    chunk_id: str          # Unique identifier
    file_path: Path        # Original file
    start_line: int        # Starting line (1-indexed)
    end_line: int          # Ending line (inclusive)
    code: str              # Chunk code
    context: str           # Necessary context
    metadata: dict         # Additional info
```

---

## Dependencies

### New External Dependencies

Add to `requirements.txt`:

```
tree-sitter==0.21.0
tree-sitter-cpp==0.21.0
```

### Installation

```bash
pip install tree-sitter tree-sitter-cpp
```

---

## Testing Strategy

### Unit Tests

**File**: `tests/test_chunker.py`

```python
def test_chunk_small_file():
    """Small file (< 300 lines) should produce 1-2 chunks."""
    chunker = FileChunker(max_chunk_lines=200)
    chunks = chunker.chunk_file(Path('test_small.cpp'))
    assert len(chunks) <= 3

def test_chunk_large_file():
    """Large file (700 lines) should produce 4-5 chunks."""
    chunker = FileChunker(max_chunk_lines=200)
    chunks = chunker.chunk_file(Path('test_large.cpp'))
    assert 4 <= len(chunks) <= 6

def test_chunk_includes_context():
    """Each chunk should include file-level context."""
    chunker = FileChunker()
    chunks = chunker.chunk_file(Path('test.cpp'))
    for chunk in chunks:
        assert '#include' in chunk.context or chunk.context == ''

def test_line_numbers_correct():
    """Chunk line numbers should match original file."""
    chunker = FileChunker()
    chunks = chunker.chunk_file(Path('test.cpp'))

    # Check no overlap
    for i in range(len(chunks) - 1):
        assert chunks[i].end_line < chunks[i+1].start_line
```

**File**: `tests/test_chunk_analyzer.py`

```python
def test_analyze_chunk():
    """Chunk analysis should return valid results."""
    analyzer = ProductionAnalyzer()
    chunk_analyzer = ChunkAnalyzer(analyzer)

    chunk = Chunk(
        chunk_id='test',
        file_path=Path('test.cpp'),
        start_line=10,
        end_line=20,
        code='void foo() { int* p = new int; }',
        context='#include <iostream>',
        metadata={}
    )

    result = chunk_analyzer.analyze_chunk(chunk)
    assert len(result.issues) > 0
    # Check line numbers adjusted
    for issue in result.issues:
        assert 10 <= issue.line <= 20

def test_parallel_analysis():
    """Parallel analysis should complete successfully."""
    analyzer = ProductionAnalyzer()
    chunk_analyzer = ChunkAnalyzer(analyzer)

    chunks = [create_test_chunk(i) for i in range(5)]
    results = chunk_analyzer.analyze_chunks_parallel(chunks, max_workers=2)

    assert len(results) == 5
```

**File**: `tests/test_result_merger.py`

```python
def test_merge_results():
    """Merger should combine chunk results."""
    result1 = create_result_with_issues([10, 20])
    result2 = create_result_with_issues([30, 40])

    merger = ResultMerger()
    merged = merger.merge([result1, result2])

    assert len(merged.issues) == 4
    assert merged.issues[0].line == 10  # sorted

def test_deduplication():
    """Duplicate issues should be removed."""
    result1 = create_result_with_issues([10])  # memory leak at line 10
    result2 = create_result_with_issues([10])  # same issue

    merger = ResultMerger()
    merged = merger.merge([result1, result2])

    assert len(merged.issues) == 1  # deduplicated
```

### Integration Tests

**File**: `tests/test_chunked_analysis.py`

```python
def test_end_to_end_chunked_analysis():
    """End-to-end test of chunked analysis."""
    # Create 700-line test file
    create_large_test_file('large_test.cpp', 700)

    analyzer = ProductionAnalyzer()
    result = analyzer.analyze_file(
        Path('large_test.cpp'),
        chunk_mode=True,
        max_chunk_lines=200
    )

    # Should complete without errors
    assert result is not None
    assert 'num_chunks' in result.metadata
    assert result.metadata['num_chunks'] >= 3

def test_chunked_matches_ground_truth():
    """Chunked analysis should find expected issues."""
    analyzer = ProductionAnalyzer()
    result = analyzer.analyze_file(
        Path('test-data/large-file-001.cpp'),  # 700 lines, 15 known issues
        chunk_mode=True
    )

    # Should find most issues (≥80%)
    assert len(result.issues) >= 12
```

---

## Performance Requirements

### Speed

| File Size | Current | Target (Chunked) | Improvement |
|-----------|---------|------------------|-------------|
| 300 lines | 30s | 30s | No change |
| 700 lines | 180s (fails) | 60s | 3x faster |
| 1400 lines | N/A (fails) | 120s | Works! |

### Accuracy

- **Target**: F1 ≥ 0.60 on large files (same as small files)
- **Precision**: ≥ 0.65
- **Recall**: ≥ 0.55

### Resource Usage

- **Memory**: Linear with number of chunks (not file size)
- **Tokens**: ~1.5x whole-file analysis (due to context duplication)
- **Parallelization**: Support 2-4 concurrent chunks

---

## Error Handling

### Parse Errors

```python
try:
    tree = parser.parse(code_bytes)
except Exception as e:
    # Fallback to line-based chunking
    chunks = fallback_line_chunking(file_path, max_chunk_lines)
```

### Analysis Errors

```python
try:
    result = analyzer.analyze_chunk(chunk)
except Exception as e:
    # Log error, create empty result, continue
    result = AnalysisResult(file_path=..., issues=[], metadata={'error': str(e)})
```

---

## Rollout Plan

### Phase 5.1: Core Implementation (2 days)

**Tasks**:
- T501: Install tree-sitter dependencies
- T502: Implement FileChunker class
- T503: Implement Chunk dataclass
- T504: Write FileChunker unit tests
- T505: Implement ChunkAnalyzer class
- T506: Write ChunkAnalyzer unit tests
- T507: Implement ResultMerger class
- T508: Write ResultMerger unit tests

**Exit Criteria**: All unit tests pass (>95% coverage)

### Phase 5.2: CLI Integration (1 day)

**Tasks**:
- T509: Modify ProductionAnalyzer.analyze_file()
- T510: Add --chunk flag to CLI
- T511: Wire up components
- T512: Write integration tests
- T513: Test on sample large file

**Exit Criteria**: End-to-end chunked analysis works

### Phase 5.3: Optimization (1 day)

**Tasks**:
- T514: Implement parallel chunk processing
- T515: Add progress indicators
- T516: Optimize context extraction
- T517: Run performance benchmarks

**Exit Criteria**: 700-line file analyzed in < 60 seconds

### Phase 5.4: Documentation (0.5 days)

**Tasks**:
- T518: Update README.md
- T519: Update QUICKSTART.md
- T520: Add examples to docs/
- T521: Create large file ground truth

**Exit Criteria**: User-facing docs complete

### Phase 5.5: Evaluation (0.5 days)

**Tasks**:
- T522: Run experiments on large files
- T523: Document results in PHASE5_COMPLETE.md
- T524: Compare chunked vs non-chunked

**Exit Criteria**: PHASE5_COMPLETE.md published

---

## Success Metrics

### Functional
- ✅ 700+ line files analyzed without errors
- ✅ All unit tests pass (35+ tests)
- ✅ Integration tests pass (3+ scenarios)

### Performance
- ✅ 700 lines in < 60 seconds
- ✅ Linear scaling with file size

### Quality
- ✅ F1 ≥ 0.60 on large file ground truth
- ✅ No regression on small files (31 tests still pass)

---

## Open Questions

1. **Chunk overlap**: Should chunks overlap by N lines for continuity?
   - **Decision**: Start without overlap, add if needed

2. **Parallel vs Sequential**: Default to parallel or sequential?
   - **Decision**: Sequential by default, parallel opt-in via config

3. **Context size**: How much context to include?
   - **Decision**: All includes + current class definition

4. **Fallback strategy**: What if tree-sitter fails?
   - **Decision**: Line-based chunking (every 200 lines)

---

## Next Steps

1. **Review and approve** this specification
2. **Generate task plan** with spec-kit
3. **Execute tasks** T501-T524
4. **Test and iterate** based on results
5. **Document findings** in PHASE5_COMPLETE.md

---

**Approval Required**: Please review and approve before implementation.
