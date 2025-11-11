# Feature Specification: RAG-Enhanced Review Engine

**Feature Branch**: `002-rag-enhanced-review`
**Created**: 2025-11-11
**Status**: Draft
**Input**: User refinement: "Focus on meaningful reviews with RAG and LLM engineering, not CI/CD"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Token-Efficient Context Retrieval (Priority: P1)

As a developer reviewing a 500-line PR, I want the tool to intelligently select only relevant codebase context so that the LLM can provide deep, meaningful reviews without hitting token limits.

**Why this priority**: This is THE core differentiator. Without smart context selection, LLM reviews are either shallow (no context) or fail (context doesn't fit). This is the MVP.

**Independent Test**: Can be fully tested by indexing a C++ codebase, making a change to a function that calls other functions, and verifying that only the called functions (not the entire codebase) are included in the review context.

**Acceptance Scenarios**:

1. **Given** I change a function `processData()` that calls `validateInput()`, **When** review runs, **Then** `validateInput()` definition is retrieved from RAG, but unrelated functions are not
2. **Given** I modify a class method, **When** review runs, **Then** the base class definition and overridden virtual methods are included in context
3. **Given** a PR changes 10 functions across 5 files, **When** review runs, **Then** total context stays under 8K tokens using smart retrieval
4. **Given** I add a new function with no dependencies, **When** review runs, **Then** no additional context is retrieved (self-contained review)
5. **Given** vector DB is not initialized, **When** review runs, **Then** it falls back to git diff-only review with a warning

---

### User Story 2 - Incremental Codebase Indexing (Priority: P1)

As a developer, I want the tool to index my codebase once and update incrementally so that I don't waste time re-indexing on every review.

**Why this priority**: Indexing large C++ codebases can take minutes. Incremental updates make the tool practical for daily use.

**Independent Test**: Can be tested by running initial index, modifying a file, running incremental update, and verifying only changed files are re-indexed.

**Acceptance Scenarios**:

1. **Given** I run `cpp-reviewer index` on a fresh repo, **When** indexing completes, **Then** vector DB contains embeddings for all C++ functions/classes
2. **Given** I modify one file, **When** I run `cpp-reviewer index --incremental`, **Then** only that file is re-parsed and re-embedded
3. **Given** I switch git branches, **When** incremental index runs, **Then** deleted files are removed from vector DB
4. **Given** indexing is interrupted, **When** I restart, **Then** it resumes from last checkpoint without full re-index
5. **Given** I view index status with `cpp-reviewer index --status`, **Then** I see: total entities, last updated, vector DB size

---

### User Story 3 - Multi-Pass Review for Large PRs (Priority: P1)

As a developer with a 1000-line PR, I want the tool to review in multiple focused passes so that I get comprehensive feedback without overwhelming the LLM.

**Why this priority**: Single-pass reviews of large PRs produce shallow feedback. Multi-pass allows depth within token constraints.

**Independent Test**: Can be tested by submitting a large PR and verifying distinct review passes with different focus areas and that critical issues are reported first.

**Acceptance Scenarios**:

1. **Given** my PR has 1000 lines changed, **When** review runs, **Then** I see three passes: critical, performance, suggestions
2. **Given** pass 1 finds critical memory safety issues, **When** review completes, **Then** those issues are marked as blockers
3. **Given** I specify `--focus critical`, **When** review runs, **Then** only critical pass executes (faster, focused)
4. **Given** the first pass times out, **When** tool proceeds, **Then** it skips remaining passes but delivers partial results
5. **Given** token budget is tight, **When** multi-pass runs, **Then** token allocation is prioritized: 50% critical, 30% performance, 20% style

---

### User Story 4 - Prompt Engineering with Few-Shot Examples (Priority: P2)

As a tool maintainer, I want to provide high-quality C++ review examples in the prompt so that the LLM produces consistent, actionable feedback.

**Why this priority**: Essential for review quality, but can be refined after basic RAG pipeline works. Few-shot learning dramatically improves LLM output quality.

**Independent Test**: Can be tested by comparing review quality (precision, actionability) with and without few-shot examples using a test suite of known C++ issues.

**Acceptance Scenarios**:

1. **Given** I configure 5 few-shot examples in prompts, **When** LLM reviews code, **Then** output format matches example format (consistency)
2. **Given** examples show memory safety issues with fixes, **When** LLM finds similar issue, **Then** it provides a similar suggested fix
3. **Given** I add domain-specific examples (e.g., our codebase conventions), **When** review runs, **Then** feedback aligns with our conventions
4. **Given** I update few-shot examples, **When** next review runs, **Then** new examples are used without code changes (config-driven)

---

### User Story 5 - Token Usage Monitoring and Optimization (Priority: P2)

As a tool user, I want to see token usage statistics so that I can understand costs and optimize my review strategy.

**Why this priority**: Visibility into token usage enables optimization. Not critical for MVP but important for production use.

**Independent Test**: Can be tested by running a review and verifying accurate token counts are logged and displayed.

**Acceptance Scenarios**:

1. **Given** I run a review, **When** it completes, **Then** I see: total tokens used, tokens per file, context tokens vs output tokens
2. **Given** I view token usage with `--verbose`, **When** review runs, **Then** I see per-function breakdown of context size
3. **Given** I specify `--token-budget 4000`, **When** review runs, **Then** context retrieval is constrained to fit that budget
4. **Given** token usage is logged, **When** I analyze logs, **Then** I can identify files/functions consuming most tokens

---

### User Story 6 - Chain-of-Thought for Complex Issues (Priority: P3)

As a developer, I want the LLM to explain its reasoning for complex issues so that I understand why something is flagged.

**Why this priority**: Improves trust and learning, but not essential for MVP. Can be added after core review quality is proven.

**Independent Test**: Can be tested by enabling chain-of-thought prompting and verifying that complex issues include reasoning steps.

**Acceptance Scenarios**:

1. **Given** I enable `--explain` flag, **When** LLM finds complex issue, **Then** output includes step-by-step reasoning
2. **Given** LLM flags a subtle concurrency bug, **When** I view report, **Then** I see: "This is problematic because [reasoning chain]"
3. **Given** reasoning explains false assumptions, **When** I correct those assumptions in config, **Then** future reviews improve

---

### Edge Cases

- What happens when embeddings model is not available? → Fall back to keyword-based retrieval or diff-only review
- What happens when a function is called by 50+ other functions? → Limit retrieval to top-k most relevant callers
- What happens with template-heavy C++ code? → tree-sitter should handle, but may need special parsing rules
- What happens when git diff contains binary files or generated code? → Skip binary, optionally skip generated (config)
- What happens with circular dependencies in retrieval? → Deduplicate and limit recursion depth
- What happens when vector DB is corrupted? → Detect on startup, offer to rebuild index
- What happens with macro-heavy code that tree-sitter struggles to parse? → Graceful degradation to text-based chunking

## Requirements *(mandatory)*

### Functional Requirements - RAG System

- **FR-RAG-001**: System MUST parse C++ code using tree-sitter to extract functions, classes, methods, structs with metadata (file, line range, dependencies)
- **FR-RAG-002**: System MUST generate embeddings for code entities using local embedding model (nomic-embed-text via Ollama or sentence-transformers)
- **FR-RAG-003**: System MUST store embeddings in local vector database (ChromaDB or FAISS) with metadata indexing
- **FR-RAG-004**: System MUST support incremental index updates: only re-index changed files
- **FR-RAG-005**: System MUST retrieve relevant context for changed functions using semantic similarity search
- **FR-RAG-006**: System MUST limit retrieved context to fit within token budget (configurable, default 8K tokens)
- **FR-RAG-007**: System MUST deduplicate retrieved context (don't include same function twice)
- **FR-RAG-008**: System MUST support index management commands: init, update, status, rebuild
- **FR-RAG-009**: System MUST handle codebases up to 500K LOC efficiently (index in < 30 min)

### Functional Requirements - Token Optimization

- **FR-TOK-001**: System MUST implement prompt compression: summarize unchanged code, full detail on changes
- **FR-TOK-002**: System MUST support token budget allocation across multiple review passes
- **FR-TOK-003**: System MUST log token usage per request with breakdown (context, output, total)
- **FR-TOK-004**: System MUST support configurable token budget with automatic context trimming
- **FR-TOK-005**: System MUST prioritize critical context (changed code) over supplementary context (callees)
- **FR-TOK-006**: System MUST track token efficiency metrics: issues found per 1K tokens used

### Functional Requirements - LLM Engineering

- **FR-LLM-001**: System MUST support few-shot prompting with configurable examples
- **FR-LLM-002**: System MUST implement multi-pass review strategy (critical → performance → style)
- **FR-LLM-003**: System MUST support chain-of-thought prompting for complex issues (optional flag)
- **FR-LLM-004**: System MUST validate LLM output and retry with repaired prompt if malformed
- **FR-LLM-005**: System MUST support model parameter tuning (temperature, top_p, top_k) via config
- **FR-LLM-006**: System MUST implement streaming with incremental output parsing

### Functional Requirements - Core Review (retained from 001)

- **FR-CORE-001**: System MUST detect git repository context and extract diff
- **FR-CORE-002**: System MUST filter for C++ files and focus on changed lines
- **FR-CORE-003**: System MUST categorize comments: memory-safety, modern-cpp, performance, security, concurrency
- **FR-CORE-004**: System MUST assign severity: critical, warning, suggestion, info
- **FR-CORE-005**: System MUST output markdown and JSON formats
- **FR-CORE-006**: System MUST handle errors gracefully with actionable messages

### Key Entities

- **CodeEntity**: Represents a function, class, or method with fields: name, signature, body, file_path, line_start, line_end, embedding, dependencies
- **VectorIndex**: Manages vector DB with methods: add_entities, query_similar, update_entity, delete_entity, get_stats
- **PromptBuilder**: Constructs LLM prompts with fields: few_shot_examples, context_entities, changed_code, token_budget, current_tokens
- **ReviewPass**: Represents one review iteration with fields: pass_name, focus_categories, severity_threshold, token_budget, comments
- **TokenUsage**: Tracks token consumption with fields: context_tokens, output_tokens, total_tokens, entity_breakdown

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-RAG-001**: RAG retrieval reduces prompt size by 80% compared to including full files, while maintaining review quality
- **SC-RAG-002**: Incremental indexing completes in < 30 seconds for a 10-file change
- **SC-RAG-003**: Vector similarity retrieval returns relevant context with >90% precision (human-evaluated on test set)
- **SC-RAG-004**: Token usage stays under 8K per review for PRs with <500 lines changed

- **SC-LLM-001**: Few-shot prompting improves review precision by >30% compared to zero-shot (measured on test suite)
- **SC-LLM-002**: Multi-pass review finds 95% of known critical issues in pass 1 (critical focus)
- **SC-LLM-003**: Chain-of-thought explanations are present for >80% of complex issues (when --explain enabled)
- **SC-LLM-004**: LLM output parsing succeeds on first attempt >95% of the time (robust prompt engineering)

- **SC-QUAL-001**: Review comments have >70% precision (flagged issues are real problems, not false positives)
- **SC-QUAL-002**: Critical issue recall is >85% (finds most memory safety and security bugs in test suite)
- **SC-QUAL-003**: Token efficiency: > 0.5 actionable issues per 1000 tokens used
- **SC-QUAL-004**: Human satisfaction: >80% of reviews rated "useful" by test developers
