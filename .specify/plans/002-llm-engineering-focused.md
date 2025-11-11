# Implementation Plan: LLM Engineering for Meaningful PR Reviews

**Branch**: `002-llm-engineering-focused` | **Date**: 2025-11-11
**Core Focus**: Transform long PRs into meaningful inputs AND produce high-quality, actionable outputs

## Summary

This project is NOT about building CI/CD pipelines or git integrations. It's about **LLM engineering excellence**: taking a potentially huge PR (500-2000 lines) and making an LLM produce genuinely useful code reviews despite token constraints. The challenge is two-fold:

1. **INPUT ENGINEERING**: How to compress/structure/chunk long PRs into inputs that LLMs can process effectively
2. **OUTPUT ENGINEERING**: How to prompt/guide/refine LLM outputs to be consistently useful and actionable

## The Core Challenge

**Problem**: A 500-line C++ PR with context might need 50K+ tokens. Local LLMs have 8K-32K context windows and quality degrades with long contexts.

**Solution Strategy**: Multiple LLM engineering techniques working together:

### Input Engineering Approaches

1. **Hierarchical Map-Reduce**
   - Map: Each file reviewed independently with focused prompts
   - Reduce: Aggregate individual file reviews into PR-level insights
   - Benefit: Parallelizable, stays within token limits per file

2. **Sliding Window with Synthesis**
   - Process PR in overlapping chunks (e.g., 200 lines with 50-line overlap)
   - Synthesize findings across chunks
   - Benefit: Catches issues spanning chunk boundaries

3. **Intelligent Chunking via AST**
   - Parse C++ into functions/classes (tree-sitter)
   - Review at function level, not arbitrary line chunks
   - Include semantic context (function signature, class definition)
   - Benefit: Semantically meaningful units, better LLM understanding

4. **Context Compression via RAG**
   - When reviewing function X, retrieve only relevant context (callees, base classes)
   - Don't send entire files, send extracted relevant snippets
   - Benefit: Maximum context relevance per token

5. **Summarization Cascade**
   - Pass 1: LLM summarizes each changed file in 100 tokens
   - Pass 2: Use summaries + detailed chunks for targeted review
   - Benefit: LLM has high-level mental model before detailed analysis

6. **Diff-Focused Prompting**
   - Only show changed lines + N lines context
   - Explicitly mark additions (+) and deletions (-)
   - Include "why changed" metadata (commit message, file summary)
   - Benefit: Focus LLM attention on what actually changed

### Output Engineering Approaches

1. **Structured Output with JSON Schema**
   - Force LLM to output valid JSON with schema: `{file, line, severity, category, issue, suggestion, reasoning}`
   - Validation and retry loop if malformed
   - Benefit: Parseable, consistent, machine-processable

2. **Few-Shot Learning with Expert Examples**
   - Provide 3-5 examples of excellent C++ reviews
   - Show desired format, depth, actionability
   - Include both positive examples and failure cases
   - Benefit: Dramatically improves consistency and quality

3. **Chain-of-Thought Prompting**
   - Instruct LLM to explain reasoning: "First, I notice... Then, I realize... Therefore, this is problematic because..."
   - Makes reasoning visible and improves accuracy
   - Benefit: Higher quality insights, explainable reviews

4. **Multi-Pass Refinement**
   - Pass 1: Generate initial review
   - Pass 2: LLM critiques its own review ("Are these issues real? Any false positives?")
   - Pass 3: Refined output
   - Benefit: Self-correction reduces false positives

5. **Multi-Agent Simulation**
   - Agent 1: Security expert (focus: memory safety, vulnerabilities)
   - Agent 2: Performance expert (focus: efficiency, algorithms)
   - Agent 3: Moderator (aggregates and prioritizes findings)
   - Benefit: Specialized, high-quality feedback per domain

6. **Iterative Refinement with Human Feedback (RLHF-lite)**
   - Log all reviews with quality ratings
   - Use feedback to refine prompts and examples over time
   - Benefit: Continuous improvement loop

## Technical Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    PR Input (500-2000 lines)                │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │  INPUT ENGINEERING     │
         │  ┌──────────────────┐  │
         │  │ AST Parser       │  │  Parse C++ into semantic units
         │  │ (tree-sitter)    │  │
         │  └────────┬─────────┘  │
         │           │            │
         │  ┌────────▼─────────┐  │
         │  │ Chunking         │  │  Split into reviewable units
         │  │ Strategy         │  │  (file/function/window)
         │  └────────┬─────────┘  │
         │           │            │
         │  ┌────────▼─────────┐  │
         │  │ Context          │  │  RAG: Retrieve relevant context
         │  │ Retrieval (RAG)  │  │  (optional, for better reviews)
         │  └────────┬─────────┘  │
         │           │            │
         │  ┌────────▼─────────┐  │
         │  │ Prompt           │  │  Build prompts with:
         │  │ Construction     │  │  - Few-shot examples
         │  └────────┬─────────┘  │  - Structured format
         └───────────┼────────────┘  - Chain-of-thought instructions
                     │                - Diff-focused context
                     │
                     ▼
         ┌────────────────────────┐
         │   LLM (Ollama)         │
         │   - deepseek-coder     │
         │   - qwen2.5            │
         │   - starcoder2         │
         └────────────┬───────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │  OUTPUT ENGINEERING    │
         │  ┌──────────────────┐  │
         │  │ JSON Schema      │  │  Validate output structure
         │  │ Validation       │  │
         │  └────────┬─────────┘  │
         │           │            │
         │  ┌────────▼─────────┐  │
         │  │ Self-Refinement  │  │  LLM critiques own output
         │  │ (optional)       │  │
         │  └────────┬─────────┘  │
         │           │            │
         │  ┌────────▼─────────┐  │
         │  │ Multi-Agent      │  │  Multiple specialized reviewers
         │  │ Aggregation      │  │  (optional)
         │  └────────┬─────────┘  │
         │           │            │
         │  ┌────────▼─────────┐  │
         │  │ Map-Reduce       │  │  Combine chunk-level reviews
         │  │ Synthesis        │  │  into PR-level insights
         │  └────────┬─────────┘  │
         └───────────┼────────────┘
                     │
                     ▼
         ┌────────────────────────┐
         │  Structured Review     │
         │  (JSON/Markdown)       │
         └────────────────────────┘
```

### Implementation Phases

---

## Phase 0: Experimentation & Baseline (Priority: CRITICAL)

**Goal**: Establish baseline and experiment with LLM engineering techniques

**Why First**: We need to understand what works before building infrastructure. This is research phase.

**Tasks**:
1. Create test dataset: 10 real C++ PRs with known issues (memory leaks, performance bugs, etc.)
2. Implement simple baseline: Send entire PR to LLM, measure quality
3. Experiment with chunking strategies:
   - Fixed line chunks (200 lines)
   - AST-based function chunks
   - File-based chunks
   - Measure: Review quality, token usage, processing time
4. Experiment with prompt formats:
   - Zero-shot vs few-shot (3 examples)
   - With/without chain-of-thought
   - With/without structured output schema
   - Measure: Output consistency, false positive rate
5. Test different Ollama models on same dataset:
   - deepseek-coder:33b-instruct
   - qwen2.5:14b
   - qwen2.5:72b
   - Measure: Quality vs speed tradeoff
6. Document findings in `.specify/research/llm-experiments.md`

**Deliverables**:
- Test dataset of 10 PRs with ground truth issues
- Experimental results comparing 3-5 approaches
- Recommended strategy based on data

**Success Metrics**:
- Identify approach with >70% precision on test dataset
- Find chunking strategy that stays under 8K tokens per chunk
- Select best model for quality/speed balance

---

## Phase 1: Input Engineering - Intelligent Chunking (Priority: P1)

**Goal**: Implement the winning chunking strategy from Phase 0 experiments

**Recommended Approach** (adjust based on Phase 0 results):
- AST-based function-level chunking with tree-sitter
- Include semantic context (function signature, related types)
- Fallback to line-based chunking if AST parsing fails

**Tasks**:
1. Integrate tree-sitter for C++ parsing
2. Implement AST-based code extraction:
   - Functions (name, signature, body, line range)
   - Classes (name, inheritance, members)
   - Include/import statements
3. Implement chunking strategy:
   - Chunk size: configurable (default: function-level)
   - Include context: N lines before/after, or related definitions
4. Implement diff-aware chunking:
   - Only chunk changed functions + their immediate context
   - Mark additions/deletions explicitly
5. Handle edge cases:
   - Macro-heavy code
   - Template specializations
   - Files with no clear function boundaries
6. Write unit tests for chunking logic with various C++ patterns
7. Measure token consumption per chunk on test dataset

**Deliverables**:
- Robust C++ code chunker that produces semantic units
- Token usage stays under 8K per chunk on 95% of real PRs
- Clear visualization of how PR is chunked

**Acceptance**:
- Chunking preserves semantic meaning (functions not split mid-body)
- Token budget is respected
- Edge cases handled gracefully

---

## Phase 2: Output Engineering - Structured Prompts & Few-Shot (Priority: P1)

**Goal**: Design prompts that consistently produce high-quality, parseable reviews

**Tasks**:
1. Design JSON output schema for reviews:
```json
{
  "reviews": [
    {
      "file": "path/to/file.cpp",
      "line": 42,
      "severity": "critical|warning|suggestion|info",
      "category": "memory-safety|performance|modern-cpp|security|concurrency|style",
      "issue": "Brief description of the problem",
      "reasoning": "Why this is problematic (chain-of-thought)",
      "suggestion": "Specific code fix or recommendation",
      "confidence": 0.0-1.0
    }
  ]
}
```

2. Create few-shot example library:
   - 5 examples of excellent C++ reviews (diverse issue types)
   - Show desired format, depth, actionability
   - Include reasoning chains
   - Store in `.specify/prompts/few-shot-examples.yaml`

3. Implement prompt template system (Jinja2):
   - System prompt: Role and guidelines
   - Few-shot examples: 3-5 selected based on review focus
   - User prompt: Code chunk + diff + context + instructions
   - Output format specification: JSON schema

4. Implement chain-of-thought prompting:
   - Instruct LLM to think step-by-step
   - Format: "Analysis: [reasoning] | Issue: [problem] | Suggestion: [fix]"

5. Implement output validation and retry:
   - Parse JSON, validate against schema
   - If malformed: retry with repair prompt
   - If repeated failures: fall back to markdown parsing

6. Test prompts on Phase 0 dataset, iterate to improve precision

**Deliverables**:
- Prompt template system with few-shot library
- JSON schema with validation
- Retry logic for robustness
- Documented prompt engineering best practices

**Acceptance**:
- >95% of LLM outputs are valid JSON on first attempt
- >70% precision (flagged issues are real problems)
- Reviews include actionable suggestions, not just "this is bad"

---

## Phase 3: Map-Reduce Review Architecture (Priority: P1)

**Goal**: Combine chunk-level reviews into coherent PR-level insights

**Tasks**:
1. Implement Map phase:
   - Review each chunk independently with focused prompts
   - Parallelize where possible (multiple Ollama requests)
   - Collect structured reviews per chunk

2. Implement Reduce phase:
   - Aggregate all chunk reviews
   - LLM synthesizes PR-level insights:
     - Common patterns across chunks
     - Severity prioritization
     - Actionable summary
   - Prompt: "Given these individual reviews, provide PR-level summary and prioritized action items"

3. Implement streaming output:
   - Show chunk-level reviews as they complete
   - Show synthesis at end
   - Rich CLI with progress bars

4. Handle failures gracefully:
   - If one chunk fails, continue with others
   - Mark failed chunks in final report

5. Optimize for token efficiency:
   - Map: Detailed reviews (high token budget per chunk)
   - Reduce: Summaries only (low token budget)

**Deliverables**:
- Working map-reduce pipeline
- Parallelized chunk processing
- Synthesis step that adds PR-level insights

**Acceptance**:
- Can review 1000-line PR in <5 minutes
- Synthesis adds value beyond individual chunk reviews
- Token usage is optimized (no redundancy)

---

## Phase 4: Context Retrieval (RAG) - Optional Enhancement (Priority: P2)

**Goal**: Provide LLM with relevant codebase context beyond the diff

**Tasks**:
1. Implement code indexing:
   - Parse codebase with tree-sitter
   - Extract functions, classes with signatures
   - Generate embeddings (Ollama nomic-embed-text or sentence-transformers)
   - Store in ChromaDB or FAISS

2. Implement context retrieval:
   - For each changed function, query vector DB for:
     - Functions it calls
     - Functions that call it
     - Base classes / derived classes
   - Limit: Top-k most relevant (k=5 default)

3. Integrate into prompt construction:
   - Add retrieved context as "Related Code" section
   - Keep within token budget (allocate 30% of budget to context)

4. Implement incremental indexing:
   - Index codebase once
   - Update only changed files on subsequent reviews

5. Measure impact:
   - Compare review quality with/without RAG
   - If improvement <10%, make this optional

**Deliverables**:
- RAG system integrated into review pipeline
- Incremental indexing for efficiency
- A/B testing shows RAG improves quality

**Acceptance**:
- RAG retrieval precision >80% (retrieved context is relevant)
- Review quality improves measurably with context
- Incremental updates complete in <30 seconds

---

## Phase 5: Advanced Output Engineering - Self-Refinement (Priority: P2)

**Goal**: LLM critiques and improves its own reviews to reduce false positives

**Tasks**:
1. Implement two-pass review:
   - Pass 1: Generate initial review (standard prompt)
   - Pass 2: Critique prompt:
     ```
     Review your own analysis. For each issue you flagged:
     1. Is this a real problem or false positive?
     2. Is your suggestion actually better?
     3. Are you making assumptions about intent?
     Output: Refined review with only high-confidence issues.
     ```

2. Implement confidence scoring:
   - Pass 1: All issues
   - Pass 2: Confidence scores (0.0-1.0)
   - Filter: Only show issues with confidence >0.6 (configurable)

3. Measure impact on test dataset:
   - Does self-refinement reduce false positives?
   - What's the token cost?
   - Is it worth it?

4. Make self-refinement optional (flag: `--refine`)

**Deliverables**:
- Two-pass refinement system
- Confidence scoring
- A/B test results

**Acceptance**:
- False positive rate reduced by >20% with refinement
- Precision >80% with refinement enabled
- Token cost justified by quality improvement

---

## Phase 6: Multi-Agent Architecture - Specialized Reviewers (Priority: P3)

**Goal**: Simulate multiple expert reviewers for diverse, high-quality feedback

**Tasks**:
1. Implement specialized reviewer agents:
   - Security Agent: Focus on memory safety, vulnerabilities
     - Prompt: "You are a security expert. Review for: buffer overflows, null dereferences, use-after-free..."
   - Performance Agent: Focus on efficiency
     - Prompt: "You are a performance engineer. Review for: unnecessary copies, algorithmic complexity, cache efficiency..."
   - Modernization Agent: Focus on C++ best practices
     - Prompt: "You are a modern C++ expert. Review for: use of smart pointers, range-for loops, constexpr..."

2. Implement moderator agent:
   - Collects reviews from all agents
   - Deduplicates similar findings
   - Prioritizes by severity and consensus
   - Synthesizes final report

3. Parallelize agent execution (all review same code simultaneously)

4. Measure impact:
   - Does multi-agent find more issues?
   - Is token cost justified?

5. Make multi-agent optional (flag: `--multi-agent`)

**Deliverables**:
- Three specialized reviewer agents
- Moderator aggregation logic
- Quality comparison with single-agent

**Acceptance**:
- Multi-agent finds >15% more critical issues than single-agent
- No significant increase in false positives
- Execution time <2x single-agent (due to parallelization)

---

## Phase 7: Evaluation Framework (Priority: P1)

**Goal**: Rigorous evaluation of LLM review quality

**Tasks**:
1. Expand test dataset to 50 PRs with:
   - Ground truth issues (labeled by human experts)
   - Severity labels
   - False positive examples

2. Implement evaluation metrics:
   - Precision: % of flagged issues that are real
   - Recall: % of real issues that are flagged
   - F1 score
   - Token efficiency: Issues per 1K tokens
   - Latency: Time to review PR

3. Implement A/B testing framework:
   - Compare different prompt strategies
   - Compare models
   - Compare chunking strategies
   - Statistical significance testing

4. Create leaderboard in `.specify/evaluation/results.md`:
   - Track metric improvements over time
   - Document which techniques work best

5. Implement feedback collection:
   - After each review, optionally rate quality (1-5 stars)
   - Log for future analysis

**Deliverables**:
- 50-PR test dataset with ground truth
- Automated evaluation pipeline
- A/B testing framework
- Results leaderboard

**Acceptance**:
- Can run evaluation on full dataset in <30 minutes
- Statistical significance testing for A/B comparisons
- Clear winner identified for production use

---

## Phase 8: CLI & User Experience (Priority: P2)

**Goal**: Polished CLI for daily use

**Tasks**:
1. Implement core commands:
   - `cpp-reviewer review` - Review current PR
   - `cpp-reviewer index` - Index codebase (for RAG)
   - `cpp-reviewer eval` - Run evaluation on test dataset
   - `cpp-reviewer config` - Show/edit configuration

2. Implement flags:
   - `--model deepseek-coder:33b` - Choose model
   - `--strategy map-reduce|sliding-window|ast-chunks` - Choose approach
   - `--refine` - Enable self-refinement
   - `--multi-agent` - Enable multi-agent
   - `--focus critical` - Only critical issues
   - `--format json|markdown` - Output format
   - `--token-budget 8000` - Token limit
   - `--verbose` - Show token usage and internals

3. Implement rich output:
   - Progress bars for long reviews
   - Color-coded severity levels
   - Token usage statistics
   - Streaming results as they arrive

4. Implement configuration file (`.cpp-reviewer.yml`):
```yaml
model: deepseek-coder:33b-instruct
strategy: ast-chunks
token_budget: 8000
focus: [memory-safety, security, performance]
enable_rag: true
enable_refinement: false
enable_multi_agent: false
few_shot_examples: 5
```

5. Write comprehensive help text and examples

**Deliverables**:
- Polished CLI with all features
- Rich terminal output
- Configuration system
- User documentation

**Acceptance**:
- User can review a PR with single command
- Helpful error messages for common issues
- Configuration is intuitive

---

## Success Criteria for Project

**MVP Definition** (Phases 0-3 complete):
- Can chunk large PRs intelligently (AST-based)
- Produces structured JSON reviews with >70% precision
- Map-reduce architecture handles 1000-line PRs
- Token usage optimized (<10K per PR on average)

**Production Ready** (Phases 0-7 complete):
- Evaluation framework proves >75% precision, >80% critical recall
- Multiple strategies available (user can choose based on use case)
- RAG and advanced techniques measurably improve quality
- Token efficiency >0.5 issues per 1K tokens

**Excellence** (All phases):
- Multi-agent finds >85% of critical issues
- Self-refinement reduces false positives to <20%
- Users rate reviews as "useful" >80% of time
- Tool is used daily by real developers

## Research Questions to Answer

1. **Chunking**: AST-based vs fixed-size vs sliding window - which wins?
2. **Context**: Does RAG improve quality enough to justify complexity?
3. **Refinement**: Is self-critique worth the token cost?
4. **Multi-Agent**: Do specialized agents outperform single generalist?
5. **Models**: Best model for C++ reviews - deepseek, qwen, starcoder2?
6. **Prompts**: Few-shot vs zero-shot - how many examples optimal?
7. **Synthesis**: Does map-reduce synthesis add value or just noise?

## LLM Engineering Best Practices (Learned from This Project)

Document these as we learn:
- Optimal few-shot example count
- Best JSON schema format for consistency
- Effective chain-of-thought templates
- Token allocation strategies (context vs output)
- Model temperature settings for code review
- Retry strategies for malformed outputs
- Chunking size vs quality tradeoffs

This becomes valuable knowledge for future LLM projects.
