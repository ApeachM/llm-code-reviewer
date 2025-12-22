# LLM Code Reviewer - Documentation

**온프레미스 LLM 기반 C++ 코드 분석 플랫폼 문서**

---

## 📖 문서 네비게이션

### 🎯 프로젝트 개요

**시작하기 전에 먼저 읽어보세요!**

- **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - 프로젝트 전체 개요
  - 배경 및 목적
  - 기술 스택
  - 시스템 아키텍처
  - 핵심 개념 (온프레미스, LLM, 프롬프팅)
  - 실험 결과 및 성과

---

## 📚 가이드

### 🚀 빠른 시작
- **[guides/quickstart.md](guides/quickstart.md)** - 5분 만에 시작하기
  - 설치부터 첫 분석까지

### 🎓 완전한 가이드
- **[guides/getting-started/](guides/getting-started/)** - 프로젝트의 원리와 개발 과정
  - [00-INDEX.md](guides/getting-started/00-INDEX.md) - 학습 경로 및 네비게이션
  - [01-introduction.md](guides/getting-started/01-introduction.md) - 프로젝트 소개 및 배경 (15분)
  - [02-technical-deep-dive.md](guides/getting-started/02-technical-deep-dive.md) - 기술 심화 (60-90분) ⭐
    - 모델 선택 과정 (DeepSeek-Coder 33B)
    - Phase 0-5 개발 여정
    - 프롬프팅 기법 진화 (Zero-shot → Hybrid)
    - 실험 결과 및 메트릭
    - Ground Truth 설계
    - AST Chunking 원리
    - 기술적 결정과 트레이드오프

### 🔧 특수 가이드
- **[guides/speckit-usage.md](guides/speckit-usage.md)** - Speckit 사용 가이드

---

## 🏗️ 아키텍처

**시스템 설계 및 개발자 문서**

- **[architecture/overview.md](architecture/overview.md)** - 전체 시스템 아키텍처
  - 3-Tier 구조
  - 컴포넌트 설명
  - 데이터 흐름
  - Mermaid 다이어그램

- **[architecture/ast-chunking.md](architecture/ast-chunking.md)** - AST 기반 청킹 설명
  - 대용량 파일 처리
  - tree-sitter 사용법
  - 병렬 처리 전략

- **[architecture/developer-guide.md](architecture/developer-guide.md)** - 개발자 가이드
  - 프로젝트 기여 방법
  - 새로운 플러그인 개발
  - 커스텀 기법 구현

---

## 🔬 연구 자료

### Phase 문서 (개발 히스토리)
- **[research/phases/](research/phases/)** - Phase 0-5 완료 보고서
  - [phase0-complete.md](research/phases/phase0-complete.md) - Zero-shot 기준선 (F1: 0.498)
  - [phase1-complete.md](research/phases/phase1-complete.md) - Few-shot 학습 (F1: 0.615)
  - [phase2-complete.md](research/phases/phase2-complete.md) - 기법 비교 실험
  - [phase3-complete.md](research/phases/phase3-complete.md) - 프로덕션 도구
  - [phase4-complete.md](research/phases/phase4-complete.md) - Hybrid 기법 (F1: 0.634)
  - [phase4-hybrid.md](research/phases/phase4-hybrid.md) - Hybrid 심층 분석
  - [phase5-complete.md](research/phases/phase5-complete.md) - 대용량 파일 지원

### 실험 가이드
- **[research/experiments/](research/experiments/)** - 실험 실행 가이드
  - [instruction-for-speckit.md](research/experiments/instruction-for-speckit.md) - Speckit 실험 가이드
  - [large-pr-experiment.md](research/experiments/large-pr-experiment.md) - 대규모 PR 실험

---

## 📋 참고 자료

**빠른 참조용 문서**

- **[reference/faq.md](reference/faq.md)** - 자주 묻는 질문 (20개)
  - 일반 질문
  - 기술 질문
  - 사용 질문
  - 확장 질문
  - 성능 질문

- **[reference/troubleshooting.md](reference/troubleshooting.md)** - 문제 해결 가이드
  - 설치 문제
  - 실행 문제
  - 결과 품질 문제
  - Git/PR 문제
  - 진단 체크리스트

- **[reference/glossary.md](reference/glossary.md)** - 용어집
  - LLM 용어
  - 프롬프팅 용어
  - 평가 메트릭

---

## 📐 명세서

- **[specs/003-llm-framework-core/](specs/003-llm-framework-core/)** - 프레임워크 명세서

---

## 🗺️ 학습 경로

### 🟢 초급: "빠르게 시작하고 싶어요"
```
1. guides/quickstart.md (5분)
2. guides/getting-started/02-installation.md (30분)
3. guides/getting-started/05-usage-guide.md (45분)
4. reference/faq.md (참고용)
```
**총 소요 시간**: 1.5시간

---

### 🔵 중급: "프로젝트를 이해하고 싶어요"
```
1. PROJECT_OVERVIEW.md (20분)
2. guides/getting-started/ 전체 (3시간)
3. architecture/overview.md (20분)
4. research/phases/ 훑어보기 (30분)
```
**총 소요 시간**: 4시간

---

### 🟣 고급: "프로젝트를 확장하고 싶어요"
```
1. 위 중급 과정 완료
2. architecture/developer-guide.md (60분)
3. guides/getting-started/07-advanced-topics.md (60분)
4. 실제 플러그인 개발 (1일)
```
**총 소요 시간**: 1-2일

---

## 🔍 문서 찾기

### 목적별 빠른 링크

| 하고 싶은 것 | 문서 |
|------------|------|
| **프로젝트 이해하기** | [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) |
| **설치하기** | [guides/getting-started/02-installation.md](guides/getting-started/02-installation.md) |
| **첫 분석 실행** | [guides/quickstart.md](guides/quickstart.md) |
| **CLI 명령어 배우기** | [guides/getting-started/05-usage-guide.md](guides/getting-started/05-usage-guide.md) |
| **프롬프팅 기법 이해** | [guides/getting-started/04-prompting-techniques.md](guides/getting-started/04-prompting-techniques.md) |
| **아키텍처 이해** | [architecture/overview.md](architecture/overview.md) |
| **플러그인 만들기** | [architecture/developer-guide.md](architecture/developer-guide.md) |
| **실험 실행하기** | [guides/getting-started/06-experiments.md](guides/getting-started/06-experiments.md) |
| **문제 해결하기** | [reference/troubleshooting.md](reference/troubleshooting.md) |
| **FAQ 찾기** | [reference/faq.md](reference/faq.md) |

---

## 📝 문서 기여

문서 개선 제안이 있으신가요?

1. GitHub Issue 생성
2. Pull Request 제출
3. Slack #llm-code-reviewer에서 피드백

**좋은 문서는 함께 만들어갑니다!**

---

## 📞 도움 받기

### 단계별 도움받기
1. 먼저 [reference/faq.md](reference/faq.md) 확인
2. 그 다음 [reference/troubleshooting.md](reference/troubleshooting.md) 확인
3. 코드 작성자에게 서면 문의 

---

**최종 업데이트**: 2024-12-22
**문서 버전**: 2.0 (리팩토링 완료)
