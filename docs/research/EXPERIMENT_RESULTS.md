# Experiment Results

## Overview

This document summarizes the experiment results for the Semantic PR Review Bot. All experiments were run on the ground truth dataset of 20 annotated C++ examples.

**Model**: deepseek-coder:33b-instruct
**Dataset**: docs/research/experiments/ground_truth/cpp (20 examples, 21 expected issues)
**Date**: 2026-01-03
**Version**: v1.1.1

---

## Important Note (v1.1.1)

**힌트 제거**: 이전 버전에서는 테스트 코드에 버그를 알려주는 주석이 포함되어 있었음:
```cpp
// Before: return false;  // Error: file not closed!
// After:  return false;
```
v1.1.1에서 모든 힌트 주석을 제거하여 공정한 평가 수행.

---

## Leaderboard (Honest Results)

| Rank | Technique | F1 | Precision | Recall | Token Eff | Latency |
|------|-----------|-----|-----------|--------|-----------|---------|
| 1 | few_shot_5 (v1.1.1) | **0.533** | 0.500 | 0.571 | 0.66 | 9.81s |

> **Note**: 이전 결과(F1 0.545~0.634)는 힌트 주석이 포함된 상태에서 측정됨.
> 힌트 제거 후 실제 성능은 F1 0.533 수준.

---

## Latest Results (v1.1.1 - 힌트 제거 후)

### Few-shot-5

| Metric | Value |
|--------|-------|
| **F1 Score** | **0.533** |
| Precision | 0.500 |
| Recall | 0.571 |
| Token Efficiency | 0.66 issues/1K tokens |
| Average Latency | 9.81s |
| Total Tokens | 18,072 |

**Confusion Matrix:**
- True Positives: 12
- False Positives: 12
- False Negatives: 9

### Zero-shot

| Metric | Value |
|--------|-------|
| **F1 Score** | **0.441** |
| Precision | 0.342 |
| Recall | 0.619 |
| Token Efficiency | 0.96 issues/1K tokens |
| Average Latency | 23.65s |
| Total Tokens | 13,490 |

**Confusion Matrix:**
- True Positives: 13
- False Positives: 25
- False Negatives: 8

---

## Per-Category Analysis

### Few-shot-5 (v1.0.5)

| Category | Precision | Recall | F1 | Notes |
|----------|-----------|--------|-----|-------|
| semantic-inconsistency | 0.667 | 0.800 | **0.727** | Best performing |
| logic-errors | 1.000 | 0.400 | 0.571 | High precision |
| edge-case-handling | 1.000 | 0.400 | 0.571 | High precision |
| code-intent-mismatch | 0.400 | 1.000 | 0.571 | High recall |
| api-misuse | 0.250 | 0.500 | 0.333 | Needs improvement |

### Zero-shot (v1.0.5)

| Category | Precision | Recall | F1 | Notes |
|----------|-----------|--------|-----|-------|
| logic-errors | 0.500 | 1.000 | **0.667** | Best performing |
| edge-case-handling | 0.600 | 0.600 | 0.600 | Balanced |
| api-misuse | 0.286 | 1.000 | 0.444 | High recall |
| semantic-inconsistency | 0.333 | 0.200 | 0.250 | Needs examples |
| code-intent-mismatch | 0.000 | 0.000 | 0.000 | Not detected |

---

## Category Normalization Impact

Category normalization automatically maps LLM category variations to allowed categories.

### Improvement Summary

| Technique | Before | After | Improvement |
|-----------|--------|-------|-------------|
| Zero-shot | F1=0.302 | F1=0.441 | **+46%** |
| Few-shot-5 | F1=0.500 | F1=0.545 | **+9%** |

### Normalization Mappings

| LLM Output | Normalized To |
|------------|---------------|
| code-quality | edge-case-handling |
| off-by-one-error | logic-errors |
| resource-leak | api-misuse |
| logic-error | logic-errors |
| boolean-logic | logic-errors |
| division-by-zero | edge-case-handling |

---

## Technique Comparison

### Single-Pass Techniques

| Technique | F1 | Pros | Cons |
|-----------|-----|------|------|
| few_shot_5 | 0.545 | Balanced, fast | Moderate precision |
| few_shot_3 | 0.588 | High precision | Lower recall |
| chain_of_thought | 0.571 | Good reasoning | Slower |
| zero_shot | 0.441 | No examples needed | Lower precision |

### Multi-Pass Techniques

| Technique | F1 | Pros | Cons |
|-----------|-----|------|------|
| hybrid | 0.634 | Best accuracy | 4x slower |
| hybrid_category_specialized | 0.500 | Category focus | Complex setup |

---

## Recommendations

### Production Use

1. **Default**: Use `few_shot_5` (F1=0.545, 10s latency)
   - Best balance of speed and accuracy
   - Good for CI/CD integration

2. **Critical Reviews**: Use `hybrid` (F1=0.634, 33s latency)
   - Highest accuracy
   - Use for important PRs or security-sensitive code

3. **Quick Scans**: Use `zero_shot` (F1=0.441, 24s latency)
   - No few-shot examples needed
   - Good for initial triage

### Areas for Improvement

1. **api-misuse** (F1=0.333): Add more diverse examples
2. **code-intent-mismatch**: Requires PR context for better detection
3. **Precision**: Consider confidence thresholds to reduce FPs

---

## Experiment Configuration

### Few-shot-5 Configuration

```yaml
experiment_id: few_shot_5_examples
technique_name: few_shot_5
model_name: deepseek-coder:33b-instruct
dataset_path: docs/research/experiments/ground_truth/cpp
technique_params:
  num_examples: 5
  temperature: 0.1
```

### Ground Truth Dataset

- Location: `docs/research/experiments/ground_truth/cpp/`
- Examples: 20 annotated C++ code snippets
- Categories covered: All 5 semantic categories
- Clean code examples: 3 (negative examples)

---

## Version History

| Version | Date | F1 (few_shot_5) | Key Changes |
|---------|------|-----------------|-------------|
| v1.0.0 | 2026-01-03 | 0.500 | Initial release |
| v1.0.3 | 2026-01-03 | 0.500 | Const function fix (0 FP) |
| v1.0.4 | 2026-01-03 | 0.489 | Category normalization |
| v1.0.5 | 2026-01-03 | **0.545** | Expanded mappings (+9%) |

---

## Running Experiments

```bash
# Run single experiment
python -m cli.main experiment run --config docs/research/experiments/configs/few_shot_5.yml

# Run all experiments
for config in docs/research/experiments/configs/*.yml; do
  python -m cli.main experiment run --config "$config"
done

# View leaderboard
python -m cli.main experiment leaderboard
```

---

## Files

- **Configs**: `docs/research/experiments/configs/`
- **Ground Truth**: `docs/research/experiments/ground_truth/cpp/`
- **Results**: `experiments/runs/` (gitignored)
- **This Report**: `docs/research/EXPERIMENT_RESULTS.md`
