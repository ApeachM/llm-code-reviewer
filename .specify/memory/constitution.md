<!--
=============================================================================
CONSTITUTION SYNC IMPACT REPORT
=============================================================================
Version: 1.0.0 → 1.0.0 (no version change - validation run)
Date: 2025-11-11
Type: Initial validation and sync check

Changes:
- No principle modifications
- No sections added or removed
- Constitution already complete with all concrete values

Template Alignment Status:
✅ .specify/templates/spec-template.md - Generic template, no updates needed
✅ .specify/templates/tasks-template.md - Generic template, no updates needed
✅ .specify/templates/plan-template.md - Constitution Check updated with concrete gates
    → Updated: plan-template.md lines 30-43 now enumerate all 6 core principles
    → Each principle has a checkbox for validation during feature planning

Follow-up Actions:
None - All templates synchronized with constitution v1.0.0

Validation Results:
✅ No placeholder tokens remaining in constitution
✅ All dates in ISO format (YYYY-MM-DD)
✅ Principles are declarative and testable
✅ Version follows semantic versioning
✅ All sections complete
=============================================================================
-->

# C++ LLM PR Reviewer Constitution

## Core Principles

### I. Privacy-First, Local LLM Only
- All code review analysis must be performed using local LLM models via Ollama
- No code or PR data shall be transmitted to external cloud services
- Supported models: deepseek-coder, starcoder2, qwen2.5, and other Ollama-compatible models
- Model selection should be configurable per-project or per-review

### II. Git-Native Integration
- Primary workflow: PR-based code review comparing feature branches to master/main
- Must extract and analyze git diffs between base commit and PR head
- Support both GitHub, GitLab, and plain git repository workflows
- Review output should be git-comment compatible (line-level feedback)

### III. Token-Efficient, Context-Aware Review
- PRIMARY GOAL: Generate meaningful, high-quality C++ reviews within token constraints
- Use RAG (Retrieval-Augmented Generation) to provide relevant context without full codebase
- Strategies for token efficiency:
  - Incremental review: Focus only on changed lines and immediate context
  - Smart context selection: Retrieve only relevant function/class definitions
  - Multi-pass review: Critical issues first, then detailed suggestions
  - Context compression: Summarize unchanged code, full detail on changes only
- Review quality over quantity: Better to deeply review 50 lines than superficially scan 500

### IV. C++ Code Quality Focus
- Specialized analysis for C++ code patterns, idioms, and best practices
- Review categories (prioritized for local LLM):
  - Memory safety (leaks, dangling pointers, RAII violations) - CRITICAL
  - Modern C++ standards compliance (C++11/14/17/20/23) - HIGH
  - Performance considerations (unnecessary copies, algorithmic complexity) - HIGH
  - Security vulnerabilities (buffer overflows, injection risks) - CRITICAL
  - Thread safety and concurrency issues - MEDIUM
  - Code style and readability - LOW (only if token budget allows)

### V. Actionable, Structured Output
- Review comments must be specific, line-referenced, and actionable
- Support multiple output formats:
  - Human-readable markdown reports
  - JSON for CI/CD integration
  - Git-compatible comment format
- Severity levels: critical, warning, suggestion, info
- Include code snippets and suggested fixes where applicable

### VI. LLM Engineering Excellence
- Prompt engineering for consistent, high-quality reviews
- Few-shot examples of good C++ reviews in prompts
- Chain-of-thought reasoning for complex issues
- Self-consistency: Multiple review passes with voting
- Configuration file (.cpp-reviewer.yml) for:
  - Model selection and parameters (temperature, top_p, etc.)
  - Review focus areas (enable/disable categories)
  - Token budget allocation strategy
  - RAG retrieval parameters (top_k, similarity threshold)

## Technical Requirements

### Performance Standards
- Review initiation: < 5 seconds
- Analysis of typical PR (< 500 lines changed): < 2 minutes
- Support streaming output for real-time feedback
- Efficient diff parsing and context extraction

### Technology Stack
- Language: Python 3.11+ (for rapid development and Ollama SDK integration)
- LLM Interface: Ollama Python client with streaming support
- RAG Components:
  - Vector Database: ChromaDB or FAISS (lightweight, embeddable)
  - Embeddings: sentence-transformers or Ollama embedding models (nomic-embed-text)
  - Code Parser: tree-sitter for C++ AST parsing and chunking
- Git Integration: GitPython or pygit2
- CLI Framework: Click or Typer
- Output Formatting: Rich for terminal, Jinja2 for templates
- Testing: pytest with git repository fixtures

### Deployment
- Installable via pip/uv as standalone tool
- Minimal dependencies for easy on-premise deployment
- Configuration via `.cpp-reviewer.yml` file
- Local vector DB storage (no external services required)

## Review Workflow

### Standard PR Review Process (RAG-Enhanced)
1. **Indexing Phase** (one-time or incremental):
   - Parse C++ codebase with tree-sitter to extract functions, classes, methods
   - Generate embeddings for each code entity
   - Store in vector database with metadata (file, line, dependencies)

2. **Review Phase** (per PR):
   - Detect PR context (branch, base commit, changed files)
   - Extract git diff with context lines
   - Filter for C++ files (.cpp, .hpp, .cc, .h, .cxx, .hxx)
   - For each changed function/class:
     - Retrieve relevant context from vector DB (related functions, base classes, callers)
     - Build token-efficient prompt with only essential context
     - Apply prompt compression techniques (summarize unchanged parts)
   - Submit to local LLM via Ollama with streaming
   - Parse and format LLM responses
   - Generate structured review output

3. **Multi-Pass Strategy** (for large PRs):
   - Pass 1: Critical issues only (memory safety, security)
   - Pass 2: Performance and modern C++ compliance
   - Pass 3: Style and suggestions (if token budget allows)

### Quality Gates
- Must handle large PRs gracefully (chunk processing)
- Timeout protection (max 10 minutes per review)
- Fallback to simpler models if primary model unavailable
- Clear error messages for configuration issues

## Governance

### Development Standards
- All features must include unit tests and integration tests
- Documentation required for public APIs and CLI commands
- Follow semantic versioning: MAJOR.MINOR.PATCH
- Breaking changes require migration guide

### Review Quality Principles
- **PRIMARY METRIC**: Review usefulness and actionability, not coverage
- False positives are acceptable; missed critical issues are not
- Transparency: log all LLM interactions and token usage for optimization
- Continuous improvement: collect feedback on review quality
- Measure success by:
  - Precision: % of flagged issues that are real problems
  - Critical recall: % of known critical issues detected
  - Token efficiency: Issues found per 1000 tokens used
  - Human satisfaction: Would developer read this review?

**Version**: 1.0.0 | **Ratified**: 2025-11-11 | **Last Amended**: 2025-11-11
