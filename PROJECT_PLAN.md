# Project Transformation Plan: Semantic PR Review Bot

**Version**: 1.0
**Last Updated**: 2026-01-03
**Status**: Phase 0 Complete, Phase 1 Ready to Start

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current State Analysis](#current-state-analysis)
3. [Problem Statement](#problem-statement)
4. [Target Architecture](#target-architecture)
5. [Category Strategy](#category-strategy)
6. [Implementation Phases](#implementation-phases)
7. [Timeline & Milestones](#timeline--milestones)
8. [Risk Assessment](#risk-assessment)
9. [Success Metrics](#success-metrics)
10. [Deployment Strategy](#deployment-strategy)
11. [Maintenance Plan](#maintenance-plan)
12. [Appendix](#appendix)

---

## Executive Summary

### Project Mission

Transform the existing LLM code analysis research platform into a **production-ready semantic PR review bot** that complements static/dynamic analysis by detecting **logic errors and intent mismatches** that automated tools cannot catch.

### Key Insight

The company already has comprehensive static and dynamic analysis pipelines:
- **AddressSanitizer/MemorySanitizer**: Memory errors
- **ThreadSanitizer**: Data races and concurrency issues
- **clang-tidy**: Style, modernization, performance
- **Valgrind**: Memory leaks and profiling

**Gap**: These tools cannot detect:
- Logic errors requiring semantic understanding (off-by-one errors)
- API misuse patterns in error paths
- Code behavior not matching documentation/naming
- Missing edge case handling
- Implementation not matching PR intent

**Solution**: LLM-powered review bot focused exclusively on semantic issues.

### Transformation Scope

- **Phase 0** (✅ Complete): Documentation and project rebranding
- **Phase 1** (🔄 Next): Category replacement and few-shot example rewrite
- **Phase 2** (⏳ Planned): Ground truth dataset rebuild
- **Phase 3** (⏳ Planned): CI/CD integration (GitLab CI/Jenkins)
- **Phase 4** (⏳ Planned): Production hardening and deployment

### Expected Outcomes

- **For Developers**: Catch semantic bugs before human review
- **For Reviewers**: Focus on architecture, not logic bugs
- **For Team**: Reduce review cycle time by 20-30%
- **For Quality**: Improve code correctness without adding review overhead

### Timeline

**Total Duration**: 8-12 days (2-3 weeks)
**Target Completion**: End of January 2026

---

## Current State Analysis

### Architecture Assessment

**Framework Core** (`framework/`):
- ✅ **Well-designed**: Modular, extensible, domain-agnostic
- ✅ **Technique library**: 6 techniques implemented and validated
- ✅ **Chunking support**: AST-based with parallel processing
- ✅ **Experiment infrastructure**: Comprehensive metrics and validation
- ✅ **Type safety**: Pydantic models throughout

**Rating**: 9/10 - Excellent foundation, minimal changes needed

**Domain Plugin** (`plugins/cpp_plugin.py`):
- ❌ **Wrong focus**: 5 categories overlap with static analysis
- ❌ **Wrong examples**: Few-shot examples show memory/performance issues
- ❌ **Wrong prompt**: System prompt focuses on detectable issues
- ✅ **Good structure**: Plugin interface is well-designed

**Rating**: 3/10 - Needs complete replacement of content (not structure)

**CLI** (`cli/main.py`):
- ✅ **Good commands**: `analyze file/dir/pr` cover main use cases
- ⚠️ **Missing flags**: No `--changed-lines-only` or PR context support
- ⚠️ **No API integration**: Cannot post results to GitLab/GitHub

**Rating**: 7/10 - Good base, needs Phase 3 enhancements

**Ground Truth Dataset** (`experiments/ground_truth/cpp/`):
- ❌ **Wrong issues**: 90% are static-analysis-detectable
- ❌ **Wrong distribution**: Heavily skewed to memory-safety (7/21 issues)
- ✅ **Good format**: JSON format is flexible and well-structured

**Rating**: 2/10 - Needs complete rebuild

### Code Quality Metrics

| Metric | Current State | Assessment |
|--------|---------------|------------|
| **Type Coverage** | ~95% (mypy strict mode) | ✅ Excellent |
| **Test Coverage** | 84 tests, phased integration | ✅ Good |
| **Code Formatting** | black + ruff configured | ✅ Excellent |
| **Documentation** | Comprehensive docs/ folder | ✅ Excellent |
| **Tech Debt** | Minimal, clean architecture | ✅ Excellent |

### Current Categories (❌ To Be Replaced)

| Category | Examples in Dataset | Overlap with Static Analysis | Keep? |
|----------|---------------------|----------------------------|-------|
| `memory-safety` | 7 | ❌ 100% (ASan, Valgrind) | ❌ Remove |
| `modern-cpp` | 5 | ⚠️ 80% (clang-tidy modernize-*) | ❌ Remove |
| `performance` | 3 | ❌ 100% (clang-tidy performance-*) | ❌ Remove |
| `security` | 3 | ⚠️ 60% (static analyzers) | ❌ Remove |
| `concurrency` | 3 | ❌ 100% (ThreadSanitizer) | ❌ Remove |

**Total**: 21 issues, ~90% detectable by existing tools

---

## Problem Statement

### The Core Problem

**Current system detects issues that existing tools already catch better, faster, and more accurately.**

### Evidence

1. **Speed Comparison**:
   - LLM analysis: 8-33 seconds per file
   - clang-tidy: <1 second per file
   - AddressSanitizer: Real-time during execution

2. **Accuracy Comparison**:
   - LLM F1 score: 0.615 (few-shot-5) for memory leaks
   - AddressSanitizer: 100% detection rate for memory leaks

3. **Cost Comparison**:
   - LLM: ~620 tokens per file × model cost
   - Static analysis: Free

### Why This Matters

- **Wasted compute**: Running LLM to detect what clang-tidy already found
- **False confidence**: Lower accuracy than static analysis
- **Missed opportunity**: LLMs excel at semantic understanding, not low-level bug detection
- **User confusion**: Developers ignore bot reports because static analysis already flagged them

### The Solution

**Shift focus to semantic issues that ONLY LLMs can detect.**

Requirements:
1. Issue must require understanding code **intent**
2. Issue must not be detectable by static/dynamic analysis
3. Issue must be actionable and clearly explained
4. Issue must be worth reviewing (not trivial)

---

## Target Architecture

### High-Level System Design

```
┌─────────────────────────────────────────────────────────────┐
│              Developer Creates/Updates PR                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│          GitLab CI / Jenkins (Self-Hosted)                  │
│  Trigger: On merge request events                           │
│  Actions:                                                    │
│    1. Checkout code (fetch PR metadata)                     │
│    2. Get changed files and PR description                  │
│    3. Run semantic-pr-reviewer CLI                          │
│    4. Post results to MR via API                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│             semantic-pr-reviewer CLI                        │
│  Command: analyze pr --changed-lines-only                   │
│          --pr-context-from-description                       │
│  Steps:                                                      │
│    1. Parse PR description for intended changes             │
│    2. Extract changed lines from git diff                   │
│    3. Pass context to ProductionAnalyzer                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│               ProductionAnalyzer                            │
│  Components:                                                 │
│    - CppPlugin (semantic categories + examples)             │
│    - FewShot5Technique (default)                            │
│    - FileChunker (for large files)                          │
│    - ResultMerger (deduplication)                           │
│  Output: AnalysisResult with semantic issues                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│            Ollama LLM (deepseek-coder:33b)                  │
│  Prompt includes:                                            │
│    - System prompt (semantic focus)                         │
│    - 5 few-shot examples (semantic errors)                  │
│    - PR context (description, intent)                       │
│    - Code to analyze (changed lines only)                   │
│  Output: JSON array of issues                               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              GitLab/GitHub API Client                       │
│  Actions:                                                    │
│    1. Format issues as inline comments                      │
│    2. Post comments to specific lines                       │
│    3. Add summary comment                                   │
│    4. Update existing bot comments (avoid spam)             │
└─────────────────────────────────────────────────────────────┘
```

### Key Architectural Decisions

#### Decision 1: Keep Framework, Replace Plugin Content

**Rationale**: Framework architecture (techniques, experiments, chunking) is excellent. Only plugin content (categories, examples, prompt) needs replacement.

**Impact**: Minimal code changes, maximum leverage of existing infrastructure.

#### Decision 2: Self-Hosted CI/CD (Not GitHub Actions)

**Rationale**: User specified self-hosted CI/CD (GitLab CI or Jenkins).

**Impact**: Need to implement webhook handling and API clients for GitLab.

#### Decision 3: Changed Lines Only (Not Full File)

**Rationale**: PR review should focus on what changed, not entire file.

**Impact**: Need to implement git diff parsing and line filtering.

#### Decision 4: PR Context Awareness

**Rationale**: To detect code-intent-mismatch, bot needs PR description.

**Impact**: Need to parse PR description and pass as context to LLM.

#### Decision 5: Preserve Experiment Infrastructure

**Rationale**: Technique validation is valuable for future improvements.

**Impact**: Keep experiments/ folder, run new experiments with semantic dataset.

---

## Category Strategy

### New Category Framework

All categories must meet these criteria:
1. ✅ **Not detectable by static analysis** (clang-tidy, cppcheck)
2. ✅ **Not detectable by dynamic analysis** (ASan, TSan, Valgrind)
3. ✅ **Requires semantic understanding** (intent, context, meaning)
4. ✅ **Actionable and clear** (developer can fix immediately)
5. ✅ **Worth reviewing** (not trivial style issues)

### Category 1: `logic-errors`

**Definition**: Errors in program logic that compile and run but produce wrong results.

**Characteristics**:
- Requires understanding loop invariants
- Requires understanding comparison semantics
- Requires understanding boundary conditions

**Examples**:

```cpp
// Example 1.1: Off-by-one error
std::vector<int> nums = {1, 2, 3, 4, 5};
for (int i = 0; i <= nums.size(); i++) {  // Bug: should be <
    process(nums[i]);
}
// Issue: Loop accesses nums[5] which is out of bounds

// Example 1.2: Wrong comparison operator
if (age != 18) {  // Bug: should be >=
    allow_voting();
}
// Issue: Only allows voting for exactly age 18, not 18+

// Example 1.3: Incorrect boolean logic
if (!is_valid || !has_permission) {  // Bug: should be &&
    grant_access();
}
// Issue: Grants access if EITHER check fails (opposite of intent)
```

**Why Static Analysis Misses This**:
- Code is syntactically correct
- May not violate any rules (no out-of-bounds access yet)
- Requires understanding **intent** (what should loop do?)

**Severity Distribution**:
- Critical: Results in crashes or data corruption
- High: Results in incorrect behavior in common cases
- Medium: Results in incorrect behavior in edge cases

### Category 2: `api-misuse`

**Definition**: Incorrect usage of APIs, libraries, or system calls that compiles but violates usage contracts.

**Characteristics**:
- Resource lifecycle violations (acquire without release)
- Wrong call ordering
- Missing required calls
- Parameter semantics violated

**Examples**:

```cpp
// Example 2.1: File not closed in error path
FILE* f = fopen("data.txt", "r");
if (!f) return -1;
if (validate(data)) {
    return -1;  // Bug: file not closed
}
fclose(f);
// Issue: Early return leaks file handle

// Example 2.2: Mutex not unlocked in error path
mutex.lock();
if (!process_data()) {
    return false;  // Bug: mutex not unlocked
}
mutex.unlock();
// Issue: Mutex remains locked, causing deadlock

// Example 2.3: Vector reallocation invalidates iterator
std::vector<int> nums = {1, 2, 3};
auto it = nums.begin();
nums.push_back(4);  // Bug: may reallocate, invalidating it
*it = 10;  // Use of invalidated iterator
// Issue: Undefined behavior after reallocation
```

**Why Static Analysis Misses This**:
- Control flow analysis is complex (many paths)
- Some analyzers detect some cases, but miss error paths
- Requires understanding **API contracts**

**Severity Distribution**:
- Critical: Resource leaks, deadlocks
- High: Common error paths affected
- Medium: Rare error paths affected

### Category 3: `semantic-inconsistency`

**Definition**: Code behavior doesn't match naming, documentation, or expectations.

**Characteristics**:
- Function does more/less than name implies
- Side effects contradicting function purpose
- Misleading variable/function names
- Behavior contradicting comments

**Examples**:

```cpp
// Example 3.1: Getter modifies state
int getTotalPrice() {
    discountApplied = true;  // Bug: getter shouldn't modify state
    return price * (1 - discount);
}
// Issue: Function named "get" has side effect

// Example 3.2: Variable name doesn't match content
int userCount = calculateTotalRevenue();  // Bug: name vs content
// Issue: Variable named "count" contains revenue

// Example 3.3: Function doesn't match comment
// Returns true if user is admin
bool checkAdminAccess() {
    return user.role == "moderator";  // Bug: checks moderator, not admin
}
// Issue: Comment says admin, code checks moderator
```

**Why Static Analysis Misses This**:
- Code is functionally correct
- Requires understanding **semantic meaning** of names
- Requires understanding **expected behavior**

**Severity Distribution**:
- Critical: Misleading behavior causes bugs elsewhere
- High: Violates principle of least surprise
- Medium: Confusing but still functional

### Category 4: `edge-case-handling`

**Definition**: Missing checks or handling for boundary conditions and edge cases.

**Characteristics**:
- No empty container checks
- No null/nullptr checks
- No integer overflow checks
- No division by zero checks
- Missing boundary condition validation

**Examples**:

```cpp
// Example 4.1: No empty vector check
std::vector<int> nums = getUserInput();
int first = nums[0];  // Bug: no empty check
int last = nums[nums.size() - 1];
// Issue: Crashes if vector is empty

// Example 4.2: No null check
Widget* widget = findWidget(id);
widget->activate();  // Bug: no null check
// Issue: Crashes if widget not found

// Example 4.3: Integer overflow not checked
int total = a + b + c;  // Bug: no overflow check
// Issue: Overflow causes wraparound to negative

// Example 4.4: Division by zero
double average = total / count;  // Bug: no zero check
// Issue: Division by zero if count is 0
```

**Why Static Analysis Misses This**:
- Some cases detected (e.g., null dereference)
- But many edge cases require **domain knowledge**
- Requires understanding **valid input ranges**

**Severity Distribution**:
- Critical: Crashes on common edge cases
- High: Crashes on rare but possible edge cases
- Medium: Incorrect behavior on edge cases

### Category 5: `code-intent-mismatch`

**Definition**: Implementation doesn't align with stated intent (PR description, requirements, commit message).

**Characteristics**:
- Requires PR description as context
- Compares code changes vs stated goals
- Checks for incomplete implementations
- Identifies unintended side effects

**Examples**:

```cpp
// PR Description: "Fix calculation to handle negative numbers correctly"

// Example 5.1: Incomplete fix
int calculateTotal(int value) {
    // Bug: Still doesn't handle negatives
    return value * 2;
}
// Issue: PR says "handle negatives" but no negative handling added

// Example 5.2: Wrong fix
int calculateTotal(int value) {
    int absValue = std::abs(value);  // Bug: PR didn't say use absolute
    return absValue * 2;
}
// Issue: Takes absolute value instead of handling negatives properly

// Example 5.3: Only renamed variable
int calculateTotal(int inputValue) {  // Bug: just renamed parameter
    return inputValue * 2;  // No logic change
}
// Issue: PR says "fix calculation" but only renamed variable
```

**Why Static Analysis Misses This**:
- Code may be syntactically and semantically correct
- Requires understanding **intended changes from PR description**
- Requires **comparing intent vs implementation**

**Severity Distribution**:
- Critical: Complete mismatch (wrong fix applied)
- High: Incomplete implementation (missing parts)
- Medium: Partially correct but not fully addressing intent

### Category Comparison Matrix

| Category | Requires Intent Understanding | Requires Code Understanding | Requires API Knowledge | Requires Domain Knowledge |
|----------|------------------------------|----------------------------|----------------------|--------------------------|
| `logic-errors` | ✅ High | ✅ High | ⚠️ Medium | ⚠️ Medium |
| `api-misuse` | ⚠️ Medium | ✅ High | ✅ High | ⚠️ Low |
| `semantic-inconsistency` | ✅ High | ✅ High | ⚠️ Low | ⚠️ Medium |
| `edge-case-handling` | ⚠️ Medium | ✅ High | ⚠️ Medium | ✅ High |
| `code-intent-mismatch` | ✅ Very High | ✅ High | ⚠️ Low | ⚠️ Low |

---

## Implementation Phases

### Phase 0: Documentation & Branding ✅ COMPLETE

**Duration**: 1 day
**Status**: ✅ Complete
**Git Tag**: `v0-baseline`

**Objectives**:
1. Preserve original research platform state
2. Rebrand project as semantic PR review bot
3. Update all documentation
4. Create transformation roadmap

**Completed Tasks**:
- ✅ Created `archive/research-platform` git tag
- ✅ Rewrote README.md with PR bot focus
- ✅ Updated CLAUDE.md with semantic categories
- ✅ Updated pyproject.toml metadata (name, version, description)
- ✅ Created MIGRATION.md (transformation guide)
- ✅ Created PROJECT_PLAN.md (this document)

**Deliverables**:
- [x] Git tag preserving original state
- [x] Updated README.md
- [x] Updated CLAUDE.md
- [x] Updated pyproject.toml
- [x] MIGRATION.md documentation
- [x] PROJECT_PLAN.md roadmap

**Validation**:
```bash
# Verify tag exists
git tag -l archive/research-platform

# Verify metadata updated
grep "semantic-pr-reviewer" pyproject.toml

# Verify docs exist
ls -l README.md CLAUDE.md MIGRATION.md PROJECT_PLAN.md
```

**Git Commit**:
```bash
git add .
git commit -m "docs: Phase 0 complete - project rebranding and documentation

- Rebrand from LLM research platform to semantic PR review bot
- Update README, CLAUDE.md with semantic focus
- Create MIGRATION.md and PROJECT_PLAN.md
- Update pyproject.toml metadata
- Preserve original state in archive/research-platform tag"

git tag -a v0-baseline -m "Phase 0 complete: Documentation and branding"
```

---

### Phase 1: Core Category Replacement 🔄 NEXT

**Duration**: 1-2 days
**Status**: 🔄 Ready to start
**Git Tag**: `v1.0-core-categories` (when complete)

**Objectives**:
1. Replace 5 old categories with 5 new semantic categories
2. Rewrite 5 few-shot examples with semantic errors
3. Rewrite system prompt to focus on complementing static analysis
4. Update category validation in models.py

**Tasks**:

#### Task 1.1: Update Category Validation

**File**: `framework/models.py` (lines 34-40)

**Current Code**:
```python
allowed = {'memory-safety', 'modern-cpp', 'performance', 'security', 'concurrency'}
```

**New Code**:
```python
allowed = {
    'logic-errors',
    'api-misuse',
    'semantic-inconsistency',
    'edge-case-handling',
    'code-intent-mismatch'
}
```

**Validation**:
```bash
# Test that new categories pass validation
python -c "from framework.models import Issue; print(Issue(category='logic-errors', severity='critical', line=1, description='test').category)"
```

#### Task 1.2: Update CppPlugin Categories

**File**: `plugins/cpp_plugin.py` (lines 34-41)

**Current Code**:
```python
@property
def categories(self) -> List[str]:
    return [
        'memory-safety',
        'modern-cpp',
        'performance',
        'security',
        'concurrency'
    ]
```

**New Code**:
```python
@property
def categories(self) -> List[str]:
    """
    Semantic-focused categories that complement static/dynamic analysis.

    These categories focus on issues that require understanding code intent
    and cannot be detected by existing tools (ASan, TSan, clang-tidy, Valgrind).
    """
    return [
        'logic-errors',           # Off-by-one, wrong operators, boolean logic
        'api-misuse',             # Wrong API usage, missing cleanup
        'semantic-inconsistency', # Code behavior vs naming/docs
        'edge-case-handling',     # Missing boundary checks
        'code-intent-mismatch'    # Code vs PR description
    ]
```

#### Task 1.3: Rewrite Few-Shot Examples

**File**: `plugins/cpp_plugin.py` (lines 43-129)

Replace all 5 examples with semantic error examples.

**Example 1: Logic Error (Off-by-one)**
```python
ex1 = {
    'id': 'semantic_001',
    'description': 'Off-by-one error in loop condition',
    'code': '''std::vector<int> numbers = {1, 2, 3, 4, 5};
int sum = 0;
for (int i = 0; i <= numbers.size(); i++) {
    sum += numbers[i];
}
return sum;''',
    'issues': [{
        'category': 'logic-errors',
        'severity': 'critical',
        'line': 3,
        'description': 'Off-by-one error: loop condition allows out-of-bounds access',
        'reasoning': 'Loop uses <= instead of <, causing access to numbers[5] when vector has 5 elements (indices 0-4). This will cause undefined behavior or crash. Should be i < numbers.size().',
        'suggested_fix': 'Change loop condition from "i <= numbers.size()" to "i < numbers.size()"'
    }]
}
```

**Example 2: API Misuse (Resource leak)**
```python
ex2 = {
    'id': 'semantic_002',
    'description': 'File handle not closed in error path',
    'code': '''FILE* f = fopen("data.txt", "r");
if (!f) {
    return -1;
}
if (!validate_data(f)) {
    return -1;  // Bug: file not closed
}
fclose(f);
return 0;''',
    'issues': [{
        'category': 'api-misuse',
        'severity': 'high',
        'line': 6,
        'description': 'File handle not closed in error path',
        'reasoning': 'fopen() on line 1 succeeds, but early return on line 6 skips fclose() on line 8. File handle leaks when validation fails. All return paths must close resources.',
        'suggested_fix': 'Add fclose(f) before line 6 return, or use RAII wrapper like std::unique_ptr with custom deleter'
    }]
}
```

**Example 3: Semantic Inconsistency**
```python
ex3 = {
    'id': 'semantic_003',
    'description': 'Function named "get" modifies state unexpectedly',
    'code': '''class ShoppingCart {
    int total_price = 0;
    bool discount_applied = false;

    int getTotalPrice() {
        discount_applied = true;  // Bug: getter shouldn't modify state
        return total_price * 0.9;
    }
};''',
    'issues': [{
        'category': 'semantic-inconsistency',
        'severity': 'medium',
        'line': 6,
        'description': 'Getter function has unexpected side effect',
        'reasoning': 'Function named getTotalPrice() implies a pure getter that just returns a value. However, it modifies discount_applied state on line 6. This violates the principle of least surprise and can cause hard-to-debug issues if called multiple times.',
        'suggested_fix': 'Rename to applyDiscountAndGetPrice() or split into two functions: applyDiscount() and getTotalPrice()'
    }]
}
```

**Example 4: Edge Case Handling**
```python
ex4 = {
    'id': 'semantic_004',
    'description': 'Missing empty container check before access',
    'code': '''std::vector<int> getUserScores() {
    return database.query("SELECT score FROM users");
}

void processScores() {
    auto scores = getUserScores();
    int highest = scores[0];  // Bug: no empty check
    int lowest = scores[scores.size() - 1];
    display(highest, lowest);
}''',
    'issues': [{
        'category': 'edge-case-handling',
        'severity': 'critical',
        'line': 7,
        'description': 'No check for empty vector before accessing elements',
        'reasoning': 'If getUserScores() returns empty vector (no users in database), accessing scores[0] and scores[size()-1] causes undefined behavior or crash. Must check !scores.empty() before access.',
        'suggested_fix': 'Add check: if (scores.empty()) { handle_error(); return; } before line 7'
    }]
}
```

**Example 5: Clean Code (Negative Example)**
```python
ex5 = {
    'id': 'semantic_005',
    'description': 'Clean code with proper edge case handling',
    'code': '''std::vector<int> getUserScores() {
    return database.query("SELECT score FROM users");
}

void processScores() {
    auto scores = getUserScores();
    if (scores.empty()) {
        std::cerr << "No scores found\\n";
        return;
    }
    int highest = scores[0];
    int lowest = scores[scores.size() - 1];
    display(highest, lowest);
}''',
    'issues': []  # No issues - properly handles empty case
}
```

#### Task 1.4: Rewrite System Prompt

**File**: `plugins/cpp_plugin.py` (lines 138-167)

**New Prompt**:
```python
def get_system_prompt(self) -> str:
    """Get system prompt emphasizing semantic analysis."""
    return """You are an expert C++ code reviewer focusing on SEMANTIC issues and LOGIC errors.

CONTEXT: Your company already has comprehensive static and dynamic analysis:
- AddressSanitizer/MemorySanitizer: Detects memory errors (leaks, use-after-free, buffer overflows)
- ThreadSanitizer: Detects data races and concurrency issues
- clang-tidy: Detects style issues, modernization opportunities, performance problems
- Valgrind: Detects memory leaks and profiling issues

YOUR ROLE: Detect issues that these tools CANNOT detect.

FOCUS ON these 5 categories:

1. logic-errors: Errors in program logic
   - Off-by-one errors in loops (<=  vs <)
   - Wrong comparison operators (< vs <=, == vs !=)
   - Incorrect boolean logic (!a || !b vs !a && !b)
   - Wrong loop iteration direction
   - Incorrect boundary conditions

2. api-misuse: Incorrect API usage patterns
   - Resource not released in error paths (fopen without fclose)
   - Mutex not unlocked in error paths
   - API calls in wrong order
   - Iterator invalidation after container modification
   - Wrong parameter order when types match but semantics differ

3. semantic-inconsistency: Code behavior doesn't match expectations
   - Function named "get" modifies state (side effects)
   - Variable name doesn't match content (userCount contains revenue)
   - Function behavior contradicts documentation
   - Misleading function/variable names

4. edge-case-handling: Missing checks for boundary conditions
   - No empty container check before access
   - No null/nullptr check before dereference
   - No integer overflow check
   - No division by zero check
   - Missing validation of input ranges

5. code-intent-mismatch: Code doesn't match stated intent
   - (Only applicable when PR description is provided)
   - Implementation doesn't match PR description
   - Incomplete fix (PR says "handle X" but code doesn't)
   - Wrong fix applied

DO NOT REPORT these (already caught by existing tools):
❌ Memory leaks (missing delete) → AddressSanitizer detects
❌ Use-after-free → AddressSanitizer detects
❌ Data races → ThreadSanitizer detects
❌ Buffer overflows → AddressSanitizer detects
❌ Performance issues (unnecessary copies) → clang-tidy detects
❌ Style issues (missing const) → clang-tidy detects

SEVERITY LEVELS:
- critical: Logic error causing crashes or wrong results
- high: Incorrect behavior in common scenarios
- medium: Edge cases not handled, misleading code
- low: Minor semantic improvements

OUTPUT FORMAT:
Respond with JSON array of issues. If no semantic issues found, return [].

Example:
[
  {
    "category": "logic-errors",
    "severity": "critical",
    "line": 23,
    "description": "Off-by-one error in loop condition",
    "reasoning": "Loop uses <= instead of <, causing access to array[size] which is out of bounds. Should be i < size.",
    "suggested_fix": "Change 'i <= size' to 'i < size'"
  }
]

Remember: Your value is in catching semantic issues that require understanding code INTENT. Don't duplicate what static analysis already does."""
```

#### Task 1.5: Update Tests

**Files**: Update tests that reference old categories

```bash
# Find tests referencing old categories
grep -r "memory-safety\|performance\|concurrency" tests/

# Update to use new categories
# This will likely affect:
# - tests/test_phase1_integration.py
# - tests/test_phase2_integration.py
```

**Validation**:
```bash
# Run tests after changes
pytest tests/ -v

# Verify new categories work
pytest tests/test_phase1_integration.py -v
```

**Deliverables**:
- [x] Updated `framework/models.py` category validation
- [x] Updated `plugins/cpp_plugin.py` categories property
- [x] 5 new few-shot examples with semantic errors
- [x] New system prompt focusing on complementing static analysis
- [x] Updated tests to use new categories
- [x] Manual validation with sample files

**Git Commit**:
```bash
git add framework/models.py plugins/cpp_plugin.py tests/
git commit -m "feat: Phase 1 complete - replace categories with semantic focus

Categories changed:
- Removed: memory-safety, performance, concurrency, security, modern-cpp
- Added: logic-errors, api-misuse, semantic-inconsistency,
         edge-case-handling, code-intent-mismatch

Few-shot examples:
- Replaced all 5 examples with semantic error demonstrations
- Focus on issues static/dynamic analysis cannot detect

System prompt:
- Explicitly states existing tool coverage (ASan, TSan, clang-tidy)
- Emphasizes complementing, not duplicating existing analysis
- Provides clear category definitions and DO NOT REPORT list

Tests:
- Updated to use new categories
- All phased integration tests passing"

git tag -a v1.0-core-categories -m "Phase 1 complete: Core categories replaced"
```

---

### Phase 2: Ground Truth Dataset Rebuild ⏳ PLANNED

**Duration**: 2-3 days
**Status**: ⏳ Pending Phase 1 completion
**Git Tag**: `v1.0-dataset-ready` (when complete)

**Objectives**:
1. Archive old ground truth dataset
2. Create 20 new annotated examples with semantic errors
3. Ensure balanced distribution across categories
4. Run experiments to validate F1 scores
5. Compare old vs new technique performance

**Tasks**:

#### Task 2.1: Archive Old Dataset

```bash
# Move old dataset to archive
mkdir -p experiments/ground_truth/cpp.old
mv experiments/ground_truth/cpp/*.json experiments/ground_truth/cpp.old/

# Document what was archived
echo "# Old Ground Truth Dataset (Research Platform)

This dataset contains 20 C++ examples focused on memory safety, performance,
and concurrency issues. It was used for research phase (Phases 0-5).

These issues are now detected by existing static/dynamic analysis tools:
- AddressSanitizer: memory-safety issues
- ThreadSanitizer: concurrency issues
- clang-tidy: performance and modernization

**Preserved for**: Historical reference and research comparison
**Not used for**: Production bot validation

See MIGRATION.md for details." > experiments/ground_truth/cpp.old/README.md
```

#### Task 2.2: Design New Dataset

**Requirements**:
- 20 total examples
- 4 examples per category (balanced distribution)
- Each example has 1 clear semantic issue
- Mix of severity levels (critical, high, medium)
- Real-world scenarios (not toy examples)
- Diverse code patterns

**Category Distribution**:
- `logic-errors`: 4 examples
  - Off-by-one in loop
  - Wrong comparison operator
  - Incorrect boolean logic
  - Wrong boundary condition

- `api-misuse`: 4 examples
  - File not closed in error path
  - Mutex not unlocked in error path
  - Iterator invalidation
  - Resource leak in exception path

- `semantic-inconsistency`: 4 examples
  - Getter with side effects
  - Variable name vs content mismatch
  - Function name vs behavior mismatch
  - Comment vs code contradiction

- `edge-case-handling`: 4 examples
  - No empty container check
  - No null pointer check
  - No integer overflow check
  - No division by zero check

- `code-intent-mismatch`: 4 examples
  - Incomplete implementation
  - Wrong fix applied
  - Only renamed variable (no logic change)
  - Side effect not mentioned in PR description

#### Task 2.3: Create Examples

**File Format** (JSON, same as before):
```json
{
  "id": "semantic_logic_001",
  "description": "Off-by-one error in array iteration",
  "code": "int calculate_sum(const std::vector<int>& numbers) {\n    int sum = 0;\n    for (size_t i = 0; i <= numbers.size(); i++) {\n        sum += numbers[i];\n    }\n    return sum;\n}",
  "file_path": "src/calculator.cpp",
  "expected_issues": [
    {
      "category": "logic-errors",
      "severity": "critical",
      "line": 3,
      "description": "Off-by-one error: loop condition allows out-of-bounds access",
      "reasoning": "Loop uses <= instead of <, allowing i to equal numbers.size(). This accesses numbers[size] which is out of bounds. Valid indices are 0 to size-1."
    }
  ]
}
```

**Create 20 files**:
- `experiments/ground_truth/cpp/semantic_logic_001.json` (off-by-one)
- `experiments/ground_truth/cpp/semantic_logic_002.json` (wrong operator)
- `experiments/ground_truth/cpp/semantic_logic_003.json` (boolean logic)
- `experiments/ground_truth/cpp/semantic_logic_004.json` (boundary condition)
- `experiments/ground_truth/cpp/semantic_api_001.json` (file leak)
- `experiments/ground_truth/cpp/semantic_api_002.json` (mutex leak)
- `experiments/ground_truth/cpp/semantic_api_003.json` (iterator invalidation)
- `experiments/ground_truth/cpp/semantic_api_004.json` (exception safety)
- `experiments/ground_truth/cpp/semantic_inconsistent_001.json` (getter side effect)
- ... (continue for all 20)

#### Task 2.4: Run Experiments

**Create new experiment configs**:

```yaml
# experiments/configs/semantic_few_shot_5.yml
experiment_id: semantic_few_shot_5
technique_name: few_shot_5
model_name: deepseek-coder:33b-instruct
dataset_path: experiments/ground_truth/cpp
seed: 42
```

**Run experiments**:
```bash
# Run all techniques on new dataset
python -m cli.main experiment run --config experiments/configs/semantic_few_shot_5.yml
python -m cli.main experiment run --config experiments/configs/semantic_hybrid.yml
python -m cli.main experiment run --config experiments/configs/semantic_chain_of_thought.yml

# View results
python -m cli.main experiment leaderboard
```

**Expected Results** (to be measured):
- F1 scores may be lower initially (0.5-0.6 range)
- Semantic issues are harder to detect than clear-cut memory leaks
- But these issues CANNOT be detected by any other tool

#### Task 2.5: Document Dataset

**File**: `experiments/ground_truth/cpp/DATASET_README.md`

```markdown
# Semantic Error Ground Truth Dataset

**Version**: 2.0 (Semantic Focus)
**Created**: 2026-01-03
**Total Examples**: 20
**Purpose**: Validate semantic PR review bot

## Overview

This dataset contains 20 annotated C++ examples focused on **semantic errors**
that cannot be detected by static or dynamic analysis tools.

**Key Principle**: Every issue in this dataset requires understanding code INTENT.

## Category Distribution

| Category | Count | Avg Severity | Example Issues |
|----------|-------|--------------|----------------|
| logic-errors | 4 | Critical | Off-by-one, wrong operators |
| api-misuse | 4 | High-Critical | Missing cleanup in error paths |
| semantic-inconsistency | 4 | Medium-High | Getter with side effects |
| edge-case-handling | 4 | Critical | No empty container checks |
| code-intent-mismatch | 4 | High | Incomplete implementation |

## Design Principles

1. **Real-world scenarios**: Not toy examples, based on actual bugs
2. **Clear intent**: Each example has obvious intended behavior
3. **Single issue**: One clear semantic error per example
4. **Actionable**: Developer can fix immediately
5. **Negative examples**: Include 3 clean code examples

## Validation Criteria

For each example, we verify:
- ✅ Issue is NOT detectable by AddressSanitizer
- ✅ Issue is NOT detectable by ThreadSanitizer
- ✅ Issue is NOT detectable by clang-tidy (tested with all checks)
- ✅ Issue requires understanding code intent
- ✅ Issue is clearly explained in reasoning field

## Comparison with Old Dataset

| Aspect | Old Dataset (v1.0) | New Dataset (v2.0) |
|--------|-------------------|-------------------|
| **Focus** | Memory/performance/concurrency | Semantic/logic errors |
| **Overlap with tools** | ~90% | ~5% |
| **Examples** | 20 | 20 |
| **Categories** | 5 (tool-detectable) | 5 (semantic) |
| **Avg F1 Score** | 0.615 | TBD (expected 0.5-0.6) |

## Usage

```bash
# Run experiment on this dataset
python -m cli.main experiment run --config experiments/configs/semantic_few_shot_5.yml

# View all examples
ls experiments/ground_truth/cpp/semantic_*.json

# Validate dataset format
python -c "from framework.models import GroundTruthExample; import json;
files = Path('experiments/ground_truth/cpp').glob('semantic_*.json');
[GroundTruthExample(**json.load(open(f))) for f in files]"
```

## Maintenance

When adding new examples:
1. Verify not detectable by static/dynamic analysis
2. Include clear reasoning and suggested fix
3. Test with all techniques
4. Update this README with new count
```

**Deliverables**:
- [x] Old dataset archived to `experiments/ground_truth/cpp.old/`
- [x] 20 new semantic error examples created
- [x] Balanced distribution across 5 categories
- [x] Experiment results for all techniques
- [x] Dataset documentation (DATASET_README.md)
- [x] Comparison report (old vs new F1 scores)

**Validation**:
```bash
# Verify 20 new examples
ls experiments/ground_truth/cpp/semantic_*.json | wc -l  # Should be 20

# Verify format
python -c "from framework.models import GroundTruthExample; import json; from pathlib import Path;
files = Path('experiments/ground_truth/cpp').glob('semantic_*.json');
examples = [GroundTruthExample(**json.load(open(f))) for f in files];
print(f'Loaded {len(examples)} examples successfully')"

# Run experiments
pytest tests/test_phase1_integration.py -v
pytest tests/test_phase2_integration.py -v
```

**Git Commit**:
```bash
git add experiments/ground_truth/cpp/
git commit -m "data: Phase 2 complete - semantic error ground truth dataset

New dataset:
- 20 examples focused on semantic errors
- Balanced across 5 categories (4 each)
- All issues require intent understanding
- ~5% overlap with static analysis (vs 90% old dataset)

Old dataset:
- Archived to experiments/ground_truth/cpp.old/
- Preserved for historical reference

Experiments:
- Ran all techniques on new dataset
- F1 scores: [to be filled after experiments]
- See DATASET_README.md for details"

git tag -a v1.0-dataset-ready -m "Phase 2 complete: Ground truth dataset rebuilt"
```

---

### Phase 3: CI/CD Integration ⏳ PLANNED

**Duration**: 3-4 days
**Status**: ⏳ Pending Phase 2 completion
**Git Tag**: `v1.0-cicd-integration` (when complete)

**Objectives**:
1. Create GitLab CI pipeline configuration
2. Implement GitLab API client for posting comments
3. Add `--changed-lines-only` flag to CLI
4. Add PR context awareness (read PR description)
5. Implement inline comment posting (line-level)
6. Add comment management (update existing comments)

**Tasks**:

#### Task 3.1: Create GitLab CI Pipeline

**File**: `.gitlab-ci.yml`

```yaml
# Semantic PR Review Bot - GitLab CI Pipeline

stages:
  - review

variables:
  OLLAMA_HOST: "http://ollama-server:11434"  # Self-hosted Ollama
  MODEL_NAME: "deepseek-coder:33b-instruct"

semantic-review:
  stage: review
  image: python:3.11-slim

  # Only run on merge requests
  only:
    - merge_requests

  before_script:
    # Install dependencies
    - apt-get update && apt-get install -y git curl
    - pip install -e .

  script:
    # Get MR metadata
    - export MR_TITLE="$(curl --header "PRIVATE-TOKEN: $GITLAB_TOKEN" "$CI_API_V4_URL/projects/$CI_PROJECT_ID/merge_requests/$CI_MERGE_REQUEST_IID" | jq -r '.title')"
    - export MR_DESCRIPTION="$(curl --header "PRIVATE-TOKEN: $GITLAB_TOKEN" "$CI_API_V4_URL/projects/$CI_PROJECT_ID/merge_requests/$CI_MERGE_REQUEST_IID" | jq -r '.description')"

    # Run semantic analysis
    - |
      python -m cli.main analyze pr \
        --base $CI_MERGE_REQUEST_TARGET_BRANCH_NAME \
        --head $CI_MERGE_REQUEST_SOURCE_BRANCH_NAME \
        --changed-lines-only \
        --pr-description "$MR_DESCRIPTION" \
        --model $MODEL_NAME \
        --output review.json \
        --format json

    # Post results to MR
    - python integrations/gitlab_poster.py --mr-iid $CI_MERGE_REQUEST_IID --results review.json

  artifacts:
    paths:
      - review.json
    expire_in: 7 days

  allow_failure: true  # Don't block MR if bot fails
```

#### Task 3.2: Implement GitLab API Client

**File**: `integrations/gitlab_client.py` (NEW)

```python
"""GitLab API client for posting review comments."""

import os
from typing import List, Dict, Optional
import requests
from framework.models import Issue

class GitLabClient:
    """Client for interacting with GitLab API."""

    def __init__(self, token: Optional[str] = None, base_url: Optional[str] = None):
        self.token = token or os.getenv('GITLAB_TOKEN')
        self.base_url = base_url or os.getenv('CI_API_V4_URL')
        self.project_id = os.getenv('CI_PROJECT_ID')

        if not all([self.token, self.base_url, self.project_id]):
            raise ValueError("Missing GitLab credentials")

        self.headers = {
            'PRIVATE-TOKEN': self.token,
            'Content-Type': 'application/json'
        }

    def post_mr_note(self, mr_iid: int, body: str) -> Dict:
        """Post a note (comment) to merge request."""
        url = f"{self.base_url}/projects/{self.project_id}/merge_requests/{mr_iid}/notes"
        response = requests.post(url, headers=self.headers, json={'body': body})
        response.raise_for_status()
        return response.json()

    def post_discussion(
        self,
        mr_iid: int,
        body: str,
        position: Dict
    ) -> Dict:
        """Post inline comment on specific line."""
        url = f"{self.base_url}/projects/{self.project_id}/merge_requests/{mr_iid}/discussions"
        data = {
            'body': body,
            'position': position
        }
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def get_mr_discussions(self, mr_iid: int) -> List[Dict]:
        """Get all discussions (comments) on MR."""
        url = f"{self.base_url}/projects/{self.project_id}/merge_requests/{mr_iid}/discussions"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def update_discussion_note(
        self,
        mr_iid: int,
        discussion_id: str,
        note_id: int,
        body: str
    ) -> Dict:
        """Update existing discussion note."""
        url = f"{self.base_url}/projects/{self.project_id}/merge_requests/{mr_iid}/discussions/{discussion_id}/notes/{note_id}"
        response = requests.put(url, headers=self.headers, json={'body': body})
        response.raise_for_status()
        return response.json()

    def format_issues_as_comment(self, issues: List[Issue]) -> str:
        """Format issues as markdown comment."""
        if not issues:
            return """## 🤖 Semantic Code Review

✅ No semantic issues detected!

Your code looks good from a semantic perspective. The bot checked for:
- Logic errors (off-by-one, wrong operators)
- API misuse (missing cleanup)
- Semantic inconsistencies
- Edge case handling
- Intent mismatch with PR description

---
*This review complements static analysis (ASan, TSan, clang-tidy). Memory, performance, and concurrency issues are caught by those tools.*"""

        # Group by category
        by_category = {}
        for issue in issues:
            by_category.setdefault(issue.category, []).append(issue)

        # Build comment
        lines = [
            "## 🤖 Semantic Code Review",
            "",
            f"Found **{len(issues)} issue(s)** requiring attention:",
            ""
        ]

        # Summary
        lines.append("### Summary")
        for category, cat_issues in sorted(by_category.items()):
            lines.append(f"- **{category}**: {len(cat_issues)}")
        lines.append("")

        # Detailed issues
        lines.append("### Detailed Findings")
        for issue in issues:
            severity_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵"}
            emoji = severity_emoji.get(issue.severity, "⚪")

            lines.extend([
                f"#### {emoji} Line {issue.line} | `{issue.category}` | {issue.severity.title()}",
                "",
                f"**Issue**: {issue.description}",
                "",
                f"**Why this matters**: {issue.reasoning}",
                ""
            ])

            if issue.suggested_fix:
                lines.extend([
                    f"**Suggested fix**: {issue.suggested_fix}",
                    ""
                ])

            lines.append("---")
            lines.append("")

        lines.extend([
            "*This review focuses on semantic issues. Memory safety, performance, and concurrency are covered by your existing analysis pipeline (ASan, TSan, clang-tidy).*"
        ])

        return "\n".join(lines)
```

**File**: `integrations/gitlab_poster.py` (NEW)

```python
"""Script to post review results to GitLab MR."""

import sys
import json
import argparse
from pathlib import Path
from gitlab_client import GitLabClient
from framework.models import AnalysisResult, Issue

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mr-iid', type=int, required=True)
    parser.add_argument('--results', type=Path, required=True)
    parser.add_argument('--inline', action='store_true', help='Post inline comments')
    args = parser.parse_args()

    # Load results
    with open(args.results) as f:
        results = json.load(f)

    # Parse into Issue objects
    issues = [Issue(**issue_data) for issue_data in results.get('issues', [])]

    # Create GitLab client
    client = GitLabClient()

    # Check for existing bot comments
    discussions = client.get_mr_discussions(args.mr_iid)
    bot_discussions = [
        d for d in discussions
        if d['notes'][0]['body'].startswith('## 🤖 Semantic Code Review')
    ]

    # Format comment
    comment = client.format_issues_as_comment(issues)

    # Update existing comment or create new
    if bot_discussions:
        discussion = bot_discussions[0]
        note = discussion['notes'][0]
        client.update_discussion_note(
            args.mr_iid,
            discussion['id'],
            note['id'],
            comment
        )
        print(f"Updated existing comment in discussion {discussion['id']}")
    else:
        client.post_mr_note(args.mr_iid, comment)
        print(f"Posted new comment to MR !{args.mr_iid}")

    # Post inline comments if requested
    if args.inline:
        # TODO: Implement inline comment posting with position data
        pass

if __name__ == '__main__':
    main()
```

#### Task 3.3: Add `--changed-lines-only` Flag

**File**: `cli/main.py` (modify analyze pr command)

```python
@cli.command('pr')
@click.option('--base', default='main', help='Base branch')
@click.option('--head', default='HEAD', help='Head branch')
@click.option('--changed-lines-only', is_flag=True, help='Only analyze changed lines')
@click.option('--pr-description', default='', help='PR description for context')
@click.option('--model', '-m', default='deepseek-coder:33b-instruct')
@click.option('--output', '-o', type=click.Path())
@click.option('--format', type=click.Choice(['markdown', 'json']), default='markdown')
def analyze_pr(base, head, changed_lines_only, pr_description, model, output, format):
    """Analyze pull request changes."""
    # ... implementation
```

#### Task 3.4: Implement Changed Lines Filtering

**File**: `plugins/production_analyzer.py` (add method)

```python
def get_changed_lines(self, file_path: Path, base: str, head: str) -> Set[int]:
    """Get line numbers that changed in file."""
    import subprocess

    # Run git diff to get changed lines
    cmd = [
        'git', 'diff',
        f'{base}...{head}',
        '--unified=0',  # No context lines
        '--', str(file_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    # Parse diff output for line numbers
    changed_lines = set()
    for line in result.stdout.split('\n'):
        if line.startswith('@@'):
            # Parse @@ -old_start,old_count +new_start,new_count @@
            parts = line.split('@@')[1].strip().split()
            new_range = parts[1]  # +new_start,new_count
            if ',' in new_range:
                start, count = new_range[1:].split(',')
                for i in range(int(start), int(start) + int(count)):
                    changed_lines.add(i)
            else:
                changed_lines.add(int(new_range[1:]))

    return changed_lines

def filter_issues_by_changed_lines(
    self,
    issues: List[Issue],
    changed_lines: Set[int]
) -> List[Issue]:
    """Filter issues to only those on changed lines."""
    return [issue for issue in issues if issue.line in changed_lines]
```

**Deliverables**:
- [x] `.gitlab-ci.yml` pipeline configuration
- [x] `integrations/gitlab_client.py` API client
- [x] `integrations/gitlab_poster.py` posting script
- [x] `--changed-lines-only` flag implementation
- [x] Changed lines filtering logic
- [x] PR description context passing
- [x] Comment management (update vs create)
- [x] Integration test with real GitLab instance

**Validation**:
```bash
# Test GitLab client locally
python -c "from integrations.gitlab_client import GitLabClient;
client = GitLabClient();
print('GitLab client initialized')"

# Test with mock MR
GITLAB_TOKEN=test MR_IID=1 python integrations/gitlab_poster.py --mr-iid 1 --results test_results.json

# Test changed lines detection
python -c "from plugins.production_analyzer import ProductionAnalyzer;
analyzer = ProductionAnalyzer();
lines = analyzer.get_changed_lines(Path('test.cpp'), 'main', 'feature');
print(f'Changed lines: {lines}')"
```

**Git Commit**:
```bash
git add .gitlab-ci.yml integrations/ cli/ plugins/
git commit -m "feat: Phase 3 complete - CI/CD integration

GitLab CI:
- Created .gitlab-ci.yml pipeline
- Triggers on merge request events
- Fetches MR metadata (title, description)
- Runs analysis on changed lines only
- Posts results as MR comments

API Integration:
- GitLabClient for API interaction
- Post/update MR notes (comments)
- Inline comment support (line-level)
- Comment management (update existing)

CLI Enhancements:
- --changed-lines-only flag
- --pr-description flag for context
- --format json option
- Changed lines filtering

Tests:
- Integration tests with mock GitLab API
- E2E test with real MR"

git tag -a v1.0-cicd-integration -m "Phase 3 complete: CI/CD integration"
```

---

### Phase 4: Production Hardening ⏳ PLANNED

**Duration**: 2-3 days
**Status**: ⏳ Pending Phase 3 completion
**Git Tag**: `v1.0-production` (when complete)

**Objectives**:
1. Add comprehensive error handling
2. Implement retry logic for LLM timeouts
3. Add monitoring and logging
4. Optimize performance (caching, batching)
5. Create deployment guide
6. Add health check endpoint

**Tasks**:

#### Task 4.1: Error Handling

**File**: `framework/ollama_client.py` (enhance)

```python
import time
from tenacity import retry, stop_after_attempt, wait_exponential

class OllamaClient:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def generate(self, prompt: str, model: str, **kwargs) -> Dict:
        """Generate with retry logic."""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={'model': model, 'prompt': prompt, **kwargs},
                timeout=120  # 2 minute timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.Timeout:
            logger.error(f"Ollama timeout for model {model}")
            raise
        except requests.RequestException as e:
            logger.error(f"Ollama request failed: {e}")
            raise
```

#### Task 4.2: Monitoring & Logging

**File**: `framework/monitor.py` (NEW)

```python
"""Monitoring and metrics collection."""

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List
from datetime import datetime

@dataclass
class AnalysisMetrics:
    """Metrics for a single analysis run."""
    file_path: str
    technique: str
    model: str
    latency: float
    tokens_used: int
    issues_found: int
    timestamp: datetime = field(default_factory=datetime.now)
    error: Optional[str] = None

class MetricsCollector:
    """Collect and report analysis metrics."""

    def __init__(self):
        self.metrics: List[AnalysisMetrics] = []
        self.logger = logging.getLogger(__name__)

    def record(self, metrics: AnalysisMetrics):
        """Record analysis metrics."""
        self.metrics.append(metrics)
        self.logger.info(
            f"Analysis complete: {metrics.file_path} | "
            f"{metrics.latency:.2f}s | "
            f"{metrics.issues_found} issues | "
            f"{metrics.tokens_used} tokens"
        )

    def get_summary(self) -> Dict:
        """Get summary statistics."""
        if not self.metrics:
            return {}

        return {
            'total_analyses': len(self.metrics),
            'avg_latency': sum(m.latency for m in self.metrics) / len(self.metrics),
            'total_tokens': sum(m.tokens_used for m in self.metrics),
            'total_issues': sum(m.issues_found for m in self.metrics),
            'error_rate': sum(1 for m in self.metrics if m.error) / len(self.metrics)
        }
```

#### Task 4.3: Performance Optimization

**File**: `framework/cache.py` (NEW)

```python
"""Result caching to avoid redundant LLM calls."""

import hashlib
import json
from pathlib import Path
from typing import Optional
from framework.models import AnalysisResult

class ResultCache:
    """Cache analysis results by code content hash."""

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)

    def _get_cache_key(self, code: str, technique: str, model: str) -> str:
        """Generate cache key from code + technique + model."""
        content = f"{code}{technique}{model}"
        return hashlib.sha256(content.encode()).hexdigest()

    def get(self, code: str, technique: str, model: str) -> Optional[AnalysisResult]:
        """Get cached result if available."""
        key = self._get_cache_key(code, technique, model)
        cache_file = self.cache_dir / f"{key}.json"

        if cache_file.exists():
            with open(cache_file) as f:
                data = json.load(f)
                return AnalysisResult(**data)
        return None

    def set(self, code: str, technique: str, model: str, result: AnalysisResult):
        """Cache analysis result."""
        key = self._get_cache_key(code, technique, model)
        cache_file = self.cache_dir / f"{key}.json"

        with open(cache_file, 'w') as f:
            json.dump(result.model_dump(), f)
```

#### Task 4.4: Deployment Guide

**File**: `DEPLOYMENT.md` (NEW)

```markdown
# Deployment Guide: Semantic PR Review Bot

## Prerequisites

### 1. Self-Hosted Ollama Server

```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Pull model
ollama pull deepseek-coder:33b-instruct

# Start server (background)
ollama serve &

# Verify
curl http://localhost:11434/api/tags
```

### 2. GitLab CI Runner

```bash
# Register self-hosted runner
gitlab-runner register \
  --url https://gitlab.company.com \
  --token YOUR_RUNNER_TOKEN \
  --executor docker \
  --description "semantic-pr-reviewer"
```

### 3. Environment Variables

Set in GitLab CI/CD settings:
- `GITLAB_TOKEN`: Personal access token with `api` scope
- `OLLAMA_HOST`: URL to Ollama server (e.g., `http://ollama-server:11434`)

## Deployment Steps

### Step 1: Clone Repository

```bash
git clone <repo-url>
cd semantic-pr-reviewer
git checkout v1.0-production
```

### Step 2: Install Dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -e .
```

### Step 3: Configure GitLab CI

Add `.gitlab-ci.yml` to your project (already in repo).

### Step 4: Test Locally

```bash
# Test analysis
python -m cli.main analyze file test-data/sample.cpp

# Test with changed lines
git checkout -b test-branch
# Make changes
git commit -am "Test change"
python -m cli.main analyze pr --base main --head test-branch --changed-lines-only
```

### Step 5: Deploy to CI

```bash
# Push to GitLab
git push origin main

# Create test MR
# CI should automatically trigger semantic-review job
```

## Monitoring

### View Logs

```bash
# GitLab CI logs
# Go to CI/CD > Pipelines > semantic-review job

# Local logs
tail -f /var/log/semantic-pr-reviewer.log
```

### Health Check

```bash
# Check Ollama server
curl http://ollama-server:11434/api/tags

# Check bot can reach Ollama
OLLAMA_HOST=http://ollama-server:11434 python -c "from framework.ollama_client import OllamaClient; print(OllamaClient().list_models())"
```

## Troubleshooting

### Bot Not Posting Comments

1. Check GitLab token permissions
2. Verify `CI_MERGE_REQUEST_IID` is available
3. Check network connectivity to GitLab API

### Ollama Timeouts

1. Check Ollama server is running
2. Increase timeout in `ollama_client.py`
3. Use smaller model (qwen2.5-coder:14b)

### High Resource Usage

1. Enable result caching
2. Reduce parallel workers in chunker
3. Use smaller model
4. Limit max file size

## Performance Tuning

### Cache Configuration

```python
# Enable caching in production_analyzer.py
from framework.cache import ResultCache
cache = ResultCache(Path(".cache/results"))
```

### Model Selection

| Model | Speed | Accuracy | Memory |
|-------|-------|----------|--------|
| deepseek-coder:33b | Slow | High | 18GB |
| qwen2.5-coder:14b | Fast | Medium | 8GB |
| codellama:13b | Fast | Medium | 7GB |

### Parallel Processing

```python
# Adjust workers in chunker
chunker = FileChunker(max_workers=2)  # Reduce from default 4
```

## Maintenance

### Weekly Tasks
- Review false positives
- Update few-shot examples if patterns emerge
- Check Ollama server disk space

### Monthly Tasks
- Update model to latest version
- Review F1 scores and adjust thresholds
- Archive old cache entries

### Quarterly Tasks
- Evaluate new models
- Re-run experiments on ground truth
- Update documentation
```

**Deliverables**:
- [x] Enhanced error handling with retries
- [x] Monitoring and metrics collection
- [x] Result caching implementation
- [x] Logging infrastructure
- [x] DEPLOYMENT.md guide
- [x] Health check scripts
- [x] Performance tuning documentation

**Git Commit**:
```bash
git add framework/ DEPLOYMENT.md
git commit -m "feat: Phase 4 complete - production hardening

Error Handling:
- Retry logic for LLM timeouts (3 attempts, exponential backoff)
- Comprehensive exception handling
- Graceful degradation on failures

Monitoring:
- MetricsCollector for analysis statistics
- Structured logging (JSON format)
- Performance metrics (latency, tokens, errors)

Performance:
- Result caching by code hash
- Configurable parallel workers
- Model selection guide

Deployment:
- Comprehensive DEPLOYMENT.md guide
- Health check scripts
- Troubleshooting documentation
- Performance tuning recommendations

Production Ready:
- All critical paths have error handling
- Metrics exported for monitoring
- Deployment tested on self-hosted CI"

git tag -a v1.0-production -m "Phase 4 complete: Production ready - v1.0"
```

---

## Timeline & Milestones

### Summary Timeline

| Phase | Duration | Status | Completion Date |
|-------|----------|--------|----------------|
| Phase 0 | 1 day | ✅ Complete | 2026-01-03 |
| Phase 1 | 1-2 days | 🔄 Next | 2026-01-05 (target) |
| Phase 2 | 2-3 days | ⏳ Pending | 2026-01-08 (target) |
| Phase 3 | 3-4 days | ⏳ Pending | 2026-01-12 (target) |
| Phase 4 | 2-3 days | ⏳ Pending | 2026-01-15 (target) |
| **Total** | **9-13 days** | - | **2026-01-15 (target)** |

### Critical Path

```
Phase 0 ──► Phase 1 ──► Phase 2 ──► Phase 3 ──► Phase 4
(docs)     (categories)  (dataset)  (CI/CD)    (hardening)
```

Dependencies:
- Phase 1 must complete before Phase 2 (dataset uses new categories)
- Phase 2 should complete before Phase 3 (validate before deployment)
- Phase 3 and Phase 4 can partially overlap

### Milestones

| Milestone | Phase | Criteria | Git Tag |
|-----------|-------|----------|---------|
| **M0: Project Rebranded** | 0 | Documentation updated | `v0-baseline` |
| **M1: Categories Replaced** | 1 | New categories validated | `v1.0-core-categories` |
| **M2: Dataset Ready** | 2 | 20 examples, F1 scores measured | `v1.0-dataset-ready` |
| **M3: CI/CD Integrated** | 3 | Bot posts MR comments | `v1.0-cicd-integration` |
| **M4: Production Launch** | 4 | Deployed to production | `v1.0-production` |

### Risk Buffer

**Contingency**: Add 20% buffer (2-3 days) for:
- Unexpected bugs during integration
- GitLab API issues
- Dataset quality iteration
- Performance optimization

**Realistic Timeline**: 11-16 days (2-3 weeks)

---

## Risk Assessment

### High Risk

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **LLM F1 scores too low on semantic dataset** | Medium | High | - Accept lower F1 (0.5-0.6 OK for semantic issues)<br>- Iterate on few-shot examples<br>- Try different models |
| **GitLab CI runner resource constraints** | Medium | High | - Use smaller model (qwen2.5-coder:14b)<br>- Implement caching<br>- Add resource limits |
| **False positive rate too high** | Medium | High | - Add confidence thresholding<br>- Improve few-shot examples<br>- Add user feedback mechanism |

### Medium Risk

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Ollama server downtime** | Low | Medium | - Add retry logic<br>- Health check before analysis<br>- Fail gracefully |
| **Integration with existing tools** | Medium | Medium | - Document clearly what bot does vs static analysis<br>- Add explicit filtering in system prompt |
| **Dataset creation takes longer** | Medium | Medium | - Start with 10 examples, expand later<br>- Reuse some adapted old examples |

### Low Risk

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Team adoption** | Low | Low | - Clear documentation<br>- Show value with examples<br>- Gradual rollout |
| **Model updates break compatibility** | Low | Low | - Pin model version<br>- Test before upgrading |

---

## Success Metrics

### Phase 1 Success Criteria

✅ New categories validated in models.py
✅ 5 new few-shot examples created
✅ System prompt focuses on complementing static analysis
✅ All tests passing with new categories
✅ Manual validation shows correct issue detection

### Phase 2 Success Criteria

✅ 20 new semantic error examples created
✅ Balanced distribution (4 per category)
✅ F1 scores measured for all techniques
✅ F1 score ≥ 0.50 (acceptable for semantic issues)
✅ No overlap with static analysis (validated manually)

### Phase 3 Success Criteria

✅ GitLab CI pipeline triggers on MR events
✅ Bot successfully posts comments to MR
✅ Changed lines filtering works correctly
✅ PR description context passed to LLM
✅ No false triggers or crashes in production

### Phase 4 Success Criteria

✅ Error handling covers all critical paths
✅ Retry logic prevents transient failures
✅ Monitoring shows key metrics (latency, tokens, errors)
✅ Deployment guide validated on test environment
✅ Performance acceptable (<30s per MR)

### Overall Success Criteria

**Technical**:
- ✅ Bot deployed to production CI/CD
- ✅ Analyzing PRs automatically
- ✅ F1 score ≥ 0.50 on semantic dataset
- ✅ <5% overlap with static analysis detections

**Business**:
- ✅ Catches 2+ semantic issues per week that would have been missed
- ✅ <10% false positive rate (based on developer feedback)
- ✅ Developers find suggestions actionable

**Operational**:
- ✅ <1% failure rate in CI/CD pipeline
- ✅ <30s latency per PR (acceptable for CI)
- ✅ No manual intervention required for 95% of MRs

---

## Deployment Strategy

### Phased Rollout

#### Phase 1: Alpha (Internal Team)
- Deploy to 1-2 test projects
- Team members create test MRs
- Gather feedback on false positives
- Iterate on few-shot examples

**Duration**: 1 week
**Criteria to advance**: <20% false positive rate, positive feedback

#### Phase 2: Beta (Friendly Users)
- Deploy to 5-10 projects
- Invite volunteers for early testing
- Monitor metrics (false positives, latency)
- Add FAQ based on user questions

**Duration**: 2 weeks
**Criteria to advance**: <15% false positive rate, stable performance

#### Phase 3: General Availability
- Deploy to all projects (optional integration)
- Document how to opt-in
- Provide training materials
- Offer support channel

**Duration**: Ongoing
**Success**: 30%+ adoption rate within 3 months

### Rollback Plan

If critical issues discovered:
1. Disable bot in `.gitlab-ci.yml` (set `allow_failure: true`, add `when: manual`)
2. Revert to previous git tag
3. Fix issue in separate branch
4. Re-validate before re-deployment

---

## Maintenance Plan

### Weekly Maintenance

**Tasks**:
- Review bot comments for false positives
- Check error logs for failures
- Monitor resource usage (Ollama server)

**Owner**: DevOps/QA team

### Monthly Maintenance

**Tasks**:
- Update few-shot examples based on patterns
- Re-run experiments on ground truth
- Review F1 scores and adjust thresholds
- Update documentation with new learnings

**Owner**: Bot maintainer

### Quarterly Maintenance

**Tasks**:
- Evaluate new models (e.g., updated deepseek-coder)
- Consider new categories based on user feedback
- Performance optimization review
- Security audit (API tokens, access control)

**Owner**: Engineering team

### Continuous Improvement

**Metrics to track**:
- False positive rate (developer feedback)
- False negative rate (manual review of PRs)
- Developer satisfaction (surveys)
- Adoption rate (% of PRs reviewed by bot)

**Improvement process**:
1. Collect user feedback via MR comments
2. Analyze false positives to identify patterns
3. Update few-shot examples or system prompt
4. Re-validate with experiments
5. Deploy improved version

---

## Appendix

### A. Category Decision Matrix

| Category | Static Analysis Can Detect? | Requires Intent Understanding? | Include in Bot? |
|----------|----------------------------|-------------------------------|-----------------|
| Memory leaks | ✅ Yes (ASan, Valgrind) | ❌ No | ❌ No |
| Use-after-free | ✅ Yes (ASan) | ❌ No | ❌ No |
| Data races | ✅ Yes (TSan) | ❌ No | ❌ No |
| Buffer overflow | ✅ Yes (ASan) | ❌ No | ❌ No |
| Performance issues | ✅ Yes (clang-tidy) | ❌ No | ❌ No |
| **Off-by-one errors** | ⚠️ Sometimes | ✅ Yes | ✅ Yes |
| **API misuse** | ⚠️ Sometimes | ✅ Yes | ✅ Yes |
| **Semantic inconsistency** | ❌ No | ✅ Yes | ✅ Yes |
| **Edge case handling** | ⚠️ Sometimes | ✅ Yes | ✅ Yes |
| **Intent mismatch** | ❌ No | ✅ Yes | ✅ Yes |

### B. Tool Comparison

| Tool | Type | What It Detects | Latency | Accuracy |
|------|------|----------------|---------|----------|
| **AddressSanitizer** | Dynamic | Memory errors | Runtime | 100% |
| **ThreadSanitizer** | Dynamic | Data races | Runtime | ~90% |
| **clang-tidy** | Static | Style, performance, bugs | <1s | ~80% |
| **Valgrind** | Dynamic | Memory leaks, profiling | Runtime (slow) | ~95% |
| **cppcheck** | Static | Bugs, undefined behavior | <1s | ~70% |
| **Semantic PR Bot** | LLM | Semantic issues, logic errors | 8-33s | TBD (target: 50-60%) |

### C. Example PR Review

**PR Title**: "Fix user score calculation"

**PR Description**: "This PR fixes the calculation logic to handle edge cases where users have no scores yet."

**Code Changes**:
```cpp
// Before
int getAverageScore(int userId) {
    auto scores = database.getScores(userId);
    int sum = 0;
    for (int i = 0; i <= scores.size(); i++) {  // Bug 1: off-by-one
        sum += scores[i];
    }
    return sum / scores.size();  // Bug 2: no empty check
}

// After
int getAverageScore(int userId) {
    auto scores = database.getScores(userId);
    if (scores.empty()) {  // Fixed Bug 2
        return 0;
    }
    int sum = 0;
    for (int i = 0; i < scores.size(); i++) {  // Fixed Bug 1
        sum += scores[i];
    }
    return sum / scores.size();
}
```

**Bot Review**:
```
## 🤖 Semantic Code Review

✅ Great job! The fixes address the stated intent in the PR description.

### Analysis

The PR description mentioned "handle edge cases where users have no scores yet" and the code correctly:

1. ✅ Added empty check on line 3 (edge-case-handling fixed)
2. ✅ Fixed off-by-one error in loop condition (logic-errors fixed)

Both fixes align with the PR intent and resolve semantic issues that static analysis might have missed.

---
*This review focused on semantic issues. Memory safety and performance are covered by your existing analysis pipeline.*
```

### D. References

- [PROJECT_PLAN.md](PROJECT_PLAN.md) - This document
- [MIGRATION.md](MIGRATION.md) - Migration from research platform
- [CLAUDE.md](CLAUDE.md) - Development guidelines
- [README.md](README.md) - User documentation
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide (Phase 4)

---

**Document Status**: Living document, updated as project progresses
**Next Review Date**: After each phase completion
**Owner**: Project maintainers

---

*This plan represents a pragmatic transformation from research to production, focusing on delivering value by complementing existing tools rather than duplicating them.*
