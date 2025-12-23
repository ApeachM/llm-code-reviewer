# Architecture Guide

**C++ LLM Code Reviewer - Complete Architecture Documentation**

This document explains how the entire system works, from high-level concepts to implementation details.

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Core Components](#core-components)
4. [Data Flow](#data-flow)
5. [Technique System](#technique-system)
6. [Plugin Architecture](#plugin-architecture)
7. [Large File Support](#large-file-support)
8. [Example Walkthrough](#example-walkthrough)

---

## Overview

### What is this project?

A **domain-agnostic LLM code analysis platform** that uses Large Language Models (Ollama) to review code and find bugs. While it currently supports C++, the architecture is designed to support any programming language through plugins.

### Key Features

- 🎯 **Multiple Analysis Techniques**: Zero-shot, Few-shot, Chain-of-Thought, Hybrid
- 🔌 **Plugin Architecture**: Easy to add new languages (C++, Python, RTL, etc.)
- 📊 **Experiment Framework**: Compare techniques with F1 scores
- 🚀 **Production Ready**: CLI for file/directory/PR analysis
- 📦 **Large File Support**: Handles 700+ line files via chunking
- 🤖 **Local LLMs**: Uses Ollama (no API keys needed)

---

## System Architecture

### High-Level Overview

```mermaid
graph TB
    subgraph "User Interface Layer"
        CLI[CLI Commands]
        CLI --> |analyze file| FileCmd[File Analysis]
        CLI --> |analyze dir| DirCmd[Directory Analysis]
        CLI --> |analyze pr| PRCmd[PR Review]
    end

    subgraph "Analysis Layer"
        FileCmd --> PA[ProductionAnalyzer]
        DirCmd --> PA
        PRCmd --> PA
        PA --> |uses| Plugin[Domain Plugin]
        PA --> |uses| Technique[Analysis Technique]
    end

    subgraph "Technique Layer"
        Technique --> ZS[Zero-Shot]
        Technique --> FS[Few-Shot]
        Technique --> CoT[Chain-of-Thought]
        Technique --> Hybrid[Hybrid]
    end

    subgraph "LLM Layer"
        ZS --> Ollama[Ollama Client]
        FS --> Ollama
        CoT --> Ollama
        Hybrid --> Ollama
        Ollama --> |local| LLM[deepseek-coder:33b]
    end

    subgraph "Plugin Layer"
        Plugin --> CppPlugin[C++ Plugin]
        Plugin --> FuturePlugin[Future Plugins...]
        CppPlugin --> |provides| Examples[Few-Shot Examples]
        CppPlugin --> |provides| Filters[File Filters]
    end

    subgraph "Support Systems"
        PA --> Chunker[File Chunker]
        Chunker --> |tree-sitter| AST[AST Parser]
        PA --> Merger[Result Merger]
    end

    style CLI fill:#1976d2,color:#fff
    style PA fill:#e65100,color:#fff
    style Ollama fill:#7b1fa2,color:#fff
    style CppPlugin fill:#388e3c,color:#fff
```

### Three-Layer Architecture

```mermaid
graph LR
    subgraph "Layer 1: Framework Core"
        A[Analysis Techniques]
        B[Evaluation System]
        C[Experiment Runner]
    end

    subgraph "Layer 2: Domain Plugins"
        D[C++ Plugin]
        E[Future Plugins]
    end

    subgraph "Layer 3: Applications"
        F[CLI]
        G[Production Analyzer]
    end

    A --> D
    A --> E
    D --> F
    D --> G
    E --> F
    E --> G

    style A fill:#1976d2,color:#fff
    style D fill:#388e3c,color:#fff
    style F fill:#f9a825,color:#fff
```

**Layer 1**: Domain-agnostic analysis techniques
**Layer 2**: Language-specific plugins (C++, Python, etc.)
**Layer 3**: User-facing applications (CLI, API, etc.)

---

## Core Components

### 1. ProductionAnalyzer

**Location**: `plugins/production_analyzer.py`

**Purpose**: Main orchestrator for code analysis.

```mermaid
graph TD
    PA[ProductionAnalyzer]
    PA --> Init[Initialize with Plugin & Model]
    Init --> File[analyze_file]
    Init --> Dir[analyze_directory]
    Init --> PR[analyze_pull_request]

    File --> Check{File Size?}
    Check -->|< 300 lines| Direct[Direct Analysis]
    Check -->|≥ 300 lines| Chunk[Chunked Analysis]

    Direct --> Technique[Analysis Technique]
    Chunk --> Chunker[FileChunker]
    Chunker --> Multiple[Multiple Chunks]
    Multiple --> Parallel[Parallel Analysis]
    Parallel --> Merge[ResultMerger]

    Technique --> Result[AnalysisResult]
    Merge --> Result

    style PA fill:#e65100,color:#fff
    style Check fill:#f9a825,color:#fff
    style Result fill:#2e7d32,color:#fff
```

**Key Methods**:

```python
class ProductionAnalyzer:
    def analyze_file(self, file_path: Path, chunk_mode: bool = False) -> AnalysisResult:
        """
        Analyze a single file.

        Flow:
        1. Check if file should be analyzed (plugin filter)
        2. Read file content
        3. If chunking enabled and file > threshold:
           a. FileChunker splits into chunks
           b. ChunkAnalyzer analyzes each chunk in parallel
           c. ResultMerger combines results
        4. Otherwise: Direct analysis with technique
        5. Return AnalysisResult with issues
        """
```

### 2. Analysis Techniques

**Location**: `framework/techniques/`

All techniques implement `BaseTechnique` interface:

```python
class BaseTechnique(ABC):
    @abstractmethod
    def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """Analyze code and return issues."""
        pass
```

#### Available Techniques

```mermaid
graph TB
    Base[BaseTechnique]
    Base --> ZS[ZeroShotTechnique]
    Base --> FS[FewShotTechnique]
    Base --> CoT[ChainOfThoughtTechnique]
    Base --> MP[MultiPassTechnique]
    Base --> Hybrid[HybridTechnique]

    ZS --> |F1: 0.498| ZSDesc[Simple prompt, no examples]
    FS --> |F1: 0.615| FSDesc[5 examples, best single technique]
    CoT --> |F1: 0.596| CoTDesc[Step-by-step reasoning]
    MP --> |F1: 0.601| MPDesc[Multiple passes, filtering]
    Hybrid --> |F1: 0.634| HybridDesc[Few-shot + CoT + filtering]

    style FS fill:#2e7d32,color:#fff
    style Hybrid fill:#558b2f,color:#fff
```

**Winner**: Few-Shot-5 (F1=0.615) for production, Hybrid (F1=0.634) for best performance.

### 3. Domain Plugins

**Location**: `plugins/`

Plugins provide language-specific knowledge:

```python
class DomainPlugin(ABC):
    @abstractmethod
    def get_file_extensions(self) -> List[str]:
        """Return supported file extensions."""

    @abstractmethod
    def should_analyze_file(self, file_path: Path) -> bool:
        """Return True if file should be analyzed."""

    @abstractmethod
    def get_few_shot_examples(self) -> List[Example]:
        """Return few-shot examples for this domain."""

    @abstractmethod
    def get_categories(self) -> List[str]:
        """Return issue categories for this domain."""
```

**C++ Plugin Example**:

```python
class CppPlugin(DomainPlugin):
    def get_file_extensions(self) -> List[str]:
        return ['.cpp', '.cc', '.cxx', '.h', '.hpp']

    def should_analyze_file(self, file_path: Path) -> bool:
        # Skip test files, third-party, etc.
        if 'test' in file_path.name.lower():
            return False
        return True

    def get_categories(self) -> List[str]:
        return [
            'memory-safety',    # malloc/free, new/delete
            'concurrency',      # data races, deadlocks
            'performance',      # unnecessary copies
            'modern-cpp',       # C++11/14/17 features
            'correctness'       # logic errors
        ]
```

### 4. Large File Support (Phase 5)

**Components**: FileChunker, ChunkAnalyzer, ResultMerger

```mermaid
graph LR
    Large[Large File<br/>700+ lines]
    Large --> FC[FileChunker]
    FC --> |tree-sitter| AST[Parse AST]
    AST --> C1[Chunk 1<br/>lines 1-200]
    AST --> C2[Chunk 2<br/>lines 201-400]
    AST --> C3[Chunk 3<br/>lines 401-600]
    AST --> C4[Chunk 4<br/>lines 601-700]

    C1 --> CA[ChunkAnalyzer]
    C2 --> CA
    C3 --> CA
    C4 --> CA

    CA --> |parallel| R1[Result 1]
    CA --> |parallel| R2[Result 2]
    CA --> |parallel| R3[Result 3]
    CA --> |parallel| R4[Result 4]

    R1 --> RM[ResultMerger]
    R2 --> RM
    R3 --> RM
    R4 --> RM

    RM --> |deduplicate| Final[Final Result<br/>11 issues]

    style FC fill:#1976d2,color:#fff
    style CA fill:#7b1fa2,color:#fff
    style RM fill:#388e3c,color:#fff
```

**FileChunker** (`framework/chunker.py`):
- Uses tree-sitter to parse C++ AST
- Extracts functions/classes as chunks (~200 lines each)
- Preserves context (includes, usings, namespaces)
- Fallback to line-based chunking if parse fails

**ChunkAnalyzer** (`framework/chunk_analyzer.py`):
- Analyzes each chunk independently
- Adds file-level context to each chunk
- Adjusts line numbers back to file coordinates
- Supports parallel processing (4 workers)

**ResultMerger** (`framework/result_merger.py`):
- Deduplicates issues by (line, category)
- Prefers issues with longer reasoning
- Combines metadata (tokens, latency, etc.)

---

## Data Flow

### Single File Analysis (No Chunking)

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant ProductionAnalyzer as PA
    participant CppPlugin
    participant FewShotTechnique as Technique
    participant OllamaClient as Ollama
    participant LLM

    User->>CLI: python -m cli.main analyze file test.cpp
    CLI->>PA: analyze_file(test.cpp)
    PA->>CppPlugin: should_analyze_file(test.cpp)?
    CppPlugin-->>PA: True
    PA->>PA: Read file content (100 lines)
    PA->>Technique: analyze(code)
    Technique->>CppPlugin: get_few_shot_examples()
    CppPlugin-->>Technique: 5 examples
    Technique->>Technique: Build prompt with examples
    Technique->>Ollama: generate(prompt)
    Ollama->>LLM: HTTP request to Ollama
    LLM-->>Ollama: JSON response
    Ollama-->>Technique: Parsed issues
    Technique-->>PA: AnalysisResult(issues=[...])
    PA-->>CLI: AnalysisResult
    CLI-->>User: Found 4 issue(s)
```

### Large File Analysis (With Chunking)

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant PA as ProductionAnalyzer
    participant FC as FileChunker
    participant CA as ChunkAnalyzer
    participant Technique
    participant RM as ResultMerger

    User->>CLI: python -m cli.main analyze file large.cpp --chunk
    CLI->>PA: analyze_file(large.cpp, chunk_mode=True)
    PA->>PA: Check file size (645 lines)
    PA->>FC: chunk_file(large.cpp, max_lines=200)
    FC->>FC: Parse with tree-sitter
    FC->>FC: Extract 20 functions
    FC-->>PA: [Chunk1, Chunk2, ..., Chunk20]

    PA->>CA: analyze_chunks_parallel(chunks, workers=4)

    par Parallel Analysis
        CA->>Technique: analyze(Chunk1)
        Technique-->>CA: Result1
    and
        CA->>Technique: analyze(Chunk2)
        Technique-->>CA: Result2
    and
        CA->>Technique: analyze(Chunk3)
        Technique-->>CA: Result3
    and
        CA->>Technique: analyze(Chunk4)
        Technique-->>CA: Result4
    end

    CA-->>PA: [Result1, ..., Result20]
    PA->>RM: merge([Result1, ..., Result20])
    RM->>RM: Deduplicate by (line, category)
    RM->>RM: Sort by line number
    RM-->>PA: Combined AnalysisResult (11 unique issues)
    PA-->>CLI: AnalysisResult
    CLI-->>User: Found 11 issue(s) in 20 chunks
```

---

## Technique System

### How Techniques Work

Each technique is a strategy for prompting the LLM:

#### 1. Zero-Shot

```python
prompt = f"""
Analyze this C++ code for bugs:

{code}

Find issues in these categories:
- memory-safety
- concurrency
- performance

Return JSON: [{{"line": X, "category": "...", "description": "..."}}]
"""
```

**Pros**: Simple, no examples needed
**Cons**: Lower accuracy (F1=0.498)

#### 2. Few-Shot (Production Default)

```python
examples = plugin.get_few_shot_examples()  # 5 examples

prompt = f"""
I'll show you examples of C++ bugs, then analyze new code.

Example 1:
Code: int* p = new int; // never deleted
Issue: {{"line": 1, "category": "memory-safety", "description": "Memory leak"}}

Example 2:
... (4 more examples)

Now analyze this code:
{code}
"""
```

**Pros**: Best single technique (F1=0.615)
**Cons**: Requires curated examples

#### 3. Chain-of-Thought

```python
prompt = f"""
Analyze this code step-by-step:

Step 1: Read the code
Step 2: Identify potential issues
Step 3: For each issue:
   a. What is the bug?
   b. Why is it a problem?
   c. How severe is it?
Step 4: Return JSON with issues

Code:
{code}
"""
```

**Pros**: Better reasoning (F1=0.596)
**Cons**: Slower (more tokens)

#### 4. Hybrid (Best Performance)

```python
# Pass 1: Few-shot for broad coverage
few_shot_issues = few_shot_technique.analyze(code)

# Pass 2: Chain-of-thought for specific categories
cot_issues = cot_technique.analyze(code, categories=['memory-safety'])

# Pass 3: Deduplicate and filter by confidence
all_issues = few_shot_issues + cot_issues
deduplicated = deduplicate(all_issues)
filtered = [i for i in deduplicated if i.confidence > 0.7]
```

**Pros**: Best accuracy (F1=0.634)
**Cons**: 2x cost (two LLM calls)

---

## Plugin Architecture

### Why Plugins?

Different programming languages have different:
- **Bug patterns**: C++ has memory leaks, Python has type errors
- **Best practices**: C++17 features, Python 3.10 features
- **Code structure**: Classes, functions, modules
- **Tools**: Compilers, linters, formatters

**Solution**: Plugin system separates language-specific knowledge from core analysis.

### Plugin Interface

```mermaid
classDiagram
    class DomainPlugin {
        <<abstract>>
        +get_file_extensions() List[str]
        +should_analyze_file(Path) bool
        +get_few_shot_examples() List[Example]
        +get_categories() List[str]
        +preprocess_code(str) str
        +postprocess_result(AnalysisResult) AnalysisResult
    }

    class CppPlugin {
        +get_file_extensions() ['.cpp', '.h']
        +should_analyze_file() Skip tests/third-party
        +get_few_shot_examples() 5 C++ examples
        +get_categories() memory/concurrency/perf
    }

    class PythonPlugin {
        +get_file_extensions() ['.py']
        +get_categories() type-safety/syntax/imports
    }

    class RTLPlugin {
        +get_file_extensions() ['.v', '.sv']
        +get_categories() timing/power/area
    }

    DomainPlugin <|-- CppPlugin
    DomainPlugin <|-- PythonPlugin
    DomainPlugin <|-- RTLPlugin
```

### Creating a New Plugin

**Example: Python Plugin** (not yet implemented)

```python
# plugins/python_plugin.py

from plugins.domain_plugin import DomainPlugin, Example

class PythonPlugin(DomainPlugin):
    def get_file_extensions(self) -> List[str]:
        return ['.py']

    def should_analyze_file(self, file_path: Path) -> bool:
        # Skip __init__.py, test files
        if file_path.name == '__init__.py':
            return False
        if 'test_' in file_path.name:
            return False
        return True

    def get_categories(self) -> List[str]:
        return [
            'type-safety',      # None checks, type hints
            'exception-handling',  # try/except
            'imports',          # circular imports
            'python-idioms'     # use list comprehension
        ]

    def get_few_shot_examples(self) -> List[Example]:
        return [
            Example(
                code="x = None\nprint(x.upper())",
                issues=[
                    Issue(
                        line=2,
                        category='type-safety',
                        description='AttributeError: NoneType has no attribute upper'
                    )
                ]
            ),
            # ... more examples
        ]
```

**Usage**:

```python
# Use Python plugin
analyzer = ProductionAnalyzer(plugin=PythonPlugin())
result = analyzer.analyze_file(Path('script.py'))
```

---

## Large File Support

### Problem

Files with 700+ lines:
- **Token limit exceeded**: Few-shot-5 uses ~500 tokens, leaving ~1500 for code. 700 lines = 3000-4000 tokens.
- **Context overload**: LLM forgets issues at the beginning by the end.
- **Slow**: 2-3+ minutes to analyze.

### Solution: Function-Level Chunking

```mermaid
graph TB
    subgraph "Input"
        LF[Large File<br/>700 lines]
    end

    subgraph "Step 1: Parse"
        LF --> TS[tree-sitter<br/>C++ Parser]
        TS --> AST[Abstract Syntax Tree]
    end

    subgraph "Step 2: Extract"
        AST --> EF[Extract Functions]
        EF --> F1[Function 1<br/>lines 10-50]
        EF --> F2[Function 2<br/>lines 60-120]
        EF --> F3[Function 3<br/>lines 130-200]
        EF --> FN[... 20 functions]
    end

    subgraph "Step 3: Add Context"
        F1 --> C1[Chunk 1<br/>context + function1]
        F2 --> C2[Chunk 2<br/>context + function2]
        F3 --> C3[Chunk 3<br/>context + function3]

        Context[File Context<br/>includes, usings] --> C1
        Context --> C2
        Context --> C3
    end

    subgraph "Step 4: Analyze in Parallel"
        C1 --> A1[Analyze Chunk 1]
        C2 --> A2[Analyze Chunk 2]
        C3 --> A3[Analyze Chunk 3]

        A1 --> R1[Issues: line 15, 42]
        A2 --> R2[Issues: line 87, 103]
        A3 --> R3[Issues: line 156]
    end

    subgraph "Step 5: Merge & Deduplicate"
        R1 --> Merge[ResultMerger]
        R2 --> Merge
        R3 --> Merge
        Merge --> Final[Final Result<br/>5 unique issues<br/>sorted by line]
    end

    style LF fill:#c62828,color:#fff
    style AST fill:#3949ab,color:#fff
    style C1 fill:#00796b,color:#fff
    style A1 fill:#f9a825,color:#fff
    style Final fill:#388e3c,color:#fff
```

### Key Implementation Details

#### Context Extraction

```python
def _extract_file_context(self, tree, code_text: str) -> str:
    """
    Extract file-level declarations that affect all functions.

    Extracts:
    - #include directives
    - using statements
    - namespace aliases
    """
    context_lines = []
    for node in tree.root_node.children:
        if node.type in ['preproc_include', 'using_declaration']:
            context_lines.append(code_text[node.start_byte:node.end_byte])
    return '\n'.join(context_lines)
```

**Result**: Each chunk gets necessary context without full file.

#### Line Number Adjustment

```python
def _adjust_line_numbers(self, result: AnalysisResult, chunk: Chunk) -> AnalysisResult:
    """
    Adjust line numbers from chunk coordinates to file coordinates.

    Example:
    - Context: 5 lines
    - Chunk starts at file line 100
    - Issue reported at line 8 (in chunk+context)
    - Adjusted: file line = 100 + (8 - 5 - 1) = 102
    """
    context_lines = len(chunk.context.split('\n'))

    for issue in result.issues:
        chunk_line = issue.line
        file_line = chunk.start_line + (chunk_line - context_lines - 2)

        # Clamp to chunk bounds
        file_line = max(chunk.start_line, min(file_line, chunk.end_line))
        issue.line = file_line

    return result
```

**Result**: Issues reference correct line numbers in original file.

#### Deduplication

```python
def _deduplicate_issues(self, issues: List[Issue]) -> List[Issue]:
    """
    Remove duplicate issues across chunks.

    Strategy:
    1. Group by (line, category)
    2. Within group, keep issue with longest reasoning
    """
    groups = {}
    for issue in issues:
        key = (issue.line, issue.category)
        if key not in groups:
            groups[key] = []
        groups[key].append(issue)

    deduplicated = []
    for group in groups.values():
        # Keep most detailed issue
        best = max(group, key=lambda i: len(i.reasoning))
        deduplicated.append(best)

    return sorted(deduplicated, key=lambda i: i.line)
```

**Result**: No duplicate issues at chunk boundaries.

---

## Example Walkthrough

Let's walk through a complete analysis to see how all pieces fit together.

### User Command

```bash
python -m cli.main analyze file example.cpp --chunk
```

### Step-by-Step Execution

#### 1. CLI Entry Point

```python
# cli/main.py

@cli.command()
@click.argument('file_path')
@click.option('--chunk/--no-chunk', default=False)
def file(file_path: str, chunk: bool):
    # Create analyzer
    analyzer = ProductionAnalyzer(
        plugin=CppPlugin(),
        model_name='deepseek-coder:33b-instruct'
    )

    # Analyze file
    result = analyzer.analyze_file(
        Path(file_path),
        chunk_mode=chunk
    )

    # Display results
    console.print(f"Found {len(result.issues)} issue(s)")
    for issue in result.issues:
        console.print(f"Line {issue.line}: {issue.description}")
```

#### 2. ProductionAnalyzer Decision

```python
# plugins/production_analyzer.py

def analyze_file(self, file_path: Path, chunk_mode: bool = False) -> AnalysisResult:
    # Check if file should be analyzed
    if not self.plugin.should_analyze_file(file_path):
        return None  # Skip

    # Read file
    code = file_path.read_text()
    lines = len(code.split('\n'))

    # Decision: chunk or direct?
    if chunk_mode and lines > 300:
        return self._analyze_chunked(file_path, max_chunk_lines=200)
    else:
        return self._analyze_direct(code)
```

**In our example**: File has 645 lines → Use chunking

#### 3. Chunking Process

```python
# framework/chunker.py

def chunk_file(self, file_path: Path) -> List[Chunk]:
    # Parse with tree-sitter
    tree = self.parser.parse(file_path.read_bytes())

    # Extract file context
    context = self._extract_file_context(tree, code_text)
    # context = "#include <iostream>\n#include <vector>\nusing namespace std;"

    # Extract functions/classes
    chunks = []
    for node in tree.root_node.children:
        if node.type == 'function_definition':
            chunk = self._create_chunk_from_node(node, file_path, code_text, context)
            chunks.append(chunk)

    return chunks  # 20 chunks
```

**Result**: 20 chunks, each ~30 lines of code + 3 lines of context

#### 4. Parallel Analysis

```python
# framework/chunk_analyzer.py

def analyze_chunks_parallel(self, chunks: List[Chunk], max_workers: int = 4):
    results = []

    with ThreadPoolExecutor(max_workers=4) as executor:
        # Submit all chunks
        futures = {
            executor.submit(self.analyze_chunk, chunk): chunk
            for chunk in chunks
        }

        # Collect results
        for future in as_completed(futures):
            result = future.result()
            results.append(result)

    return results  # 20 results
```

**Timeline**: 20 chunks × 8 seconds each ÷ 4 workers = **40 seconds total**

#### 5. Individual Chunk Analysis

For each chunk:

```python
# framework/chunk_analyzer.py

def analyze_chunk(self, chunk: Chunk) -> AnalysisResult:
    # Combine context + code
    full_code = f"{chunk.context}\n\n{chunk.code}"
    # full_code = """
    # #include <iostream>
    # using namespace std;
    #
    # void processData(vector<int> data) {
    #     for (int i = 0; i < data.size(); i++) {
    #         cout << data[i] << endl;
    #     }
    # }
    # """

    # Analyze with technique
    request = AnalysisRequest(code=full_code, language='cpp')
    result = self.analyzer.technique.analyze(request)
    # result.issues = [
    #     Issue(line=6, category='performance', description='Pass by value'),
    #     Issue(line=7, category='modern-cpp', description='Use range-for')
    # ]

    # Adjust line numbers
    result = self._adjust_line_numbers(result, chunk)
    # result.issues[0].line = 23  # Adjusted to file coordinates
    # result.issues[1].line = 24

    return result
```

#### 6. Merge Results

```python
# framework/result_merger.py

def merge(self, chunk_results: List[AnalysisResult]) -> AnalysisResult:
    # Collect all issues
    all_issues = []
    for result in chunk_results:
        all_issues.extend(result.issues)
    # all_issues = 23 issues (some duplicates)

    # Deduplicate
    deduplicated = self._deduplicate_issues(all_issues)
    # deduplicated = 11 unique issues

    # Sort by line number
    sorted_issues = sorted(deduplicated, key=lambda i: i.line)

    # Combine metadata
    metadata = {
        'technique': 'chunked_analysis',
        'num_chunks': len(chunk_results),  # 20
        'total_tokens': sum(r.metadata['tokens_used'] for r in chunk_results),
        'total_latency': sum(r.metadata['latency'] for r in chunk_results)
    }

    return AnalysisResult(issues=sorted_issues, metadata=metadata)
```

#### 7. Display to User

```python
# cli/main.py (continued)

console.print(f"\nFound {len(result.issues)} issue(s):\n")

for issue in result.issues:
    severity_emoji = {
        'critical': '🔴',
        'warning': '🟡',
        'info': '🔵'
    }[issue.severity]

    console.print(f"{severity_emoji} Line {issue.line} [{issue.category}] {issue.description}")
    console.print(f"   {issue.reasoning}\n")
```

**Output**:

```
Analyzing file: example.cpp
Model: deepseek-coder:33b-instruct
Chunk mode: Enabled (max 200 lines per chunk)

Found 11 issue(s):

🔴 Line 10 [memory-safety] Memory leak - dynamically allocated array never deleted
   Array 'data' is allocated with 'new[]' but no corresponding 'delete[]'.

🟡 Line 23 [performance] Pass by value instead of reference
   Function takes vector by value, causing unnecessary copy.

🟡 Line 24 [modern-cpp] Use range-based for loop
   Traditional for loop can be replaced with range-for for safety.

... (8 more issues)

Analysis completed in 42.3 seconds (20 chunks, 4 workers)
```

---

## Summary

### Key Takeaways

1. **Three-Layer Architecture**: Framework → Plugins → Applications
2. **Plugin System**: Easy to add new languages (just implement DomainPlugin)
3. **Multiple Techniques**: Zero-shot, Few-shot, CoT, Hybrid (F1: 0.498 → 0.634)
4. **Production Ready**: Few-shot-5 technique (F1=0.615) used by default
5. **Large File Support**: Tree-sitter chunking handles 700+ line files in 40s
6. **Parallel Processing**: 4 workers analyze chunks concurrently

### Architecture Principles

- **Modularity**: Each component has single responsibility
- **Extensibility**: Add languages via plugins, add techniques via BaseTechnique
- **Testability**: 83/84 tests passing (98.8%)
- **Performance**: Parallel chunking for large files
- **Transparency**: F1 scores, ground truth, experiment tracking

### For Developers

- **Adding a language**: Implement `DomainPlugin` (see Python example above)
- **Adding a technique**: Inherit from `BaseTechnique` and implement `analyze()`
- **Modifying analysis**: Override `ProductionAnalyzer` methods
- **Adding commands**: Add Click commands to `cli/main.py`

---

**Next Steps**: See [DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md) for hands-on tutorial.
