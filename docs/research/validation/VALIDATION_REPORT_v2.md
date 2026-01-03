# Validation Report v2: Honest Evaluation

**Date**: 2026-01-03
**Version**: v1.1.1 (힌트 제거 후 재검증)

## 변경 사항

이전 검증에서 테스트 코드에 버그 힌트 주석이 포함되어 있어 LLM이 주석을 읽고 답변할 수 있는 문제가 발견됨.

**제거된 힌트 예시:**
```cpp
// 이전 (힌트 포함)
return false;  // Error: file not closed!
return value >= min || value <= max;  // Wrong operator!

// 이후 (힌트 제거)
return false;
return value >= min || value <= max;
```

---

## 1. Validation Test Results (힌트 제거 후)

### 테스트 파일: `verilator_style_bugs_clean.cpp`

**심어놓은 버그 7개:**

| # | Line | Bug Type | Category |
|---|------|----------|----------|
| 1 | 29 | Off-by-one (`i <= size`) | logic-errors |
| 2 | 35 | Boolean logic (`\|\|` vs `&&`) | logic-errors |
| 3 | 50 | Resource leak (no fclose) | api-misuse |
| 4 | 66 | Getter side effect | semantic-inconsistency |
| 5 | 91 | Division by zero | edge-case-handling |
| 6 | 95 | Integer truncation | logic-errors |
| 7 | 103 | Boolean logic (`\|\|` vs `&&`) | logic-errors |

### 검출 결과

| Bug | Expected | Detected | Result |
|-----|----------|----------|--------|
| Off-by-one | ✓ | ✓ | ✅ TP |
| Boolean (isValidBitRange) | ✓ | ✗ | ❌ FN |
| Resource leak | ✓ | ✓ | ✅ TP |
| Getter side effect | ✓ | ✓ | ✅ TP |
| Division by zero | ✓ | ✓ | ✅ TP |
| Integer truncation | ✓ | ✗ | ❌ FN |
| Boolean (isValidRange) | ✓ | ✓ | ✅ TP |
| Input validation (redundant) | ✗ | ✓ | ⚠️ FP |

### Metrics

| Metric | Value |
|--------|-------|
| True Positives | 5 |
| False Positives | 1 |
| False Negatives | 2 |
| **Precision** | **83.3%** |
| **Recall** | **71.4%** |
| **F1 Score** | **0.769** |

---

## 2. Ground Truth Experiment Results (힌트 제거 후)

### Configuration
- **Model**: deepseek-coder:33b-instruct
- **Technique**: few_shot_5
- **Dataset**: 20 examples, 21 expected issues

### Before vs After (힌트 제거)

| Metric | Before (힌트 있음) | After (힌트 없음) | 변화 |
|--------|-------------------|------------------|------|
| F1 Score | 0.545 | **0.533** | -2.2% |
| Precision | 0.522 | 0.500 | -4.2% |
| Recall | 0.571 | 0.571 | 0% |

### Per-Category Metrics (힌트 제거 후)

| Category | Precision | Recall | F1 |
|----------|-----------|--------|-----|
| logic-errors | 1.000 | 0.600 | **0.750** |
| code-intent-mismatch | 0.400 | 1.000 | 0.571 |
| edge-case-handling | 1.000 | 0.400 | 0.571 |
| semantic-inconsistency | 0.429 | 0.600 | 0.500 |
| api-misuse | 0.286 | 0.500 | 0.364 |

---

## 3. 결론

### 힌트 제거 영향

힌트 제거 후 성능이 약간 하락했지만 (F1: 0.545 → 0.533), 변화가 크지 않음.
이는 LLM이 주석보다는 실제 코드 패턴을 분석하고 있음을 시사함.

### 강점

1. **Off-by-one 검출**: 100% 정확도
2. **Division by zero**: 안정적 검출
3. **Resource leak**: 에러 경로에서 누수 검출
4. **Boolean logic**: 대부분 검출

### 약점

1. **Integer truncation**: 검출 실패 (part/total * 100 패턴)
2. **중복 Boolean logic**: 같은 파일 내 유사 패턴 중 일부 누락
3. **False Positives**: 가끔 정상 코드를 문제로 오인

### 실제 성능 요약

| Test Type | Precision | Recall | F1 |
|-----------|-----------|--------|-----|
| Validation (7 bugs) | 83.3% | 71.4% | **0.769** |
| Ground Truth (21 issues) | 50.0% | 57.1% | **0.533** |

---

## 4. 파일 위치

- **Clean test file**: `docs/research/validation/test_cases/verilator_style_bugs_clean.cpp`
- **Ground truth (fixed)**: `docs/research/experiments/ground_truth/cpp/`
- **Few-shot examples (fixed)**: `plugins/cpp_plugin.py`
- **Config files (fixed)**: `docs/research/experiments/configs/`

---

## 5. 재현 방법

```bash
# Validation test
python -m cli.main analyze file docs/research/validation/test_cases/verilator_style_bugs_clean.cpp

# Ground truth experiment
python -m cli.main experiment run --config docs/research/experiments/configs/few_shot_5.yml
```
