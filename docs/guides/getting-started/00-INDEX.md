# Getting Started Guide - 시작하기

LLM 기반 코드 리뷰어 프로젝트의 완전한 가이드입니다.

---

## 📚 문서 구성

### [Chapter 01: 프로젝트 소개](01-introduction.md)
**예상 소요 시간**: 15분

- 프로젝트 배경 및 동기
- 왜 On-premises LLM인가?
- 핵심 컨셉 설명 (C++ 개발자 관점)

**읽어야 할 대상**: 모든 사용자

---

### [Chapter 02: 기술 심화](02-technical-deep-dive.md)
**예상 소요 시간**: 60-90분

- LLM 모델 선택 과정 (DeepSeek-Coder 33B 선택 이유)
- Phase 0-5 개발 여정
- 프롬프팅 기법 진화 (Zero-shot → Few-shot → CoT → Hybrid)
- 실험 결과와 메트릭 (F1 scores, precision, recall)
- Ground Truth Dataset 설계
- 3-Tier 아키텍처
- AST 기반 Chunking
- 주요 기술적 결정과 트레이드오프

**읽어야 할 대상**:
- 발표 준비하는 팀원
- 프로젝트 원리를 이해하고 싶은 개발자
- LLM 프롬프팅 기법에 관심 있는 연구자

---

## 🎯 학습 경로

### 최소 경로 (15분)
```
01-introduction.md
```
**목적**: 프로젝트가 뭔지만 알면 됨

---

### 발표 준비 경로 (75-105분)
```
01-introduction.md
  ↓
02-technical-deep-dive.md (전체)
```
**목적**: 동료들에게 설명할 수 있을 정도로 이해

**핵심 섹션**:
- 모델 선택 과정
- Phase 0-5 개발 여정
- 프롬프팅 기법 진화
- 실험 결과

---

### 심화 학습 경로 (2-3시간)
```
01-introduction.md
  ↓
02-technical-deep-dive.md
  ↓
docs/research/phases/ (Phase 0-5 상세 문서)
  ↓
docs/architecture/overview.md
```
**목적**: 프로젝트를 확장하거나 개선하고 싶음

---

## 💡 주제별 빠른 링크

| 궁금한 내용 | 읽을 문서 |
|------------|----------|
| 왜 이 프로젝트를 만들었나? | [01-introduction.md](01-introduction.md) |
| 어떤 모델을 썼나? | [02-technical-deep-dive.md § 모델 선택](02-technical-deep-dive.md#2-llm-모델-선택-과정) |
| F1 score가 뭔가? | [02-technical-deep-dive.md § Ground Truth](02-technical-deep-dive.md#5-ground-truth-dataset-설계) |
| Few-shot이 뭔가? | [02-technical-deep-dive.md § 프롬프팅 기법](02-technical-deep-dive.md#4-프롬프팅-기법-진화) |
| Hybrid 기법이 뭔가? | [02-technical-deep-dive.md § Phase 4](02-technical-deep-dive.md#phase-4-hybrid-기법-개발-완료-2025-11-11) |
| 큰 파일은 어떻게 처리하나? | [02-technical-deep-dive.md § AST Chunking](02-technical-deep-dive.md#7-ast-기반-chunking) |
| 아키텍처가 궁금함 | [02-technical-deep-dive.md § 아키텍처](02-technical-deep-dive.md#6-3-tier-아키텍처-설계) |
| 실험 결과가 궁금함 | [02-technical-deep-dive.md § Phase 2](02-technical-deep-dive.md#phase-2-기법-비교-실험-완료-2025-11-11) |

---

## 📖 추가 참고 자료

### 연구 자료
- [Phase 0-5 상세 문서](../../research/phases/)
- [실험 가이드](../../research/experiments/)

### 아키텍처
- [시스템 아키텍처 상세](../../architecture/overview.md)
- [AST Chunking 상세](../../architecture/ast-chunking.md)

### 참고 문서
- [용어 사전](../../reference/glossary.md)
- [FAQ](../../reference/faq.md)
- [문제 해결](../../reference/troubleshooting.md)

---

**메인 문서 허브로 돌아가기**: [docs/README.md](../../README.md)
