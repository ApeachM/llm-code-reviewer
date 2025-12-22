# Chapter 08: 자주 묻는 질문 (FAQ)

---

## 일반 질문

### Q1: 이 프로젝트는 무엇인가요?
**A**: 온프레미스 환경에서 실행되는 LLM 기반 C++ 코드 분석 도구입니다. DGX-SPARK + Ollama + DeepSeek-Coder를 사용하여 코드의 버그를 자동으로 탐지합니다.

### Q2: 왜 ChatGPT나 Claude API를 쓰지 않나요?
**A**: 사내 보안 정책상 외부 API에 코드를 전송할 수 없습니다. 이 프로젝트는 모든 처리를 내부 네트워크에서만 수행합니다.

### Q3: 정확도는 어느 정도인가요?
**A**: F1 스코어 0.615 (Few-shot-5 기법). 이는:
- 정밀도 66.7%: 탐지한 버그의 67%가 실제 버그
- 재현율 57.1%: 실제 버그의 57%를 탐지
- 사람보다는 낮지만 일관성 있음

### Q4: 어떤 언어를 지원하나요?
**A**: 현재는 C++만 지원합니다. Python, RTL 등 다른 언어는 플러그인을 추가하면 지원 가능합니다.

### Q5: 무료인가요?
**A**: 네! Ollama는 오픈소스이고, DeepSeek-Coder도 무료로 사용 가능합니다. 하지만 DGX-SPARK 같은 GPU 하드웨어는 필요합니다.

---

## 기술 질문

### Q6: Ollama가 무엇인가요?
**A**: LLM을 로컬에서 실행할 수 있게 해주는 도구입니다. Docker처럼 모델을 다운로드하고 실행할 수 있습니다.

### Q7: GPU가 없으면 사용할 수 없나요?
**A**: GPU 없이도 사용 가능하지만 매우 느립니다:
- GPU 있음: 파일당 8초
- GPU 없음: 파일당 2-5분

더 작은 모델(qwen2.5-coder:14b)을 사용하면 개선됩니다.

### Q8: 프롬프팅 기법이란 무엇인가요?
**A**: LLM에게 질문하는 방식입니다. 예시:
- **Zero-shot**: 예시 없이 질문 (F1: 0.526)
- **Few-shot-5**: 5개 예시 제공 (F1: 0.615) ⭐
- **Hybrid**: 여러 기법 혼합 (F1: 0.634, 느림)

### Q9: 어떤 기법을 사용해야 하나요?
**A**:
- 일반적인 경우: **Few-shot-5** (균형 잡힌 성능)
- 중요한 PR: **Hybrid** (높은 정확도, 4배 느림)
- 빠른 스캔: **Few-shot-3** (조금 낮은 정확도)

### Q10: Ground truth 데이터셋이란?
**A**: 정답이 표시된 20개의 C++ 예제 파일입니다. 실험에서 기법의 성능을 측정하는 데 사용됩니다.

---

## 사용 질문

### Q11: 대용량 파일은 어떻게 분석하나요?
**A**: `--chunk` 플래그를 사용하세요:
```bash
python -m cli.main analyze file large.cpp --chunk
```
파일을 함수 단위로 나누어 병렬로 분석합니다 (4배 빠름).

### Q12: 결과를 파일로 저장하려면?
**A**: `--output` 옵션 사용:
```bash
python -m cli.main analyze file test.cpp --output report.md
```

### Q13: PR 리뷰를 자동화하려면?
**A**: GitHub Actions를 설정하세요:
```yaml
- name: Analyze PR
  run: python -m cli.main analyze pr --output review.md
```

### Q14: 특정 카테고리만 검사할 수 있나요?
**A**: 현재는 모든 카테고리를 함께 검사합니다. 카테고리 필터링은 향후 추가 예정입니다.

### Q15: False positive가 많으면 어떻게 하나요?
**A**: 
1. Hybrid 기법 사용 (정밀도 향상)
2. 결과를 신뢰도(confidence)로 필터링
3. Ground truth에 false positive 예시 추가

---

## 확장 질문

### Q16: Python 플러그인을 만들 수 있나요?
**A**: 네! `DomainPlugin`을 상속받아 구현하면 됩니다:
```python
class PythonPlugin(DomainPlugin):
    def get_file_extensions(self):
        return ['.py']
    def get_categories(self):
        return ['type-safety', 'imports']
    # ...
```
자세한 내용은 [Chapter 07: 고급 주제](07-advanced-topics.md) 참고.

### Q17: 새로운 프롬프팅 기법을 추가하려면?
**A**: `BaseTechnique`를 상속받아 구현:
```python
class MyTechnique(SinglePassTechnique):
    def analyze(self, request):
        # 프롬프트 생성
        # LLM 호출
        # 결과 파싱
        return AnalysisResult(...)
```

### Q18: 다른 LLM 모델을 사용할 수 있나요?
**A**: 네! Ollama에서 지원하는 모든 모델 사용 가능:
```bash
ollama pull codellama:34b
python -m cli.main analyze file test.cpp --model codellama:34b
```

---

## 성능 질문

### Q19: 분석이 너무 느려요
**A**: 
1. GPU 사용 확인: `nvidia-smi`
2. 더 작은 모델 사용: `qwen2.5-coder:14b`
3. 청킹 사용: `--chunk` 플래그
4. 병렬 워커 늘리기 (코드 수정 필요)

### Q20: 메모리가 부족해요
**A**:
1. 더 작은 모델 사용 (14B 대신 33B)
2. Swap 메모리 늘리기
3. GPU VRAM 활용 (Ollama 자동 감지)

---

## 문제 해결

더 자세한 문제 해결은 [Chapter 09: Troubleshooting](09-troubleshooting.md)을 참고하세요.

---

**다음**: [Chapter 09: Troubleshooting](09-troubleshooting.md) →
**이전**: [Chapter 05: 실습 가이드](05-usage-guide.md) ←
