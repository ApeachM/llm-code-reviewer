# Semantic PR Review Bot

**An LLM-powered code review system that catches semantic errors and logic issues that static analysis tools miss.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Overview

This bot **complements** your existing static/dynamic analysis pipeline (AddressSanitizer, ThreadSanitizer, clang-tidy, Valgrind) by focusing on issues that automated tools cannot detect:

- **Logic errors**: Off-by-one errors, wrong comparison operators, incorrect boolean logic
- **API misuse**: Incorrect usage patterns, missing cleanup calls, wrong parameter order
- **Semantic inconsistency**: Code behavior doesn't match naming or documentation
- **Edge case handling**: Missing boundary checks, unhandled corner cases
- **Intent mismatch**: Implementation doesn't align with PR description or requirements

### Key Features

✅ **Semantic-focused analysis** - Detects issues that require understanding code intent
✅ **CI/CD integration** - Works with GitLab CI, Jenkins, GitHub Actions
✅ **Context-aware** - Analyzes PR description to understand intended changes
✅ **Inline comments** - Posts review comments directly on problematic code lines
✅ **Technique flexibility** - Multiple LLM prompting strategies (few-shot, chain-of-thought, hybrid)
✅ **Large file support** - AST-based chunking with parallel processing

---

## Quick Start

### Prerequisites

- Python 3.11+
- [Ollama](https://ollama.ai/) installed and running (for local LLM inference)
- A code model downloaded (default: `deepseek-coder:33b-instruct`)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd semantic-pr-reviewer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Download LLM model (18GB, requires ~20GB disk space)
ollama pull deepseek-coder:33b-instruct

# Alternative: Use smaller model (8GB)
ollama pull qwen2.5-coder:14b
```

### Basic Usage

```bash
# Analyze a single C++ file
python -m cli.main analyze file src/main.cpp

# Analyze entire directory
python -m cli.main analyze dir src/ --output report.md

# Analyze PR changes (local testing)
python -m cli.main analyze pr --base main --head feature-branch --output pr-review.md

# Use alternative CLI entry point
llm-framework analyze file src/main.cpp
```

**Example output**:

```
Analyzing PR: feature/add-calculation
Model: deepseek-coder:33b-instruct

Found 2 issue(s):

● Line 23 [logic-errors] Off-by-one error in loop condition
  Loop uses <= instead of <, allowing access to array[size] which is out of bounds.
  Suggested fix: Change 'i <= size' to 'i < size'

● Line 45 [api-misuse] File handle not closed in error path
  fopen() on line 42 but early return on line 45 skips fclose() on line 48.
  Suggested fix: Close file before all return statements or use RAII wrapper
```

---

## What This Bot Catches (vs. Static Analysis)

| Issue Type | Example | Detected By |
|------------|---------|-------------|
| Memory leaks | `new` without `delete` | ❌ Bot<br>✅ AddressSanitizer, Valgrind |
| Data races | Unsynchronized access | ❌ Bot<br>✅ ThreadSanitizer |
| Performance | Unnecessary copies | ❌ Bot<br>✅ clang-tidy |
| **Logic errors** | `i <= size` instead of `i < size` | ✅ **Bot**<br>❌ Static analysis |
| **API misuse** | Missing `fclose()` in error path | ✅ **Bot**<br>🟡 Some static analyzers |
| **Semantic issues** | Function named `get()` modifies state | ✅ **Bot**<br>❌ Static analysis |
| **Edge cases** | No empty vector check before access | ✅ **Bot**<br>🟡 Some static analyzers |
| **Intent mismatch** | Code doesn't match PR description | ✅ **Bot**<br>❌ No tool |

---

## CI/CD Integration

### GitLab CI

Create `.gitlab-ci.yml`:

```yaml
stages:
  - review

semantic-review:
  stage: review
  image: python:3.11
  before_script:
    - pip install -e .
    - curl https://ollama.ai/install.sh | sh
    - ollama serve &
    - sleep 5
    - ollama pull deepseek-coder:33b-instruct
  script:
    - python -m cli.main analyze pr --base $CI_MERGE_REQUEST_TARGET_BRANCH_NAME --head $CI_MERGE_REQUEST_SOURCE_BRANCH_NAME --output review.md
    # TODO: Post review.md to MR comments via GitLab API
  only:
    - merge_requests
```

### Jenkins

```groovy
pipeline {
    agent any

    stages {
        stage('Semantic Review') {
            when {
                changeRequest()
            }
            steps {
                sh 'pip install -e .'
                sh 'ollama pull deepseek-coder:33b-instruct'
                sh 'python -m cli.main analyze pr --base ${CHANGE_TARGET} --head ${CHANGE_BRANCH} --output review.md'
                // TODO: Post to PR via API
            }
        }
    }
}
```

### GitHub Actions

Create `.github/workflows/pr-review.yml`:

```yaml
name: Semantic Code Review

on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  pull-requests: write

jobs:
  semantic-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -e .

      - name: Setup Ollama
        run: |
          curl https://ollama.ai/install.sh | sh
          ollama serve &
          sleep 5
          ollama pull deepseek-coder:33b-instruct

      - name: Run semantic analysis
        run: |
          python -m cli.main analyze pr \
            --base ${{ github.event.pull_request.base.ref }} \
            --head ${{ github.event.pull_request.head.ref }} \
            --output review.md

      # TODO: Post review.md to PR comments
```

---

## Issue Categories

The bot focuses on **5 semantic categories**:

### 1. logic-errors
Off-by-one errors, wrong comparison operators, incorrect boolean logic
```cpp
// Bad: Off-by-one error
for (int i = 0; i <= vec.size(); i++) {  // Accesses vec[size]!
    process(vec[i]);
}
```

### 2. api-misuse
Incorrect API usage patterns, missing required calls, resource leaks
```cpp
// Bad: File not closed in error path
FILE* f = fopen("data.txt", "r");
if (!validate(f)) {
    return -1;  // Leaked file handle!
}
fclose(f);
```

### 3. semantic-inconsistency
Code behavior doesn't match naming, documentation, or expectations
```cpp
// Bad: "get" function modifies state
int getTotalPrice() {
    discountApplied = true;  // Side effect!
    return price * (1 - discount);
}
```

### 4. edge-case-handling
Missing boundary checks, unhandled corner cases
```cpp
// Bad: No empty check
std::vector<int> nums = getUserInput();
int first = nums[0];  // Crashes if empty!
```

### 5. code-intent-mismatch
Implementation doesn't match PR description or stated requirements
```cpp
// PR says: "Fix calculation to handle negative numbers"
// But code only renames variable without logic change
int calculateTotal(int value) {
    int result = value;  // Still doesn't handle negatives!
    return result;
}
```

---

## Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────┐
│         CI/CD System (GitLab/Jenkins)        │
│  - Triggered on PR creation/update           │
│  - Fetches PR metadata and changed files     │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│        CLI: analyze pr command               │
│  - Parses git diff for changed lines         │
│  - Reads PR description for context          │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│          ProductionAnalyzer                  │
│  - C++ plugin (semantic categories)          │
│  - Few-shot-5 technique (default)            │
│  - AST-based chunking for large files        │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│      Ollama LLM (deepseek-coder:33b)         │
│  - Local inference (no external API)         │
│  - Detects semantic issues                   │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│        ResultFormatter & API Client          │
│  - Formats as inline PR comments             │
│  - Posts to GitLab/GitHub via API            │
└─────────────────────────────────────────────┘
```

### Directory Structure

```
semantic-pr-reviewer/
├── framework/              # Core LLM analysis framework
│   ├── techniques/        # Prompting strategies (few-shot, CoT, hybrid)
│   ├── models.py          # Pydantic data models
│   ├── ollama_client.py   # Ollama API interface
│   ├── chunker.py         # AST-based file chunking
│   └── ...
├── plugins/               # Domain-specific plugins
│   ├── cpp_plugin.py     # C++ semantic analyzer
│   └── domain_plugin.py  # Plugin interface
├── cli/                   # Command-line interface
│   └── main.py           # Entry point
├── experiments/           # Research artifacts (kept for reference)
│   ├── ground_truth/     # Annotated examples
│   └── configs/          # Experiment configurations
├── integrations/          # CI/CD integrations (Phase 3)
│   ├── gitlab_client.py  # GitLab API
│   └── github_client.py  # GitHub API
└── tests/                 # Test suite
```

---

## Configuration

### Selecting a Technique

For production, **few-shot-5** is recommended (best balance of accuracy and speed).

To use a different technique, modify the analysis call:

```python
# Default: few-shot-5 (F1: 0.615, ~8s per file)
analyzer = ProductionAnalyzer(model_name="deepseek-coder:33b-instruct")

# For critical PRs: hybrid (F1: 0.634, ~33s per file)
analyzer = ProductionAnalyzer(
    model_name="deepseek-coder:33b-instruct",
    technique_config={'technique_name': 'hybrid'}
)
```

| Technique | F1 Score | Latency | Use Case |
|-----------|----------|---------|----------|
| few-shot-5 | 0.615 | 8.15s | Default (best balance) |
| hybrid | 0.634 | 32.76s | Critical PRs (highest accuracy) |
| chain-of-thought | 0.571 | 23.94s | Complex logic analysis |
| few-shot-3 | 0.588 | 7.12s | Fast review for large PRs |

### Supported Models

Tested with Ollama models:
- `deepseek-coder:33b-instruct` (recommended, 18GB)
- `qwen2.5-coder:14b` (faster, 8GB)
- `codellama:34b` (alternative)

```bash
# Use smaller model
python -m cli.main analyze file src/main.cpp --model qwen2.5-coder:14b
```

---

## Development

### Running Tests

```bash
# All tests
pytest tests/

# Run phased integration tests
pytest tests/test_phase1_integration.py
pytest tests/test_phase3_integration.py

# Run in parallel (faster)
pytest tests/ -n auto
```

### Code Quality

```bash
# Format code (100-char line length)
black framework/ plugins/ cli/ tests/

# Lint
ruff check framework/ plugins/ cli/ tests/

# Type check (strict mode)
mypy framework/ plugins/ cli/

# Run all checks
black . && ruff check . && mypy framework/ plugins/ cli/
```

### Adding a New Language Plugin

1. Create `plugins/python_plugin.py` inheriting from `DomainPlugin`
2. Implement required methods: `get_categories()`, `get_few_shot_examples()`, etc.
3. Add ground truth dataset in `experiments/ground_truth/python/`
4. Register in ProductionAnalyzer

See `plugins/cpp_plugin.py` for reference implementation.

---

## Documentation

- **[PROJECT_PLAN.md](docs/PROJECT_PLAN.md)** - Comprehensive project transformation plan
- **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Production deployment guide
- **[EXPERIMENT_RESULTS.md](experiments/EXPERIMENT_RESULTS.md)** - Experiment results and leaderboard
- **[VALIDATION_REPORT.md](validation/VALIDATION_REPORT.md)** - Real-world validation results
- **[MIGRATION.md](MIGRATION.md)** - Migration from research platform to PR bot
- **[CLAUDE.md](CLAUDE.md)** - Instructions for Claude Code assistant
- **[docs/](docs/)** - Additional architecture and usage documentation

### Phase Documentation (Historical)

The project evolved through 5 research phases:
- [Phase 0-5 docs](docs/research/phases/) - Research findings and metrics

---

## Troubleshooting

### Ollama Connection Issues

```bash
# Check if Ollama is running
ollama list

# Start Ollama
ollama serve
```

### Model Not Found

```bash
# Download the model
ollama pull deepseek-coder:33b-instruct

# List available models
ollama list
```

### Out of Memory

1. Use smaller model: `qwen2.5-coder:14b`
2. Reduce max_tokens in config
3. Enable chunking for large files: `--chunk --chunk-size 150`

---

## Project History

This project was originally a **research platform** for evaluating LLM prompting techniques on code analysis tasks. It has been transformed into a **production PR review bot** focused on semantic issues.

See [MIGRATION.md](MIGRATION.md) for transformation details and `archive/research-platform` tag for original state.

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Contact

- **Issues**: GitHub Issues
- **Internal Support**: [Contact your team]

---

**Built to complement your existing analysis pipeline and catch what automated tools miss.**
