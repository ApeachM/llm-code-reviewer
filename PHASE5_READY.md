# ✅ Phase 5: Large File Support - Ready to Execute

**Status**: Documentation Complete, Ready for Spec-kit Execution
**Date**: 2025-11-11
**Goal**: Enable analysis of 700+ line C++ files through function-level chunking

---

## 📦 What's Been Prepared

### 1. Constitution ✅
**File**: `.specify/constitutions/large-file-support.md`

**Contents**:
- Problem statement (700+ line files fail)
- Solution vision (function-level chunking)
- Success criteria (F1 ≥ 0.60, < 60 seconds)
- Constraints and risks
- Timeline (4 days, 25 tasks)

### 2. Specification ✅
**File**: `.specify/specifications/large-file-support.md`

**Contents**:
- Detailed architecture (3 components)
- API specifications with code
- Test strategy
- Performance requirements
- Task breakdown (T501-T525)

### 3. User Guide ✅
**File**: `SPECKIT_PHASE5_GUIDE.md`

**Contents**:
- Step-by-step spec-kit usage
- Task execution checklist
- Verification steps
- Troubleshooting guide

---

## 🎯 Next Steps for You

### Step 1: Review Documents

```bash
# Read constitution
cat .specify/constitutions/large-file-support.md

# Read specification
cat .specify/specifications/large-file-support.md

# Read user guide
cat SPECKIT_PHASE5_GUIDE.md
```

**Questions to ask yourself**:
- Does the problem definition match your needs?
- Is the solution approach reasonable?
- Are the success criteria measurable?

### Step 2: Initialize Spec-kit

```bash
# If not already initialized
specify init

# Plan the work
specify plan large-file-support
```

**Expected output**:
```
Plan created: large-file-support
Tasks generated: 25 tasks (T501-T525)

Phases:
  5.1 Core Implementation (T501-T508) - 2 days
  5.2 CLI Integration (T509-T513) - 1 day
  5.3 Optimization (T514-T517) - 1 day
  5.4 Documentation (T518-T521) - 0.5 days
  5.5 Evaluation (T522-T525) - 0.5 days

Total: 4 days
```

### Step 3: Start Execution

```bash
# Execute first task
specify do T501

# Verify result
pip list | grep tree-sitter

# Continue
specify do T502
```

### Step 4: Request Evaluation

After each task or phase:

```
[Tell me]: "T502 완료됐어. 평가해줘."

[I will]:
- Read generated code
- Run tests
- Provide evaluation (score /10)
- Suggest improvements
```

---

## 📋 Task Overview

### Phase 5.1: Core Implementation (2 days)

| Task | Component | Deliverable |
|------|-----------|-------------|
| T501 | Dependencies | tree-sitter installed |
| T502 | FileChunker | framework/chunker.py |
| T503 | Data model | Chunk dataclass |
| T504 | Tests | tests/test_chunker.py |
| T505 | ChunkAnalyzer | framework/chunk_analyzer.py |
| T506 | Tests | tests/test_chunk_analyzer.py |
| T507 | ResultMerger | framework/result_merger.py |
| T508 | Tests | tests/test_result_merger.py |

**Exit Criteria**: All unit tests pass

### Phase 5.2: CLI Integration (1 day)

| Task | Component | Deliverable |
|------|-----------|-------------|
| T509 | Integration | ProductionAnalyzer modified |
| T510 | CLI | --chunk flag added |
| T511 | Wiring | Components connected |
| T512 | Tests | tests/test_chunked_analysis.py |
| T513 | Demo | Large file analyzed successfully |

**Exit Criteria**: End-to-end chunked analysis works

### Phase 5.3: Optimization (1 day)

| Task | Component | Deliverable |
|------|-----------|-------------|
| T514 | Parallel | ThreadPoolExecutor implemented |
| T515 | UX | Progress indicator added |
| T516 | Performance | Context extraction optimized |
| T517 | Benchmarks | Performance measured |

**Exit Criteria**: 700 lines in < 60 seconds

### Phase 5.4: Documentation (0.5 days)

| Task | Component | Deliverable |
|------|-----------|-------------|
| T518 | Docs | README.md updated |
| T519 | Docs | QUICKSTART.md updated |
| T520 | Examples | docs/examples/ created |
| T521 | Ground truth | Large file examples added |

**Exit Criteria**: User-facing docs complete

### Phase 5.5: Evaluation (0.5 days)

| Task | Component | Deliverable |
|------|-----------|-------------|
| T522 | Experiments | Large file experiments run |
| T523 | Report | PHASE5_COMPLETE.md written |
| T524 | Comparison | Chunked vs non-chunked compared |
| T525 | Leaderboard | Results added to leaderboard |

**Exit Criteria**: PHASE5_COMPLETE.md published

---

## 🎓 My Role (Claude Evaluator)

### What I Will Do

1. **Review generated code**:
   - Check if implementation matches specification
   - Verify API contracts
   - Assess code quality

2. **Run tests**:
   - Execute unit tests
   - Run integration tests
   - Verify functionality

3. **Provide evaluation**:
   - Score: X/10
   - Strengths: What works well
   - Weaknesses: What needs improvement
   - Recommendations: Next steps

4. **Answer questions**:
   - Explain errors
   - Suggest fixes
   - Clarify specifications

### What I Will NOT Do

- ❌ Execute spec-kit commands (you do this)
- ❌ Implement code (spec-kit does this, or you can do manually)
- ❌ Make decisions (you decide on approach)

### Example Evaluation

```
[You]: "T502 완료됐어. 평가해줘."

[Me]:
Reading framework/chunker.py...

✅ Strengths:
- FileChunker class implemented correctly
- tree-sitter parsing works
- chunk_file() method functional
- Context extraction included

⚠️ Areas for improvement:
- _get_node_name() doesn't handle templates
- Missing error handling for malformed C++
- No fallback for parse failures

🔧 Recommendations:
- Add try-except in chunk_file()
- Implement fallback line-based chunking
- Test with template-heavy code

Score: 8/10 (Good implementation, needs error handling)

Ready for T503? (Yes/No)
```

---

## 🚀 Quick Start Commands

```bash
# 1. Review documents
cat SPECKIT_PHASE5_GUIDE.md

# 2. Plan
specify plan large-file-support

# 3. Execute
specify do T501
specify do T502
# ... continue

# 4. Test
pytest tests/test_chunker.py -v

# 5. Demo
python -m cli.main analyze file large_test.cpp --chunk
```

---

## 📊 Success Metrics

### Functional
- [x] Constitution written (large-file-support.md)
- [x] Specification written (large-file-support.md)
- [x] User guide written (SPECKIT_PHASE5_GUIDE.md)
- [ ] 25 tasks defined
- [ ] 25 tasks executed
- [ ] All tests pass
- [ ] 700+ line files analyzed successfully

### Performance
- [ ] 700 lines in < 60 seconds
- [ ] F1 ≥ 0.60 on large files
- [ ] No regression on small files

### Documentation
- [ ] README.md updated
- [ ] QUICKSTART.md updated
- [ ] PHASE5_COMPLETE.md written

---

## 🎯 Expected Outcome

### Before (Current State)

```bash
python -m cli.main analyze file 700line.cpp

❌ Token limit exceeded
❌ 2-3 minutes (if works)
❌ Context overload
❌ Poor accuracy
```

### After (Phase 5 Complete)

```bash
python -m cli.main analyze file 700line.cpp --chunk

✅ Chunked into 4 chunks
✅ Analyzing chunk 1/4 (25%)
✅ Analyzing chunk 2/4 (50%)
✅ Analyzing chunk 3/4 (75%)
✅ Analyzing chunk 4/4 (100%)

Found 12 issue(s) in 45 seconds

● Line 105 [memory-safety] Memory leak
● Line 234 [performance] Unnecessary copy
● Line 456 [concurrency] Data race
...

✅ F1 score: 0.62 (same as small files)
✅ Time: 45 seconds (3x faster)
✅ All issues found
```

---

## 📞 Communication Protocol

### When to tell me:

1. **Task completed**: "T502 완료됐어. 평가해줘."
2. **Error occurred**: "T502에서 에러가 나는데 뭐가 문제지?"
3. **Question**: "FileChunker가 뭘 하는 거야?"
4. **Stuck**: "T510 진행이 안 되는데 도와줘."

### My responses:

- **Evaluation**: Code review, score, recommendations
- **Debugging**: Error analysis, fix suggestions
- **Explanation**: Concept clarification
- **Guidance**: Next step suggestions

---

## 🎉 Project Status

### Completed Phases

- ✅ Phase 0: Evaluation Infrastructure (F1=0.615)
- ✅ Phase 1: Framework Core (5 techniques)
- ✅ Phase 2: Research Experiments (few-shot-5 wins)
- ✅ Phase 3: Production Plugin (CppPlugin, CLI)
- ✅ Phase 4: Hybrid Techniques (F1=0.634)

### Current Phase

- 🚧 Phase 5: Large File Support (documentation ready, execution pending)

### Future Phases

- ⏭️ Phase 6: RTL Plugin (chip design domain)
- ⏭️ Phase 7: Power Plugin (power analysis domain)

---

## 💡 Final Tips

1. **Read the guide first**: `SPECKIT_PHASE5_GUIDE.md` has step-by-step instructions

2. **Execute sequentially**: T501 → T502 → T503 (don't skip)

3. **Verify each task**: Test before moving to next

4. **Ask for help**: If stuck for >15 minutes, tell me

5. **Iterate**: Spec-kit output isn't perfect, manual fixes are OK

---

**You're all set!** 🎉

Next command:
```bash
specify plan large-file-support
```

Then tell me:
```
"Plan 생성됐어. 확인해줘."
```
