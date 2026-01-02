# Migration Guide: Research Platform → Semantic PR Review Bot

This document explains the transformation of this project from an **LLM research platform** to a **production-ready semantic PR review bot**.

---

## Table of Contents

1. [Overview](#overview)
2. [Why the Transformation?](#why-the-transformation)
3. [Key Changes](#key-changes)
4. [Migration Timeline](#migration-timeline)
5. [Breaking Changes](#breaking-changes)
6. [Backward Compatibility](#backward-compatibility)
7. [Accessing the Original Research Platform](#accessing-the-original-research-platform)

---

## Overview

**Original Purpose**: Research platform for evaluating LLM prompting techniques (zero-shot, few-shot, chain-of-thought, hybrid) on code analysis tasks.

**New Purpose**: Production PR review bot that catches **semantic errors and logic issues** that existing static/dynamic analysis tools cannot detect.

**Key Insight**: The company already has comprehensive static/dynamic analysis pipelines (AddressSanitizer, ThreadSanitizer, clang-tidy, Valgrind). This bot fills the gap by detecting issues that require understanding **code intent and semantics**.

---

## Why the Transformation?

### Original Project Focused On

- ✅ Research comparing LLM prompting techniques
- ✅ Validating techniques with F1 scores on ground truth datasets
- ✅ Detecting memory safety issues (leaks, use-after-free, buffer overflows)
- ✅ Detecting performance issues (unnecessary copies, inefficiencies)
- ✅ Detecting concurrency issues (data races, deadlocks)

### Problems With Original Approach

❌ **Overlap with existing tools**: Memory safety, performance, and concurrency issues are already caught by:
- AddressSanitizer / MemorySanitizer (memory errors)
- ThreadSanitizer (data races)
- clang-tidy (performance, modernization)
- Valgrind (memory leaks)

❌ **Redundant detection**: LLM detecting what static analysis can detect is:
- Slower (8-33s per file vs milliseconds)
- Less accurate (F1: 0.615 vs 100% for static analysis)
- More expensive (token costs)

❌ **Wrong use case**: LLMs excel at **semantic understanding**, not low-level bug detection.

### New Focus: Semantic Issues

✅ **Logic errors**: Off-by-one errors, wrong comparison operators
✅ **API misuse**: Missing cleanup calls in error paths
✅ **Semantic inconsistency**: Function named `get()` modifies state
✅ **Edge case handling**: No empty vector check before access
✅ **Intent mismatch**: Code doesn't match PR description

These require **understanding code intent** - something static analysis cannot do.

---

## Key Changes

### 1. Category Replacement

| Old Category | Why Removed | New Category | Focus |
|-------------|-------------|--------------|-------|
| `memory-safety` | AddressSanitizer detects these | `logic-errors` | Off-by-one, wrong operators |
| `performance` | clang-tidy detects these | `api-misuse` | Missing cleanup, wrong usage |
| `concurrency` | ThreadSanitizer detects these | `semantic-inconsistency` | Code vs documentation |
| `security` (partial) | Static analyzers detect many | `edge-case-handling` | Missing boundary checks |
| `modern-cpp` (kept but refocused) | Some overlap with clang-tidy | `code-intent-mismatch` | Code vs PR description |

### 2. Few-Shot Example Changes

#### Old Examples (Research Platform)

```cpp
// Example 1: Memory leak - raw pointer never deleted
int* ptr = new int(10);
*ptr = 42;
return 0;
// Issue: memory-safety, Critical
```

**Problem**: AddressSanitizer detects this instantly.

#### New Examples (PR Review Bot)

```cpp
// Example 1: Off-by-one error in loop
std::vector<int> nums = {1, 2, 3, 4, 5};
for (int i = 0; i <= nums.size(); i++) {  // Bug!
    sum += nums[i];
}
// Issue: logic-errors, Critical
// Reasoning: Loop uses <= instead of <, causing out-of-bounds access
```

**Why better**: Static analysis may warn about potential out-of-bounds, but LLM understands the **semantic error** (wrong loop condition) and can explain **why** this is wrong.

### 3. System Prompt Changes

#### Old Prompt Focus

```
You are an expert C++ code reviewer. Analyze for:
- Memory leaks (missing delete, use-after-free)
- Data races (unsynchronized access)
- Performance issues (unnecessary copies)
- Security vulnerabilities
```

#### New Prompt Focus

```
You are an expert C++ code reviewer focusing on SEMANTIC issues.

Your company already has static/dynamic analysis (ASan, TSan, clang-tidy, Valgrind).
DO NOT report issues those tools can catch.

FOCUS ON:
- Logic errors (off-by-one, wrong operators)
- API misuse (missing cleanup in error paths)
- Semantic inconsistency (code behavior vs name)
- Edge cases (missing boundary checks)
- Intent mismatch (code vs PR description)
```

### 4. Documentation & Branding

| Aspect | Old | New |
|--------|-----|-----|
| Project name | `llm-framework` | `semantic-pr-reviewer` |
| Main README | Research platform focus | PR review bot focus |
| CLAUDE.md | Research instructions | Production bot configuration |
| pyproject.toml name | `llm-framework` | `semantic-pr-reviewer` |
| CLI entry point | `llm-framework` | `semantic-pr-reviewer` (Phase 1+) |

### 5. Ground Truth Dataset

#### Old Dataset (20 examples)

- 7 memory-safety issues (leaks, use-after-free, buffer overflow)
- 5 modern-cpp issues (smart pointers, auto, range-for)
- 3 performance issues (unnecessary copies)
- 3 security issues (hardcoded credentials)
- 3 concurrency issues (data races)
- **Total**: 21 issues across 20 files

**Problem**: 90%+ of these are detectable by static/dynamic analysis.

#### New Dataset (20 examples) - Phase 2

- 4 logic-errors examples
- 4 api-misuse examples
- 4 semantic-inconsistency examples
- 4 edge-case-handling examples
- 4 code-intent-mismatch examples
- **Total**: 20 issues across 20 files

**Improvement**: 100% focus on semantic issues that require understanding intent.

---

## Migration Timeline

### Phase 0: Documentation & Branding (Current)
**Status**: ✅ Complete
**Git Tag**: `v0-baseline`

Changes:
- Created `archive/research-platform` tag to preserve original state
- Updated README.md with PR review bot focus
- Updated CLAUDE.md with semantic issue categories
- Updated pyproject.toml metadata
- Created this MIGRATION.md document
- Created PROJECT_PLAN.md with transformation roadmap

### Phase 1: Core Category Replacement
**Status**: 🔄 Pending
**Git Tag**: `v1.0-core-categories` (when complete)

Changes:
- Update `framework/models.py` category validation
- Rewrite `plugins/cpp_plugin.py`:
  - Replace 5 categories
  - Replace 5 few-shot examples
  - Rewrite system prompt
- Update tests for new categories
- Run manual validation

**Estimated Duration**: 1-2 days

### Phase 2: Ground Truth Dataset Rebuild
**Status**: ⏳ Pending
**Git Tag**: `v1.0-dataset-ready` (when complete)

Changes:
- Archive old dataset (`experiments/ground_truth/cpp.old/`)
- Create 20 new semantic error examples
- Run experiments to validate F1 scores
- Update experiment configs
- Document dataset design decisions

**Estimated Duration**: 2-3 days

### Phase 3: CI/CD Integration
**Status**: ⏳ Pending
**Git Tag**: `v1.0-cicd-integration` (when complete)

Changes:
- Create `.gitlab-ci.yml` or `Jenkinsfile`
- Implement `integrations/gitlab_client.py`
- Add `--changed-lines-only` flag to CLI
- Add PR context awareness
- Implement inline comment posting

**Estimated Duration**: 3-4 days

### Phase 4: Production Hardening
**Status**: ⏳ Pending
**Git Tag**: `v1.0-production` (when complete)

Changes:
- Optimize output format for PR comments
- Add comprehensive error handling
- Implement retry logic and timeouts
- Add monitoring and logging
- Create deployment guide
- Performance optimization

**Estimated Duration**: 2-3 days

---

## Breaking Changes

### For Users

1. **Category names changed**
   - Old: `memory-safety`, `performance`, `concurrency`, `security`, `modern-cpp`
   - New: `logic-errors`, `api-misuse`, `semantic-inconsistency`, `edge-case-handling`, `code-intent-mismatch`

   **Impact**: Experiment configs using old categories will fail validation.

   **Migration**: Update your experiment configs to use new categories.

2. **Ground truth dataset format unchanged**
   - Format: Still JSON with same structure
   - Content: Different examples (semantic errors instead of memory errors)

   **Impact**: Old experiment results are still valid for historical comparison, but not comparable to new results.

   **Migration**: Keep old results in `experiments/runs.old/` for reference.

3. **System prompt completely rewritten**
   - Old: Focused on memory, performance, concurrency
   - New: Focused on semantic issues, explicitly excludes static-analysis-detectable issues

   **Impact**: Custom prompts may no longer work as expected.

   **Migration**: Review and update custom prompts to align with semantic focus.

### For Developers

1. **Plugin interface unchanged**
   - `DomainPlugin` abstract class remains the same
   - Method signatures unchanged

   **Impact**: None - existing plugin code structure is compatible.

   **Migration**: Only content of `get_categories()` and `get_few_shot_examples()` needs updating.

2. **Technique interface unchanged**
   - `BaseTechnique`, `SinglePassTechnique`, `MultiPassTechnique` unchanged
   - Technique factory still works the same way

   **Impact**: None - techniques work identically.

   **Migration**: No code changes needed.

3. **CLI interface mostly unchanged**
   - Commands: `analyze file`, `analyze dir`, `analyze pr` still work
   - Phase 3 adds: `--changed-lines-only`, `--webhook-mode` flags

   **Impact**: Minimal - new flags are optional.

   **Migration**: Update CI/CD scripts to use new flags when available.

---

## Backward Compatibility

### What Still Works

✅ **Experiment infrastructure**
- `python -m cli.main experiment run --config <file>`
- `python -m cli.main experiment leaderboard`
- Experiment result storage and visualization

✅ **CLI commands**
- `analyze file <path>`
- `analyze dir <path>`
- `analyze pr --base <branch> --head <branch>`

✅ **Technique selection**
- All techniques (zero-shot, few-shot, chain-of-thought, hybrid) still work
- Technique factory unchanged

✅ **Large file support**
- AST-based chunking with tree-sitter
- Parallel processing with ThreadPoolExecutor
- Result merging and deduplication

### What Changed

❌ **Categories**
- Old category names no longer valid
- Must use new semantic-focused categories

❌ **Few-shot examples**
- Old examples replaced with semantic error examples
- Cannot use old examples with new categories

❌ **Ground truth dataset**
- Old dataset archived
- New dataset has different issues

❌ **System prompt**
- Old prompt removed
- New prompt focuses on complementing static analysis

### Migration Path for Old Experiments

If you want to reproduce old research results:

```bash
# Checkout the research platform tag
git checkout archive/research-platform

# Run old experiments
python -m cli.main experiment run --config experiments/configs/few_shot_5.yml

# Return to current version
git checkout main
```

---

## Accessing the Original Research Platform

The original research platform is preserved and accessible:

### Via Git Tag

```bash
# View the tag
git tag -l archive/research-platform

# Checkout the original state
git checkout archive/research-platform

# Browse original code, docs, experiments
ls experiments/ground_truth/cpp/
cat README.md

# Return to current version
git checkout main
```

### What's Preserved

✅ **Original categories**: memory-safety, performance, concurrency, security, modern-cpp
✅ **Original few-shot examples**: Memory leaks, use-after-free, data races
✅ **Original ground truth dataset**: 20 examples with memory/performance issues
✅ **Original documentation**: Research-focused README and docs
✅ **Experiment results**: All runs in `experiments/runs/` (if committed)
✅ **Research phase docs**: Phase 0-5 completion reports

### Using Both Versions

You can maintain both versions if needed:

```bash
# Keep research platform in separate branch
git checkout archive/research-platform
git checkout -b research-platform-archive

# Continue PR bot development in main
git checkout main
```

---

## Comparing Results: Old vs New

### Old Categories F1 Scores (Research Platform)

| Technique | Overall F1 | memory-safety F1 | performance F1 | concurrency F1 |
|-----------|-----------|------------------|----------------|----------------|
| few-shot-5 | 0.615 | 0.800 | 0.400 | 0.667 |
| hybrid | 0.634 | 0.818 | 0.500 | 0.667 |
| chain-of-thought | 0.571 | 0.750 | 0.333 | 0.500 |

**Analysis**: High F1 on memory-safety because examples are clear-cut (leak or no leak). But **these are already caught by AddressSanitizer**.

### New Categories F1 Scores (PR Review Bot) - TBD in Phase 2

| Technique | Overall F1 | logic-errors F1 | api-misuse F1 | semantic-inconsistency F1 |
|-----------|-----------|-----------------|---------------|---------------------------|
| few-shot-5 | TBD | TBD | TBD | TBD |
| hybrid | TBD | TBD | TBD | TBD |
| chain-of-thought | TBD | TBD | TBD | TBD |

**Expected**: Lower F1 scores initially (semantic issues are harder), but **these cannot be caught by any existing tool**.

---

## FAQ

### Q: Can I still use the old categories?

**A**: Not in the current version. The old categories have been removed from validation in `framework/models.py`. You must use the new semantic-focused categories.

However, you can:
1. Checkout the `archive/research-platform` tag to use old categories
2. Create a custom branch with old categories if needed for research

### Q: Why not support both old and new categories?

**A**: To avoid confusion and ensure all detections are production-relevant. The old categories detect issues that existing tools handle better. Maintaining both would dilute the bot's focus and create misleading results.

### Q: Will old experiment results be deleted?

**A**: No. Old experiment results in `experiments/runs/` are preserved (if committed). They serve as historical reference for the research phase. New experiments will generate new results in the same directory.

### Q: What happens to the Phase 0-5 documentation?

**A**: All phase documentation remains in `docs/research/phases/`. These documents explain the research journey and are valuable for understanding technique selection and dataset design decisions.

### Q: Can I contribute new semantic categories?

**A**: Yes! Follow the process in `CLAUDE.md` under "Adding a New Domain Plugin". Ensure new categories:
1. Focus on semantic issues (not detectable by static analysis)
2. Have clear few-shot examples
3. Are validated with ground truth dataset
4. Don't overlap with existing categories

### Q: What about Python/JavaScript support?

**A**: Currently C++ only. Python/JavaScript plugins can be added in future phases following the existing plugin architecture. The framework is language-agnostic.

---

## Summary

| Aspect | Before (Research Platform) | After (PR Review Bot) |
|--------|---------------------------|----------------------|
| **Purpose** | Research LLM techniques | Production PR reviews |
| **Focus** | Memory/performance/concurrency | Semantic/logic errors |
| **Categories** | memory-safety, performance, concurrency, security, modern-cpp | logic-errors, api-misuse, semantic-inconsistency, edge-case-handling, code-intent-mismatch |
| **Overlap with static analysis** | ~90% | ~5% |
| **Value proposition** | Technique comparison | Complement existing tools |
| **Deployment** | Local testing only | CI/CD integration |
| **Git tag** | `archive/research-platform` | `main` branch |

---

## Next Steps

1. ✅ **Read PROJECT_PLAN.md** - Detailed transformation roadmap
2. ⏭️ **Phase 1**: Update categories and few-shot examples
3. ⏭️ **Phase 2**: Rebuild ground truth dataset
4. ⏭️ **Phase 3**: Integrate with GitLab CI/Jenkins
5. ⏭️ **Phase 4**: Production hardening and deployment

---

**For questions or concerns about this migration, please:**
- Review `PROJECT_PLAN.md` for detailed implementation plan
- Check `CLAUDE.md` for development guidelines
- Consult git history for rationale behind specific changes
- Reach out to the team for clarification

---

*This migration represents a fundamental shift from research to production. The transformation aligns the project with real-world needs: complementing static analysis instead of duplicating it.*
