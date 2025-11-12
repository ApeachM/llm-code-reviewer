# Implementation Plan: Domain-Agnostic LLM Engineering Framework

**Branch**: `003-llm-framework-core` | **Date**: 2025-11-11 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/003-llm-framework-core/spec.md`

## Summary

Build an **LLM engineering research platform** that discovers, measures, and documents which prompting techniques work best for code analysis. This is NOT just another code analysis tool - the primary value is systematic experimentation proving techniques like few-shot learning (+40% accuracy), multi-pass review (-20% false positives), chain-of-thought (+30% complex bugs), and diff-focused prompting (-50% tokens). Framework provides domain-agnostic infrastructure (experimental harness, A/B testing, metrics calculation, technique library) with plugin architecture allowing extension to multiple domains (C++, RTL, Power, Design).

**Core Differentiator**: LLM engineering mastery productized as framework. The artifact is not "a C++ reviewer" but "documented evidence of which LLM techniques work, with reusable infrastructure to apply them."

## Technical Context

**Language/Version**: Python 3.11+ (type hints, dataclasses, match statements, modern async)
**Primary Dependencies**:
- ollama-python (local LLM interface with streaming)
- pydantic 2.0+ (runtime validation, settings management, JSON schema)
- pytest + pytest-xdist (parallel testing)
- rich (terminal UI for experiment progress)
- numpy + scipy (metrics calculation, statistical significance testing)
- pandas (results aggregation, trend analysis)
- pyyaml (configuration management)
- tree-sitter (C++ parsing - plugin specific)

**Storage**:
- File-based: JSON for ground truth datasets, experiment configs, results
- Timestamped experiment runs for reproducibility
- No database required (research artifact storage, not transactional system)

**Testing**: pytest with fixtures for:
- Technique unit tests (mocked LLM responses)
- Integration tests (real Ollama calls on small examples)
- Evaluation framework tests (ground truth comparison)
- Plugin contract tests (interface compliance)

**Target Platform**: Linux/macOS desktop (developer workstation with local Ollama)
**Project Type**: Single-project CLI tool + library (not web/mobile)

**Performance Goals** (RESEARCH PRIMARY):
- **Experimental throughput**: Evaluate 1 technique on 20 examples in <5 minutes
- **Reproducibility**: Same experiment config → same technique ranking
- **Statistical power**: Detect ≥10% quality difference with p<0.05
- **Analysis speed** (secondary): <60 seconds for 500-line PR analysis

**Constraints**:
- **Privacy**: All processing local, zero network calls except Ollama localhost
- **Token limits**: Handle 8k-32k context windows via chunking
- **Compute**: Must run on laptop (16GB RAM, no GPU required)
- **Offline**: Fully functional without internet (post-model download)

**Scale/Scope**:
- **Ground truth**: 20-50 annotated examples per domain
- **Technique matrix**: 10-20 configurations to compare
- **Domains**: 2-3 domains (C++, RTL initially)
- **Experiment velocity**: Run full matrix in <30 minutes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify this feature aligns with all constitutional principles (Constitution v2.0.0):

- [x] **Privacy-First, Local LLM Only**: All inference via local Ollama, no cloud APIs, fully on-premise
- [x] **Domain-Agnostic Plugin Architecture**: Clear separation - framework (LLM techniques) vs plugins (domain logic)
- [x] **LLM Engineering Excellence**: Core value proposition - few-shot, multi-pass, CoT, self-critique as modular techniques
- [x] **Data-Driven Evaluation Framework**: Experimental infrastructure is Phase 0 (first!), metrics everywhere
- [x] **Token Efficiency & Context Management**: Diff-focused prompting, token budget allocation, monitoring built-in
- [x] **Production-Ready Engineering**: Pydantic validation, pytest testing, type hints, error handling

*All boxes checked. No violations.*

## Project Structure

### Documentation (this feature)

```text
specs/003-llm-framework-core/
├── plan.md              # This file
├── research.md          # Phase 0: Experimental infrastructure design
├── data-model.md        # Phase 1: Domain entities (Plugin, Technique, Experiment, Result)
├── quickstart.md        # User guide: Running experiments, creating plugins
├── contracts/           # Phase 1: Plugin interface, Technique interface
└── checklists/
    └── requirements.md  # Quality validation (completed)
```

### Source Code (repository root) - EXPERIMENT-FIRST STRUCTURE

```text
framework/
├── __init__.py
├── domain_plugin.py           # ABC: Plugin interface (5 required methods)
├── llm_engine.py              # Orchestrator: Runs techniques via Ollama
├── experiment_runner.py       # ⭐ NEW: A/B testing framework
├── evaluation.py              # ⭐ NEW: Metrics calculator (precision, recall, F1, tokens)
├── prompt_logger.py           # ⭐ NEW: Log all LLM interactions
├── statistical_analyzer.py    # ⭐ NEW: Significance testing (t-test, p-values)
├── config.py                  # Pydantic settings management
├── models.py                  # Pydantic models: AnalysisRequest, Issue, Result
└── techniques/                # ⭐ NEW: Modular, swappable techniques
    ├── __init__.py
    ├── base.py                # BaseTechnique ABC
    ├── few_shot.py            # FewShotTechnique(num_examples: int)
    ├── multi_pass.py          # MultiPassTechnique(num_passes: int)
    ├── chain_of_thought.py    # ChainOfThoughtTechnique(depth: str)
    ├── diff_focused.py        # DiffFocusedTechnique(context_lines: int)
    └── self_critique.py       # SelfCritiqueTechnique(confidence_threshold: float)

plugins/
├── __init__.py
├── cpp/
│   ├── __init__.py
│   ├── plugin.py              # CppPlugin implementation
│   ├── parser.py              # tree-sitter C++ parsing
│   ├── examples.json          # 10+ few-shot examples
│   └── prompts.py             # Prompt templates
└── rtl/                       # Future: RTL plugin
    └── ...

experiments/                   # ⭐ NEW: Research artifact storage
├── ground_truth/              # Annotated examples (version controlled!)
│   └── cpp/
│       ├── example_001.json   # {code, file_path, expected_issues: [...]}
│       ├── example_002.json
│       └── ... (20+ total)
├── configs/                   # Experiment configurations
│   ├── baseline_zero_shot.yml
│   ├── few_shot_3.yml
│   ├── few_shot_5.yml
│   ├── few_shot_10.yml
│   ├── multi_pass_2.yml
│   ├── multi_pass_3.yml
│   ├── combo_5shot_2pass.yml
│   └── ...
├── runs/                      # Timestamped experiment results (gitignored)
│   └── 2025-11-11_143052_few_shot_5/
│       ├── config.yml         # Snapshot of experiment config
│       ├── results.json       # All metrics
│       ├── prompts.log        # Every prompt sent to LLM
│       └── details/           # Per-example results
│           ├── example_001_result.json
│           └── ...
└── leaderboard.md             # ⭐ RESEARCH ARTIFACT: Best techniques ranking

cli/
├── __init__.py
├── main.py                    # Click CLI: analyze, evaluate, compare, experiment
└── ui.py                      # Rich progress bars, result tables

tests/
├── unit/
│   ├── test_techniques.py     # Mock LLM, test each technique
│   ├── test_evaluation.py     # Metrics calculation correctness
│   └── test_plugins.py        # Plugin interface compliance
├── integration/
│   ├── test_experiment_runner.py  # End-to-end experiment
│   └── test_cpp_plugin.py     # Real Ollama, small examples
└── fixtures/
    ├── mock_ground_truth.json
    └── mock_llm_responses.py

prompts/                       # Prompt engineering artifacts (tracked!)
└── cpp/
    ├── system_prompt.txt      # Base instructions
    ├── few_shot_examples/     # Versioned example sets
    │   ├── v1_memory_safety.json
    │   ├── v2_modern_cpp.json
    │   └── ...
    └── critique_prompt.txt    # Self-critique instructions

test-data/                     # Integration test data
└── cpp/
    └── sample-pr-001/         # Existing test PR data
        ├── diff.patch
        ├── expected-issues.md
        └── ...

docs/                          # User documentation
├── quickstart.md              # Get started in 5 minutes
├── plugin-development.md      # Build your own plugin
├── experiment-guide.md        # Run A/B tests
└── technique-library.md       # Catalog of techniques

pyproject.toml                 # Project metadata, dependencies
.llm-framework.yml             # User configuration template
README.md                      # Project overview
```

**Structure Decision**: Single-project layout (Option 1) with research emphasis. The `experiments/` directory is first-class - this is a research platform, so experimental artifacts (ground truth, configs, runs, leaderboard) are peer to source code, not buried in tests. Technique modularity emphasized via `framework/techniques/` directory.

## Complexity Tracking

No constitutional violations. Complexity is justified:

| Design Choice | Rationale | Alternative Rejected |
|---------------|-----------|---------------------|
| Separate `techniques/` module | Each technique (few-shot, multi-pass, CoT) must be independently testable and swappable. Enables A/B testing foundation of research value. | Hardcoding techniques into LLMEngine would prevent comparative analysis and make research findings untraceable. |
| Experiment-first directory structure | Ground truth datasets, experiment configs, and results are PRIMARY ARTIFACTS of research platform. Elevating to top-level makes research workflow explicit. | Burying in `tests/` treats experiments as second-class, hides research value. |
| Timestamped experiment runs | Reproducibility requires exact snapshot: config, prompts, results. Timestamped directories enable: "What was configuration that achieved F1=0.85 on 2025-11-15?" | Overwriting results loses history, makes claiming improvements non-credible. |
| Prompt logging | Core research question is "which prompts work best?" Cannot answer without complete prompt history. Enables post-hoc analysis: "Why did this example cause false positive?" | Without logging, debugging technique failures is impossible. Research becomes anecdotal. |

## Phase 0: Experimental Infrastructure (Day 1-2) ⭐ CRITICAL FOUNDATION

**Goal**: Build measurement infrastructure BEFORE building anything to measure. Cannot claim "technique X is better" without rigorous evaluation framework.

**Why First**: Constitution Principle IV (Data-Driven Evaluation) mandates measurement. All subsequent work depends on ability to run experiments and trust results.

### Deliverables

1. **GroundTruthDataset Class** (`framework/evaluation.py`)
   - Load annotated examples from JSON
   - Schema: `{code, file_path, expected_issues: [{category, severity, line, description}]}`
   - Validation: Pydantic models ensure schema compliance
   - 20+ manually annotated C++ examples in `experiments/ground_truth/cpp/`

2. **MetricsCalculator** (`framework/evaluation.py`)
   - Calculate precision, recall, F1 per example and aggregated
   - Per-category breakdowns (memory-safety precision, performance recall)
   - Token efficiency: issues found per 1K tokens
   - Latency tracking: time per pass, total time
   - False positive/negative classification with details

3. **ExperimentRunner** (`framework/experiment_runner.py`)
   - Load experiment config (YAML)
   - Run technique on all ground truth examples
   - Collect all metrics
   - Save timestamped results to `experiments/runs/{timestamp}_{technique_name}/`
   - Generate summary report

4. **PromptLogger** (`framework/prompt_logger.py`)
   - Log every prompt sent to LLM with metadata: timestamp, technique, example_id, model
   - Log every response with token count, latency
   - Structured format (JSON lines) for analysis
   - Enable queries: "Show all prompts that resulted in false positives"

5. **StatisticalAnalyzer** (`framework/statistical_analyzer.py`)
   - Compare two techniques: t-test for precision/recall/F1 differences
   - Report p-values, effect sizes, confidence intervals
   - Determine: "Is technique A significantly better than B? (p<0.05)"
   - Generate comparison reports with recommendations

### Research Artifact: 20+ Annotated C++ Examples

**Critical Path**: Cannot evaluate without ground truth. This is MANUAL WORK requiring domain expertise.

**Example Format** (`experiments/ground_truth/cpp/example_001.json`):
```json
{
  "id": "example_001",
  "description": "Memory leak - raw pointer never deleted",
  "code": "int* ptr = new int(10);\n// ... usage\n// missing delete ptr;",
  "file_path": "memory_leak.cpp",
  "expected_issues": [
    {
      "category": "memory-safety",
      "severity": "critical",
      "line": 1,
      "description": "Memory leak - dynamically allocated pointer never deleted",
      "reasoning": "new without corresponding delete causes memory leak"
    }
  ]
}
```

**Annotation Guidelines**:
- Cover all priority categories: memory-safety (CRITICAL), modern-cpp (HIGH), performance (HIGH), security (CRITICAL), concurrency (MEDIUM)
- Mix of positive (has issues) and negative (clean code) examples
- Vary complexity: simple (1 issue) to complex (multiple interacting issues)
- Real-world patterns from actual C++ codebases

**Time Estimate**: 4-6 hours for 20 examples (domain expert required)

### Success Criteria (Phase 0)

- ✅ Can load 20+ ground truth examples, validate schema
- ✅ Can run experiment: apply technique, get precision/recall/F1
- ✅ Results save to timestamped directory with full reproduction data
- ✅ Prompts logged, queryable
- ✅ Statistical comparison between two configs shows significance testing

**Exit Gate**: Run dummy experiment (mocked LLM responses) end-to-end. Verify metrics calculation, result storage, prompt logging all function correctly.

---

## Phase 1: Framework Core + Technique Library (Day 3-7)

**Goal**: Implement domain-agnostic LLM techniques as modular, composable, independently testable components.

### 1.1: Domain Plugin Interface (`framework/domain_plugin.py`)

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pydantic import BaseModel

class DomainPlugin(ABC):
    """
    Domain-specific plugin interface.
    Framework handles LLM techniques; plugin provides domain knowledge.
    """

    @abstractmethod
    def get_few_shot_examples(self, category: str = None) -> List[Dict]:
        """Return 5-10 expert examples per category for few-shot learning."""
        pass

    @abstractmethod
    def parse_artifact(self, content: str) -> Dict[str, Any]:
        """Parse code/design into analyzable units (functions, modules, blocks)."""
        pass

    @abstractmethod
    def format_diff(self, diff: str) -> str:
        """Format git diff for LLM analysis (BEFORE/AFTER highlighting)."""
        pass

    @abstractmethod
    def validate_output(self, llm_output: str) -> List['Issue']:
        """Parse and validate LLM output against domain schema."""
        pass

    @abstractmethod
    def format_report(self, issues: List['Issue'], format: str) -> str:
        """Format issues as markdown, JSON, or git-comment."""
        pass
```

### 1.2: BaseTechnique Interface (`framework/techniques/base.py`)

```python
from abc import ABC, abstractmethod
from typing import Dict, Any
from pydantic import BaseModel

class TechniqueConfig(BaseModel):
    """Configuration for a technique (serializable to YAML)."""
    name: str
    version: str
    parameters: Dict[str, Any]

class BaseTechnique(ABC):
    """
    Base class for LLM techniques (few-shot, multi-pass, CoT, etc.).
    Each technique is independently testable via mocked LLM.
    """

    def __init__(self, config: TechniqueConfig):
        self.config = config

    @abstractmethod
    def build_prompt(self, code: str, context: Dict, plugin: 'DomainPlugin') -> str:
        """Construct prompt using this technique's strategy."""
        pass

    @abstractmethod
    def process_response(self, response: str, metadata: Dict) -> Dict[str, Any]:
        """Process LLM response, extract structured data."""
        pass

    def execute(self, code: str, context: Dict, llm_client, plugin: 'DomainPlugin') -> Dict:
        """Standard execution flow: build prompt → call LLM → process response."""
        prompt = self.build_prompt(code, context, plugin)
        response = llm_client.generate(prompt)
        return self.process_response(response, {'prompt': prompt, 'tokens': response.token_count})
```

### 1.3: Technique Implementations

**FewShotTechnique** (`framework/techniques/few_shot.py`):
- Config parameter: `num_examples: int` (0 for zero-shot, 3/5/10 for few-shot)
- Retrieves N examples per category from plugin
- Injects examples into prompt template
- Research shows: 5-shot optimal (+40% accuracy vs zero-shot)

**MultiPassTechnique** (`framework/techniques/multi_pass.py`):
- Config parameter: `num_passes: int` (1=single, 2=critique, 3=refine)
- Pass 1: Initial analysis
- Pass 2: Self-critique ("Which findings might be false positives?")
- Pass 3: Refinement (arbitrate conflicts, add confidence scores)
- Research shows: 2-pass reduces false positives by 20%

**ChainOfThoughtTechnique** (`framework/techniques/chain_of_thought.py`):
- Config parameter: `depth: str` ("shallow", "deep")
- Prompts LLM to explain reasoning step-by-step before conclusion
- Deep: "1. What does code do? 2. What could go wrong? 3. Why problematic? 4. How to fix?"
- Research shows: +30% complex bug detection

**DiffFocusedTechnique** (`framework/techniques/diff_focused.py`):
- Config parameter: `context_lines: int` (2-5 lines before/after change)
- Formats diff with BEFORE/AFTER highlighting, changed lines marked
- Omits unchanged code to save tokens
- Research shows: -50% token consumption vs full-file analysis

**SelfCritiqueTechnique** (`framework/techniques/self_critique.py`):
- Config parameter: `confidence_threshold: float` (0.0-1.0)
- Asks LLM to rate confidence for each finding
- Filters issues below threshold
- Research shows: -15% false positives when threshold=0.7

### 1.4: LLMEngine Orchestration (`framework/llm_engine.py`)

```python
class LLMEngine:
    """
    Orchestrates techniques + Ollama client.
    Framework responsibility: technique execution, not domain logic.
    """

    def __init__(self, model: str, plugin: DomainPlugin):
        self.ollama = OllamaClient(model=model)
        self.plugin = plugin

    def analyze(self, code: str, technique: BaseTechnique, context: Dict = None) -> AnalysisResult:
        """
        Run single technique on code.
        Returns: AnalysisResult with issues, metrics, metadata.
        """
        result = technique.execute(code, context or {}, self.ollama, self.plugin)
        issues = self.plugin.validate_output(result['output'])

        return AnalysisResult(
            issues=issues,
            token_count=result['tokens'],
            latency=result['latency'],
            technique=technique.config.name,
            metadata=result
        )
```

### 1.5: Minimal CppPlugin (Just Enough to Test)

**Goal**: Validate plugin interface with simplest possible implementation. Full C++ plugin comes later (Phase 3).

**Minimal Implementation**:
- `get_few_shot_examples()`: Return 3 hardcoded examples (memory leak, unnecessary copy, modern C++)
- `parse_artifact()`: Trivial - return code as-is (no AST parsing yet)
- `format_diff()`: Simple BEFORE/AFTER text formatting
- `validate_output()`: Parse JSON, create Issue objects
- `format_report()`: Basic markdown template

**Time Saved**: No tree-sitter integration, no comprehensive example curation yet. Those are Phase 3 polish.

### Success Criteria (Phase 1)

- ✅ Plugin interface defined with contracts, type hints
- ✅ BaseTechnique interface with 5 implementations (few-shot, multi-pass, CoT, diff-focused, self-critique)
- ✅ Each technique independently unit-testable (mocked LLM)
- ✅ LLMEngine can run any technique on any plugin
- ✅ Minimal CppPlugin passes interface compliance tests
- ✅ Integration test: Run FewShotTechnique(3) on one ground truth example, get metrics

**Exit Gate**: End-to-end test with real Ollama: CppPlugin + FewShotTechnique(5) on example_001.json → returns precision/recall/F1.

---

## Phase 2: Technique Experiments - THE CORE VALUE! (Day 8-12) ⭐⭐⭐

**Goal**: DISCOVER which LLM techniques work best for code analysis. Generate research findings with statistical rigor. This is what differentiates framework from "just another tool."

### 2.1: Experiment Matrix

Run all combinations, measure everything:

**Technique Configurations** (`experiments/configs/`):
1. `baseline_zero_shot.yml` - No examples, single pass
2. `few_shot_3.yml` - 3 examples per category
3. `few_shot_5.yml` - 5 examples per category
4. `few_shot_10.yml` - 10 examples per category
5. `multi_pass_2.yml` - Initial + self-critique
6. `multi_pass_3.yml` - Initial + critique + refinement
7. `chain_of_thought_shallow.yml` - Basic CoT
8. `chain_of_thought_deep.yml` - Detailed step-by-step
9. `diff_focused_3lines.yml` - 3 lines context before/after
10. `combo_5shot_2pass.yml` - Few-shot(5) + MultiPass(2)
11. `combo_5shot_cot_critique.yml` - Few-shot(5) + CoT(deep) + Critique
12. `best_all_techniques.yml` - Winning combination from experiments

**Model Variations**:
- deepseek-coder:33b (primary)
- qwen2.5:14b (comparison)

**Dataset**: 20 ground truth C++ examples

**Total Experiments**: 12 configs × 2 models × 20 examples = 480 LLM calls

### 2.2: Experiment Execution

```bash
# Run single experiment
llm-framework experiment run --config few_shot_5.yml --model deepseek-coder:33b

# Run full matrix (all configs, one model)
llm-framework experiment matrix --model deepseek-coder:33b

# Compare two techniques
llm-framework experiment compare \
  --baseline experiments/runs/2025-11-11_001_zero_shot \
  --treatment experiments/runs/2025-11-11_002_few_shot_5
```

**Output Per Experiment**:
- `experiments/runs/{timestamp}_{technique_name}/results.json`
  - Aggregate metrics: precision, recall, F1, token_efficiency, latency
  - Per-category metrics: memory-safety precision, performance recall, etc.
  - Per-example results: true positives, false positives, false negatives
- `experiments/runs/{timestamp}_{technique_name}/prompts.log`
  - Every prompt sent to LLM
  - Every response received
  - Token counts, latencies
- `experiments/runs/{timestamp}_{technique_name}/analysis.md`
  - Statistical summary
  - Best/worst performing examples
  - Failure mode analysis (why false positives occurred)

### 2.3: Statistical Analysis & Leaderboard

After running matrix, generate comparative analysis:

```bash
# Generate leaderboard from all experiments
llm-framework experiment leaderboard --output experiments/leaderboard.md
```

**Leaderboard Format** (`experiments/leaderboard.md`):
```markdown
# LLM Technique Leaderboard - C++ Code Analysis
*Generated: 2025-11-11 | Dataset: 20 annotated examples | Model: deepseek-coder:33b*

## Overall Rankings (by F1 Score)

| Rank | Technique | F1 | Precision | Recall | Tokens/Issue | Latency | Significance |
|------|-----------|-----|-----------|--------|-------------|---------|--------------|
| 1 | 5-shot + CoT + Critique | 0.87 | 0.89 | 0.85 | 2847 | 145s | - |
| 2 | 5-shot + 2-pass | 0.83 | 0.86 | 0.80 | 2103 | 98s | p=0.03 vs #1 |
| 3 | 10-shot single-pass | 0.78 | 0.82 | 0.75 | 3421 | 67s | p=0.01 vs #1 |
| 4 | 5-shot single-pass | 0.74 | 0.79 | 0.70 | 1956 | 52s | p<0.001 vs #1 |
| 5 | 3-shot single-pass | 0.67 | 0.71 | 0.63 | 1542 | 41s | p<0.001 vs #1 |
| 6 | Zero-shot baseline | 0.52 | 0.58 | 0.47 | 1204 | 35s | p<0.001 vs #1 |

## Key Findings

✅ **Few-shot learning is THE most effective technique**: 5-shot beats zero-shot by +42% F1 (p<0.001)
✅ **Multi-pass critique reduces false positives**: 2-pass improves precision by +9% over single-pass (p=0.02)
✅ **Diminishing returns beyond 5 examples**: 10-shot only +6% F1 over 5-shot but +70% more tokens
✅ **Chain-of-thought helps complex bugs**: CoT improves memory-safety recall by +15% (p=0.01)
⚠️ **Diff-focused not yet tested** - requires PR diff format examples

## Recommendations

**For maximum quality** (precision/recall): Use `combo_5shot_cot_critique.yml` (Rank #1)
- Trade-off: 2.5x tokens vs baseline, 4x latency
- Best for: Critical code review where thoroughness matters

**For balanced quality/cost**: Use `few_shot_5.yml` (Rank #4)
- Trade-off: Acceptable quality at reasonable token cost
- Best for: Regular PR reviews

**For speed**: Use `few_shot_3.yml` (Rank #5)
- Trade-off: Lower recall but 3x faster than best technique
- Best for: Quick feedback in development loop

## Per-Category Performance

### Memory Safety (Critical Issues)

| Technique | Precision | Recall | F1 |
|-----------|-----------|--------|-----|
| 5-shot + CoT + Critique | 0.95 | 0.91 | 0.93 |
| Zero-shot baseline | 0.62 | 0.51 | 0.56 |
| **Improvement** | **+53%** | **+78%** | **+66%** |

### Modern C++ Compliance

[Similar tables for each category...]

## Failure Analysis

**Top False Positive Causes**:
1. Overzealous const-correctness suggestions (12 false positives)
   - Fix: Refine few-shot examples to show when const NOT needed
2. Misidentifying smart pointer usage (8 false positives)
   - Fix: Add more smart pointer examples to few-shot set

**Top False Negative Causes**:
1. Subtle use-after-free in multi-threaded code (4 missed)
   - Fix: Add concurrency examples, increase CoT depth
2. Modern C++ range-for opportunities (7 missed)
   - Fix: Add more modern C++ examples to few-shot set
```

### 2.4: Research Artifact: Documented Findings

**Deliverable**: `experiments/findings.md` - Publication-quality writeup

**Sections**:
1. **Research Question**: Which LLM prompting techniques are most effective for code analysis?
2. **Methodology**: Controlled experiment, 12 configs, 20 ground truth examples, statistical testing
3. **Results**: Leaderboard, per-category analysis, significance testing
4. **Discussion**: Few-shot dominates, multi-pass reduces false positives, CoT helps complex bugs
5. **Limitations**: Dataset size (20 examples), single domain (C++), limited model comparison
6. **Future Work**: Larger datasets, more domains, technique combinations, RLHF-style improvement

### Success Criteria (Phase 2)

- ✅ All 12 technique configs successfully run on 20 examples
- ✅ Statistical comparison shows significant differences (p<0.05) between top/bottom techniques
- ✅ Leaderboard generated with clear rankings and recommendations
- ✅ Documented findings explaining WHAT works and WHY
- ✅ Failure analysis identifies improvement opportunities (better examples, refined prompts)
- ✅ Reproducible: Re-running experiments yields same rankings (±5% metric variance acceptable)

**THIS IS THE PRODUCT**: Research findings prove framework's LLM engineering excellence.

---

## Phase 3: Production C++ Plugin (Day 13-16)

**Goal**: Now that we know which techniques work best (from Phase 2 experiments), build production-quality C++ plugin using winning configuration.

### 3.1: Comprehensive Few-Shot Examples

Curate 15+ high-quality examples across categories:
- Memory safety: 4 examples (leak, use-after-free, double-free, dangling pointer)
- Modern C++: 3 examples (range-for, auto, smart pointers)
- Performance: 3 examples (unnecessary copy, pass-by-value, algorithmic complexity)
- Security: 2 examples (buffer overflow, null pointer dereference)
- Concurrency: 2 examples (race condition, deadlock risk)

**Quality Criteria** (based on Phase 2 findings):
- Specific, not generic (bad: "use smart pointers", good: "use std::unique_ptr<int> p = std::make_unique<int>(10)")
- Include code snippet + issue + reasoning + suggested fix
- Calibrated to reduce false positives (learned from failure analysis)

### 3.2: Tree-sitter C++ Parsing

Implement proper AST-based parsing:
- Extract functions, classes, methods from code
- Identify changed entities in PR diffs
- Enable chunking for large files (handle >32k token limit)

### 3.3: Diff-Focused Prompting

Implement diff formatting learned from research:
```
File: data_processor.cpp
Function: DataProcessor::getSum()

BEFORE (Base):
31    int getSum() const {
32        int sum = 0;
33        for (size_t i = 0; i < data.size(); i++) {
34            sum += data[i];
35        }
36        return sum;
37    }

AFTER (PR):
33    int getSum() {                          // ❌ REMOVED const
34        if (cachedSum != nullptr) {         // ✅ ADDED
35            return *cachedSum;              // ✅ ADDED
36        }
37        cachedSum = new int(0);             // ✅ ADDED (raw pointer!)
38        for (size_t i = 0; i < data.size(); i++) {
39            *cachedSum += data[i];          // ❌ CHANGED
40        }
41        return *cachedSum;
42    }

Focus on: What changed and potential issues with new code.
```

### 3.4: Winning Technique Configuration

Apply best-performing config from Phase 2 (likely `combo_5shot_cot_critique.yml`):
- FewShotTechnique(num_examples=5)
- ChainOfThoughtTechnique(depth="deep") for memory-safety and security
- MultiPassTechnique(num_passes=2) for self-critique
- DiffFocusedTechnique(context_lines=3) for PR analysis

### 3.5: Integration Test on sample-pr-001

Run production C++ plugin on existing test PR:
```bash
llm-framework analyze-pr --domain cpp --pr test-data/cpp/sample-pr-001/
```

**Expected Output**:
- Detects 3+ of 4 known critical issues from `expected-issues.md`
- <20% false positive rate
- Completes in <3 minutes
- Markdown report with line-referenced comments

### Success Criteria (Phase 3)

- ✅ 15+ curated few-shot examples across all categories
- ✅ Tree-sitter C++ parsing extracts functions/classes correctly
- ✅ Diff-focused prompting formats PR diffs optimally
- ✅ Production config uses winning techniques from Phase 2
- ✅ Achieves precision ≥75%, critical recall ≥85% on ground truth
- ✅ sample-pr-001 analysis completes successfully with actionable feedback

**Exit Gate**: User can run `llm-framework analyze-pr --domain cpp <path>` and get high-quality review in <3 minutes.

---

## Phase 4: RTL Extension & Domain Transfer (Week 3+) - FUTURE

**Goal**: Prove domain-agnostic architecture by extending to RTL without modifying framework core.

### 4.1: RTL Plugin Development

- Verilog/SystemVerilog parsing (tree-sitter-verilog)
- RTL-specific few-shot examples (timing, CDC, power, synthesis)
- RTL issue categories, severity levels
- Module:line output format (RTL tool conventions)

### 4.2: Domain Transfer Measurement

**Research Question**: Do techniques optimized for C++ transfer to RTL?

**Experiment**: Run same technique configs (few-shot 3/5/10, multi-pass, CoT) on RTL ground truth.

**Success Metric**: Techniques maintain ≥80% of quality improvement from C++ to RTL.

**Expected Finding**: Few-shot and multi-pass transfer well (domain-agnostic), but example quality critical (domain-specific).

### Success Criteria (Phase 4)

- ✅ RTL plugin implements DomainPlugin interface without framework changes
- ✅ RTL ground truth dataset (20+ annotated Verilog examples)
- ✅ Technique transfer experiments show ≥80% quality retention C++ → RTL
- ✅ Framework supports 2 domains, validates extensibility claim

---

## Key Design Decisions

### 1. Experiment-First Architecture

**Decision**: Build evaluation infrastructure (Phase 0) BEFORE building features to evaluate.

**Rationale**: Cannot credibly claim "technique X is better" without rigorous measurement. Evaluation framework enables all research value.

**Alternative Rejected**: Build C++ plugin first, add evaluation later. Rejected because: (1) Would optimize blind, (2) Cannot prove claims, (3) Misses research opportunity.

### 2. Technique Modularity

**Decision**: Each technique (few-shot, multi-pass, CoT) is separate class implementing BaseTechnique.

**Rationale**: Enables A/B testing (swap FewShotTechnique(3) for FewShotTechnique(5)), independent testing (mock LLM), composition (combine techniques).

**Alternative Rejected**: Hardcode techniques into LLMEngine. Rejected because: (1) Cannot A/B test, (2) Cannot measure individual contribution, (3) Violates research goal.

### 3. Prompt Logging Always On

**Decision**: Log every prompt, every response, every token count by default.

**Rationale**: Research requires complete data. Post-hoc analysis: "Why did example X produce false positive?" Cannot answer without prompt history.

**Alternative Rejected**: Opt-in logging. Rejected because: (1) Users forget to enable, (2) Loses research data, (3) Cannot debug failures.

### 4. Timestamped Experiment Runs

**Decision**: Never overwrite experiment results. Save to `experiments/runs/{timestamp}_{name}/`.

**Rationale**: Reproducibility and credibility require historical record. Claim "improvement from v1 to v2" needs both results preserved.

**Alternative Rejected**: Single `results.json` file overwritten each run. Rejected because: (1) Loses history, (2) Cannot track improvements, (3) Non-reproducible.

### 5. Ground Truth as Code

**Decision**: Ground truth examples version-controlled in git (`experiments/ground_truth/`).

**Rationale**: Ground truth is research artifact, not test data. Changes to ground truth should be reviewed, tracked. Enables: "Results improved because we fixed mislabeled example, not because technique improved."

**Alternative Rejected**: External database, Google Sheets. Rejected because: (1) No change tracking, (2) Not reproducible, (3) Not portable.

### 6. Plugin Over Inheritance

**Decision**: Domains implement DomainPlugin interface, not extend base class.

**Rationale**: Clear contract (5 methods), explicit dependencies (plugin needs framework, framework doesn't need specific plugin), easier testing.

**Alternative Rejected**: Inheritance-based plugin system. Rejected because: (1) Tight coupling, (2) Multiple inheritance issues, (3) Less explicit dependencies.

### 7. Configuration via YAML, Not Code

**Decision**: Experiment configs are YAML files, not Python code.

**Rationale**: Non-programmers can create configs, configs are data (version control, diff), prevents arbitrary code execution, easier to generate configs programmatically.

**Alternative Rejected**: Python config files (like Django settings). Rejected because: (1) Requires Python knowledge, (2) Can execute arbitrary code, (3) Harder to validate.

### 8. Research Artifacts First-Class

**Decision**: `experiments/` directory is peer to `framework/` and `plugins/`, not inside `tests/`.

**Rationale**: Research artifacts (ground truth, configs, runs, leaderboard) are PRIMARY VALUE, not auxiliary test data. Architecture should make this explicit.

**Alternative Rejected**: Bury experiments in `tests/`. Rejected because: (1) Hides research value, (2) Implies experiments are second-class, (3) Unintuitive for research users.

### 9. Minimal Plugin First, Full Later

**Decision**: Phase 1 builds minimal CppPlugin (just enough to test), Phase 3 builds production plugin.

**Rationale**: Enables fast iteration on framework without blocked by tree-sitter integration. Validates architecture early.

**Alternative Rejected**: Build production C++ plugin first. Rejected because: (1) Blocks framework development, (2) Wastes time if architecture changes, (3) Delays Phase 2 experiments.

### 10. Local-Only, Offline-First

**Decision**: All LLM inference via local Ollama, no cloud APIs, no telemetry, no analytics.

**Rationale**: Constitution Principle I (Privacy-First), enables use in security-sensitive environments, zero operational dependencies, zero cost at scale.

**Alternative Rejected**: Cloud API (OpenAI, Anthropic) option. Rejected because: (1) Violates constitution, (2) Requires API keys/billing, (3) Sends proprietary code to external services.

---

## Dependencies

### External Dependencies

**CRITICAL - Blocks All Work**:
1. **Ollama Installed & Running**
   - Required for: All LLM inference
   - Installation: `curl -fsSL https://ollama.ai/install.sh | sh`
   - Models needed: `ollama pull deepseek-coder:33b` and `ollama pull qwen2.5:14b`
   - Verification: `ollama list` shows models

2. **Ground Truth Dataset Annotation**
   - Required for: Phase 0 (evaluation), Phase 2 (experiments)
   - Time estimate: 4-6 hours (domain expert required)
   - Format: 20+ JSON files with code + expected issues
   - Blocking: Cannot evaluate techniques without ground truth

**NON-BLOCKING**:
3. **Python 3.11+**
   - Required for: All code
   - Installation: Via system package manager
   - Verification: `python --version`

4. **Python Dependencies**
   - ollama-python, pydantic, pytest, rich, numpy, scipy, pandas, pyyaml
   - Installation: `pip install -r requirements.txt`

### Internal Dependencies (Phase Ordering)

**Dependency Graph**:
```
Phase 0 (Experimental Infrastructure)
  └─> Phase 1 (Framework Core + Techniques)
       └─> Phase 2 (Experiments - CORE VALUE!)
            └─> Phase 3 (Production C++ Plugin)
                 └─> Phase 4 (RTL Extension)
```

**Critical Path**: Phase 0 → Phase 1 → Phase 2
- Phase 0 provides evaluation capability (required for all subsequent work)
- Phase 1 provides techniques to evaluate (required for experiments)
- Phase 2 generates research findings (primary deliverable)
- Phase 3 and 4 are secondary (productionization, extensibility proof)

**Parallel Opportunities**:
- Ground truth annotation (Phase 0) can happen in parallel with framework design
- Plugin interface design (Phase 1) can happen in parallel with technique implementation
- Phase 3 C++ plugin polish can overlap with Phase 4 RTL plugin start

---

## Performance Goals

### Research Performance (PRIMARY)

**Experimental Throughput**:
- Goal: Evaluate 1 technique config on 20 examples in <5 minutes
- Breakdown: 20 examples × 15s per LLM call = 5 minutes
- Enabler: Parallel execution via pytest-xdist (4-8 workers)

**Reproducibility**:
- Goal: Same config → same technique ranking (±5% metric variance)
- Verification: Run experiment 3 times, check rankings stable
- Critical for: Research credibility

**Statistical Power**:
- Goal: Detect ≥10% quality difference with p<0.05
- Requires: Sufficient sample size (20 examples minimum)
- Verification: Power analysis (scipy.stats)

**Matrix Coverage**:
- Goal: Run full 12-config matrix in <30 minutes
- Breakdown: 12 configs × 5 minutes each = 60 minutes
- Optimization: Parallel experiment execution (2-3 configs at once)
- Realistic: 30-45 minutes on laptop

### Product Performance (SECONDARY)

**Analysis Speed**:
- Goal: <60 seconds for 500-line PR analysis
- Breakdown:
  - Diff parsing: <1s
  - Context retrieval: <5s (if using simple symbol lookup, not RAG)
  - LLM inference: 30-40s (multi-pass with deepseek-coder:33b)
  - Result formatting: <1s
- Acceptable: 60s is good UX for thorough review

**Token Efficiency**:
- Goal: >0.5 issues per 1K tokens
- Measurement: Total tokens consumed / issues found
- Baseline (zero-shot): ~0.3 issues/1K tokens
- Target (5-shot + 2-pass): >0.5 issues/1K tokens (validated in Phase 2)

**Quality Goals**:
- Precision: ≥75% (3 of 4 flagged issues are real)
- Critical Recall: ≥85% (misses at most 1-2 of 10 critical issues)
- Validated against ground truth in Phase 2

### Resource Constraints

**Compute**:
- Target: Laptop with 16GB RAM, 8-core CPU, no GPU
- LLM: deepseek-coder:33b requires ~20GB disk, ~12GB RAM during inference
- Acceptable: 30-60s per analysis on laptop

**Storage**:
- Ground truth: ~1MB (20 examples × 50KB each)
- Experiment results: ~10MB per full matrix run (12 configs × 20 examples × detailed logs)
- Models: ~20-40GB (Ollama model storage)
- Total: <100GB for complete research artifacts

**Network**:
- Requirement: NONE (fully offline after model download)
- Ollama: localhost:11434 (no internet)
- Zero telemetry, zero analytics

---

## Success Criteria

### Phase 0: Experimental Infrastructure

- ✅ GroundTruthDataset loads 20+ examples, validates schema
- ✅ MetricsCalculator computes precision, recall, F1, per-category metrics
- ✅ ExperimentRunner executes config, saves timestamped results
- ✅ PromptLogger captures all LLM interactions
- ✅ StatisticalAnalyzer compares techniques with significance testing
- ✅ Dummy experiment (mocked LLM) runs end-to-end successfully

### Phase 1: Framework Core + Techniques

- ✅ DomainPlugin interface defined with 5 required methods
- ✅ BaseTechnique interface with 5 implementations
- ✅ Each technique independently unit-testable (95% code coverage)
- ✅ LLMEngine orchestrates any technique on any plugin
- ✅ Minimal CppPlugin passes interface compliance tests
- ✅ Integration test: Real Ollama call on one ground truth example succeeds

### Phase 2: Experiments (CORE VALUE!)

- ✅ **12 technique configs successfully run on 20 ground truth examples**
- ✅ **Statistical comparison shows significant differences (p<0.05) between techniques**
- ✅ **Leaderboard generated with rankings and recommendations**
- ✅ **Documented findings explain WHAT works and WHY**
- ✅ **Failure analysis identifies improvement opportunities**
- ✅ **Reproducibility verified: re-running yields same rankings (±5% variance)**

### Phase 3: Production C++ Plugin

- ✅ 15+ curated few-shot examples across categories
- ✅ Tree-sitter C++ parsing extracts functions/classes
- ✅ Diff-focused prompting formats PR diffs optimally
- ✅ Achieves precision ≥75%, critical recall ≥85% on ground truth
- ✅ sample-pr-001 analysis succeeds with actionable feedback in <3 minutes

### Phase 4: RTL Extension (Future)

- ✅ RTL plugin implements DomainPlugin without framework changes
- ✅ RTL ground truth dataset (20+ examples)
- ✅ Technique transfer maintains ≥80% quality improvement
- ✅ Framework validated as domain-agnostic

### Overall Project Success

**RESEARCH SUCCESS (Primary)**:
- ✅ Successfully ranks 5+ LLM techniques by effectiveness with statistical evidence
- ✅ Quantifies improvements: "Technique X beats baseline by Y% (p<0.05)"
- ✅ Reproducible experiments (same config → same results)
- ✅ Documented findings suitable for publication/blog post

**PRODUCT SUCCESS (Secondary)**:
- ✅ Framework supports 2+ domains (C++, RTL)
- ✅ C++ plugin achieves quality goals (precision ≥75%, recall ≥85%)
- ✅ Token efficiency >0.5 issues/1K tokens
- ✅ Developer can build new plugin in <8 hours

**ARCHITECTURE SUCCESS (Validation)**:
- ✅ Plugin architecture validated (RTL plugin with zero framework changes)
- ✅ Technique modularity validated (A/B testing works)
- ✅ Evaluation framework validated (credible comparative analysis)

---

## Risk Mitigation

### Risk 1: Ground Truth Annotation Delays (HIGH PROBABILITY, HIGH IMPACT)

**Risk**: 20+ example annotation takes longer than 4-6 hours, blocks all experimentation.

**Mitigation**:
- Start annotation ASAP (during Phase 0 implementation)
- Use existing `test-data/cpp/sample-pr-001/` as first examples
- Lower initial bar: Accept imperfect annotations, refine iteratively
- Parallelize: Split annotation across multiple domain experts if available

**Contingency**: Start with 10 examples (enough for initial ranking), add more as experiments progress.

### Risk 2: Technique Rankings Unstable (MEDIUM PROBABILITY, HIGH IMPACT)

**Risk**: Running experiments multiple times yields different rankings (reproducibility failure).

**Mitigation**:
- Fix random seeds in LLM calls (temperature=0 or low temperature)
- Use deterministic model settings (no sampling randomness)
- Large enough dataset (20 examples minimum for statistical power)
- Multiple runs per technique, report variance

**Contingency**: If variance high (>10%), increase dataset size or use confidence intervals in ranking.

### Risk 3: Ollama Performance Too Slow (MEDIUM PROBABILITY, MEDIUM IMPACT)

**Risk**: deepseek-coder:33b too slow on laptop, experiments take hours instead of minutes.

**Mitigation**:
- Test early (Phase 0) - measure latency on sample examples
- Use smaller model for experiments (qwen2.5:14b) if needed
- Parallelize experiment execution (run multiple configs simultaneously)

**Contingency**: Accept slower turnaround (1-2 hours for matrix) or switch to faster model.

### Risk 4: Few-Shot Examples Don't Transfer Across Domains (LOW PROBABILITY, MEDIUM IMPACT)

**Risk**: Techniques optimized for C++ don't work for RTL (Phase 4 fails).

**Mitigation**:
- Phase 2 experiments specifically test technique sensitivity to example quality
- Document which techniques are example-dependent vs example-agnostic
- Plan for domain-specific example curation per plugin

**Contingency**: Expected finding - few-shot quality matters, framework still valuable for systematic optimization per domain.

### Risk 5: False Positive Rate Too High (MEDIUM PROBABILITY, MEDIUM IMPACT)

**Risk**: Even best technique has <75% precision, fails quality goal.

**Mitigation**:
- Multi-pass self-critique specifically targets false positive reduction
- Confidence scoring enables filtering low-confidence findings
- Iterative example refinement based on failure analysis

**Contingency**: Adjust precision goal or add human-in-the-loop filtering step.

---

## Out of Scope (Explicit Non-Goals)

1. **CI/CD Integration** - Users integrate via CLI, framework doesn't build GitHub Actions
2. **Web UI** - CLI only, users wrap with UI if needed
3. **Multi-user Deployment** - Single-user workstation deployment
4. **Cloud Deployment** - On-premise only, no cloud hosting
5. **RAG/Vector Database** - Unless Phase 2 experiments prove necessary (unlikely for PR diffs)
6. **Model Fine-tuning** - Use pre-trained Ollama models only
7. **Real-time Collaboration** - No concurrent analysis, no shared state
8. **Auto-fix Application** - Report issues only, no code modification
9. **IDE Integration** - No VS Code/IntelliJ plugins
10. **GitHub/GitLab API** - Users fetch PRs externally, framework analyzes provided content

---

## Next Steps After Planning

1. ✅ Review plan with stakeholders (ensure research focus aligned with goals)
2. ✅ Run `/speckit.tasks` to generate task breakdown (translate plan phases into actionable tasks)
3. ⏳ Phase 0 Day 1: Start ground truth annotation (critical path!)
4. ⏳ Phase 0 Day 1-2: Implement experimental infrastructure (MetricsCalculator, ExperimentRunner, PromptLogger)
5. ⏳ Phase 1 Day 3-7: Build framework core + techniques
6. ⏳ Phase 2 Day 8-12: **RUN EXPERIMENTS** - generate research value!

**The plan emphasizes that LLM engineering research (discovering what works) IS the product, not just building another code review tool.**
