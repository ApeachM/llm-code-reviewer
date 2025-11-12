<!--
=============================================================================
CONSTITUTION SYNC IMPACT REPORT
=============================================================================
Version: 1.0.0 → 2.0.0 (MAJOR version bump)
Date: 2025-11-11
Type: Architectural transformation - single-domain to multi-domain framework

BREAKING CHANGES:
- Project scope: "C++ LLM PR Reviewer" → "Extensible LLM Engineering Framework"
- Architecture: Monolithic C++ tool → Plugin-based multi-domain platform
- Domain support: C++ only → C++, RTL/Verilog, Power, Design methodology

Principle Changes:
✏️  Principle I: "Privacy-First, Local LLM Only" → "Privacy-First, Local LLM Only" (unchanged in concept, updated wording)
✏️  Principle II: "Git-Native Integration" → REMOVED (moved to plugin responsibility)
✏️  Principle III: "Token-Efficient, Context-Aware Review" → "LLM Engineering Excellence" (expanded scope)
✏️  Principle IV: "C++ Code Quality Focus" → "Domain-Agnostic Plugin Architecture" (complete redefinition)
➕ Principle V: "Data-Driven Evaluation Framework" (NEW - experimental rigor)
✏️  Principle VI: "Actionable, Structured Output" → "Token Efficiency & Context Management" (refocused)
✏️  Principle VII: "LLM Engineering Excellence" → MERGED into Principle III
➕ Principle VIII: "Production-Ready Engineering" (NEW - extensibility emphasis)

Removed Sections:
- Technical Requirements (moved to individual plugin specifications)
- Review Workflow (now plugin-specific, framework provides tools)

Added Sections:
- Plugin Architecture Requirements
- Domain Expansion Roadmap
- Evaluation Framework Requirements

Template Alignment Status:
✅ .specify/templates/plan-template.md - Constitution Check updated with v2.0.0 principles (lines 30-43)
⚠️  .specify/templates/spec-template.md - Generic template still valid, consider plugin-specific guidance section
⚠️  .specify/templates/tasks-template.md - Consider adding plugin development task phase examples

Follow-up Actions:
1. ✅ DONE: Update plan-template.md Constitution Check with new 6 principles
2. ⚠️  REQUIRED: Review all existing C++ code review specs - must be refactored as "C++ plugin" under new architecture
3. ⚠️  RECOMMENDED: Create plugin development templates/guidelines
4. ⚠️  REQUIRED: Update all active feature branches to align with v2.0.0 principles
5. ⚠️  REQUIRED: Define plugin interface contract (see Plugin Architecture Requirements section)
6. ⚠️  REQUIRED: Establish evaluation framework structure before any domain work begins

Migration Impact:
- All existing C++-specific features must be migrated to plugin architecture
- New plugin interface must be defined before any domain-specific work
- Existing constitution v1.0.0 features are incompatible with v2.0.0 architecture

Validation Results:
✅ No placeholder tokens remaining
✅ All dates in ISO format (YYYY-MM-DD)
✅ Principles are declarative and testable
✅ Version follows semantic versioning (MAJOR bump justified)
✅ All sections complete
=============================================================================
-->

# Extensible LLM Engineering Framework Constitution

## Core Principles

### I. Privacy-First, Local LLM Only
- All LLM inference MUST be performed using local models via Ollama
- No code, data, or analysis results shall be transmitted to external cloud services
- Supported models: Any Ollama-compatible models (deepseek-coder, qwen2.5, llama3, etc.)
- Model selection MUST be configurable per-domain and per-task
- Framework MUST operate fully on-premise without internet connectivity

**Rationale**: Enables use in security-sensitive environments (enterprise, defense, healthcare) where data privacy is non-negotiable.

### II. Domain-Agnostic Plugin Architecture
- Core framework MUST NOT contain domain-specific logic (C++, RTL, Power, etc.)
- All domain knowledge MUST be encapsulated in plugins
- Plugin interface MUST be well-defined, versioned, and stable
- Framework provides universal capabilities:
  - Few-shot prompt engineering with example management
  - Multi-pass review orchestration (initial → self-critique → refinement)
  - Chain-of-thought reasoning scaffolding
  - Structured output validation (JSON schemas)
  - Token budget management and monitoring
- Plugins provide domain-specific capabilities:
  - Expert examples (5-10 per category)
  - Code/artifact parsing and chunking strategies
  - Issue categories and severity definitions
  - Domain-specific validation rules
  - Output formatting preferences

**Rationale**: Enables rapid expansion to new domains (RTL, Power, Design) without core rewrites. Separates LLM engineering expertise from domain expertise.

### III. LLM Engineering Excellence
- Few-shot learning: 5-10 carefully curated expert examples per domain category
- Multi-pass review strategy:
  - Pass 1: Initial analysis with chain-of-thought reasoning
  - Pass 2: Self-critique to identify false positives and missed issues
  - Pass 3: Refinement incorporating critique feedback
- Chain-of-thought prompting for complex analysis requiring reasoning steps
- Structured JSON output with Pydantic schema validation
- Prompt versioning and A/B testing of prompt variations
- Temperature and sampling parameters tuned per domain and task type
- Few-shot example curation: high-quality over quantity

**Rationale**: Local LLMs require sophisticated prompting techniques to match cloud API quality. Multi-pass self-critique significantly improves precision.

### IV. Data-Driven Evaluation Framework
- Every LLM technique MUST be measured quantitatively
- Required metrics:
  - Precision: % of reported issues that are real problems
  - Recall: % of known issues detected (when ground truth available)
  - F1 Score: Harmonic mean of precision and recall
  - Token efficiency: Issues found per 1000 tokens consumed
  - Latency: Time to complete analysis
- A/B testing framework for comparing:
  - Prompt variations (few-shot examples, instruction wording)
  - Model selection (deepseek vs qwen vs llama)
  - Multi-pass strategies (2-pass vs 3-pass)
  - Temperature and sampling parameters
- Ground truth datasets per domain with known issues
- Automated evaluation runs on every prompt/technique change
- Results MUST be documented with conclusions (what works, what doesn't)

**Rationale**: "In LLM engineering, we trust data, not intuition." Prevents prompt degradation and enables continuous improvement.

### V. Token Efficiency & Context Management
- PRIMARY GOAL: Maximize insight per token consumed
- Smart context selection strategies:
  - Incremental analysis: Focus on changed/relevant sections only
  - RAG retrieval: Pull only related definitions, not entire codebase
  - Context compression: Summarize unchanged code, detail only changes
  - Adaptive context: More context for complex issues, minimal for simple ones
- Token budget allocation:
  - Critical analysis (safety, security): Unlimited tokens if needed
  - Performance analysis: Medium token budget
  - Style/readability: Minimal tokens (only if budget allows)
- Token monitoring and reporting per analysis
- Fallback strategies when token limits approached

**Rationale**: Local LLM context windows are limited (8k-32k typical). Better to deeply analyze 100 lines than superficially scan 1000.

### VI. Production-Ready Engineering
- Type safety: Pydantic models for all data structures
- Interface contracts: Plugins implement well-defined interfaces
- Extensibility: New domains via plugins, no core changes required
- Testability:
  - Unit tests for all core framework components
  - Integration tests per plugin with ground truth datasets
  - Contract tests for plugin interface compliance
- Maintainability:
  - Clear separation: framework vs plugin code
  - Versioned plugin API (semantic versioning)
  - Plugin discovery and loading mechanism
  - Configuration management per domain
- Error handling: Graceful degradation, clear error messages
- Documentation: API docs, plugin development guide, domain guides

**Rationale**: This is production infrastructure, not a research prototype. Poor engineering multiplies across all domains.

## Plugin Architecture Requirements

### Plugin Interface Contract

Each domain plugin MUST implement:

1. **Artifact Parser**: Extract analyzable units from domain artifacts
   - Input: File content or diff
   - Output: Structured units (functions, modules, blocks, etc.)

2. **Example Provider**: Supply few-shot examples for each issue category
   - 5-10 expert examples per category
   - Examples must include: code snippet, issue explanation, suggested fix
   - Examples versioned and A/B testable

3. **Prompt Builder**: Construct domain-specific prompts using framework templates
   - Insert domain examples into framework's few-shot template
   - Add domain-specific instructions
   - Respect token budgets

4. **Output Validator**: Validate LLM output against domain schema
   - Parse JSON output
   - Validate issue categories, severity levels, line numbers
   - Reject malformed or hallucinated outputs

5. **Issue Formatter**: Format issues for domain-specific tools
   - Human-readable reports
   - Tool-specific formats (GitHub comments, CI/CD integration, etc.)

### Plugin Registration

Plugins register with framework via:
- Plugin manifest: domain name, version, supported file types
- Entry point for plugin loading
- Configuration schema for domain-specific settings

### Core Framework Responsibilities

Framework provides to all plugins:
- Multi-pass orchestration
- Token budget tracking
- LLM client abstraction (Ollama integration)
- Evaluation framework and metrics collection
- A/B testing infrastructure
- Configuration management
- Logging and observability

## Domain Expansion Roadmap

### Phase 1: C++ Code Review (Validation)
**Goal**: Validate framework architecture with known domain

- Migrate existing C++ PR review logic to plugin
- Establish plugin interface patterns
- Build evaluation framework with C++ ground truth dataset
- Target metrics: Precision >80%, Recall >70%, <2min per 500 lines
- Success criteria: Match or exceed existing v1.0.0 C++ review quality

### Phase 2: RTL/Verilog Analysis (Extension)
**Goal**: Prove domain-agnostic architecture

- Develop RTL plugin (syntax checking, clock domain, FSM analysis)
- Reuse framework's multi-pass and few-shot infrastructure
- New evaluation dataset: RTL design issues
- Demonstrates: Framework adds value beyond C++ use case

### Phase 3: Power Optimization (High-Value Domain)
**Goal**: Enter premium domain with expert knowledge

- Power plugin: Clock gating, voltage scaling, power domain analysis
- High-value use case: Power optimization in chip design
- Demonstrates: Framework enables rapid entry to specialized domains

### Phase 4: Design Methodology Review (Premium Service)
**Goal**: Move beyond code to design/architecture review

- Design plugin: Architecture patterns, methodology compliance
- Premium use case: Design review automation
- Demonstrates: Framework handles non-code analysis

## Technical Requirements

### Technology Stack (Framework Core)
- **Language**: Python 3.11+ (type hints, dataclasses, match statements)
- **Type Safety**: Pydantic v2 for all data models
- **LLM Interface**: Ollama Python client with streaming support
- **Plugin System**: Entry points or dynamic loading
- **Testing**: pytest with fixtures for plugins
- **CLI**: Click or Typer for extensible commands
- **Configuration**: YAML/TOML with validation

### Performance Standards
- Plugin loading: <1 second
- Analysis initiation: <5 seconds
- Typical analysis (500 lines): <3 minutes (including multi-pass)
- Token efficiency: >0.5 issues per 1000 tokens
- Memory: <2GB RAM for framework + single plugin

### Deployment
- Installable via pip/uv with plugin extras: `pip install llm-framework[cpp,rtl]`
- Framework core has minimal dependencies
- Plugins can have domain-specific dependencies (tree-sitter, parsers)
- Docker image for on-premise deployment
- Configuration via `.llm-framework.yml` with plugin sections

## Evaluation Framework Requirements

### Ground Truth Datasets

Each domain plugin MUST provide:
- 20+ annotated examples with known issues
- Issue categories: Critical, High, Medium, Low severity
- Expected output for each example
- Regular updates as new patterns discovered

### Metrics Collection

Framework automatically tracks:
- Per-plugin metrics (precision, recall, F1)
- Per-technique metrics (few-shot vs zero-shot, 2-pass vs 3-pass)
- Token consumption per analysis
- Latency per pass and total
- Model performance comparison (deepseek vs qwen, etc.)

### A/B Testing Infrastructure

Enable experiments:
- Prompt variation testing (control vs treatment)
- Example set comparison (different few-shot examples)
- Model comparison (different Ollama models)
- Parameter tuning (temperature, top_p, top_k)
- Statistical significance testing (t-test, p-values)

### Reporting

Generate reports:
- Weekly metrics summary per domain
- Technique comparison reports
- Model performance benchmarks
- Token efficiency trends
- Recommendations for prompt/technique improvements

## Governance

### Development Standards
- All features MUST include unit tests (core) or integration tests (plugins)
- Plugin interface changes require RFC and review
- Breaking changes to plugin API require MAJOR version bump
- Documentation required: framework API, plugin development guide, domain guides
- Follow semantic versioning: MAJOR.MINOR.PATCH

### Amendment Procedure
- Constitution changes require:
  1. RFC document explaining rationale
  2. Impact analysis on existing plugins
  3. Migration path for breaking changes
  4. Review by framework maintainers
- Version bump rules:
  - MAJOR: Backward incompatible principle changes, plugin API breaks
  - MINOR: New principles, expanded guidance, new framework capabilities
  - PATCH: Clarifications, wording improvements, non-semantic fixes

### Quality Gates
- New plugins MUST achieve:
  - Precision >70% on ground truth dataset
  - Recall >60% on ground truth dataset
  - <5 minute analysis time for typical examples
  - Complete plugin interface implementation
- Framework changes MUST NOT regress existing plugin metrics

### Review Quality Principles
- **PRIMARY METRIC**: Precision (minimize false positives)
- Secondary metrics: Recall (catch critical issues), Token efficiency
- Philosophy: Better to miss low-priority issues than overwhelm with false positives
- Continuous improvement: Every false positive is a learning opportunity
- Transparency: Log all prompts, outputs, and metrics for analysis

**Version**: 2.0.0 | **Ratified**: 2025-11-11 | **Last Amended**: 2025-11-11
