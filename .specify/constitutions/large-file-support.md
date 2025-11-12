# Constitution: Large File Support for C++ Code Reviewer

## Problem Statement

The current C++ LLM code reviewer fails on large files (700+ lines) due to:

1. **Token Limit Exceeded**: Few-shot-5 technique uses ~500 tokens for examples + system prompt, leaving only ~1500 tokens for code. A 700-line file requires ~3000-4000 tokens, exceeding the configured `max_tokens=2000`.

2. **Context Overload**: Even if token limits are increased, LLMs struggle with maintaining context over 700+ lines. Issues at the beginning of the file are forgotten by the time the model reaches the end.

3. **Slow Processing**: Large files take 2-3+ minutes to analyze, making the tool impractical for interactive development workflows.

4. **Poor Accuracy**: Context overload leads to missed issues and increased false positives. The F1 score (currently 0.615 on 20-line examples) likely drops significantly on large files.

## Current User Experience

```bash
# User tries to analyze a 700-line file
python -m cli.main analyze file large_module.cpp

# Potential outcomes:
❌ Token limit error (if max_tokens too small)
❌ Incomplete analysis (model runs out of context)
❌ 2-3 minute wait (user gets impatient)
❌ Poor results (missed issues, false positives)
```

## Desired User Experience

```bash
# User analyzes the same 700-line file with chunking
python -m cli.main analyze file large_module.cpp --chunk

# Expected outcomes:
✅ Analysis completes successfully
✅ Results in < 1 minute (5x faster)
✅ Maintains accuracy (F1 ≥ 0.60)
✅ Clear progress indication ("Analyzing chunk 3/5...")
✅ Comprehensive report covering all functions
```

## Solution Vision

**Implement function-level chunking** to analyze large files by:

1. **Parsing**: Use tree-sitter to parse C++ files into AST
2. **Chunking**: Extract functions/classes as independent chunks (~150 lines each)
3. **Context Preservation**: Include necessary context (imports, class definitions) in each chunk
4. **Parallel Analysis**: Analyze chunks concurrently for speed
5. **Result Merging**: Combine and deduplicate issues from all chunks
6. **Line Mapping**: Adjust line numbers back to original file coordinates

## Success Criteria

### Functional Requirements
- ✅ Analyze files up to 2000+ lines without errors
- ✅ Support both chunked and non-chunked modes (user choice)
- ✅ Backward compatible with existing CLI
- ✅ Work with all existing techniques (few-shot-5, hybrid, etc.)

### Performance Requirements
- ✅ 700-line file analyzed in < 60 seconds (vs 2-3 minutes)
- ✅ Linear scaling: 1400 lines in ~120 seconds
- ✅ Support for parallel chunk processing

### Quality Requirements
- ✅ Maintain F1 ≥ 0.60 (same as small files)
- ✅ No duplicate issues across chunk boundaries
- ✅ Accurate line numbers in final report
- ✅ Context-aware analysis (each chunk has necessary imports/definitions)

### Usability Requirements
- ✅ Simple CLI flag: `--chunk`
- ✅ Automatic chunking recommendation for large files
- ✅ Progress indicator: "Analyzing chunk 3/5 (60%)"
- ✅ Clear documentation and examples

## Constraints

### Technical Constraints
1. **Must use existing Ollama models**: No new model downloads required
2. **Tree-sitter dependency**: Add tree-sitter-cpp for parsing
3. **Backward compatibility**: Existing `analyze file` command must still work
4. **Memory efficient**: Don't load entire file into memory multiple times

### Design Constraints
1. **Optional feature**: Chunking is opt-in via `--chunk` flag
2. **No breaking changes**: All existing tests must pass
3. **Plugin architecture**: Should work with any DomainPlugin (not just CppPlugin)
4. **Framework changes**: Minimize changes to core framework

### Resource Constraints
1. **Implementation time**: Target 3-4 days (Phase 5.1-5.4)
2. **Testing**: Must include ground truth for large files
3. **Documentation**: Update README, QUICKSTART, and add examples

## Risks and Mitigation

### Risk 1: Context Loss Between Chunks
**Impact**: Issues that span multiple functions might be missed

**Mitigation**:
- Include class definition and imports in every chunk
- Add overlap between chunks (last 10 lines of previous chunk)
- Implement cross-chunk validation pass (optional)

### Risk 2: Duplicate Issues at Chunk Boundaries
**Impact**: Same issue reported multiple times from different chunks

**Mitigation**:
- Smart deduplication based on (line, category, description similarity)
- Use embedding similarity for fuzzy matching
- Prefer issues with more detailed reasoning

### Risk 3: Tree-sitter Parse Errors
**Impact**: Malformed C++ code cannot be parsed

**Mitigation**:
- Fallback to line-based chunking (every N lines)
- Graceful degradation: log warning and use fallback
- Test with real-world C++ code (templates, macros, etc.)

### Risk 4: Performance Regression on Small Files
**Impact**: Chunking overhead slows down small file analysis

**Mitigation**:
- Only enable chunking when `--chunk` flag is present
- Automatically skip chunking for files < 300 lines
- Benchmark small files before/after implementation

### Risk 5: Increased Token Cost
**Impact**: Chunks have overlapping context → more tokens used

**Mitigation**:
- Minimize context to essential imports/definitions only
- Document token usage in reports
- Make chunk size configurable (trade-off: speed vs cost)

## Non-Goals (Out of Scope)

- ❌ Line-level diff analysis (only analyze changed lines in PR)
  - Reason: Context is crucial, analyzing isolated lines misses issues

- ❌ Real-time streaming analysis (show results as they come)
  - Reason: Deduplication requires all chunks to complete first

- ❌ Cross-file analysis (detect issues across multiple files)
  - Reason: Different problem, requires dependency graph analysis

- ❌ Automatic code fixing (generate patches for issues)
  - Reason: Phase 6 feature, not part of large file support

## Stakeholders and Dependencies

### Primary Users
- C++ developers analyzing large codebases
- Teams using this tool in CI/CD for PR reviews
- Researchers evaluating LLM techniques on large files

### Dependencies
- **tree-sitter-cpp**: For C++ AST parsing
- **Existing framework**: Must integrate cleanly with ProductionAnalyzer
- **Ollama models**: deepseek-coder:33b-instruct (primary), qwen2.5:14b (fallback)

### External Interfaces
- **CLI**: Add `--chunk` flag, maintain existing commands
- **Plugin API**: DomainPlugin must support chunking (optional method)
- **Ground truth**: Create large file examples (700+ lines with annotated issues)

## Validation and Testing

### Validation Strategy
1. **Unit tests**: FileChunker, ChunkAnalyzer, ResultMerger components
2. **Integration tests**: End-to-end chunked file analysis
3. **Ground truth**: 3 large files (500, 700, 1000 lines) with known issues
4. **Regression tests**: Verify small files still work correctly
5. **Performance benchmarks**: Measure speed improvement

### Success Metrics
- All unit tests pass (>95% coverage)
- Integration tests pass (3/3 large files analyzed correctly)
- F1 score ≥ 0.60 on large file ground truth
- Speed: 700 lines in < 60 seconds
- No regression: existing 31 tests still pass

## Timeline and Phases

### Phase 5.1: Core Chunking (Est. 1-2 days)
- Implement FileChunker with tree-sitter
- Implement ChunkAnalyzer
- Implement ResultMerger
- Unit tests for all components

### Phase 5.2: CLI Integration (Est. 1 day)
- Add `--chunk` flag to CLI
- Modify ProductionAnalyzer to support chunking
- Wire up components
- Integration tests

### Phase 5.3: Optimization (Est. 1 day)
- Implement parallel chunk processing
- Add progress indicators
- Optimize context extraction
- Performance benchmarks

### Phase 5.4: Documentation (Est. 0.5 days)
- Update README.md with chunking examples
- Update QUICKSTART.md
- Add large file ground truth examples
- Document chunking algorithm

### Phase 5.5: Evaluation (Est. 0.5 days)
- Run experiments on large files
- Compare chunked vs non-chunked (if possible)
- Document results in PHASE5_COMPLETE.md

**Total Estimated Time**: 4 days

## Alignment with Project Vision

This feature aligns with the project's core mission:

1. **"LLM Engineering 정수"**: Demonstrates how to handle LLM context limitations
2. **Experiment-first design**: Measure chunking effectiveness with ground truth
3. **Production-ready**: Makes tool practical for real-world large codebases
4. **Plugin architecture**: Chunking can extend to RTL, Python, etc.

## Next Steps

After this constitution is approved:

1. **Create detailed specification** with:
   - API designs (FileChunker, ChunkAnalyzer, ResultMerger)
   - Algorithm pseudocode
   - Data structures (Chunk, ChunkResult)
   - CLI interface changes

2. **Generate task plan** with:
   - ~20-30 specific, actionable tasks
   - Dependencies between tasks
   - Estimated time per task

3. **Execute implementation**:
   - Use spec-kit to generate code
   - Test each component
   - Iterate based on results

4. **Evaluate and document**:
   - Run experiments
   - Document results
   - Update user-facing docs

---

**Approval Required**: Once this constitution is reviewed and approved, proceed to detailed specification.
