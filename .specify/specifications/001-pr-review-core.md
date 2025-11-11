# Feature Specification: Core PR Review Engine

**Feature Branch**: `001-pr-review-core`
**Created**: 2025-11-11
**Status**: Draft
**Input**: User description: "C++ LLM-based PR code reviewer using local Ollama models"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - CLI-based PR Review (Priority: P1)

As a C++ developer, I want to run a code review on my PR from the command line so that I can get immediate feedback on my changes before pushing to remote.

**Why this priority**: This is the core MVP functionality. Without this, the tool provides no value. Everything else builds on top of this foundational capability.

**Independent Test**: Can be fully tested by running `cpp-reviewer review` in a git repository with uncommitted changes or a feature branch, and receiving a markdown report with review comments.

**Acceptance Scenarios**:

1. **Given** I'm on a feature branch with changes, **When** I run `cpp-reviewer review`, **Then** I receive a markdown report with line-specific review comments
2. **Given** I specify a base branch with `--base main`, **When** the tool runs, **Then** it compares my branch against main branch
3. **Given** my PR has 10 changed C++ files, **When** review completes, **Then** I see comments organized by file and severity level
4. **Given** the review finds memory safety issues, **When** I view the report, **Then** critical issues are highlighted and include suggested fixes
5. **Given** I'm in a directory without git, **When** I run the tool, **Then** I receive a clear error message explaining git repository is required

---

### User Story 2 - Model Selection and Configuration (Priority: P2)

As a developer, I want to choose which LLM model to use for review so that I can balance between review depth and speed.

**Why this priority**: Different models have different strengths. deepseek-coder may be better for in-depth analysis, while smaller models like starcoder2 are faster. Users need flexibility.

**Independent Test**: Can be tested by running `cpp-reviewer review --model deepseek-coder:33b-instruct` and verifying that specific model is used and review quality matches model capabilities.

**Acceptance Scenarios**:

1. **Given** I specify `--model deepseek-coder:33b-instruct`, **When** review runs, **Then** that specific model is used for analysis
2. **Given** I have a `.cpp-reviewer.yml` config file with `model: qwen2.5:14b`, **When** I run without `--model` flag, **Then** the configured model is used
3. **Given** I specify a model that doesn't exist in Ollama, **When** review starts, **Then** I receive a helpful error listing available models
4. **Given** no model is specified and no config exists, **When** review runs, **Then** a sensible default model (deepseek-coder:33b-instruct) is used

---

### User Story 3 - Multiple Output Formats (Priority: P2)

As a CI/CD engineer, I want review results in JSON format so that I can integrate the tool into our automated pipeline and fail builds on critical issues.

**Why this priority**: Essential for CI/CD integration. Without structured output, the tool is limited to manual use only.

**Independent Test**: Can be tested by running `cpp-reviewer review --format json` and receiving valid JSON output that can be parsed and validated against a schema.

**Acceptance Scenarios**:

1. **Given** I specify `--format json`, **When** review completes, **Then** I receive valid JSON with fields: files, comments, severity, line numbers
2. **Given** I specify `--format markdown`, **When** review completes, **Then** I receive a formatted markdown report suitable for GitHub comments
3. **Given** I pipe output to a file with `--output review.json`, **When** review completes, **Then** results are written to that file
4. **Given** JSON output contains critical issues, **When** I parse the JSON, **Then** I can extract all critical items and exit with non-zero code

---

### User Story 4 - Selective Review Focus (Priority: P3)

As a developer working on performance optimization, I want to enable only performance-related review categories so that I get focused feedback without noise.

**Why this priority**: Nice-to-have for focused reviews. Users can still get value from full reviews, but this improves signal-to-noise ratio for specific tasks.

**Independent Test**: Can be tested by running `cpp-reviewer review --focus performance,memory-safety` and verifying only those categories appear in output.

**Acceptance Scenarios**:

1. **Given** I specify `--focus memory-safety`, **When** review runs, **Then** only memory safety comments are included
2. **Given** I configure `focus: [performance, concurrency]` in config file, **When** review runs, **Then** only those two categories are analyzed
3. **Given** I specify `--exclude style`, **When** review runs, **Then** all categories except style are included
4. **Given** I specify an invalid category name, **When** tool starts, **Then** I receive an error with list of valid categories

---

### User Story 5 - GitHub/GitLab Integration (Priority: P3)

As a team lead, I want the tool to automatically post review comments to our GitHub PRs so that developers see feedback inline with their code.

**Why this priority**: Quality-of-life improvement. Manual copy-paste of reviews works but is tedious. This is nice-to-have after core functionality is solid.

**Independent Test**: Can be tested by running `cpp-reviewer review --github-pr 123` in a repository with GitHub remote, and verifying comments appear on the PR.

**Acceptance Scenarios**:

1. **Given** I specify `--github-pr 123` with valid GH token, **When** review completes, **Then** comments are posted to PR #123
2. **Given** I'm on a branch with an open PR, **When** I run with `--auto-detect-pr`, **Then** the tool finds and comments on the corresponding PR
3. **Given** I specify `--gitlab-mr 456`, **When** review completes, **Then** comments are posted to GitLab merge request #456
4. **Given** authentication fails, **When** tool tries to post comments, **Then** review still completes locally and error is clearly reported

---

### Edge Cases

- What happens when a PR contains only non-C++ files (e.g., markdown, JSON)? → Tool should skip review and notify user
- What happens when Ollama service is not running? → Tool should detect this early and provide clear error with instructions
- What happens with extremely large PRs (1000+ lines changed)? → Tool should chunk the review and show progress, or warn about timeout
- What happens when LLM returns malformed output? → Tool should have robust parsing with fallback to partial results
- What happens when git diff fails (detached HEAD, merge conflicts)? → Clear error messages with recovery suggestions
- What happens when multiple C++ standards are mixed in one PR? → Tool should detect and review according to each file's standard
- What happens when analyzing generated code (protobuf, third-party)? → Config option to exclude paths

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST detect git repository context and extract PR/branch diff information
- **FR-002**: System MUST filter changed files to include only C++ source files (.cpp, .hpp, .cc, .h, .cxx, .hxx)
- **FR-003**: System MUST interface with Ollama to send code and receive review feedback
- **FR-004**: System MUST parse git diffs and extract line-level context for reviews
- **FR-005**: System MUST categorize review comments into: memory-safety, modern-cpp, performance, style, security, concurrency
- **FR-006**: System MUST assign severity levels: critical, warning, suggestion, info
- **FR-007**: System MUST generate output in multiple formats: markdown, JSON, git-comment format
- **FR-008**: System MUST support model selection via CLI flag or config file
- **FR-009**: System MUST provide streaming output for long-running reviews
- **FR-010**: System MUST handle errors gracefully and provide actionable error messages
- **FR-011**: System MUST validate Ollama connectivity before starting review
- **FR-012**: System MUST support configuration via `.cpp-reviewer.yml` file
- **FR-013**: System MUST allow filtering review focus by categories
- **FR-014**: System MUST include suggested fixes in review comments where applicable
- **FR-015**: System MUST support GitHub and GitLab API integration for posting comments (optional feature)
- **FR-016**: System MUST timeout after configurable duration (default 10 minutes) to prevent hanging
- **FR-017**: System MUST log all LLM interactions for debugging and quality improvement

### Key Entities

- **Review**: Represents a single PR review session with metadata (timestamp, model used, file count, comment count)
- **Comment**: Individual review feedback with fields: file_path, line_number, category, severity, message, suggested_fix
- **Config**: User configuration with fields: model, focus_categories, exclude_patterns, output_format, timeout
- **GitContext**: Represents the git state with fields: base_branch, feature_branch, base_commit, head_commit, changed_files, diff
- **OllamaClient**: Interface to Ollama service with methods: list_models, generate_review, check_health

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Tool successfully reviews a PR with 100 lines of C++ changes in under 60 seconds using deepseek-coder:33b
- **SC-002**: Tool detects at least 80% of known memory safety issues in test suite
- **SC-003**: Tool produces valid JSON output that passes schema validation 100% of the time
- **SC-004**: Tool handles git repository errors gracefully without crashes or stack traces visible to users
- **SC-005**: Tool works offline without any external network calls (all processing local via Ollama)
- **SC-006**: Users can install and run their first review within 5 minutes of installation
- **SC-007**: Tool provides actionable error messages that allow users to self-resolve 90% of common issues
- **SC-008**: Review comments include file:line references that match git diff line numbers accurately
