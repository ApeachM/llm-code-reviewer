# Developer Guide

**Hands-on guide for contributors and developers**

This guide shows you how to work with the codebase through practical examples.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Project Structure](#project-structure)
3. [Common Tasks](#common-tasks)
4. [Adding New Features](#adding-new-features)
5. [Testing](#testing)
6. [Debugging](#debugging)

---

## Getting Started

### Prerequisites

```bash
# Required
- Python 3.10+
- Ollama (for local LLM)
- Git

# Optional
- tree-sitter-cpp (installed automatically)
```

### Setup

```bash
# 1. Clone repository
git clone <your-repo-url>
cd cpp-llm-reviewer

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Ollama model
ollama pull deepseek-coder:33b-instruct

# 5. Run tests
pytest tests/ -v

# 6. Try a simple analysis
python -m cli.main analyze file test-data/sample-pr-001/after.cpp
```

---

## Project Structure

```
cpp-llm-reviewer/
├── cli/                      # Command-line interface
│   └── main.py              # CLI commands (file, dir, pr)
├── framework/               # Core analysis framework
│   ├── chunker.py           # File chunking (Phase 5)
│   ├── chunk_analyzer.py    # Chunk analysis
│   ├── result_merger.py     # Result deduplication
│   ├── evaluation.py        # F1 score calculation
│   ├── experiment_runner.py # Experiment framework
│   ├── models.py            # Data models (Pydantic)
│   ├── ollama_client.py     # Ollama LLM client
│   └── techniques/          # Analysis techniques
│       ├── base.py          # BaseTechnique interface
│       ├── zero_shot.py     # Zero-shot technique
│       ├── few_shot.py      # Few-shot technique (production)
│       ├── chain_of_thought.py
│       ├── multi_pass.py
│       └── hybrid.py        # Best technique (F1=0.634)
├── plugins/                 # Domain plugins
│   ├── domain_plugin.py     # Plugin interface
│   ├── cpp_plugin.py        # C++ plugin (production)
│   └── production_analyzer.py  # Main analyzer
├── tests/                   # Test suite (83/84 passing)
│   ├── test_chunker.py
│   ├── test_chunk_analyzer.py
│   ├── test_result_merger.py
│   ├── test_integration_chunking.py
│   ├── test_phase0_integration.py
│   └── test_phase1_integration.py
├── experiments/             # Research experiments
│   ├── configs/             # Experiment configurations
│   ├── ground_truth/        # 20 annotated examples
│   └── results/             # Experiment results (gitignored)
├── docs/                    # Documentation
│   ├── architecture/        # Architecture docs (you are here)
│   ├── PHASE0-5_COMPLETE.md # Phase completion docs
│   └── README.md            # Docs index
├── test-data/               # Test data
│   └── sample-pr-001/       # Sample PR with bugs
├── README.md                # Main documentation
├── QUICKSTART.md            # 5-minute tutorial
└── requirements.txt         # Python dependencies
```

---

## Common Tasks

### 1. Analyze a File

```bash
# Simple analysis
python -m cli.main analyze file mycode.cpp

# With chunking (for large files)
python -m cli.main analyze file large.cpp --chunk

# With custom chunk size
python -m cli.main analyze file large.cpp --chunk --chunk-size 150

# Save to markdown
python -m cli.main analyze file mycode.cpp --output report.md
```

### 2. Analyze a Directory

```bash
# Analyze all C++ files in src/
python -m cli.main analyze dir src/

# With chunking enabled
python -m cli.main analyze dir src/ --chunk

# Save report
python -m cli.main analyze dir src/ --output project-review.md
```

### 3. Review a Pull Request

```bash
# Compare branches
python -m cli.main analyze pr --base main --head feature-branch

# Save PR review
python -m cli.main analyze pr --base main --head feature --output pr-review.md

# With chunking for large PRs
python -m cli.main analyze pr --base main --head feature --chunk
```

### 4. Run an Experiment

```bash
# Run single experiment
python -m cli.main experiment run --config experiments/configs/few_shot_5.yml

# Compare techniques
python -m cli.main experiment compare few-shot-5 hybrid

# View leaderboard
python -m cli.main experiment leaderboard
```

### 5. Run Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_chunker.py -v

# With coverage
pytest tests/ --cov=framework --cov-report=html

# Fast tests only (skip slow LLM calls)
pytest tests/ -m "not slow"
```

---

## Adding New Features

### Example 1: Add a New Programming Language

Let's add Python support!

#### Step 1: Create Plugin

```python
# plugins/python_plugin.py

from plugins.domain_plugin import DomainPlugin, Example
from framework.models import Issue

class PythonPlugin(DomainPlugin):
    def get_file_extensions(self) -> List[str]:
        return ['.py']

    def should_analyze_file(self, file_path: Path) -> bool:
        # Skip test files and __init__.py
        if file_path.name == '__init__.py':
            return False
        if file_path.name.startswith('test_'):
            return False
        return True

    def get_categories(self) -> List[str]:
        return [
            'type-safety',      # None checks, type hints
            'exception-handling',  # try/except issues
            'imports',          # circular imports
            'python-idioms',    # unpythonic code
            'security'          # eval, exec, etc.
        ]

    def get_few_shot_examples(self) -> List[Example]:
        return [
            Example(
                code='''
def get_user_name(user):
    return user.name  # Bug: user might be None
''',
                issues=[
                    Issue(
                        line=2,
                        category='type-safety',
                        severity='critical',
                        description='Potential AttributeError if user is None',
                        reasoning='Function does not check if user is None before accessing .name attribute'
                    )
                ]
            ),
            Example(
                code='''
import json

def load_config():
    with open('config.json') as f:
        return json.load(f)  # Bug: no exception handling
''',
                issues=[
                    Issue(
                        line=4,
                        category='exception-handling',
                        severity='warning',
                        description='FileNotFoundError not handled',
                        reasoning='If config.json does not exist, program will crash'
                    )
                ]
            ),
            # Add 3 more examples for 5 total
        ]

    def preprocess_code(self, code: str) -> str:
        # Optional: Add Python-specific preprocessing
        return code

    def postprocess_result(self, result: AnalysisResult) -> AnalysisResult:
        # Optional: Add Python-specific post-processing
        return result
```

#### Step 2: Use Plugin

```python
# In cli/main.py or your script

from plugins.python_plugin import PythonPlugin
from plugins.production_analyzer import ProductionAnalyzer

# Create analyzer with Python plugin
analyzer = ProductionAnalyzer(plugin=PythonPlugin())

# Analyze Python file
result = analyzer.analyze_file(Path('script.py'))

# Display results
for issue in result.issues:
    print(f"Line {issue.line}: {issue.description}")
```

#### Step 3: Add Tests

```python
# tests/test_python_plugin.py

import pytest
from plugins.python_plugin import PythonPlugin

def test_python_extensions():
    plugin = PythonPlugin()
    assert '.py' in plugin.get_file_extensions()

def test_should_analyze_file():
    plugin = PythonPlugin()

    # Should analyze
    assert plugin.should_analyze_file(Path('script.py'))
    assert plugin.should_analyze_file(Path('main.py'))

    # Should skip
    assert not plugin.should_analyze_file(Path('__init__.py'))
    assert not plugin.should_analyze_file(Path('test_foo.py'))

def test_few_shot_examples():
    plugin = PythonPlugin()
    examples = plugin.get_few_shot_examples()

    assert len(examples) >= 5
    assert all(isinstance(ex, Example) for ex in examples)
    assert all(len(ex.issues) > 0 for ex in examples)

def test_categories():
    plugin = PythonPlugin()
    categories = plugin.get_categories()

    assert 'type-safety' in categories
    assert 'exception-handling' in categories
```

#### Step 4: Run Tests

```bash
pytest tests/test_python_plugin.py -v
```

---

### Example 2: Add a New Analysis Technique

Let's create a "Critique" technique that finds code smells!

#### Step 1: Implement Technique

```python
# framework/techniques/critique.py

from framework.techniques.base import BaseTechnique
from framework.models import AnalysisRequest, AnalysisResult, Issue

class CritiqueTechnique(BaseTechnique):
    """
    Critique technique for code quality issues.

    Focuses on:
    - Code smells (long functions, deep nesting)
    - Naming issues (unclear variable names)
    - Design patterns (violations)
    """

    def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        # Build prompt
        prompt = self._build_prompt(request)

        # Call LLM
        response = self.client.generate(prompt)

        # Parse response
        issues = self._parse_response(response)

        return AnalysisResult(
            issues=issues,
            metadata={
                'technique': 'critique',
                'tokens_used': response.get('tokens', 0),
                'latency': response.get('latency', 0)
            }
        )

    def _build_prompt(self, request: AnalysisRequest) -> str:
        return f'''
You are a code reviewer focusing on code quality and maintainability.

Review this {request.language} code for code smells:

1. Function length (> 50 lines)
2. Deep nesting (> 3 levels)
3. Unclear variable names (x, temp, data)
4. Magic numbers (hardcoded constants)
5. Duplicate code
6. Missing abstractions

Code:
```{request.language}
{request.code}
```

For each issue found, return JSON:
[{{
  "line": <line number>,
  "category": "<code-smell-type>",
  "severity": "<info|warning|critical>",
  "description": "<brief description>",
  "reasoning": "<why is this a problem>",
  "confidence": <0.0-1.0>
}}]

Return only valid JSON, no other text.
'''

    def _parse_response(self, response: str) -> List[Issue]:
        # Parse JSON response
        import json
        try:
            data = json.loads(response)
            return [Issue(**item) for item in data]
        except:
            return []
```

#### Step 2: Register Technique

```python
# framework/techniques/__init__.py

from framework.techniques.critique import CritiqueTechnique

class TechniqueFactory:
    @staticmethod
    def create(technique_name: str, client, config: dict):
        techniques = {
            'zero-shot': ZeroShotTechnique,
            'few-shot': FewShotTechnique,
            'chain-of-thought': ChainOfThoughtTechnique,
            'multi-pass': MultiPassTechnique,
            'hybrid': HybridTechnique,
            'critique': CritiqueTechnique,  # <-- Add here
        }

        if technique_name not in techniques:
            raise ValueError(f"Unknown technique: {technique_name}")

        return techniques[technique_name](client, config)
```

#### Step 3: Create Experiment Config

```yaml
# experiments/configs/critique.yml

experiment_id: critique
technique_name: critique
model_name: deepseek-coder:33b-instruct

# Model parameters
temperature: 0.2
max_tokens: 2000

# Technique parameters
technique_params:
  focus_areas:
    - function-length
    - nesting
    - naming
    - magic-numbers
```

#### Step 4: Run Experiment

```bash
python -m cli.main experiment run --config experiments/configs/critique.yml
```

---

### Example 3: Add Chunking for New Language

Let's add Python chunking support!

#### Step 1: Install tree-sitter-python

```bash
pip install tree-sitter-python
```

#### Step 2: Extend FileChunker

```python
# framework/chunker.py

class FileChunker:
    def __init__(self, language: str = 'cpp', max_chunk_lines: int = 200):
        self.language = language
        self.max_chunk_lines = max_chunk_lines

        # Initialize parser based on language
        if language == 'cpp':
            import tree_sitter_cpp as ts_cpp
            CPP_LANGUAGE = Language(ts_cpp.language())
            self.parser = Parser(CPP_LANGUAGE)
        elif language == 'python':
            import tree_sitter_python as ts_python
            PY_LANGUAGE = Language(ts_python.language())
            self.parser = Parser(PY_LANGUAGE)
        else:
            raise ValueError(f"Unsupported language: {language}")

    def chunk_file(self, file_path: Path) -> List[Chunk]:
        # Parse file
        tree = self.parser.parse(file_path.read_bytes())

        # Extract based on language
        if self.language == 'cpp':
            return self._chunk_cpp(tree, file_path)
        elif self.language == 'python':
            return self._chunk_python(tree, file_path)

    def _chunk_python(self, tree, file_path: Path) -> List[Chunk]:
        """Chunk Python file by functions and classes."""
        chunks = []
        code_text = file_path.read_text()

        # Extract imports as context
        context = self._extract_python_context(tree, code_text)

        # Extract functions and classes
        for node in tree.root_node.children:
            if node.type in ['function_definition', 'class_definition']:
                chunk = self._create_chunk_from_node(node, file_path, code_text, context)
                chunks.append(chunk)

        return chunks

    def _extract_python_context(self, tree, code_text: str) -> str:
        """Extract Python imports."""
        context_lines = []
        for node in tree.root_node.children:
            if node.type in ['import_statement', 'import_from_statement']:
                context_lines.append(code_text[node.start_byte:node.end_byte])
        return '\n'.join(context_lines)
```

#### Step 3: Use Python Chunking

```python
from framework.chunker import FileChunker

# Create Python chunker
chunker = FileChunker(language='python', max_chunk_lines=150)

# Chunk Python file
chunks = chunker.chunk_file(Path('large_script.py'))

print(f"Split into {len(chunks)} chunks")
for chunk in chunks:
    print(f"  {chunk.chunk_id}: lines {chunk.start_line}-{chunk.end_line}")
```

---

## Testing

### Test Structure

```
tests/
├── unit/                    # Unit tests (fast, no LLM)
│   ├── test_chunker.py
│   ├── test_chunk_analyzer.py
│   └── test_result_merger.py
├── integration/             # Integration tests (slow, with LLM)
│   ├── test_integration_chunking.py
│   ├── test_phase0_integration.py
│   └── test_phase1_integration.py
└── fixtures/                # Test fixtures
    └── sample_code.cpp
```

### Writing Tests

#### Unit Test Example

```python
# tests/test_chunker.py

import pytest
from framework.chunker import FileChunker, Chunk

def test_chunk_small_file(tmp_path):
    """Test chunking a small C++ file."""
    # Create test file
    file_path = tmp_path / "test.cpp"
    file_path.write_text('''
#include <iostream>

void foo() {
    std::cout << "Hello" << std::endl;
}

int main() {
    foo();
    return 0;
}
''')

    # Chunk file
    chunker = FileChunker(language='cpp')
    chunks = chunker.chunk_file(file_path)

    # Assertions
    assert len(chunks) == 2  # foo() and main()
    assert all(isinstance(c, Chunk) for c in chunks)
    assert chunks[0].chunk_id.endswith(':foo:3-5')
    assert '#include <iostream>' in chunks[0].context

@pytest.mark.parametrize("max_lines,expected_chunks", [
    (50, 4),   # Small chunks
    (100, 2),  # Medium chunks
    (200, 1),  # Large chunks
])
def test_chunk_respects_max_lines(tmp_path, max_lines, expected_chunks):
    """Test that chunking respects max_lines parameter."""
    # Create large file
    file_path = tmp_path / "large.cpp"
    code = "void func() {\n" + "    int x;\n" * 100 + "}"
    file_path.write_text(code)

    # Chunk with different sizes
    chunker = FileChunker(max_chunk_lines=max_lines)
    chunks = chunker.chunk_file(file_path)

    assert len(chunks) >= expected_chunks
```

#### Integration Test Example

```python
# tests/integration/test_production_analyzer.py

import pytest
from plugins.production_analyzer import ProductionAnalyzer
from plugins.cpp_plugin import CppPlugin

@pytest.mark.slow  # Mark as slow (requires LLM)
def test_analyze_file_with_bugs(tmp_path):
    """Test that analyzer finds known bugs."""
    # Create buggy code
    file_path = tmp_path / "buggy.cpp"
    file_path.write_text('''
void leaky() {
    int* p = new int(42);
    // BUG: Never deleted
}
''')

    # Analyze
    analyzer = ProductionAnalyzer(plugin=CppPlugin())
    result = analyzer.analyze_file(file_path)

    # Assertions
    assert result is not None
    assert len(result.issues) > 0
    assert any('leak' in issue.description.lower() for issue in result.issues)
    assert any(issue.line == 2 for issue in result.issues)
```

### Running Tests

```bash
# All tests
pytest tests/ -v

# Fast tests only (skip LLM calls)
pytest tests/ -m "not slow"

# Specific category
pytest tests/unit/ -v              # Unit tests
pytest tests/integration/ -v       # Integration tests

# With coverage
pytest tests/ --cov=framework --cov-report=html
open htmlcov/index.html  # View coverage report

# Parallel execution
pytest tests/ -n auto  # Use all CPU cores
```

---

## Debugging

### Debug Techniques

#### 1. Enable Prompt Logging

```python
# cli/main.py or your script

from framework.prompt_logger import PromptLogger

# Enable logging
PromptLogger.enable(log_dir='logs/')

# Run analysis
analyzer = ProductionAnalyzer()
result = analyzer.analyze_file(Path('test.cpp'))

# View logs
# logs/2025-11-12_14-30-00_prompt.txt  # Prompt sent to LLM
# logs/2025-11-12_14-30-00_response.txt  # LLM response
```

#### 2. Inspect Chunks

```python
from framework.chunker import FileChunker

chunker = FileChunker()
chunks = chunker.chunk_file(Path('large.cpp'))

for i, chunk in enumerate(chunks):
    print(f"\n=== Chunk {i+1} ===")
    print(f"ID: {chunk.chunk_id}")
    print(f"Lines: {chunk.start_line}-{chunk.end_line}")
    print(f"Context:\n{chunk.context[:100]}...")
    print(f"Code:\n{chunk.code[:100]}...")
```

#### 3. Test Individual Technique

```python
from framework.techniques import FewShotTechnique
from framework.ollama_client import OllamaClient
from framework.models import AnalysisRequest

# Create client
client = OllamaClient(model_name='deepseek-coder:33b-instruct')

# Create technique
technique = FewShotTechnique(client, config={'num_examples': 3})

# Test on sample code
request = AnalysisRequest(
    code='int* p = new int; // Never deleted',
    language='cpp'
)

result = technique.analyze(request)

print(f"Found {len(result.issues)} issues:")
for issue in result.issues:
    print(f"  Line {issue.line}: {issue.description}")
```

#### 4. Verbose CLI Output

```bash
# Set environment variable for verbose logging
export VERBOSE=1

# Run analysis
python -m cli.main analyze file test.cpp

# Output will show:
# - Chunk creation details
# - LLM prompts and responses
# - Deduplication process
# - Timing information
```

---

## Tips & Best Practices

### 1. Performance

```python
# Use chunking for files > 300 lines
result = analyzer.analyze_file(Path('large.cpp'), chunk_mode=True)

# Adjust chunk size for your use case
# Larger chunks = fewer LLM calls, but may hit token limit
# Smaller chunks = more LLM calls, but better quality
result = analyzer.analyze_file(
    Path('large.cpp'),
    chunk_mode=True,
    max_chunk_lines=150  # Default: 200
)

# Use parallel workers
result = analyzer.analyze_file(
    Path('large.cpp'),
    chunk_mode=True,
    max_workers=8  # Default: 4
)
```

### 2. Accuracy

```python
# Use Hybrid technique for best F1 score
from framework.techniques import HybridTechnique

analyzer = ProductionAnalyzer(
    technique_class=HybridTechnique  # F1=0.634
)

# Or use Few-shot-5 for fast & good results
from framework.techniques import FewShotTechnique

analyzer = ProductionAnalyzer(
    technique_class=FewShotTechnique  # F1=0.615, faster
)
```

### 3. Custom Filtering

```python
# Filter results by severity
result = analyzer.analyze_file(Path('test.cpp'))
critical_issues = [i for i in result.issues if i.severity == 'critical']

# Filter by category
memory_issues = [i for i in result.issues if i.category == 'memory-safety']

# Filter by confidence
high_confidence = [i for i in result.issues if i.confidence > 0.8]
```

---

## Next Steps

- **Read Architecture**: See [ARCHITECTURE.md](./ARCHITECTURE.md) for system design
- **Try Examples**: Run commands from QUICKSTART.md
- **Experiment**: Create new techniques or plugins
- **Contribute**: Submit PRs with new features or bug fixes

---

**Questions?** Open an issue on GitHub or check existing documentation in `docs/`.
