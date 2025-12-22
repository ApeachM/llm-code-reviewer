# Chapter 05: 실습 가이드

**예상 소요 시간**: 45분

---

## 🎯 학습 목표

이 챕터를 마치면 다음을 할 수 있습니다:
- ✅ CLI 명령어 마스터
- ✅ 파일/디렉토리/PR 분석 실행
- ✅ 대용량 파일 분석 (청킹)
- ✅ 결과 해석 및 활용

---

## 실습 1: 단일 파일 분석

### 1.1 기본 분석

**테스트 파일 생성**:
```bash
cat > memory_issues.cpp << 'EOF'
#include <iostream>
#include <vector>

void processData(std::vector<int> data) {  // ⚠️ Pass by value
    for (int i = 0; i < data.size(); i++) {  // ⚠️ Traditional loop
        std::cout << data[i] << std::endl;
    }
}

int main() {
    int* ptr = new int[100];  // ⚠️ Memory leak
    processData({1, 2, 3});
    return 0;
}
EOF
```

**분석 실행**:
```bash
python -m cli.main analyze file memory_issues.cpp
```

**기대 출력**:
```
Analyzing file: memory_issues.cpp
Model: deepseek-coder:33b-instruct

Found 3 issue(s):

● Line 4 [performance] Pass by value instead of reference
  Function takes vector by value, causing unnecessary copy. Use const reference.

● Line 5 [modern-cpp] Use range-based for loop
  Traditional for loop can be replaced with range-for for clarity and safety.

● Line 11 [memory-safety] Memory leak - dynamically allocated array never deleted
  Array allocated with 'new[]' but no corresponding 'delete[]'. Memory leak.
```

### 1.2 결과를 파일로 저장

```bash
python -m cli.main analyze file memory_issues.cpp --output report.md
```

**생성된 report.md**:
```markdown
# Code Analysis Report

**File**: memory_issues.cpp
**Model**: deepseek-coder:33b-instruct
**Date**: 2024-12-22

## Issues Found: 3

### Issue 1: Line 4
**Category**: performance
**Severity**: medium
...
```

---

## 실습 2: 디렉토리 전체 분석

### 2.1 테스트 디렉토리 생성

```bash
mkdir test_project
cd test_project

# 여러 파일 생성
cat > file1.cpp << 'EOF'
int* createData() {
    return new int[10];  // Memory leak
}
EOF

cat > file2.cpp << 'EOF'
void unsafeFunction(char* buf) {
    strcpy(buf, "Very long string that causes overflow");  // Buffer overflow
}
EOF

cat > file3.cpp << 'EOF'
#include <memory>
std::unique_ptr<int> safeCode() {
    return std::make_unique<int>(42);  // ✅ Safe!
}
EOF
```

### 2.2 디렉토리 분석

```bash
python -m cli.main analyze dir test_project/
```

**기대 출력**:
```
Analysis Summary
┏━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric          ┃ Value ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Files Analyzed  │ 3     │
│ Total Issues    │ 2     │
│ Critical Issues │ 1     │
│ High Issues     │ 1     │
│ Medium Issues   │ 0     │
│ Low Issues      │ 0     │
└─────────────────┴───────┘

Issues by Category:
  memory-safety: 1
  security: 1
```

---

## 실습 3: Pull Request 분석

### 3.1 Git 저장소 준비

```bash
# Git 저장소 초기화
git init
git add .
git commit -m "Initial commit"

# feature 브랜치 생성
git checkout -b feature/new-api

# 버그가 있는 파일 추가
cat > api.cpp << 'EOF'
#include <string>

class API {
public:
    std::string getData() {
        char* data = new char[1024];  // Memory leak!
        // ... 처리 ...
        return std::string(data);
    }
};
EOF

git add api.cpp
git commit -m "Add new API"
```

### 3.2 PR 분석 실행

```bash
python -m cli.main analyze pr --base main --head feature/new-api --output pr-review.md
```

**출력**:
```
Analyzing PR: main...feature/new-api
Repository: .
Model: deepseek-coder:33b-instruct

Analyzed 1 changed file(s)
Found 1 issue(s)

📄 api.cpp:
  ● Line 6 [memory-safety] Memory leak in getData()

PR review saved to: pr-review.md
💡 Tip: Copy this markdown to your PR comment!
```

---

## 실습 4: 대용량 파일 분석 (청킹)

### 4.1 대용량 파일 생성

```bash
# 700+ 라인 파일 생성 (자동)
python << 'EOFPY'
with open('large_file.cpp', 'w') as f:
    f.write('#include <iostream>\n\n')
    for i in range(1, 51):  # 50개 함수
        f.write(f'''
void function{i}() {{
    int* ptr = new int({i});  // Bug: Memory leak
    std::cout << "Function {i}" << std::endl;
    // ... more code ...
}}
''')
    f.write('\nint main() {\n')
    for i in range(1, 51):
        f.write(f'    function{i}();\n')
    f.write('    return 0;\n}\n')
EOFPY
```

### 4.2 청킹 없이 분석 (느림)

```bash
time python -m cli.main analyze file large_file.cpp
```

**출력**:
```
Analyzing file: large_file.cpp (700 lines)
Model: deepseek-coder:33b-instruct

Warning: File is large (700 lines). Consider using --chunk flag.

Found 50 issue(s)

Time: 120 seconds
```

### 4.3 청킹 사용 (빠름!)

```bash
time python -m cli.main analyze file large_file.cpp --chunk
```

**출력**:
```
Analyzing file: large_file.cpp
Model: deepseek-coder:33b-instruct
Chunk mode: Enabled (max 200 lines per chunk)

Chunking: 50 functions into 20 chunks
Analyzing in parallel (4 workers)...

Found 50 issue(s) in 20 chunks

Time: 30 seconds (4x faster!)
```

---

## 실습 5: 다양한 옵션 사용

### 5.1 다른 모델 사용

```bash
# 더 작은 모델 (빠르지만 정확도 낮음)
python -m cli.main analyze file test.cpp --model qwen2.5-coder:14b

# 더 큰 모델 (느리지만 정확도 높음, 있다면)
python -m cli.main analyze file test.cpp --model codellama:70b
```

### 5.2 청크 크기 조정

```bash
# 작은 청크 (더 많은 청크, 더 빠름)
python -m cli.main analyze file large.cpp --chunk --chunk-size 100

# 큰 청크 (적은 청크, 더 정확)
python -m cli.main analyze file large.cpp --chunk --chunk-size 300
```

---

## 결과 해석 가이드

### 이슈 심각도 (Severity)

| 심각도 | 의미 | 예시 | 조치 |
|--------|------|------|------|
| **critical** | 즉시 수정 필요 | 메모리 누수, 버퍼 오버플로우 | 바로 수정 |
| **high** | 곧 수정 필요 | 보안 취약점, 데이터 레이스 | 이번 스프린트 |
| **medium** | 개선 권장 | 불필요한 복사, 비효율적 코드 | 다음 스프린트 |
| **low** | 선택적 개선 | 스타일, modern-cpp 제안 | 시간 될 때 |

### 카테고리 (Category)

| 카테고리 | 탐지 내용 | F1 스코어 |
|----------|-----------|----------|
| **memory-safety** | 메모리 누수, use-after-free | 0.800 ⭐ |
| **security** | SQL injection, 하드코딩된 비밀번호 | 1.000 ⭐⭐ |
| **performance** | 불필요한 복사, 비효율적 알고리즘 | 0.800 ⭐ |
| **modern-cpp** | 스마트 포인터, auto, range-for | 0.250 ⚠️ |
| **concurrency** | 데이터 레이스, 데드락 | 0.571 |

---

## 실전 사용 패턴

### 패턴 1: 로컬 개발 중

```bash
# 코드 작성 후 바로 분석
vim my_code.cpp
python -m cli.main analyze file my_code.cpp

# 이슈가 없으면 커밋
git add my_code.cpp
git commit -m "Add new feature"
```

### 패턴 2: PR 리뷰 전

```bash
# PR 생성 전 자가 검토
python -m cli.main analyze pr --output review.md

# 리뷰 결과 확인
cat review.md

# 이슈 수정 후 다시 확인
# ... 수정 ...
python -m cli.main analyze pr --output review.md
```

### 패턴 3: CI/CD 파이프라인

```yaml
# .github/workflows/code-review.yml
name: AI Code Review
on: [pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install Ollama
        run: curl https://ollama.ai/install.sh | sh
      - name: Pull Model
        run: ollama pull deepseek-coder:33b-instruct
      - name: Analyze PR
        run: python -m cli.main analyze pr --output review.md
      - name: Post Comment
        # PR에 결과 코멘트
```

---

## 다음 단계

실습을 모두 완료했다면:

### 더 알아보기
- [Chapter 04: 프롬프팅 기법](04-prompting-techniques.md) - 기법 상세
- [Chapter 06: 실험 실행](06-experiments.md) - 새로운 기법 평가
- [Chapter 07: 고급 주제](07-advanced-topics.md) - 플러그인 개발

### 문제 해결
- [Chapter 08: FAQ](08-faq.md) - 자주 묻는 질문
- [Chapter 09: Troubleshooting](09-troubleshooting.md) - 문제 해결

---

**다음**: [Chapter 08: FAQ](08-faq.md) →
**이전**: [Chapter 02: 설치 가이드](02-installation.md) ←
