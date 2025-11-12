# LLM Framework - Domain-Agnostic Code Analysis Platform

**A research platform for evaluating and deploying LLM-powered code analysis across multiple domains.**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Overview

This framework provides a **modular, plugin-based architecture** for LLM-powered code analysis. It combines:

- **Research infrastructure** - Ground truth datasets, metrics, experiment tracking
- **Technique library** - Modular implementations (zero-shot, few-shot, chain-of-thought, hybrid)
- **Domain plugins** - Separates framework from domain knowledge (C++, RTL, Python, etc.)
- **Production tools** - CLI, git integration, PR review workflows

**Key Features**:

✅ **Experiment-first design** - Measure what works before deploying
✅ **Plugin architecture** - Add new domains without changing framework
✅ **Production-ready** - CLI commands for file/directory/PR analysis
✅ **Research-validated** - All techniques tested with F1 scores, precision, recall
✅ **Cost-optimized** - Token efficiency tracking, technique comparison

---

## Quick Start

### Prerequisites

- Python 3.12+
- [Ollama](https://ollama.ai/) installed and running
- A code model downloaded (default: `deepseek-coder:33b-instruct`)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/llm-framework.git
cd llm-framework

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Download LLM model (if not already installed)
ollama pull deepseek-coder:33b-instruct
```

### Basic Usage

```bash
# Analyze a single C++ file
python -m cli.main analyze file src/main.cpp

# Analyze entire directory
python -m cli.main analyze dir src/ --output report.md

# Analyze changes in a pull request
python -m cli.main analyze pr --base main --head feature-branch --output pr-review.md
```

**Example output**:

```
Analyzing file: src/memory_leak.cpp
Model: deepseek-coder:33b-instruct

Found 2 issue(s):

● Line 5 [memory-safety] Memory leak - dynamically allocated pointer never deleted
  Pointer allocated with 'new' on line 5 but no corresponding 'delete'. Memory leak on every execution.

● Line 12 [performance] Unnecessary copy in loop
  Vector passed by value in loop. Use const reference to avoid copies.
```

---

## Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    LLM Framework (Core)                      │
│  - Techniques: ZeroShot, FewShot, ChainOfThought, Hybrid   │
│  - ExperimentRunner, MetricsCalculator, OllamaClient       │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ Protocol: BaseTechnique
                            │
┌─────────────────────────────────────────────────────────────┐
│                   Domain Plugins (Pluggable)                 │
│  - CppPlugin: C++ code analysis (memory, modern-cpp, perf)  │
│  - (Future) RtlPlugin, PythonPlugin, etc.                   │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ Protocol: DomainPlugin
                            │
┌─────────────────────────────────────────────────────────────┐
│                 Production Applications                       │
│  - ProductionAnalyzer: File/dir/PR analysis                 │
│  - CLI: analyze file/dir/pr commands                        │
│  - (Future) GitHub Actions, pre-commit hooks                │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

**Framework Core** (`framework/`):
- `techniques/` - LLM prompting strategies (zero-shot, few-shot, CoT, hybrid)
- `models.py` - Pydantic models for type safety
- `experiment_runner.py` - Run experiments on ground truth datasets
- `metrics_calculator.py` - Precision, recall, F1, token efficiency
- `ollama_client.py` - Interface to Ollama API

**Domain Plugins** (`plugins/`):
- `domain_plugin.py` - Abstract base class for plugins
- `cpp_plugin.py` - C++ analyzer (5 categories, 5 curated examples)
- `production_analyzer.py` - Production-ready analyzer

**CLI** (`cli/`):
- `main.py` - Command-line interface for experiments and production analysis

**Experiments** (`experiments/`):
- `ground_truth/cpp/` - 20 annotated C++ examples
- `configs/` - Experiment configuration files
- `runs/` - Experiment results (metrics, prompts, logs)

---

## Usage Guide

### 1. Production Analysis

#### Analyze a Single File

```bash
python -m cli.main analyze file src/main.cpp
```

**Options**:
- `--model, -m` - Ollama model to use (default: `deepseek-coder:33b-instruct`)
- `--output, -o` - Save report to markdown file

**Example**:
```bash
python -m cli.main analyze file src/main.cpp --output report.md
```

---

#### Analyze a Directory

```bash
python -m cli.main analyze dir src/
```

**Options**:
- `--model, -m` - Ollama model to use
- `--output, -o` - Save report to markdown file
- `--recursive/--no-recursive` - Recurse into subdirectories (default: recursive)

**Example**:
```bash
# Analyze all C++ files in src/ recursively
python -m cli.main analyze dir src/ --output directory_report.md

# Non-recursive (only top-level files)
python -m cli.main analyze dir src/ --no-recursive
```

**Output**:
```
       Analysis Summary
┏━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric          ┃ Value ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Files Analyzed  │ 12    │
│ Total Issues    │ 8     │
│ Critical Issues │ 2     │
│ High Issues     │ 3     │
│ Medium Issues   │ 2     │
│ Low Issues      │ 1     │
└─────────────────┴───────┘

Issues by Category:
  memory-safety: 3
  performance: 2
  modern-cpp: 2
  concurrency: 1
```

---

#### Analyze Pull Request

```bash
python -m cli.main analyze pr --base main --head feature-branch
```

**Options**:
- `--repo, -r` - Path to git repository (default: `.`)
- `--base, -b` - Base branch to compare against (default: `main`)
- `--head, -h` - Head branch/commit (default: `HEAD`)
- `--model, -m` - Ollama model to use
- `--output, -o` - Save report to markdown file

**Example**:
```bash
# Analyze current branch vs main
python -m cli.main analyze pr --output pr-review.md

# Analyze specific branch comparison
python -m cli.main analyze pr --base develop --head feature/new-api --output review.md
```

**Workflow**:
1. Runs `git diff --name-only` to find changed files
2. Analyzes only changed C++ files (`.cpp`, `.h`, etc.)
3. Generates markdown report suitable for PR comments

---

### 2. Research & Experiments

#### Run a Single Experiment

```bash
python -m cli.main experiment run --config experiments/configs/few_shot_5.yml
```

**What it does**:
1. Loads experiment configuration (technique, model, dataset)
2. Runs analysis on all examples in ground truth dataset
3. Compares detected issues vs expected issues
4. Calculates metrics (precision, recall, F1, token efficiency)
5. Saves results to `experiments/runs/`

**Output**:
```
Starting experiment: few_shot_5_examples
Technique: few_shot_5
Model: deepseek-coder:33b-instruct
Dataset: experiments/ground_truth/cpp (20 examples)
------------------------------------------------------------
[1/20] Analyzing example_001...
  Expected: 1 issues
  Detected: 1 issues
  Latency: 8.24s
[2/20] Analyzing example_002...
  ...

============================================================
EXPERIMENT RESULTS
============================================================
Precision: 0.667
Recall:    0.571
F1 Score:  0.615
Token Efficiency: 0.97 issues/1K tokens
Avg Latency: 8.15s
Total Tokens: 12396
Total Time: 163.05s

Per-Category Metrics:
  memory-safety:
    Precision: 0.750
    Recall:    0.857
    F1:        0.800
  modern-cpp:
    Precision: 0.000
    Recall:    0.000
    F1:        0.000
  ...
```

---

#### Create Custom Experiment

Create a new config file in `experiments/configs/`:

```yaml
# my_experiment.yml
experiment_id: my_custom_experiment
technique_name: few_shot_5  # or: zero_shot, chain_of_thought, hybrid
model_name: deepseek-coder:33b-instruct
dataset_path: experiments/ground_truth/cpp

technique_params:
  system_prompt: |
    You are an expert C++ code reviewer...

  few_shot_examples:
    - id: example_001
      code: "int* ptr = new int(10);\nreturn 0;"
      issues:
        - category: memory-safety
          severity: critical
          line: 1
          description: "Memory leak"
          reasoning: "Allocated with 'new' but no 'delete'"

  temperature: 0.1
  max_tokens: 2000

seed: 42
```

Run it:
```bash
python -m cli.main experiment run --config experiments/configs/my_experiment.yml
```

---

#### Compare Techniques

```bash
python -m cli.main experiment leaderboard
```

**Output** (example):
```
              Technique Leaderboard
┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┓
┃ Technique             ┃ F1     ┃ Latency   ┃
┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━┩
│ hybrid                │ 0.634  │ 32.76s    │
│ few_shot_5            │ 0.615  │ 8.15s     │
│ few_shot_3            │ 0.588  │ 7.12s     │
│ chain_of_thought      │ 0.571  │ 23.94s    │
│ zero_shot             │ 0.526  │ 7.15s     │
└───────────────────────┴────────┴───────────┘
```

---

## Techniques

The framework includes 5 prompting techniques, validated with experiments:

| Technique | F1 Score | Latency | Best For | Trade-offs |
|-----------|----------|---------|----------|------------|
| **Hybrid** | **0.634** | 32.76s | Critical PRs, modern C++ | 4x slower, 2x cost, but best accuracy |
| **Few-shot-5** | **0.615** | 8.15s | **General use** (recommended) | Best speed/accuracy balance |
| Few-shot-3 | 0.588 | 7.12s | Cost-sensitive analysis | Lower accuracy, 20% token savings |
| Chain-of-thought | 0.571 | 23.94s | Modern-cpp specific | Slow, but 0.727 F1 on modern-cpp |
| Zero-shot | 0.526 | 7.15s | Baseline / benchmarking | Fast but lowest accuracy |

### Technique Details

#### 1. Zero-Shot
**Strategy**: Direct prompt with no examples
**Pros**: Fast, low token cost
**Cons**: Lowest accuracy (F1=0.526)

#### 2. Few-Shot (3 or 5 examples)
**Strategy**: Provide examples before target code
**Pros**: Best balance of speed and accuracy
**Cons**: Modern-cpp category fails (0.000 F1)
**Recommended**: Use **few-shot-5** as default

#### 3. Chain-of-Thought
**Strategy**: Ask LLM to show reasoning in `<thinking>` tags
**Pros**: Excellent on modern-cpp (0.727 F1 vs 0.000)
**Cons**: 3x slower than few-shot

#### 4. Hybrid (Few-shot + CoT)
**Strategy**: Run few-shot for broad coverage, CoT for specific categories
**Pros**: Best overall F1 (0.634), unlocks modern-cpp
**Cons**: 4x slower, 2x cost
**When to use**: Critical PRs, modern C++ codebases

#### 5. Multi-pass Self-Critique
**Strategy**: Two LLM calls - detect then critique
**Status**: Implemented but not yet evaluated

---

## Configuration

### Selecting a Technique

For production analysis, the technique is automatically selected (few-shot-5 by default).

To use a different technique, modify `plugins/production_analyzer.py`:

```python
# Default: few-shot-5
analyzer = ProductionAnalyzer(model_name="deepseek-coder:33b-instruct")

# Use hybrid for critical PRs
config = {
    'technique_name': 'hybrid',
    'technique_params': {
        'few_shot_config': {...},
        'cot_config': {...}
    }
}
analyzer = ProductionAnalyzer(
    model_name="deepseek-coder:33b-instruct",
    technique_config=config
)
```

### Supported Models

Tested with:
- `deepseek-coder:33b-instruct` (recommended, 18GB)
- `qwen2.5-coder:14b` (faster, 8GB)
- `codellama:34b` (alternative)

To use a different model:
```bash
python -m cli.main analyze file src/main.cpp --model qwen2.5-coder:14b
```

---

## Domain Plugins

### C++ Plugin (Built-in)

**Categories**:
- `memory-safety` - Memory leaks, use-after-free, buffer overflows
- `modern-cpp` - Opportunities for smart pointers, auto, range-for
- `performance` - Unnecessary copies, inefficient operations
- `security` - Hardcoded credentials, SQL injection, input validation
- `concurrency` - Data races, deadlocks, missing synchronization

**Few-shot Examples**: 5 curated examples covering all categories

**File Filtering**:
- Analyzes: `.cpp`, `.cc`, `.cxx`, `.h`, `.hpp`, `.hxx`
- Skips: Test files, third-party directories (`third_party/`, `vendor/`, etc.)

---

### Creating a Custom Plugin

To add support for a new domain (Python, RTL, etc.):

1. **Create plugin class** in `plugins/`:

```python
# plugins/python_plugin.py
from plugins.domain_plugin import DomainPlugin

class PythonPlugin(DomainPlugin):
    @property
    def name(self) -> str:
        return "python"

    @property
    def supported_extensions(self) -> List[str]:
        return ['.py']

    @property
    def categories(self) -> List[str]:
        return ['type-safety', 'security', 'performance', 'style']

    def get_few_shot_examples(self, num_examples: int = 5) -> List[Dict]:
        return [
            {
                'id': 'example_001',
                'code': 'def process(x):\n    return x + 1',
                'issues': [
                    {
                        'category': 'type-safety',
                        'severity': 'medium',
                        'line': 1,
                        'description': 'Missing type hints',
                        'reasoning': 'Function lacks type annotations...'
                    }
                ]
            },
            # ... more examples
        ]

    def get_system_prompt(self) -> str:
        return """You are an expert Python code reviewer.
        Analyze code for: type-safety, security, performance, style.
        Respond with JSON array of issues..."""
```

2. **Create ground truth dataset**:
   - Add 20+ annotated examples to `experiments/ground_truth/python/`
   - Each example: code + expected issues

3. **Run experiments**:
```bash
python -m cli.main experiment run --config experiments/configs/python_few_shot_5.yml
```

4. **Use in production**:
```python
analyzer = ProductionAnalyzer(plugin=PythonPlugin())
```

---

## Project Structure

```
llm-framework/
├── framework/              # Core framework
│   ├── techniques/        # Prompting techniques
│   │   ├── zero_shot.py
│   │   ├── few_shot.py
│   │   ├── chain_of_thought.py
│   │   ├── multi_pass.py
│   │   └── hybrid.py
│   ├── models.py          # Pydantic models
│   ├── experiment_runner.py
│   ├── metrics_calculator.py
│   └── ollama_client.py
│
├── plugins/               # Domain-specific plugins
│   ├── domain_plugin.py   # Abstract base class
│   ├── cpp_plugin.py      # C++ analyzer
│   └── production_analyzer.py
│
├── cli/                   # Command-line interface
│   └── main.py
│
├── experiments/           # Research data
│   ├── ground_truth/     # Annotated examples
│   │   └── cpp/          # 20 C++ examples
│   ├── configs/          # Experiment configs
│   └── runs/             # Experiment results
│
├── tests/                 # Integration tests
│   ├── test_phase1_integration.py
│   ├── test_phase2_integration.py
│   └── test_phase3_integration.py
│
├── docs/                  # Documentation
│   ├── PHASE0_COMPLETE.md  # Evaluation infra
│   ├── PHASE1_COMPLETE.md  # Framework core
│   ├── PHASE2_FINDINGS.md  # Research results
│   ├── PHASE3_PRODUCTION.md # Production tools
│   └── PHASE4_COMPLETE.md   # Hybrid techniques
│
├── pyproject.toml         # Project metadata
├── requirements.txt       # Dependencies
└── README.md             # This file
```

---

## Research Results

### Phase 2: Technique Comparison

Comprehensive evaluation of 4 techniques on 20 C++ examples:

| Technique | F1 | Precision | Recall | Latency | Tokens |
|-----------|----|-----------|----- --|---------|--------|
| Few-shot-5 | 0.615 | 0.667 | 0.571 | 8.15s | 12,396 |
| Few-shot-3 | 0.588 | 0.625 | 0.556 | 7.12s | 9,847 |
| Chain-of-thought | 0.571 | 0.571 | 0.571 | 23.94s | 13,023 |
| Zero-shot | 0.526 | 0.625 | 0.455 | 7.15s | 8,945 |

**Key Finding**: Few-shot-5 wins overall, but chain-of-thought excels at modern-cpp (0.727 F1 vs 0.000)

See [PHASE2_FINDINGS.md](PHASE2_FINDINGS.md) for detailed analysis.

### Phase 4: Hybrid Techniques

Explored combining techniques for improved accuracy:

| Technique | F1 | Improvement | Latency | Cost |
|-----------|----|-----------  |---------|------|
| Hybrid | 0.634 | +3.1% | 32.76s | 2x tokens |
| Few-shot-5 (baseline) | 0.615 | - | 8.15s | 1x tokens |

**Key Finding**: Hybrid improves F1 by 3.1% and unlocks modern-cpp category, but at 4x latency cost.

See [PHASE4_COMPLETE.md](PHASE4_COMPLETE.md) for detailed analysis.

---

## Performance & Cost

### Token Usage

Based on 20-example experiments:

| Technique | Total Tokens | Cost per Issue | Per-File Cost |
|-----------|--------------|----------------|---------------|
| Zero-shot | 8,945 | 1,121 tokens | ~450 tokens |
| Few-shot-3 | 9,847 | 1,027 tokens | ~500 tokens |
| Few-shot-5 | 12,396 | 1,033 tokens | ~620 tokens |
| Chain-of-thought | 13,023 | 1,217 tokens | ~650 tokens |
| Hybrid | 25,181 | 1,667 tokens | ~1,260 tokens |

**Cost estimate** (with Ollama - free local inference):
- 100 files: ~620K tokens (few-shot-5)
- 1000 files: ~6.2M tokens
- At OpenAI gpt-4 pricing: ~$18.60 per 1000 files

**Latency**:
- Few-shot-5: ~8s per file
- Hybrid: ~33s per file
- 100 files: ~13.5 min (few-shot-5) or ~55 min (hybrid)

---

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/code-review.yml`:

```yaml
name: AI Code Review

on:
  pull_request:
    branches: [main]

jobs:
  analyze:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Fetch all history for git diff

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install Dependencies
        run: |
          pip install -e .

      - name: Setup Ollama
        run: |
          curl https://ollama.ai/install.sh | sh
          ollama pull deepseek-coder:33b-instruct

      - name: Run Code Analysis
        run: |
          python -m cli.main analyze pr \\
            --base ${{ github.base_ref }} \\
            --head ${{ github.head_ref }} \\
            --output review.md

      - name: Post PR Comment
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const review = fs.readFileSync('review.md', 'utf8');

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: review
            });
```

### Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Run analyzer on staged C++ files

STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\\.(cpp|h)$')

if [ -n "$STAGED_FILES" ]; then
    echo "Running C++ code analyzer..."

    for file in $STAGED_FILES; do
        python -m cli.main analyze file "$file"
        if [ $? -ne 0 ]; then
            echo "❌ Code quality issues found in $file"
            exit 1
        fi
    done

    echo "✅ Code quality checks passed"
fi
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

---

## Troubleshooting

### Ollama Connection Issues

**Error**: `ConnectionError: Cannot connect to Ollama`

**Solution**:
```bash
# Check if Ollama is running
ollama list

# If not, start Ollama
ollama serve
```

### Model Not Found

**Error**: `Model 'deepseek-coder:33b-instruct' not available`

**Solution**:
```bash
# Download the model
ollama pull deepseek-coder:33b-instruct

# Check available models
ollama list
```

### Out of Memory

**Error**: Ollama crashes or runs out of memory

**Solutions**:
1. Use smaller model: `qwen2.5-coder:14b` (8GB instead of 18GB)
2. Close other applications
3. Reduce `max_tokens` in config (e.g., 1000 instead of 2000)

### Slow Performance

**Issue**: Analysis takes too long

**Solutions**:
1. Use few-shot-3 instead of few-shot-5 (20% faster)
2. Use GPU acceleration for Ollama
3. Skip analysis of test files (already done by default)
4. Use `--no-recursive` for directory analysis

### False Positives

**Issue**: Too many incorrect issue reports

**Solutions**:
1. Use hybrid technique with higher confidence threshold
2. Add false positives to negative examples in plugin
3. Refine system prompt to be more conservative
4. Use higher precision technique (chain-of-thought)

---

## Development

### Running Tests

```bash
# Run all integration tests
pytest tests/

# Run specific phase tests
pytest tests/test_phase1_integration.py
pytest tests/test_phase2_integration.py
pytest tests/test_phase3_integration.py
```

### Adding a New Technique

1. Create technique class in `framework/techniques/`:

```python
# framework/techniques/my_technique.py
from framework.techniques.base import SinglePassTechnique

class MyTechnique(SinglePassTechnique):
    @property
    def name(self) -> str:
        return "my_technique"

    def _build_user_prompt(self, code: str) -> str:
        return f"Analyze this code:\n\n{code}"
```

2. Register in `framework/techniques/__init__.py`:

```python
from framework.techniques.my_technique import MyTechnique

class TechniqueFactory:
    _TECHNIQUE_MAP = {
        # ... existing techniques
        'my_technique': MyTechnique,
    }
```

3. Create experiment config:

```yaml
# experiments/configs/my_technique.yml
experiment_id: my_technique_test
technique_name: my_technique
model_name: deepseek-coder:33b-instruct
dataset_path: experiments/ground_truth/cpp
```

4. Run experiment:

```bash
python -m cli.main experiment run --config experiments/configs/my_technique.yml
```

---

## Contributing

Contributions are welcome! Areas for contribution:

1. **New domain plugins** (Python, RTL, JavaScript, etc.)
2. **New techniques** (RAG, fine-tuning, ensemble methods)
3. **Optimizations** (parallel execution, caching, adaptive routing)
4. **Ground truth datasets** (more examples for existing or new domains)
5. **Integration tests** (expand test coverage)
6. **Documentation** (tutorials, examples, case studies)

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Citation

If you use this framework in your research, please cite:

```bibtex
@software{llm_framework_2025,
  title = {LLM Framework: Domain-Agnostic Code Analysis Platform},
  author = {Your Name},
  year = {2025},
  url = {https://github.com/yourusername/llm-framework}
}
```

---

## Acknowledgments

- **Ollama** for providing easy-to-use local LLM inference
- **DeepSeek-Coder** for excellent code understanding capabilities
- Research community for LLM prompting techniques (few-shot, CoT, etc.)

---

## Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/llm-framework/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/llm-framework/discussions)
- **Email**: your.email@example.com

---

**Built with ❤️ for better code quality through AI**
