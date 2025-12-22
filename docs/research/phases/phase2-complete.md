# Phase 2: Experiments - RESEARCH FINDINGS ✅

**Status**: EXPERIMENTS COMPLETE - Research Data Collected

**Completion Date**: 2025-11-11

**Model**: deepseek-coder:33b-instruct (18GB)

**Dataset**: 20 annotated C++ examples (45+ issues across 5 categories)

---

## Executive Summary

We ran systematic experiments to discover which LLM prompting techniques work best for code analysis. **Few-shot learning with 5 examples emerged as the winner**, achieving **17% higher F1 score** than zero-shot baseline while maintaining good precision.

### Key Finding

**Few-shot learning improves performance, but not as dramatically as hypothesized (+17% vs +40% expected).**

---

## 📊 LEADERBOARD: Technique Rankings

```
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┓
┃ Experiment          ┃ F1    ┃ Precision ┃ Recall ┃ Token Eff ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━┩
│ 🥇 few_shot_5       │ 0.615 │ 0.667     │ 0.571  │ 0.97      │
│ 🥈 few_shot_3       │ 0.588 │ 0.769     │ 0.476  │ 0.89      │
│ 🥉 chain_of_thought │ 0.571 │ 0.571     │ 0.571  │ 0.92      │
│    zero_shot        │ 0.526 │ 0.588     │ 0.476  │ 1.37      │
└─────────────────────┴───────┴───────────┴────────┴───────────┘
```

**Winner**: Few-Shot (5 examples)
- **+17% F1 improvement** over zero-shot
- **+20% recall improvement** (better at finding issues)
- Best balance of precision and recall

---

## Detailed Results

### 1. Zero-Shot Baseline (Control Group)

**Configuration**: No examples, simple prompt

**Performance**:
- F1: **0.526**
- Precision: **0.588** (59% of detections are real)
- Recall: **0.476** (48% of issues found)
- Token Efficiency: **1.37 issues/1K tokens**
- Avg Latency: **7.89s**
- Total Tokens: **7,308**

**Per-Category Performance**:
| Category | Precision | Recall | F1 |
|----------|-----------|--------|----|
| memory-safety | 0.833 | 0.714 | 0.769 |
| security | 1.000 | 1.000 | 1.000 |
| performance | 0.500 | 0.667 | 0.571 |
| modern-cpp | 0.000 | 0.000 | 0.000 |
| concurrency | 0.000 | 0.000 | 0.000 |

**Analysis**:
- ✅ Good at memory-safety (0.769 F1)
- ✅ Perfect on security (1.000 F1)
- ❌ Failed completely on modern-cpp and concurrency
- **Issue**: Missed nuanced categories without examples

---

### 2. Few-Shot (3 Examples)

**Configuration**: 3 annotated examples (memory, concurrency, clean code)

**Performance**:
- F1: **0.588** (+12% vs zero-shot)
- Precision: **0.769** (+31% improvement!)
- Recall: **0.476** (same as zero-shot)
- Token Efficiency: **0.89 issues/1K tokens**
- Avg Latency: **6.20s** (faster!)
- Total Tokens: **11,263**

**Per-Category Performance**:
| Category | Precision | Recall | F1 |
|----------|-----------|--------|----|
| memory-safety | 0.857 | 0.857 | 0.857 |
| security | 1.000 | 1.000 | 1.000 |
| concurrency | 0.333 | 0.333 | 0.333 |
| performance | 0.000 | 0.000 | 0.000 |
| modern-cpp | 0.000 | 0.000 | 0.000 |

**Analysis**:
- ✅ **Major precision boost** (+31%) - fewer false positives
- ✅ Memory-safety improved to 0.857 F1
- ✅ Detected some concurrency issues (was 0.000)
- ❌ Still missed performance and modern-cpp
- **Insight**: 3 examples help with precision but limited recall

---

### 3. Few-Shot (5 Examples) - 🏆 WINNER

**Configuration**: 5 diverse examples covering more categories

**Performance**:
- F1: **0.615** (+17% vs zero-shot) **BEST**
- Precision: **0.667**
- Recall: **0.571** (+20% vs zero-shot) **BEST**
- Token Efficiency: **0.97 issues/1K tokens**
- Avg Latency: **8.15s**
- Total Tokens: **12,396**

**Per-Category Performance**:
| Category | Precision | Recall | F1 |
|----------|-----------|--------|----|
| memory-safety | 0.750 | 0.857 | 0.800 |
| security | 1.000 | 1.000 | 1.000 |
| performance | 1.000 | 0.667 | 0.800 |
| concurrency | 0.500 | 0.667 | 0.571 |
| modern-cpp | 0.000 | 0.000 | 0.000 |

**Analysis**:
- ✅ **Best overall performance** (0.615 F1)
- ✅ **+20% recall** - finds more real issues
- ✅ **Performance category works** (0.800 F1)
- ✅ **Concurrency improved** (0.571 F1)
- ❌ Modern-cpp still challenging
- **Key Insight**: 5 examples hits sweet spot for coverage

---

## Research Hypotheses: Validated vs Actual

| Hypothesis | Expected | Actual | Status |
|------------|----------|--------|--------|
| Few-shot improves accuracy | +40% | +17% | ⚠️ Partial |
| Few-shot reduces FP | -20% FP | +13% precision | ✅ Validated |
| More examples = better | Linear | Diminishing returns | ⚠️ Complex |

**Key Findings**:

1. **Few-shot DOES improve performance** (+17% F1)
   - Hypothesis: +40% improvement
   - Actual: +17% improvement
   - **Conclusion**: Benefit exists but smaller than expected

2. **Precision improvement is REAL** (+31% with 3 examples)
   - Fewer false positives with examples
   - LLM better understands what counts as issue

3. **Recall improvement requires coverage** (+20% with 5 examples)
   - Need examples spanning different categories
   - 3 examples → same recall as zero-shot
   - 5 examples → +20% recall improvement

4. **Token efficiency decreases** (more context = more tokens)
   - Zero-shot: 1.37 issues/1K tokens
   - Few-shot-5: 0.97 issues/1K tokens
   - **Trade-off**: Better accuracy costs more tokens

---

## Performance by Category

### Strong Categories (F1 > 0.75):
- **Security**: 1.000 F1 (perfect detection across all techniques)
- **Memory-Safety**: 0.769-0.857 F1 (all techniques perform well)
- **Performance**: 0.800 F1 (with few-shot-5 examples)

### Moderate Categories (F1 0.3-0.6):
- **Concurrency**: 0.000-0.571 F1 (improves with examples)
- **Performance**: 0.000-0.800 F1 (needs examples)

### Weak Categories (F1 < 0.3):
- **Modern-C++**: 0.000 F1 (all techniques failed)
  - Hypothesis: Requires more domain-specific knowledge
  - May need specialized examples or fine-tuning

---

## Token Efficiency Analysis

| Technique | Total Tokens | Issues Found | Efficiency |
|-----------|--------------|--------------|------------|
| Zero-shot | 7,308 | 10 | 1.37/1K |
| Few-shot-3 | 11,263 | 10 | 0.89/1K |
| Few-shot-5 | 12,396 | 12 | 0.97/1K |

**Findings**:
- Few-shot uses **50-70% more tokens** due to examples in context
- Trade-off: Higher accuracy vs higher token cost
- **ROI**: +17% F1 for +70% token cost = worthwhile for critical code

---

## Latency Analysis

| Technique | Avg Latency | Total Time (20 examples) |
|-----------|-------------|--------------------------|
| Zero-shot | 7.89s | 157.8s (2.6 min) |
| Few-shot-3 | 6.20s | 123.9s (2.1 min) |
| Few-shot-5 | 8.15s | 163.1s (2.7 min) |

**Findings**:
- Similar latency across techniques (~6-8s per example)
- Few-shot-3 slightly faster (counter-intuitive!)
- Total experiment time: **~2-3 minutes for 20 examples**

---

## Statistical Significance

**Sample Size**: 20 ground truth examples

**Effect Size** (Few-shot-5 vs Zero-shot):
- F1 improvement: +0.089 (+17%)
- Precision improvement: +0.079 (+13%)
- Recall improvement: +0.095 (+20%)

**Note**: Full statistical testing (t-tests, p-values) requires running experiments multiple times for variance estimation. Current results show clear trends but would benefit from repeated runs for statistical rigor.

---

## Practical Recommendations

### For Production Use:

1. **Use Few-Shot (5 examples)** for best accuracy
   - Provides 17% better F1 than zero-shot
   - Worth the extra token cost for critical code

2. **Use Few-Shot (3 examples)** for precision-critical tasks
   - 77% precision (highest)
   - Fewer false positives
   - Good for automated PR comments

3. **Use Zero-Shot** for token-constrained scenarios
   - 40% cheaper (fewer tokens)
   - Still catches 48% of issues
   - Good for large-scale scanning

### For Different Categories:

- **Memory-Safety**: Any technique works (0.75+ F1)
- **Security**: Any technique works (perfect 1.000 F1)
- **Performance**: Requires few-shot examples
- **Concurrency**: Requires few-shot examples
- **Modern-C++**: Needs specialized approach (all failed)

---

## Limitations & Future Work

### Current Limitations:

1. **Small dataset**: 20 examples
   - Need 100+ for statistical rigor
   - Per-category metrics have high variance

2. **Single model**: deepseek-coder:33b-instruct only
   - Should test qwen2.5, starcoder2
   - Model comparison planned but not executed

3. **Missing techniques**:
   - Chain-of-thought (timed out)
   - Multi-pass self-critique (not run)
   - Combined techniques (not run)

4. **No repeated runs**:
   - Can't calculate variance/confidence intervals
   - P-values require multiple runs

### Future Experiments:

1. **Expand dataset** to 50-100 examples
2. **Test other models** (Qwen 2.5 14B, StarCoder2)
3. **Run chain-of-thought** with longer timeout
4. **Test multi-pass self-critique** for FP reduction
5. **Test combined techniques** (few-shot + CoT + critique)
6. **Repeat experiments 3x** for statistical testing
7. **Create specialized examples** for modern-C++

---

## Conclusion

**Primary Finding**: Few-shot learning with 5 examples provides the best balance of accuracy (+17% F1) and practical utility for C++ code analysis.

**Key Insights**:
1. Examples matter - they improve both precision and recall
2. Coverage matters - 5 diverse examples > 3 similar examples
3. Category difficulty varies - some need examples, some don't
4. Token efficiency trade-off is acceptable for quality gain

**Research Value**: This experiment demonstrates that **systematic evaluation with ground truth data** can objectively measure which LLM techniques work. The leaderboard provides actionable guidance for practitioners.

**Next Steps**: Expand to Phase 3 (production C++ plugin) with few-shot-5 as the default technique.

---

## Reproducibility

All experiment results saved in:
```
experiments/runs/
├── zero_shot_baseline_20251111_134938/
├── few_shot_3_examples_20251111_135232/
└── few_shot_5_examples_20251111_135449/
```

Each directory contains:
- `metrics.json`: Full metrics breakdown
- `config.json`: Experiment configuration
- `summary.txt`: Human-readable summary
- `*_prompts.jsonl`: Complete prompt/response log

**To reproduce**:
```bash
source venv/bin/activate
python -m cli.main experiment run --config experiments/configs/zero_shot.yml
python -m cli.main experiment leaderboard
```

---

**Phase 2 Status**: ✅ COMPLETE - Research Findings Documented
**Next Phase**: Phase 3 - Production C++ Plugin (use few-shot-5 as default)

### 4. Chain-of-Thought Technique

**Configuration**: Explicit step-by-step reasoning with `<thinking>` tags

**Performance**:
- F1: **0.571** (+9% vs zero-shot, -7% vs few-shot-5)
- Precision: **0.571**
- Recall: **0.571** (+20% vs zero-shot!)
- Token Efficiency: **0.92 issues/1K tokens**
- Avg Latency: **23.94s** (3x slower!)
- Total Tokens: **13,023**

**Per-Category Performance**:
| Category | Precision | Recall | F1 |
|----------|-----------|--------|----|
| memory-safety | 0.571 | 0.571 | 0.571 |
| modern-cpp | 0.667 | 0.800 | **0.727** ⭐ |
| performance | 0.750 | 1.000 | 0.857 |
| security | 0.667 | 0.667 | 0.667 |
| concurrency | 0.000 | 0.000 | 0.000 |

**Analysis**:
- ⭐ **BREAKTHROUGH: Modern-C++ works!** (0.727 F1 vs 0.000 for all others)
  - Hypothesis: Explicit reasoning helps with nuanced modernization patterns
  - All other techniques completely failed on modern-cpp
- ✅ Perfect recall on performance (1.000)
- ❌ Failed completely on concurrency (unexpected)
- ⚠️ **3x slower latency** (23.94s vs 7-8s for others)
  - Reason: Generates reasoning text before JSON response
  - Longer responses = more inference time

**Key Insight**: 
Chain-of-thought is a **specialist technique** - excellent for specific categories (modern-cpp, performance) but not a general-purpose winner. The explicit reasoning helps the LLM understand subtle code modernization opportunities that pattern matching misses.

**Trade-off Analysis**:
- Pro: Unlocks categories that other techniques can't handle
- Pro: Higher recall on complex issues
- Con: 3x slower (23s vs 8s per example)
- Con: More tokens consumed
- Con: Unpredictable on some categories (concurrency failed)

**Recommendation**: Use chain-of-thought for **specialized analysis** of modern-cpp and performance issues, not as a general-purpose technique.

---

## Updated Research Hypotheses

| Hypothesis | Expected | Actual | Status |
|------------|----------|--------|--------|
| Few-shot improves accuracy | +40% | +17% | ⚠️ Partial |
| CoT improves complex bugs | +30% | +9% overall, **+73% on modern-cpp** | ✅ Category-specific |
| Few-shot reduces FP | -20% FP | +31% precision | ✅ Validated |

**New Finding**: Chain-of-thought is **not universally better**, but unlocks specific categories:
- Modern-C++ (0.727 F1 with CoT vs 0.000 without)
- Performance (0.857 F1 with CoT)

---

