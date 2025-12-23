# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LLM Framework is a domain-agnostic code analysis platform using local LLMs via Ollama. It provides a plugin-based architecture for LLM-powered code review with multiple prompting techniques (zero-shot, few-shot, chain-of-thought, hybrid).

**Key constraint**: All LLM inference runs locally via Ollama - no external API calls.

## Common Commands

### Installation
```bash
python -m venv venv
source venv/bin/activate
pip install -e .
ollama pull deepseek-coder:33b-instruct
```

### Running Analysis (Production)
```bash
# Single file
python -m cli.main analyze file src/main.cpp

# Directory (recursive)
python -m cli.main analyze dir src/ --output report.md

# PR changes
python -m cli.main analyze pr --base main --head feature-branch

# Large files (700+ lines) with chunking
python -m cli.main analyze file large.cpp --chunk --chunk-size 200

# Alternative: use installed CLI entry point
llm-framework analyze file src/main.cpp
```

### Running Experiments
```bash
# Run single experiment
python -m cli.main experiment run --config experiments/configs/few_shot_5.yml

# View leaderboard
python -m cli.main experiment leaderboard
```

### Running Tests
```bash
# All tests
pytest tests/

# Single test file
pytest tests/test_chunker.py

# Specific test
pytest tests/test_chunker.py::test_function_name -v
```

### Linting & Formatting
```bash
# Format code with black
black framework/ plugins/ cli/ tests/

# Lint with ruff
ruff check framework/ plugins/ cli/ tests/

# Type check with mypy
mypy framework/ plugins/ cli/
```

## Architecture

```
framework/              # Core LLM framework (domain-agnostic)
├── techniques/         # Prompting strategies: zero_shot, few_shot, chain_of_thought, hybrid
│   ├── base.py        # BaseTechnique, SinglePassTechnique, MultiPassTechnique
│   └── __init__.py    # TechniqueFactory for technique instantiation
├── models.py           # Pydantic data models (AnalysisRequest, AnalysisResult, Issue)
├── ollama_client.py    # Ollama API interface
├── chunker.py          # AST-based file chunking (tree-sitter)
├── chunk_analyzer.py   # Parallel chunk analysis
├── result_merger.py    # Deduplicate and merge chunk results
├── experiment_runner.py # Run experiments on ground truth datasets
├── evaluation.py       # Metrics calculation helpers
└── metrics_calculator.py # Precision, recall, F1, token efficiency

plugins/                # Domain-specific knowledge
├── domain_plugin.py    # Abstract base (DomainPlugin protocol)
├── cpp_plugin.py       # C++ plugin: 5 categories, 5 few-shot examples
└── production_analyzer.py # Orchestrator for file/dir/PR analysis

cli/main.py             # Click-based CLI entry point
```

### Key Abstractions

- **BaseTechnique** (`framework/techniques/base.py`): All techniques inherit from this. Implement `analyze(request: AnalysisRequest) -> AnalysisResult`.
- **DomainPlugin** (`plugins/domain_plugin.py`): Plugins provide `get_file_extensions()`, `get_few_shot_examples()`, `get_categories()`, `should_analyze_file()`.
- **ProductionAnalyzer** (`plugins/production_analyzer.py`): Main orchestrator that combines plugin + technique for analysis.

### Data Flow

1. CLI receives command (file/dir/pr)
2. ProductionAnalyzer checks file via plugin's `should_analyze_file()`
3. For large files: FileChunker splits via tree-sitter AST, ChunkAnalyzer runs parallel analysis
4. Technique builds prompt with plugin's few-shot examples
5. OllamaClient calls local LLM
6. ResultMerger deduplicates issues by (line, category)

## Prompting Techniques

| Technique | F1 Score | Use Case |
|-----------|----------|----------|
| few_shot_5 | 0.615 | Default for production |
| hybrid | 0.634 | Critical PRs (4x slower) |
| chain_of_thought | 0.571 | Modern-cpp detection |
| zero_shot | 0.526 | Baseline only |

Available technique names in `TechniqueFactory`: `zero_shot`, `few_shot_3`, `few_shot_5`, `few_shot`, `chain_of_thought`, `multi_pass`, `hybrid`, `hybrid_high_precision`, `hybrid_category_specialized`

## Adding a New Domain Plugin

1. Create `plugins/new_plugin.py` inheriting from `DomainPlugin`
2. Implement: `get_file_extensions()`, `get_categories()`, `get_few_shot_examples()`, `should_analyze_file()`
3. Add ground truth dataset in `experiments/ground_truth/new_domain/`
4. Create experiment config in `experiments/configs/`

## Adding a New Technique

1. Create `framework/techniques/new_technique.py` inheriting from `SinglePassTechnique` or `MultiPassTechnique`
2. Implement `name` property and `analyze()` method (or override `_build_user_prompt()` for single-pass)
3. Register in `framework/techniques/__init__.py` TechniqueFactory

## Ground Truth & Evaluation

- Ground truth examples: `experiments/ground_truth/cpp/` (20 annotated examples)
- Metrics tracked: Precision, Recall, F1, Token efficiency, Latency
- Results saved to: `experiments/runs/`

## C++ Plugin Categories

- `memory-safety`: Memory leaks, use-after-free, buffer overflows
- `modern-cpp`: Smart pointers, auto, range-for opportunities
- `performance`: Unnecessary copies, inefficient operations
- `security`: Hardcoded credentials, input validation
- `concurrency`: Data races, deadlocks
