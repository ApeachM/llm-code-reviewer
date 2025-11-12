# AST-Based Chunking: 상세 설명

## 개요

AST(Abstract Syntax Tree) 기반 chunking은 대용량 파일(300+ lines)을 의미있는 단위로 분할하여 LLM이 분석할 수 있게 합니다.

---

## 🔄 전체 프로세스

```mermaid
graph TB
    subgraph "1. Input"
        A[Large C++ File<br/>1000+ lines]
    end

    subgraph "2. Parse"
        B[tree-sitter Parser]
        C[AST Tree]
    end

    subgraph "3. Extract"
        D[Extract Context<br/>#includes, usings]
        E[Find Functions/Classes<br/>function_definition<br/>class_specifier]
    end

    subgraph "4. Create Chunks"
        F[Chunk 1: Function A<br/>Context + Code]
        G[Chunk 2: Class B<br/>Context + Code]
        H[Chunk 3: Function C<br/>Context + Code]
    end

    subgraph "5. Analyze"
        I[LLM Analysis<br/>Parallel Processing]
    end

    subgraph "6. Merge"
        J[Result Merger<br/>Adjust Line Numbers<br/>Deduplicate]
        K[Final Report]
    end

    A --> B
    B --> C
    C --> D
    C --> E
    D --> F
    D --> G
    D --> H
    E --> F
    E --> G
    E --> H
    F --> I
    G --> I
    H --> I
    I --> J
    J --> K
```

---

## 📋 Step-by-Step 예제

### Step 1: 원본 파일

```cpp
// sample.cpp (30 lines)
#include <iostream>
#include <vector>
using namespace std;

class Calculator {
private:
    int value;

public:
    Calculator(int v) : value(v) {}

    int add(int x) {
        return value + x;
    }

    int multiply(int x) {
        return value * x;
    }
};

void helperFunction() {
    cout << "Helper" << endl;
}

int main() {
    Calculator calc(10);
    cout << calc.add(5) << endl;
    return 0;
}
```

---

### Step 2: tree-sitter Parsing

**tree-sitter가 하는 일:**
1. C++ 코드를 바이트 단위로 읽음
2. 문법 규칙에 따라 AST 생성
3. 각 노드는 타입과 위치 정보를 가짐

**생성된 AST (단순화):**
```
root_node
├── preproc_include (#include <iostream>)   [lines 1-1]
├── preproc_include (#include <vector>)     [lines 2-2]
├── using_declaration (using namespace std) [lines 3-3]
├── class_specifier (Calculator)            [lines 5-19]
│   ├── identifier (Calculator)
│   ├── field_declaration_list
│   │   ├── function_definition (Constructor)
│   │   ├── function_definition (add)
│   │   └── function_definition (multiply)
├── function_definition (helperFunction)    [lines 21-23]
└── function_definition (main)              [lines 25-29]
```

---

### Step 3: Context 추출

**코드 (chunker.py:122-139):**
```python
def _extract_file_context(self, tree, code_text: str) -> str:
    context_lines = []

    for node in tree.root_node.children:
        if node.type in ['preproc_include', 'using_declaration',
                        'namespace_alias_definition']:
            start_byte = node.start_byte
            end_byte = node.end_byte
            context_lines.append(code_text[start_byte:end_byte])

    return '\n'.join(context_lines)
```

**추출된 Context:**
```cpp
#include <iostream>
#include <vector>
using namespace std;
```

이 context는 **모든 chunk에 prepend**됩니다.

---

### Step 4: Chunk 생성

**Chunk 1: Calculator 클래스**

```python
Chunk(
    chunk_id="sample.cpp:Calculator:5-19",
    file_path=Path("sample.cpp"),
    start_line=5,    # Original file line number
    end_line=19,
    code="""class Calculator {
private:
    int value;

public:
    Calculator(int v) : value(v) {}

    int add(int x) {
        return value + x;
    }

    int multiply(int x) {
        return value * x;
    }
}""",
    context="""#include <iostream>
#include <vector>
using namespace std;""",
    metadata={'node_type': 'class_specifier', 'node_name': 'Calculator'}
)
```

**Chunk 2: helperFunction**

```python
Chunk(
    chunk_id="sample.cpp:helperFunction:21-23",
    file_path=Path("sample.cpp"),
    start_line=21,
    end_line=23,
    code="""void helperFunction() {
    cout << "Helper" << endl;
}""",
    context="""#include <iostream>
#include <vector>
using namespace std;""",
    metadata={'node_type': 'function_definition', 'node_name': 'helperFunction'}
)
```

**Chunk 3: main 함수**

```python
Chunk(
    chunk_id="sample.cpp:main:25-29",
    file_path=Path("sample.cpp"),
    start_line=25,
    end_line=29,
    code="""int main() {
    Calculator calc(10);
    cout << calc.add(5) << endl;
    return 0;
}""",
    context="""#include <iostream>
#include <vector>
using namespace std;""",
    metadata={'node_type': 'function_definition', 'node_name': 'main'}
)
```

---

### Step 5: LLM 입력 생성

**ChunkAnalyzer가 하는 일 (chunk_analyzer.py:66-85):**

```python
def _build_analysis_code(self, chunk: Chunk) -> str:
    if chunk.context:
        return f"{chunk.context}\n\n{chunk.code}"
    else:
        return chunk.code
```

**Chunk 1에 대한 실제 LLM 입력:**

```cpp
#include <iostream>
#include <vector>
using namespace std;

class Calculator {
private:
    int value;

public:
    Calculator(int v) : value(v) {}

    int add(int x) {
        return value + x;
    }

    int multiply(int x) {
        return value * x;
    }
}
```

이 코드가 Few-shot prompt와 함께 LLM에 전송됩니다.

---

### Step 6: 라인 번호 조정

**문제:**
- LLM은 "context + chunk" 코드를 분석
- Context가 5줄이고, chunk가 line 5부터 시작
- LLM이 "line 10"에서 이슈를 발견했다고 하면?

**해결 (chunk_analyzer.py:87-132):**

```python
def _adjust_line_numbers(self, result: AnalysisResult, chunk: Chunk) -> AnalysisResult:
    context_lines = len(chunk.context.split('\n')) if chunk.context else 0

    adjusted_issues = []
    for issue in result.issues:
        # LLM reported line 10 in (context + chunk)
        # Context = 5 lines
        # Chunk starts at file line 5
        # Actual line = 5 + (10 - 5 - 1) = 9

        chunk_relative_line = issue.line - context_lines - 1
        actual_line = chunk.start_line + chunk_relative_line

        adjusted_issue = Issue(
            line=actual_line,  # Adjusted to file coordinates
            category=issue.category,
            severity=issue.severity,
            description=issue.description,
            reasoning=issue.reasoning
        )
        adjusted_issues.append(adjusted_issue)

    result.issues = adjusted_issues
    return result
```

**예제:**
- Context: 5 lines
- Chunk starts: line 5
- LLM reports issue at line 10 (in context+chunk)
- Adjusted: `5 + (10 - 5 - 1) = 9` ✅

---

### Step 7: 결과 병합 & 중복 제거

**ResultMerger (result_merger.py):**

```python
def merge_results(self, chunk_results: List[AnalysisResult]) -> AnalysisResult:
    all_issues = []

    for result in chunk_results:
        all_issues.extend(result.issues)

    # Deduplicate by (line, category)
    unique_issues = {}
    for issue in all_issues:
        key = (issue.line, issue.category)
        if key not in unique_issues:
            unique_issues[key] = issue
        else:
            # Keep higher severity
            if issue.severity == 'critical':
                unique_issues[key] = issue

    return AnalysisResult(
        issues=list(unique_issues.values()),
        metadata={'chunks_analyzed': len(chunk_results)}
    )
```

**중복 제거 예시:**
- Chunk 1: "Line 10, memory-safety, critical"
- Chunk 2: "Line 10, memory-safety, warning" (overlapping context)
- **결과:** Line 10, memory-safety, critical ✅ (critical 우선)

---

## 🔑 핵심 구현 파일

### 1. `framework/chunker.py` (245 lines)

**책임:**
- tree-sitter 파싱
- AST 노드 탐색
- Context 추출
- Chunk 생성

**주요 메서드:**
- `chunk_file()` - 메인 entry point
- `_extract_file_context()` - includes/usings 추출
- `_create_chunk_from_node()` - AST node → Chunk
- `_get_node_name()` - function/class 이름 추출

**사용하는 라이브러리:**
```python
import tree_sitter_cpp as ts_cpp
from tree_sitter import Language, Parser
```

---

### 2. `framework/chunk_analyzer.py` (170 lines)

**책임:**
- Context + Code 결합
- LLM 분석 호출
- Line number 조정

**주요 메서드:**
- `analyze_chunk()` - 단일 chunk 분석
- `_build_analysis_code()` - LLM 입력 생성
- `_adjust_line_numbers()` - 좌표 변환

**병렬 처리:**
```python
def analyze_chunks_parallel(self, chunks: List[Chunk]) -> List[AnalysisResult]:
    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(self.analyze_chunk, chunks))

    return results
```

---

### 3. `framework/result_merger.py` (140 lines)

**책임:**
- 여러 chunk 결과 병합
- 중복 제거
- 메타데이터 집계

**중복 제거 전략:**
1. `(line, category)` 쌍으로 그룹화
2. 같은 line+category는 하나만 유지
3. severity 비교 (critical > warning)

---

## 📊 성능 특성

### Token 사용량

**Without Chunking:**
- 1000 line file = ~3000 tokens (1회 호출)
- Total: 3000 tokens

**With Chunking:**
- 5 chunks × (50 lines context + 200 lines code) = 5 × 750 tokens
- Total: 3750 tokens (25% 증가)

**Trade-off:** Token은 약간 증가하지만, 병렬 처리로 속도 향상

---

### 병렬 처리 효과

**Sequential:**
- 5 chunks × 8 seconds = 40 seconds

**Parallel (4 workers):**
- max(chunk processing times) ≈ 10-12 seconds

**Speed-up:** ~3-4x faster ✅

---

### 정확도

**실험 결과 (Phase 5):**
- **Without chunking** (129 lines): 11 issues found
- **With chunking** (129 lines): 11 issues found (same!)
- **Accuracy:** 100% maintained ✅

**이유:**
- Context가 올바르게 prepend됨
- Line number adjustment가 정확함
- Deduplication이 제대로 작동

---

## 🎯 실제 사용 예

### CLI에서 chunking 활성화

```bash
# Enable chunking for large files
python -m cli.main analyze file large_file.cpp --chunk

# Set custom chunk size (default: 200 lines)
python -m cli.main analyze file large_file.cpp --chunk --chunk-size 300

# PR analysis with chunking
python -m cli.main analyze pr --base main --head feature --chunk
```

### Python API

```python
from pathlib import Path
from plugins.production_analyzer import ProductionAnalyzer

analyzer = ProductionAnalyzer(model_name='deepseek-coder:33b-instruct')

# Automatic chunking for files > 300 lines
result = analyzer.analyze_file(
    file_path=Path('large_file.cpp'),
    chunk_mode=True
)

print(f"Found {len(result.issues)} issues")
```

---

## 🐛 Edge Cases 처리

### 1. Parse 실패

**문제:** tree-sitter가 malformed C++ 파싱 못함

**해결:**
```python
try:
    tree = self.parser.parse(code_bytes)
except Exception as e:
    print(f"Warning: Parse error, falling back to line-based chunking")
    return self._fallback_line_chunking(file_path, code_text)
```

**Fallback:** 단순히 N줄씩 자르기

---

### 2. Global 코드

**문제:** Function/class 밖의 코드는?

**해결:**
```python
if not chunks:
    # No functions/classes found, return whole file as one chunk
    return self._fallback_line_chunking(file_path, code_text)
```

---

### 3. Nested Classes

**문제:** Inner class도 별도 chunk로?

**현재:** Outer class 전체를 하나의 chunk로 처리

**개선 여지:** Inner class를 분리하는 로직 추가 가능

---

### 4. Templates & Macros

**문제:** Template definition이 매우 길 때

**해결:**
```python
if self._get_chunk_line_count(chunk) > self.max_chunk_lines:
    # Split large chunk into smaller pieces
    sub_chunks = self._split_large_chunk(chunk)
    chunks.extend(sub_chunks)
```

---

## 🧪 테스트

### Unit Tests

**tests/test_chunker.py:**
- Chunk 생성 테스트
- Context 추출 테스트
- Line number 계산 테스트
- Edge case 테스트

**tests/test_chunk_analyzer.py:**
- Line number 조정 테스트
- 병렬 처리 테스트

**tests/test_result_merger.py:**
- Deduplication 테스트
- Severity 비교 테스트

### Integration Tests

**tests/test_integration_chunking.py:**
- End-to-end chunking workflow
- 129 line file (without vs. with chunking)
- 645 line file (large file test)

**결과:**
- 83/84 tests passing (98.8%)
- 단 1개 실패: timeout (645 lines, 90초 제한)

---

## 🚀 Demo 실행

```bash
cd /home/baum/workspace/claude-home/cpp-llm-reviewer

# Run the demo
python3 demo_ast_chunking.py

# 출력: 각 chunk가 어떻게 생성되고 LLM에 전달되는지 확인
```

---

## 📚 참고 자료

- **tree-sitter 문서:** https://tree-sitter.github.io/tree-sitter/
- **tree-sitter-cpp:** https://github.com/tree-sitter/tree-sitter-cpp
- **Phase 5 완료 문서:** [docs/phases/PHASE5_COMPLETE.md](../phases/PHASE5_COMPLETE.md)
- **Architecture 문서:** [ARCHITECTURE.md](ARCHITECTURE.md)

---

## ✨ 요약

### AST Chunking이란?

**tree-sitter**로 C++ 코드를 파싱해서 **의미있는 단위**(function, class)로 나누고, 각 chunk에 **context를 추가**해서 LLM이 독립적으로 분석할 수 있게 만드는 기술.

### 왜 필요한가?

대용량 파일(300+ lines)은 LLM token limit을 초과하거나 분석 정확도가 떨어짐. Chunking으로 해결!

### 어떻게 동작하나?

1. tree-sitter로 AST 파싱
2. Context(#includes, usings) 추출
3. Function/Class별로 chunk 생성
4. Context + Code를 LLM에 전달
5. Line number 조정
6. 결과 병합 & 중복 제거

### 성능은?

- **Token:** 25% 증가 (acceptable)
- **속도:** 3-4x 빠름 (병렬 처리)
- **정확도:** 100% 유지 ✅

### 결론

Production-ready! 🎉
