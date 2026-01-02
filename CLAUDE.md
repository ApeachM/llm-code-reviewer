# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Semantic PR Review Bot** is an LLM-powered code review system that catches semantic errors and logic issues that static/dynamic analysis tools miss.

**Key constraint**: All LLM inference runs locally via Ollama - no external API calls.

**Core Mission**: Complement existing static/dynamic analysis pipeline (AddressSanitizer, ThreadSanitizer, clang-tidy, Valgrind) by detecting:
- Logic errors (off-by-one, wrong operators)
- API misuse patterns
- Semantic inconsistencies (code vs documentation)
- Edge case handling issues
- Code-intent mismatch (implementation vs PR description)

**Key Features**:
- Semantic-focused analysis (NOT memory safety, NOT performance, NOT concurrency)
- CI/CD integration (GitLab CI, Jenkins, GitHub Actions)
- Production-ready CLI for file/directory/PR analysis
- Large file support via AST-based chunking (tree-sitter) with parallel processing
- Experiment infrastructure for technique validation

## Common Commands

### Installation
```bash
# Requires Python 3.11+ (specified in pyproject.toml)
python -m venv venv
source venv/bin/activate

# Editable install (creates llm-framework CLI entry point)
pip install -e .

# Optional: Install dev dependencies for linting/formatting
pip install -e ".[dev]"

# Download default LLM model (18GB, requires ~20GB disk space)
ollama pull deepseek-coder:33b-instruct

# Alternative: Use smaller model (8GB)
ollama pull qwen2.5-coder:14b
```

### Running Analysis (Production)
```bash
# Single file
python -m cli.main analyze file src/main.cpp

# Directory (recursive)
python -m cli.main analyze dir src/ --output report.md

# PR changes (local testing)
python -m cli.main analyze pr --base main --head feature-branch

# Large files (300+ lines) - automatic chunking recommended
python -m cli.main analyze file large.cpp --chunk --chunk-size 200

# Chunking uses tree-sitter AST parsing + parallel ThreadPoolExecutor (4 workers default)
# Results are automatically merged and deduplicated by (line, category)

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
# All tests (uses pytest with strict markers, verbose mode from pyproject.toml)
pytest tests/

# Single test file
pytest tests/test_chunker.py

# Specific test with verbose output
pytest tests/test_chunker.py::test_function_name -v

# Run phased integration tests (corresponds to Phase 0-5 development)
pytest tests/test_phase0_integration.py  # Zero-shot baseline
pytest tests/test_phase1_integration.py  # Few-shot learning
pytest tests/test_phase2_integration.py  # Multi-technique comparison
pytest tests/test_phase3_integration.py  # Production analyzer (file/dir/PR)
pytest tests/test_phase4_integration.py  # Hybrid techniques
pytest tests/test_phase5_integration.py  # Large file chunking

# Run tests in parallel (faster)
pytest tests/ -n auto
```

### Linting & Formatting
```bash
# Format code with black (100-char line length, Python 3.11+)
black framework/ plugins/ cli/ tests/

# Lint with ruff (100-char line length, Python 3.11+)
ruff check framework/ plugins/ cli/ tests/

# Type check with mypy (strict mode: disallow_untyped_defs enabled)
mypy framework/ plugins/ cli/

# Run all quality checks together
black framework/ plugins/ cli/ tests/ && \
ruff check framework/ plugins/ cli/ tests/ && \
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
├── cpp_plugin.py       # C++ plugin: 5 semantic categories, 5 few-shot examples
└── production_analyzer.py # Orchestrator for file/dir/PR analysis

cli/main.py             # Click-based CLI entry point

integrations/           # CI/CD integrations (Phase 3+)
├── gitlab_client.py    # GitLab API client (TODO)
└── github_client.py    # GitHub API client (TODO)
```

### Key Abstractions

**Technique Hierarchy**:
- **BaseTechnique** (`framework/techniques/base.py`): Abstract base class. All techniques implement `analyze(request: AnalysisRequest) -> AnalysisResult`.
  - **SinglePassTechnique**: Single LLM call techniques (ZeroShot, FewShot, ChainOfThought). Override `_build_user_prompt()` to customize.
  - **MultiPassTechnique**: Multiple LLM call techniques (MultiPass, Hybrid). Override `_execute_analysis()` for custom multi-step logic.

**Domain Plugin Protocol**:
- **DomainPlugin** (`plugins/domain_plugin.py`): Abstract interface for language-specific knowledge.
  - `name` property: Plugin identifier (e.g., "cpp")
  - `supported_extensions`: File extensions (e.g., [".cpp", ".h"])
  - `categories`: Issue categories (e.g., ["logic-errors", "api-misuse"])
  - `get_few_shot_examples(num)`: Returns curated training examples
  - `get_system_prompt()`: Returns domain-specific system prompt
  - `should_analyze_file(path)`: File filtering logic (skips tests, third-party code)

**Production Components**:
- **ProductionAnalyzer** (`plugins/production_analyzer.py`): Main orchestrator that combines plugin + technique for analysis. Handles file/directory/PR workflows.
- **FileChunker** (`framework/chunker.py`): AST-based chunking using tree-sitter for files 300+ lines
- **ChunkAnalyzer** (`framework/chunk_analyzer.py`): Parallel chunk processing with ThreadPoolExecutor
- **ResultMerger** (`framework/result_merger.py`): Deduplicates issues by (line, category) tuple

### Core Data Models (Pydantic)

All data structures use Pydantic for type safety and validation:

- **Issue**: Detected code issue with category, severity, line, description, reasoning, suggested_fix, confidence
- **AnalysisRequest**: Input to technique with code, file_path, language, context, technique_config
- **AnalysisResult**: Output with issues[], metadata{model, technique, latency, tokens}, raw_response
- **GroundTruthExample**: Annotated example with id, description, code, file_path, expected_issues[]
- **ExperimentConfig**: Experiment parameters (experiment_id, technique_name, model_name, dataset_path, seed)
- **MetricsResult**: Evaluation metrics (precision, recall, f1, token_efficiency, latency, total_tokens)

### Data Flow

1. CLI receives command (file/dir/pr)
2. ProductionAnalyzer checks file via plugin's `should_analyze_file()`
3. For large files (300+ lines): FileChunker splits via tree-sitter AST, ChunkAnalyzer runs parallel analysis (ThreadPoolExecutor)
4. Technique builds prompt with plugin's few-shot examples and system prompt
5. OllamaClient calls local LLM (default: deepseek-coder:33b-instruct)
6. ResultMerger deduplicates issues by (line, category) tuple and adjusts line numbers
7. Returns AnalysisResult with issues, metadata, and metrics

## Issue Categories (Semantic-Focused)

**IMPORTANT**: These categories focus on semantic issues that static/dynamic analysis CANNOT detect.

### Current Categories (Phase 1+)

- `logic-errors`: Off-by-one errors, wrong comparison operators, incorrect boolean logic
- `api-misuse`: Incorrect API usage patterns, missing cleanup calls, resource leaks in error paths
- `semantic-inconsistency`: Code behavior doesn't match naming or documentation
- `edge-case-handling`: Missing boundary checks, unhandled edge cases
- `code-intent-mismatch`: Implementation doesn't match PR description or requirements

### ❌ Categories We Do NOT Use (Covered by Static/Dynamic Analysis)

- ~~`memory-safety`~~ → AddressSanitizer, Valgrind detect these
- ~~`performance`~~ → Profilers, clang-tidy performance-* checks
- ~~`concurrency`~~ → ThreadSanitizer detects data races
- ~~`security`~~ (partially) → Static analyzers detect many security issues

### Category Validation

Categories are validated in `framework/models.py` (lines 34-40). When adding/changing categories:
1. Update `allowed` set in `models.py`
2. Update `categories` property in `plugins/cpp_plugin.py`
3. Update few-shot examples to match new categories
4. Update system prompt to explain new categories

## Prompting Techniques

| Technique | Type | F1 Score | Latency | Use Case |
|-----------|------|----------|---------|----------|
| few_shot_5 | Single-pass | 0.615 | 8.15s | **Default for production** (best speed/accuracy) |
| hybrid | Multi-pass | 0.634 | 32.76s | Critical PRs (best accuracy, 4x slower) |
| chain_of_thought | Single-pass | 0.571 | 23.94s | Complex logic analysis |
| few_shot_3 | Single-pass | 0.588 | 7.12s | Cost-sensitive (20% token savings) |
| zero_shot | Single-pass | 0.526 | 7.15s | Baseline only |
| multi_pass | Multi-pass | N/A | N/A | Self-critique with confidence scoring |

**Available technique names in TechniqueFactory**:
- Single-pass: `zero_shot`, `few_shot_3`, `few_shot_5`, `few_shot` (alias), `chain_of_thought`
- Multi-pass: `multi_pass`, `hybrid`, `hybrid_high_precision`, `hybrid_category_specialized`

## Adding a New Domain Plugin

1. Create `plugins/new_plugin.py` inheriting from `DomainPlugin`
2. Implement: `get_file_extensions()`, `get_categories()`, `get_few_shot_examples()`, `should_analyze_file()`
3. Add ground truth dataset in `experiments/ground_truth/new_domain/`
4. Create experiment config in `experiments/configs/`

## Adding a New Technique

1. Create `framework/techniques/new_technique.py` inheriting from appropriate base:
   - **SinglePassTechnique**: For one LLM call (override `_build_user_prompt()`)
   - **MultiPassTechnique**: For multiple LLM calls (override `_execute_analysis()`)
2. Implement required abstract properties and methods:
   - `name` property: Technique identifier string
   - For SinglePassTechnique: Override `_build_user_prompt(code: str) -> str`
   - For MultiPassTechnique: Override `_execute_analysis(request: AnalysisRequest) -> AnalysisResult`
3. Register in `framework/techniques/__init__.py` TechniqueFactory:
   ```python
   _TECHNIQUE_MAP = {
       # ... existing techniques
       'new_technique': NewTechnique,
   }
   ```
4. Create experiment config in `experiments/configs/new_technique.yml`
5. Run experiment: `python -m cli.main experiment run --config experiments/configs/new_technique.yml`
6. Compare results: `python -m cli.main experiment leaderboard`

## Ground Truth & Evaluation

- **Ground truth examples**: `experiments/ground_truth/cpp/` (20 annotated C++ examples)
- **Metrics tracked**:
  - Precision: TP / (TP + FP) - ratio of correct detections
  - Recall: TP / (TP + FN) - ratio of issues found
  - F1 Score: Harmonic mean of precision and recall
  - Token efficiency: Issues detected per 1K tokens
  - Latency: Average time per example
  - Per-category metrics: F1 scores for each issue category
- **Experiment results**: Saved to `experiments/runs/` with timestamp (gitignored)
- **Evaluation logic**: Issues matched by (line_number, category) tuple. Same line + same category = match.
- **Statistical analysis**: `framework/statistical_analyzer.py` computes per-category metrics and confidence intervals

## Development Patterns & Conventions

### Code Quality Standards
- **Type safety**: Use Pydantic models for all data structures. Enable mypy strict mode (`disallow_untyped_defs = true`).
- **Line length**: 100 characters (configured in pyproject.toml for black and ruff)
- **Python version**: 3.11+ required (uses modern typing features)
- **Testing**: Every new feature should have corresponding tests in `tests/`. Follow phased integration test pattern.
- **Documentation**: Update relevant docs in `docs/` when changing architecture or adding features.

### File Organization
- **Framework code**: Domain-agnostic logic goes in `framework/`
- **Domain-specific code**: Language-specific logic goes in `plugins/`
- **CLI commands**: User-facing commands in `cli/main.py` (uses Click)
- **Experiments**: Research configs in `experiments/configs/`, results in `experiments/runs/` (gitignored)
- **CI/CD integrations**: API clients and webhooks in `integrations/` (Phase 3+)

### Important Conventions
- **Technique registration**: All new techniques MUST be registered in `framework/techniques/__init__.py` TechniqueFactory
- **Plugin interface**: All plugins MUST inherit from `DomainPlugin` and implement all abstract methods
- **Issue matching**: Issues are uniquely identified by `(line_number, category)` tuple for deduplication
- **Chunking threshold**: Files 300+ lines should use chunking (configurable with `--chunk-size`)
- **Experiment workflow**: Always create config → run experiment → evaluate metrics → compare on leaderboard
- **Git workflow**: Main branch for stable releases. Use feature branches for development. Tag major milestones.

### Testing Philosophy
- **Phased tests**: Tests organized by development phase (Phase 0-5), mirroring project evolution
- **Integration over unit**: Prefer integration tests that validate end-to-end workflows
- **Ground truth validation**: All techniques tested against 20 annotated examples with F1 scores
- **Parallel execution**: Use `pytest -n auto` for faster test runs (requires pytest-xdist)

## Project Transformation Phases

This project is being transformed from a research platform to a production PR review bot:

- **Phase 0** (Current): Project rebranding and documentation update
- **Phase 1**: Replace categories with semantic-focused ones, update few-shot examples
- **Phase 2**: Rebuild ground truth dataset with semantic errors
- **Phase 3**: CI/CD integration (GitLab CI, Jenkins, GitHub Actions)
- **Phase 4**: Production hardening (error handling, monitoring, deployment)

See `PROJECT_PLAN.md` for detailed transformation roadmap.
See `MIGRATION.md` for migration from research platform.
See `archive/research-platform` git tag for original state.

## CI/CD Deployment

**Target Environment**: Self-hosted CI/CD (GitLab CI or Jenkins)

### GitLab CI Integration (Phase 3)
- Trigger on merge request events
- Fetch PR metadata (title, description, changed files)
- Run analysis on changed lines only
- Post results as MR comments via GitLab API

### Key Files (Phase 3+)
- `.gitlab-ci.yml` - CI/CD pipeline configuration
- `integrations/gitlab_client.py` - GitLab API client
- `cli/main.py` - Add `--changed-lines-only` and `--webhook-mode` flags

## Important Reminders for Development

1. **Focus on Semantic Issues**: Never suggest detecting issues that static/dynamic analysis can catch
2. **Category Alignment**: When updating categories, update in 3 places: models.py, cpp_plugin.py, and documentation
3. **Few-Shot Quality**: Few-shot examples should demonstrate semantic issues, not memory/performance issues
4. **System Prompt**: Keep system prompt focused on complementing existing tooling, not replacing it
5. **Git Tags**: Create tags for major milestones (v1.0-core-categories, v1.0-dataset-ready, etc.)
6. **Experiments**: Always validate changes with experiment runs before deploying to production

## Related Documentation

- `README.md` - User-facing project overview and quick start
- `PROJECT_PLAN.md` - Comprehensive transformation plan with phases
- `MIGRATION.md` - Migration guide from research platform
- `docs/architecture/overview.md` - Technical architecture deep dive
- `docs/guides/` - Usage guides and tutorials
