# 📘 Spec-kit 사용 가이드: Phase 5 (Large File Support)

이 문서는 spec-kit을 사용해 Phase 5를 구현하는 방법을 설명합니다.

---

## 📋 준비된 문서

제가 작성한 spec-kit 입력 문서들:

1. **Constitution**: `.specify/constitutions/large-file-support.md`
   - 문제 정의
   - 해결 비전
   - 성공 기준
   - 제약사항

2. **Specification**: `.specify/specifications/large-file-support.md`
   - 상세 아키텍처
   - 컴포넌트 설계 (FileChunker, ChunkAnalyzer, ResultMerger)
   - API 명세
   - 테스트 전략
   - 롤아웃 계획

---

## 🚀 Spec-kit 실행 단계

### Step 1: Spec-kit 초기화

```bash
# 프로젝트 루트에서
cd /home/baum/workspace/claude-home/cpp-llm-reviewer

# Spec-kit 초기화 (이미 되어있으면 스킵)
specify init
```

### Step 2: Constitution 확인

```bash
# Constitution 파일 확인
cat .specify/constitutions/large-file-support.md

# 내용 검토:
# - 문제 정의가 명확한가?
# - 해결 방향이 맞는가?
# - 성공 기준이 측정 가능한가?
```

**검토 포인트**:
- ✅ 700줄 파일 문제 명시됨
- ✅ 함수별 chunking 솔루션 제안됨
- ✅ 성공 기준: F1 ≥ 0.60, < 60초
- ✅ 제약사항: 기존 코드와 호환

### Step 3: Specification 확인

```bash
# Specification 파일 확인
cat .specify/specifications/large-file-support.md

# 내용 검토:
# - 3개 핵심 컴포넌트 (FileChunker, ChunkAnalyzer, ResultMerger)
# - API 설계 완료
# - 테스트 전략 명시
# - 25개 tasks (T501-T525)
```

**검토 포인트**:
- ✅ FileChunker: tree-sitter로 AST 파싱
- ✅ ChunkAnalyzer: 개별 chunk 분석
- ✅ ResultMerger: 결과 병합 및 중복 제거
- ✅ CLI 변경: `--chunk` flag 추가

### Step 4: Plan 생성

```bash
# Spec-kit에게 task plan 생성 요청
specify plan large-file-support

# 예상 결과: T501-T525 tasks 생성됨
```

**출력 예시**:
```
Plan created: large-file-support
Tasks: 25 tasks generated

Phase 5.1: Core Implementation (T501-T508)
Phase 5.2: CLI Integration (T509-T513)
Phase 5.3: Optimization (T514-T517)
Phase 5.4: Documentation (T518-T521)
Phase 5.5: Evaluation (T522-T525)
```

### Step 5: Tasks 확인

```bash
# 생성된 task 목록 확인
specify tasks

# 또는 특정 phase만
specify tasks --phase 5.1
```

**예상 tasks**:

```
[ ] T501: Install tree-sitter dependencies
[ ] T502: Implement FileChunker class (framework/chunker.py)
[ ] T503: Implement Chunk dataclass
[ ] T504: Write FileChunker unit tests
[ ] T505: Implement ChunkAnalyzer class (framework/chunk_analyzer.py)
[ ] T506: Write ChunkAnalyzer unit tests
[ ] T507: Implement ResultMerger class (framework/result_merger.py)
[ ] T508: Write ResultMerger unit tests
[ ] T509: Modify ProductionAnalyzer.analyze_file()
[ ] T510: Add --chunk flag to CLI
...
```

### Step 6: Task 실행 시작

```bash
# T501부터 순서대로 실행
specify do T501
```

**Spec-kit이 하는 일**:
1. T501 명세 읽기 (tree-sitter 설치)
2. Claude 세션 시작
3. 코드 생성 또는 명령 실행
4. 결과 저장

**출력 예시**:
```
Executing T501: Install tree-sitter dependencies

Running: pip install tree-sitter tree-sitter-cpp

✓ tree-sitter==0.21.0 installed
✓ tree-sitter-cpp==0.21.0 installed

Task T501 completed successfully.
```

### Step 7: 각 Task 확인 및 진행

```bash
# T502 실행 (FileChunker 구현)
specify do T502

# 결과 확인
ls -la framework/chunker.py
cat framework/chunker.py

# T503 실행 (Chunk dataclass)
specify do T503

# ... 계속 진행
```

---

## 📊 Task 진행 체크리스트

### Phase 5.1: Core Implementation

```bash
[ ] T501: pip install tree-sitter tree-sitter-cpp
    └─ 실행: specify do T501
    └─ 확인: pip list | grep tree-sitter

[ ] T502: framework/chunker.py 생성
    └─ 실행: specify do T502
    └─ 확인: cat framework/chunker.py | head -50

[ ] T503: Chunk dataclass 정의
    └─ 실행: specify do T503
    └─ 확인: grep "@dataclass" framework/chunker.py

[ ] T504: tests/test_chunker.py 작성
    └─ 실행: specify do T504
    └─ 확인: pytest tests/test_chunker.py -v

[ ] T505: framework/chunk_analyzer.py 생성
    └─ 실행: specify do T505
    └─ 확인: cat framework/chunk_analyzer.py

[ ] T506: tests/test_chunk_analyzer.py 작성
    └─ 실행: specify do T506
    └─ 확인: pytest tests/test_chunk_analyzer.py -v

[ ] T507: framework/result_merger.py 생성
    └─ 실행: specify do T507
    └─ 확인: cat framework/result_merger.py

[ ] T508: tests/test_result_merger.py 작성
    └─ 실행: specify do T508
    └─ 확인: pytest tests/test_result_merger.py -v
```

**Exit Criteria**: 모든 unit tests 통과

```bash
pytest tests/test_chunker.py tests/test_chunk_analyzer.py tests/test_result_merger.py -v
```

---

### Phase 5.2: CLI Integration

```bash
[ ] T509: plugins/production_analyzer.py 수정
    └─ 실행: specify do T509
    └─ 확인: grep "chunk_mode" plugins/production_analyzer.py

[ ] T510: cli/main.py에 --chunk flag 추가
    └─ 실행: specify do T510
    └─ 확인: python -m cli.main analyze file --help | grep chunk

[ ] T511: 컴포넌트 연결
    └─ 실행: specify do T511
    └─ 확인: 코드 리뷰

[ ] T512: tests/test_chunked_analysis.py 작성
    └─ 실행: specify do T512
    └─ 확인: pytest tests/test_chunked_analysis.py -v

[ ] T513: 샘플 큰 파일로 테스트
    └─ 실행: specify do T513
    └─ 확인: python -m cli.main analyze file large_test.cpp --chunk
```

**Exit Criteria**: End-to-end chunked analysis 동작

```bash
# 700줄 파일 생성
cat test-data/sample-pr-001/after.cpp > large_test.cpp
cat test-data/sample-pr-001/after.cpp >> large_test.cpp
cat test-data/sample-pr-001/after.cpp >> large_test.cpp
cat test-data/sample-pr-001/after.cpp >> large_test.cpp
cat test-data/sample-pr-001/after.cpp >> large_test.cpp

# 분석 실행
python -m cli.main analyze file large_test.cpp --chunk
```

---

### Phase 5.3: Optimization

```bash
[ ] T514: 병렬 chunk 처리 구현
    └─ 실행: specify do T514
    └─ 확인: grep "ThreadPoolExecutor" framework/chunk_analyzer.py

[ ] T515: Progress indicator 추가
    └─ 실행: specify do T515
    └─ 확인: python -m cli.main analyze file large.cpp --chunk (진행 바 표시)

[ ] T516: Context 추출 최적화
    └─ 실행: specify do T516
    └─ 확인: 코드 리뷰

[ ] T517: 성능 벤치마크
    └─ 실행: specify do T517
    └─ 확인: cat benchmarks/phase5_performance.md
```

**Exit Criteria**: 700줄 파일 < 60초

```bash
time python -m cli.main analyze file large_test.cpp --chunk
# Expected: < 60 seconds
```

---

### Phase 5.4: Documentation

```bash
[ ] T518: README.md 업데이트
    └─ 실행: specify do T518
    └─ 확인: grep "chunk" README.md

[ ] T519: QUICKSTART.md 업데이트
    └─ 실행: specify do T519
    └─ 확인: grep "700" QUICKSTART.md

[ ] T520: docs/ 예제 추가
    └─ 실행: specify do T520
    └─ 확인: ls docs/examples/

[ ] T521: Large file ground truth 생성
    └─ 실행: specify do T521
    └─ 확인: ls experiments/ground_truth/cpp/large_*.cpp
```

---

### Phase 5.5: Evaluation

```bash
[ ] T522: 큰 파일로 실험 실행
    └─ 실행: specify do T522
    └─ 확인: ls experiments/runs/chunked_*

[ ] T523: PHASE5_COMPLETE.md 작성
    └─ 실행: specify do T523
    └─ 확인: cat PHASE5_COMPLETE.md

[ ] T524: Chunked vs non-chunked 비교
    └─ 실행: specify do T524
    └─ 확인: grep "F1" PHASE5_COMPLETE.md

[ ] T525: Leaderboard 업데이트
    └─ 실행: specify do T525
    └─ 확인: python -m cli.main experiment leaderboard
```

---

## 🔍 각 Task 완료 후 확인 사항

### 코드 생성 확인

```bash
# Spec-kit이 파일을 생성했는지 확인
ls -la framework/chunker.py
ls -la framework/chunk_analyzer.py
ls -la framework/result_merger.py
```

### 테스트 실행

```bash
# Unit tests
pytest tests/test_chunker.py -v
pytest tests/test_chunk_analyzer.py -v
pytest tests/test_result_merger.py -v

# Integration tests
pytest tests/test_chunked_analysis.py -v

# 전체 테스트 (기존 것도 여전히 통과해야 함)
pytest tests/ -v
```

### 실제 사용

```bash
# 작은 파일 (기존 방식, 변경 없음)
python -m cli.main analyze file example_code.cpp

# 큰 파일 (새로운 chunking 방식)
python -m cli.main analyze file large_test.cpp --chunk

# Chunk 크기 조정
python -m cli.main analyze file large_test.cpp --chunk --chunk-size 150
```

---

## 🎯 제가 할 일 (평가)

각 task가 완료되면, 저에게 알려주세요:

```
당신: "T502 완료됐어. 평가해줘."

저: framework/chunker.py 읽고 평가
  ✅ FileChunker 클래스 구현됨
  ✅ tree-sitter 사용 확인
  ✅ chunk_file() 메서드 동작
  ⚠️ _get_node_name() 개선 필요

  평가: 8/10 (우수, 일부 개선 권장)
```

---

## 💡 팁

### Tip 1: Task 순서대로 진행

반드시 T501 → T502 → T503 순서로 진행하세요. Dependencies가 있습니다.

### Tip 2: 각 task 결과 확인

```bash
# T502 완료 후
specify do T502
cat framework/chunker.py  # 확인!

# 바로 다음으로 가지 말고, 테스트 먼저
pytest tests/test_chunker.py -v  # 있으면 실행
```

### Tip 3: 에러 발생 시

```bash
# Spec-kit이 에러를 내면
specify do T502  # 실패!

# 로그 확인
specify logs T502

# 재시도
specify redo T502
```

### Tip 4: 수동 수정 가능

Spec-kit이 생성한 코드를 **당신이 직접 수정**해도 됩니다:

```bash
# Spec-kit이 생성
specify do T502

# 당신이 수정
vim framework/chunker.py

# 계속 진행
specify do T503
```

---

## 🚨 예상 문제 및 해결

### 문제 1: tree-sitter 설치 실패

```bash
# T501에서 에러
specify do T501
# Error: tree-sitter-cpp not found

# 해결: 수동 설치
pip install tree-sitter tree-sitter-cpp

# Task를 완료로 표시
specify mark-done T501
```

### 문제 2: Test 파일 생성 안 됨

```bash
# T504에서 test 파일이 생성 안 됨
specify do T504

# 해결: 수동 생성
touch tests/test_chunker.py
vim tests/test_chunker.py  # 직접 작성

# 또는 저에게 요청
"test_chunker.py 코드 작성해줘"
```

### 문제 3: Integration이 안 됨

```bash
# T511에서 컴포넌트 연결이 안 됨
specify do T511

# 해결: 수동으로 import 추가
vim plugins/production_analyzer.py
# from framework.chunker import FileChunker 추가
```

---

## 📈 진행 상황 추적

### 방법 1: Spec-kit 명령어

```bash
# 전체 진행률
specify status

# Task 목록
specify tasks

# 완료된 task
specify tasks --done
```

### 방법 2: Checklist 파일

직접 체크:

```markdown
# Phase 5 Progress

## Phase 5.1: Core (2 days)
- [x] T501: Install dependencies
- [x] T502: FileChunker
- [x] T503: Chunk dataclass
- [ ] T504: Tests
...
```

---

## 🎉 완료 기준

모든 task가 완료되면:

1. **기능 테스트**:
```bash
python -m cli.main analyze file large_test.cpp --chunk
# ✅ 성공적으로 분석 완료
# ✅ < 60초
# ✅ 결과 출력
```

2. **Unit tests**:
```bash
pytest tests/ -v
# ✅ 31 existing tests pass
# ✅ 10+ new tests pass
```

3. **문서화**:
```bash
cat PHASE5_COMPLETE.md
# ✅ 결과 문서화됨
# ✅ F1 score 측정됨
# ✅ 성능 벤치마크 기록됨
```

4. **제게 평가 요청**:
```
"Phase 5 완료됐어. 평가해줘."
```

---

## 📞 도움 요청

막히면 언제든 알려주세요:

- "T502에서 에러가 나는데 뭐가 문제지?"
- "FileChunker 코드가 이상한데 확인해줄래?"
- "테스트가 실패하는데 뭘 고쳐야 해?"

---

**준비 완료! 이제 시작하세요** 🚀

```bash
specify plan large-file-support
```
