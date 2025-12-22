# Chapter 06: 실험 실행 가이드

**예상 소요 시간**: 60분

---

## 🎯 학습 목표

- ✅ Ground truth 데이터셋 이해
- ✅ 실험 설정 및 실행
- ✅ 결과 분석

---

## 1. Ground Truth 데이터셋

**위치**: `experiments/ground_truth/cpp/`

**구조**:
```json
{
  "id": "example_001",
  "description": "Memory leak",
  "code": "int* ptr = new int(10); return 0;",
  "file_path": "memory_leak.cpp",
  "expected_issues": [
    {
      "category": "memory-safety",
      "severity": "critical",
      "line": 1,
      "description": "Memory leak",
      "reasoning": "..."
    }
  ]
}
```

**현재**: 20개 예시
**권장**: 50-100개 (통계적 유의성)

---

## 2. 실험 실행

### 실험 config 작성
```yaml
# experiments/configs/my_experiment.yml
experiment_id: my_test
technique_name: few_shot_5
model_name: deepseek-coder:33b-instruct
dataset_path: experiments/ground_truth/cpp

technique_params:
  temperature: 0.1
  max_tokens: 2000
```

### 실험 실행
```bash
python -m cli.main experiment run --config experiments/configs/my_experiment.yml
```

---

## 3. 결과 분석

### 메트릭 이해
- **Precision**: 탐지한 것 중 실제 버그 비율
- **Recall**: 실제 버그 중 탐지한 비율
- **F1**: Precision과 Recall의 조화 평균

### 리더보드
```bash
python -m cli.main experiment leaderboard
```

---

상세 내용은 [docs/phases/PHASE2_COMPLETE.md](../phases/PHASE2_COMPLETE.md) 참고.

---

**다음**: [Chapter 07: 고급 주제](07-advanced-topics.md) →
**이전**: [Chapter 05: 실습 가이드](05-usage-guide.md) ←
