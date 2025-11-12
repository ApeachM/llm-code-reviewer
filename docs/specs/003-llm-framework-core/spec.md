# Feature Specification: Domain-Agnostic LLM Engineering Framework

**Feature Branch**: `003-llm-framework-core`
**Created**: 2025-11-11
**Status**: Draft
**Input**: Build a reusable framework that implements LLM engineering best practices (few-shot learning, multi-pass review, self-critique) in a domain-agnostic way.

**Core Value Proposition**: This is an **LLM engineering research and production platform** that discovers and documents which prompting techniques work best for code analysis. The framework's primary goal is to measure, compare, and optimize LLM techniques (few-shot learning, multi-pass review, chain-of-thought, self-critique) across multiple domains. Code analysis is the application; LLM engineering excellence is the product.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Framework Core & Plugin Interface (Priority: P1)

A developer wants to add support for a new code analysis domain (e.g., RTL verification, power optimization) without reimplementing LLM techniques from scratch. They should be able to focus purely on domain expertise while the framework handles few-shot prompting, multi-pass review, self-critique, and evaluation.

**Why this priority**: This is the foundational architecture that enables everything else. Without a clean plugin interface, the framework cannot be domain-agnostic.

**Independent Test**: Create a minimal "hello world" plugin that analyzes simple text files for TODO comments. If the plugin can successfully load, execute analysis using framework's multi-pass system, and produce structured output without writing any LLM orchestration code, the core interface is validated.

**Acceptance Scenarios**:

1. **Given** a developer has domain expertise (e.g., C++, RTL), **When** they implement the plugin interface (ArtifactParser, ExampleProvider, PromptBuilder, OutputValidator, IssueFormatter), **Then** they can analyze domain artifacts using framework's LLM techniques without writing prompt engineering code
2. **Given** a plugin is registered with the framework, **When** the user runs analysis on a domain file, **Then** the framework orchestrates multi-pass review (initial → self-critique → refinement) automatically with configurable few-shot examples and token budgets
3. **Given** multiple plugins are installed, **When** the user analyzes a file, **Then** the framework selects the correct plugin based on file extension or explicit domain flag

---

### User Story 2 - Experimental Platform for LLM Technique Optimization (Priority: P1)

An LLM researcher/engineer wants to systematically discover which prompting techniques (few-shot example quality, chain-of-thought variations, self-critique strategies, token allocation) produce the best results for code analysis. This is the **core value** of the framework: treating LLM techniques as first-class experimental variables.

**Why this priority**: This is the PRIMARY VALUE PROPOSITION. The framework exists to answer "which LLM techniques work best for code analysis?" Without systematic experimentation, we're just guessing. Research shows few-shot learning improves accuracy by +40% and self-critique reduces false positives by -20%, but optimal configurations are unknown. This user story enables discovery.

**Independent Test**: Configure 3 experiments: (A) 3-shot examples, (B) 5-shot examples, (C) 10-shot examples. Run all three on same C++ dataset (20 samples). System should report that 5-shot achieves highest F1 score, document token efficiency trade-offs, and make the winning configuration easy to adopt as default.

**Acceptance Scenarios**:

1. **Given** multiple few-shot example sets (3 vs 5 vs 10 examples), **When** the researcher runs A/B/C test, **Then** the framework executes all configurations on same dataset and reports which achieves best precision, recall, F1, and token efficiency
2. **Given** different prompt templates (with/without chain-of-thought, different critique strategies), **When** experiments run, **Then** the system measures effectiveness and statistical significance (t-test, p-values) of differences
3. **Given** experiment results logged over time, **When** the researcher analyzes trends, **Then** the system shows which techniques consistently perform best and documents learnings (e.g., "5-shot with explicit chain-of-thought: +35% precision, +2000 tokens cost")
4. **Given** a winning technique is identified, **When** the researcher updates configuration, **Then** future analyses use optimized technique by default, and the framework logs prompt effectiveness metrics per analysis

---

### User Story 3 - C++ Code Review Plugin (Pilot Domain) (Priority: P1)

A C++ developer wants to review pull requests locally using LLM without sending proprietary code to cloud APIs. They need actionable feedback on critical issues (memory safety, modern C++ compliance, security) with minimal false positives.

**Why this priority**: This is the pilot domain that validates the framework architecture. C++ is already scoped in constitution, making it the natural first plugin.

**Independent Test**: Run C++ plugin on a test PR containing known issues (memory leak, use-after-free, buffer overflow). Plugin should detect at least 3 of 4 critical issues with <20% false positive rate and complete analysis in under 3 minutes.

**Acceptance Scenarios**:

1. **Given** a C++ file with memory safety issues, **When** the user runs `llm-framework analyze --domain cpp file.cpp`, **Then** the system detects memory leaks, dangling pointers, and RAII violations with severity CRITICAL
2. **Given** a PR diff between feature branch and main, **When** the user runs `llm-framework analyze-pr --domain cpp`, **Then** the system extracts changed functions, retrieves relevant context, and produces line-referenced review comments
3. **Given** C++ code with no issues, **When** analysis runs, **Then** the system reports "No issues found" without false positives (validated via self-critique pass)
4. **Given** analysis completes, **When** the user views results, **Then** output includes: issue description, severity (critical/high/medium/low), file path, line number, code snippet, and suggested fix

---

### User Story 4 - Evaluation Framework for Technique Comparison (Priority: P1)

A framework developer wants to answer the fundamental question: **"Which LLM technique (few-shot count, multi-pass strategy, chain-of-thought style) works best for code analysis?"** They need to run controlled experiments comparing techniques on ground truth datasets and measure not just "did we find bugs" but "which approach finds bugs most effectively, efficiently, and consistently."

**Why this priority**: This framework's value is discovering and documenting what works. Without rigorous evaluation comparing techniques, we're just guessing. Evaluation enables data-driven optimization: "5-shot with explicit chain-of-thought gives +35% precision at +2000 token cost vs 3-shot baseline."

**Independent Test**: Create ground truth dataset with 20 annotated C++ examples. Run 3 experiments: (A) 3-shot examples, (B) 5-shot examples, (C) 5-shot + chain-of-thought. Framework should report that (C) achieves highest F1 but costs 30% more tokens, enabling informed trade-off decisions.

**Acceptance Scenarios**:

1. **Given** a ground truth dataset with labeled issues, **When** the user runs `llm-framework evaluate --domain cpp --dataset test-data/cpp-ground-truth --technique few_shot_5`, **Then** the system reports precision, recall, F1 score, token consumption, latency, AND per-category breakdowns (memory-safety precision, performance recall, etc.)
2. **Given** two different prompt configurations (control vs treatment), **When** the user runs `llm-framework compare --techniques few_shot_3,few_shot_5 --dataset test-data/cpp-ground-truth`, **Then** the system executes both on same dataset and reports comparative metrics with statistical significance (t-test, p-values), token cost differential, and recommendation ("5-shot: +12% F1, +1500 tokens, p<0.05 - RECOMMENDED")
3. **Given** evaluation completes, **When** results are saved, **Then** metrics are logged to structured format (JSON/CSV) with: timestamp, model, technique, prompt version, example set ID, all metrics, per-issue details, enabling longitudinal analysis
4. **Given** evaluation detects false positives, **When** the developer reviews results, **Then** each false positive is identified with: issue description, why it's false positive, which few-shot example may have caused it, confidence score, enabling example set improvement
5. **Given** multiple evaluation runs over time, **When** the developer views trends, **Then** the system visualizes technique evolution ("Week 1: 3-shot baseline F1=0.65, Week 2: 5-shot + CoT F1=0.82, Week 3: 5-shot + CoT + critique F1=0.89") proving continuous improvement

---

### User Story 5 - RTL Analysis Plugin (Extensibility Proof) (Priority: P2)

A hardware engineer wants to analyze Verilog/SystemVerilog code for design issues (clock domain crossings, latch inference, combinational loops) using the same framework that works for C++. This demonstrates the framework truly is domain-agnostic.

**Why this priority**: This validates the architecture's extensibility promise. If RTL plugin can be built without modifying core framework, the architecture succeeds.

**Independent Test**: Implement basic RTL plugin that detects clock domain crossing violations. If the plugin integrates without core framework changes and produces valid analysis using framework's multi-pass system, extensibility is proven.

**Acceptance Scenarios**:

1. **Given** a Verilog file with CDC issues, **When** the engineer runs `llm-framework analyze --domain rtl design.v`, **Then** the system detects clock domain crossings, missing synchronizers, and metastability risks
2. **Given** RTL-specific examples (5-10 per category), **When** the plugin constructs prompts, **Then** framework's few-shot template incorporates RTL examples without C++ contamination
3. **Given** RTL analysis completes, **When** results are formatted, **Then** output follows RTL tool conventions (module:line format, synthesis-relevant warnings)

---

### Edge Cases

- What happens when a file is too large to fit in LLM context window (>32k tokens)?
  → Framework chunks the file into analyzable units, processes each independently, then aggregates results
- How does system handle when self-critique pass contradicts initial analysis?
  → Refinement pass (Pass 3) arbitrates using higher confidence threshold; log discrepancies for review
- What if a plugin example set is poor quality (generic, not domain-specific)?
  → Evaluation metrics will show low precision/recall, alerting developer to improve examples
- What happens when Ollama service is unavailable?
  → Framework returns clear error: "LLM service unavailable. Ensure Ollama is running: `ollama serve`"
- How does framework handle malformed LLM output (invalid JSON, missing fields)?
  → OutputValidator rejects invalid outputs, framework retries once with stricter schema instructions, then logs failure

## Requirements *(mandatory)*

### Functional Requirements

#### Core Framework
- **FR-001**: System MUST provide plugin interface with 5 required components: ArtifactParser, ExampleProvider, PromptBuilder, OutputValidator, IssueFormatter
- **FR-002**: System MUST orchestrate multi-pass review: Pass 1 (initial analysis with chain-of-thought), Pass 2 (self-critique to identify false positives), Pass 3 (refinement incorporating critique). **Rationale**: Research shows multi-pass with self-critique reduces false positives by 20% compared to single-pass analysis
- **FR-003**: System MUST support few-shot learning by injecting plugin-provided examples into prompts (configurable 3-10 examples per issue category). **Rationale**: Few-shot prompting is the most effective technique, improving accuracy by 40% over zero-shot in code analysis tasks
- **FR-004**: System MUST communicate with local Ollama service for LLM inference (no cloud APIs)
- **FR-005**: System MUST track token consumption per analysis and per pass for efficiency monitoring
- **FR-006**: System MUST validate all LLM outputs against Pydantic schemas before accepting results. **Rationale**: Structured output forcing improves parsing success rate from 90% to 99%
- **FR-007**: System MUST support plugin discovery via entry points or explicit registration
- **FR-008**: System MUST load plugin configuration from `.llm-framework.yml` file with per-domain sections

#### Input Engineering (Token Optimization)
- **FR-026**: System MUST support configurable few-shot example sets with quality metrics tracking (which examples lead to best results per category)
- **FR-027**: System MUST implement diff-focused prompting that highlights only changed lines with BEFORE/AFTER context, minimizing irrelevant code. **Rationale**: Diff-focused prompting reduces token consumption by 50% while improving LLM focus on changes
- **FR-028**: System MUST provide token budget allocation strategy configurable per pass (e.g., 30% for context retrieval, 70% for analysis output)
- **FR-029**: System MUST log prompt effectiveness metrics per analysis (example set used, model, tokens consumed, issues found, quality scores) to enable iterative improvement

#### Output Engineering (Quality Optimization)
- **FR-030**: System MUST implement confidence scoring in self-critique pass where LLM rates each issue (0.0-1.0 confidence) to enable filtering uncertain findings
- **FR-031**: System MUST enforce chain-of-thought reasoning for complex issue categories (memory safety, concurrency) where LLM explains step-by-step analysis before conclusion. **Rationale**: Chain-of-thought improves complex bug detection by 30%
- **FR-032**: System MUST support quality metrics for few-shot examples (precision/recall per example, contribution to overall quality) to identify and replace poor examples

#### C++ Plugin (Pilot)
- **FR-009**: C++ plugin MUST parse C++ source files and diffs to extract functions, classes, and methods for analysis
- **FR-010**: C++ plugin MUST provide few-shot examples for categories: memory safety (CRITICAL), modern C++ compliance (HIGH), performance (HIGH), security (CRITICAL), concurrency (MEDIUM)
- **FR-011**: C++ plugin MUST validate LLM output includes: issue description, severity, file path, line number, code snippet, suggested fix
- **FR-012**: C++ plugin MUST format output as: human-readable markdown report, JSON for tool integration, git-comment format with line references
- **FR-013**: C++ plugin MUST support analysis of PR diffs (comparing feature branch to base branch)

#### Evaluation Framework (Technique Comparison Focus)
- **FR-014**: System MUST calculate comprehensive metrics for ground truth datasets: precision (% of reported issues that are real), recall (% of known issues detected), F1 score, AND per-category breakdowns (memory-safety precision, performance recall, etc.)
- **FR-015**: System MUST measure token efficiency (issues found per 1000 tokens consumed) and cost-effectiveness (quality improvement per additional token spent)
- **FR-016**: System MUST measure latency (time per pass, total analysis time) to enable quality-speed trade-off analysis
- **FR-017**: System MUST support A/B/C testing by running multiple technique configurations on same dataset and reporting comparative results with statistical significance (t-test, p-values, effect size)
- **FR-018**: System MUST log evaluation results to structured format (JSON/CSV) with: timestamp, model name, technique ID, prompt version, example set ID, all metrics, per-issue details (true positive/false positive/false negative classification)
- **FR-019**: System MUST identify and classify errors: false positives (with suspected cause: which example? which prompt phrase?), false negatives (which technique variant caught it?), enabling root cause analysis for improvement
- **FR-020**: System MUST support ground truth dataset format: input file/diff + expected issues (category, severity, line, reasoning) + metadata for reproducibility
- **FR-033**: System MUST generate technique comparison reports showing: baseline vs variants, token cost differential, statistical significance, recommendation ("Use 5-shot + CoT: +25% F1, +1500 tokens, p<0.01")
- **FR-034**: System MUST track technique evolution over time: plotting F1, precision, recall trends as prompts/examples are improved, demonstrating continuous improvement

#### Configuration & Extensibility
- **FR-021**: System MUST allow model selection per domain (e.g., deepseek-coder for C++, qwen2.5 for RTL)
- **FR-022**: System MUST allow temperature, top_p, top_k configuration per domain and per pass
- **FR-023**: System MUST support enabling/disabling review categories per analysis (e.g., skip style checks for quick review)
- **FR-024**: System MUST provide CLI with commands: analyze, analyze-pr, evaluate, test-plugin
- **FR-025**: System MUST handle errors gracefully: Ollama unavailable, invalid plugin, malformed config, LLM timeout

### Key Entities

- **Plugin**: Domain-specific module implementing the plugin interface (e.g., CppPlugin, RtlPlugin)
- **AnalysisRequest**: Input to analysis including file/diff content, domain, configuration overrides
- **Issue**: Single detected problem with attributes: description, severity, category, file_path, line_number, code_snippet, suggested_fix
- **AnalysisResult**: Collection of Issues plus metadata: token_count, latency, model_used, pass_results
- **GroundTruthExample**: Annotated example with input file and expected Issues for evaluation
- **EvaluationReport**: Metrics from evaluation including precision, recall, F1, token_efficiency, per-category breakdown
- **PromptTemplate**: Structured prompt with placeholders for domain examples, code, instructions
- **PassResult**: Output from a single pass (initial/critique/refinement) including Issues and reasoning

## Success Criteria *(mandatory)*

### Measurable Outcomes

#### LLM Engineering Excellence (Primary Value)
- **SC-001**: Framework documents which prompting techniques work best with quantitative evidence: "5-shot + chain-of-thought + self-critique achieves F1=0.85 vs 3-shot baseline F1=0.62 (p<0.01)"
- **SC-002**: Evaluation framework measures technique effectiveness across dimensions: precision ≥75%, recall ≥85% (CRITICAL issues), token efficiency ≥0.5 issues/1K tokens, latency <3min per 500 lines
- **SC-003**: A/B testing framework detects ≥10% quality improvement when comparing prompt variations (different few-shot examples, chain-of-thought styles, critique strategies) with statistical significance
- **SC-004**: System logs all prompt effectiveness data enabling continuous improvement: example set used, model, technique, tokens, quality scores, false positives identified
- **SC-005**: Confidence scoring from self-critique pass enables filtering: issues with confidence <0.7 can be optionally hidden, reducing false positive rate by ≥15%

#### Domain Extensibility (Architecture Validation)
- **SC-006**: Framework supports at least 2 domains (C++ and RTL) with separate plugins using same core LLM techniques
- **SC-007**: Developers can implement new plugin with <500 lines of domain-specific code (no LLM orchestration code required)
- **SC-008**: Technique transfer across domains works: techniques optimized for C++ maintain ≥80% of quality improvement when applied to RTL

#### Production Quality
- **SC-009**: Analysis of typical PR (<500 lines changed) completes in under 3 minutes on standard hardware (with multi-pass review)
- **SC-010**: System operates fully offline (no internet required once Ollama models downloaded)
- **SC-011**: Diff-focused prompting reduces token consumption by ≥40% compared to full-file analysis while maintaining quality
- **SC-012**: Documentation enables a domain expert with Python knowledge to build a new plugin in <8 hours

## Assumptions

1. **Ollama availability**: Users will have Ollama installed and running locally with at least one code model (deepseek-coder, qwen2.5-coder, or similar)
2. **Python environment**: Users have Python 3.11+ installed
3. **Ground truth creation**: Domain experts will manually annotate 20+ examples to create evaluation datasets
4. **Model capability**: Local LLMs (7B-34B parameters) are sufficient for meaningful code analysis with proper prompting
5. **Analysis scope**: Initial focus is on single-file or PR diff analysis, not whole-codebase analysis
6. **Plugin distribution**: Plugins will be distributed as part of the package initially; external plugin ecosystem is future work
7. **Configuration format**: YAML configuration is acceptable; no GUI configuration needed
8. **English language**: All analysis, prompts, and documentation in English initially
9. **Git integration**: Users will handle git operations (checkout, diff) externally; framework analyzes provided content
10. **Hardware**: Users have sufficient RAM (8GB+) and compute to run local LLM inference

## Out of Scope

The following are explicitly excluded from this feature:

- **CI/CD integration**: GitHub Actions, GitLab CI, Jenkins plugins (users will integrate via CLI)
- **Version control API integration**: Direct GitHub/GitLab API calls for PR fetching
- **Web UI or dashboard**: All interaction via CLI only
- **Multi-user deployment**: Single-user on-premise deployment only
- **Real-time collaboration**: No concurrent multi-user analysis
- **Cloud deployment**: On-premise only; no cloud hosting support
- **Model fine-tuning**: Use pre-trained Ollama models only; no custom training
- **RAG/vector database**: Initial version uses few-shot examples only; RAG is future enhancement
- **Cross-repository analysis**: Single repository context only
- **Automatic issue fix application**: Report issues only; no automated code modification
- **IDE integration**: No VS Code, IntelliJ, or other IDE plugins

## Dependencies

- **External**: Ollama service running locally with code-capable model installed
- **Internal**: Plugin interface must be defined before any domain plugins (C++, RTL) can be developed
- **Data**: Ground truth datasets must be created per domain to enable evaluation

## Constraints

- **Privacy**: All processing must occur locally; zero network calls to external APIs
- **Model support**: Must work with any Ollama-compatible model; no hard dependency on specific model
- **Token limits**: Must handle LLM context window limits (8k-32k typical) via chunking
- **Performance**: Multi-pass review increases latency 3x vs single-pass; acceptable trade-off for quality
- **Type safety**: All data structures must use Pydantic for runtime validation
