# 용어집 (Glossary)

LLM Code Reviewer 프로젝트에서 사용되는 주요 용어 설명

---

## LLM 관련 용어

### LLM (Large Language Model)
**대규모 언어 모델**. 방대한 양의 텍스트 데이터로 학습한 AI 모델. 텍스트를 이해하고 생성할 수 있음.
- 예시: GPT-4, Claude, DeepSeek-Coder

### 온프레미스 (On-Premises)
**자체 서버에서 실행**. 클라우드가 아닌 내부 네트워크에서 모든 처리가 이루어짐.
- 장점: 데이터 유출 위험 없음, 보안 정책 준수

### Ollama
**로컬 LLM 실행 도구**. Docker처럼 LLM 모델을 쉽게 다운로드하고 실행할 수 있게 해주는 오픈소스 도구.

### DeepSeek-Coder
**코드 특화 LLM 모델**. 33B 파라미터, 18GB 크기. 코드 이해 및 분석에 최적화됨.

### 토큰 (Token)
**LLM의 입출력 단위**. 대략 4글자 = 1토큰.
- 예시: "int* ptr = new int;" ≈ 8토큰

### 컨텍스트 윈도우 (Context Window)
**LLM이 한 번에 처리할 수 있는 최대 토큰 수**. DeepSeek-Coder는 약 4K 토큰.

---

## 프롬프팅 기법

### 프롬프팅 (Prompting)
**LLM에게 질문하는 방법**. 질문 방식에 따라 답변 품질이 달라짐.

### Zero-shot
**예시 없이 질문**. 가장 간단하지만 정확도가 낮음 (F1: 0.526).

### Few-shot Learning
**몇 개의 예시를 제공**. 예시를 보고 패턴을 학습. F1: 0.615 (Few-shot-5).
- Few-shot-3: 3개 예시
- Few-shot-5: 5개 예시 (★ 추천)

### Chain-of-Thought (CoT)
**단계별 추론**. LLM에게 단계별로 생각하도록 요청. Modern-cpp 탐지에 강함 (F1: 0.727).

### Hybrid
**여러 기법 혼합**. Few-shot + CoT를 결합. 최고 정확도 (F1: 0.634)하지만 느림.

### System Prompt
**LLM의 역할 정의**. "너는 C++ 전문가야"같은 지시사항.

### User Prompt
**실제 요청 내용**. 분석할 코드와 질문.

---

## 평가 메트릭

### Ground Truth
**정답 데이터셋**. 실제 버그가 표시된 예제 파일들. 실험에서 성능을 측정하는 기준.

### Precision (정밀도)
**탐지한 것 중 실제 버그 비율**.
- 계산: True Positive / (True Positive + False Positive)
- 예시: 10개 탐지했는데 7개가 실제 버그 → 70% 정밀도

### Recall (재현율)
**실제 버그 중 탐지한 비율**.
- 계산: True Positive / (True Positive + False Negative)
- 예시: 실제 버그 10개 중 6개 탐지 → 60% 재현율

### F1 Score
**정밀도와 재현율의 조화 평균**. 종합적인 성능 지표.
- 계산: 2 × (Precision × Recall) / (Precision + Recall)
- 높을수록 좋음 (최대 1.0)

### True Positive (TP)
**실제 버그를 버그로 정확히 탐지**. ✅ 정답!

### False Positive (FP)
**버그가 아닌데 버그로 탐지**. ❌ 거짓 긍정 (오탐).

### False Negative (FN)
**실제 버그를 놓침**. ❌ 거짓 부정 (미탐).

### True Negative (TN)
**정상 코드를 정상으로 판단**. ✅ 정답!

### Token Efficiency
**1K 토큰당 탐지한 이슈 수**. 비용 효율성 지표.
- 예시: 12K 토큰으로 12개 탐지 → 1.0 issues/1K tokens

---

## 코드 분석 용어

### 카테고리 (Category)
**버그 유형 분류**. 프로젝트에서는 5가지:
- **memory-safety**: 메모리 누수, use-after-free
- **modern-cpp**: 스마트 포인터, auto, range-for 제안
- **performance**: 불필요한 복사, 비효율적 코드
- **security**: SQL injection, 하드코딩된 비밀번호
- **concurrency**: 데이터 레이스, 데드락

### 심각도 (Severity)
**버그의 심각성**. 4단계:
- **critical**: 즉시 수정 필요 (메모리 누수, 버퍼 오버플로우)
- **high**: 곧 수정 필요 (보안 취약점)
- **medium**: 개선 권장 (성능 문제)
- **low**: 선택적 개선 (스타일)

### PR (Pull Request)
**코드 변경 제안**. Git에서 변경 사항을 리뷰받기 위한 프로세스.

---

## 아키텍처 용어

### 3-Tier Architecture
**3계층 구조**:
- Tier 1 (Framework): 핵심 프롬프팅 로직
- Tier 2 (Plugin): 언어별 도메인 지식
- Tier 3 (Application): 사용자 인터페이스 (CLI)

### Plugin
**언어별 분석기**. C++, Python, RTL 등 언어마다 별도 플러그인.

### Domain Plugin
**도메인 지식 제공자**. 카테고리, 예시, 파일 필터링 로직 포함.

### Production Analyzer
**분석 오케스트레이터**. 전체 분석 과정을 조율하는 메인 컴포넌트.

---

## 청킹 (Chunking) 관련

### AST (Abstract Syntax Tree)
**추상 구문 트리**. 코드의 구조를 트리 형태로 표현.

### tree-sitter
**고속 파서 라이브러리**. C++, Python 등 다양한 언어의 AST를 생성.

### Chunking
**파일 분할**. 대용량 파일을 작은 조각(청크)으로 나누는 과정.

### Chunk
**분할된 코드 조각**. 보통 함수 단위로 분할 (200 라인 이하).

### Context
**컨텍스트**. 각 청크에 포함되는 파일 수준 정보 (#include, using 등).

### Parallel Processing
**병렬 처리**. 여러 청크를 동시에 분석. 4배 속도 향상.

### Deduplication
**중복 제거**. 여러 청크에서 같은 이슈가 탐지되면 하나만 남김.

---

## 실험 용어

### Experiment
**실험**. 특정 기법의 성능을 Ground Truth로 평가하는 과정.

### Experiment Config
**실험 설정 파일**. YAML 형식으로 기법, 모델, 데이터셋 등을 정의.

### Leaderboard
**리더보드**. 모든 기법의 성능을 F1 스코어로 순위 매긴 표.

### Phase
**개발 단계**. Phase 0 (기준선) ~ Phase 5 (대용량 파일 지원).

---

## 기타

### DGX-SPARK
**NVIDIA GPU 서버**. AI/ML 워크로드를 위한 고성능 하드웨어.

### CLI (Command Line Interface)
**명령줄 인터페이스**. 터미널에서 명령어로 프로그램 실행.

### GitHub Actions
**CI/CD 도구**. GitHub에서 자동으로 코드를 테스트하고 배포.

### Pydantic
**Python 데이터 검증 라이브러리**. 타입 안전성 보장.

### Mermaid
**다이어그램 생성 언어**. 마크다운에서 그래프를 그릴 수 있음.

---

## 약어

| 약어 | 의미 |
|------|------|
| LLM | Large Language Model |
| AI | Artificial Intelligence |
| ML | Machine Learning |
| API | Application Programming Interface |
| CLI | Command Line Interface |
| PR | Pull Request |
| CoT | Chain-of-Thought |
| AST | Abstract Syntax Tree |
| GPU | Graphics Processing Unit |
| RAM | Random Access Memory |
| VRAM | Video RAM (GPU 메모리) |
| CI/CD | Continuous Integration/Continuous Deployment |
| YAML | Yet Another Markup Language |
| JSON | JavaScript Object Notation |

---

**더 많은 정보**:
- [Project Overview](../PROJECT_OVERVIEW.md)
- [Getting Started Guide](../guides/getting-started/00-INDEX.md)
- [FAQ](faq.md)
