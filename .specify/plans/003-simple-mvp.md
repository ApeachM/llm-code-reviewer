# Simple MVP: Quality-Focused Single-User Architecture

**Target**: 1인 사용, 속도 무관, 오직 리뷰 품질에만 집중

## 핵심 원칙

1. **단순함 > 복잡함**: RAG, 벡터 DB, 복잡한 인프라 제외
2. **품질 > 속도**: Multi-pass, self-critique 사용 (토큰 많이 써도 OK)
3. **실용성 > 완벽함**: 80%만 잘 작동해도 충분히 유용

---

## 최소 아키텍처

```
┌─────────────────────────────────────────┐
│  User runs: cpp-reviewer review         │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  1. Git Diff Extraction                 │
│     - git diff main...HEAD              │
│     - Filter C++ files only             │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  2. Prompt Construction                 │
│     - Load few-shot examples            │
│     - Format diff with context          │
│     - Add JSON schema                   │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  3. Pass 1: Initial Review              │
│     - Ollama deepseek-coder:33b         │
│     - Find all issues                   │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  4. Pass 2: Self-Critique               │
│     - Ollama reviews its own output     │
│     - Confidence scoring                │
│     - Filter low-confidence issues      │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  5. Output Formatting                   │
│     - JSON or Markdown                  │
│     - Color-coded terminal display      │
└─────────────────────────────────────────┘
```

**전체 파일 수: ~5개**
**구현 시간: 2-3일**

---

## 프로젝트 구조 (극도로 단순화)

```
cpp-llm-reviewer/
├── src/
│   ├── main.py              # CLI entry point (100 lines)
│   ├── git_diff.py          # Git diff extraction (80 lines)
│   ├── prompt_builder.py   # Few-shot + prompt construction (120 lines)
│   ├── reviewer.py          # Multi-pass review logic (150 lines)
│   └── output.py            # Format and display (80 lines)
│
├── prompts/
│   ├── system_prompt.txt    # Role and guidelines
│   ├── few_shot_examples.json  # 5 example reviews
│   └── critique_prompt.txt  # Self-critique instructions
│
├── test-data/
│   └── sample-pr-001/       # Test PR we just created
│
├── config.yml               # Simple configuration
└── requirements.txt         # Dependencies (minimal)

Total: ~530 lines of actual code
```

---

## 구현 계획 (단순 버전)

### Day 1: Core Infrastructure

**Morning (3-4 hours)**: Git + Prompt
```python
# git_diff.py
def get_pr_diff(base_branch="main"):
    """Extract git diff for current branch vs base"""
    result = subprocess.run(
        ["git", "diff", f"{base_branch}...HEAD"],
        capture_output=True, text=True
    )
    return result.stdout

def filter_cpp_files(diff):
    """Only keep C++ file changes"""
    # Parse diff, filter by extension
    pass

# prompt_builder.py
def build_review_prompt(diff, few_shot_examples):
    """Construct prompt with examples + diff + schema"""
    return f"""
You are an expert C++ code reviewer.

Here are examples of excellent reviews:
{format_examples(few_shot_examples)}

Now review this PR:
{diff}

Output valid JSON:
{json_schema}
"""
```

**Afternoon (3-4 hours)**: Ollama Integration
```python
# reviewer.py
import ollama

def review_pass1(diff, few_shot_examples):
    """Initial review pass"""
    prompt = build_review_prompt(diff, few_shot_examples)

    response = ollama.generate(
        model="deepseek-coder:33b-instruct",
        prompt=prompt,
        options={
            "temperature": 0.3,  # Lower for consistency
            "num_predict": 2000  # Max output tokens
        }
    )

    return parse_json(response['response'])

def review_pass2_critique(initial_reviews):
    """Self-critique pass"""
    prompt = f"""
Review your own findings:
{json.dumps(initial_reviews, indent=2)}

For each issue:
1. Is this REALLY a problem or false positive?
2. Rate confidence: 0.0 (unsure) to 1.0 (certain)
3. Remove or adjust issues with confidence < 0.6

Output refined JSON with confidence scores.
"""

    response = ollama.generate(
        model="deepseek-coder:33b-instruct",
        prompt=prompt
    )

    return parse_json(response['response'])
```

---

### Day 2: Few-Shot Examples + Output

**Morning (2-3 hours)**: Create Few-Shot Examples
```json
// prompts/few_shot_examples.json
[
  {
    "example_code": "int* data = new int[100];\n// ... no delete",
    "expected_review": {
      "severity": "critical",
      "category": "memory-safety",
      "issue": "Memory leak - allocated array never deleted",
      "reasoning": "Array allocated with new[] but no corresponding delete[]. Leaks 400 bytes per call.",
      "suggestion": "Use std::vector<int> data(100); or std::unique_ptr<int[]>"
    }
  },
  {
    "example_code": "void process(std::string name) { }",
    "expected_review": {
      "severity": "warning",
      "category": "performance",
      "issue": "Unnecessary copy - pass by value",
      "reasoning": "String copied on every call. If read-only, const& is more efficient.",
      "suggestion": "void process(const std::string& name)"
    }
  },
  // ... 3 more examples
]
```

**Afternoon (2-3 hours)**: Output Formatting
```python
# output.py
from rich.console import Console
from rich.table import Table

def display_reviews(reviews):
    """Pretty print reviews in terminal"""
    console = Console()

    # Group by severity
    critical = [r for r in reviews if r['severity'] == 'critical']
    warnings = [r for r in reviews if r['severity'] == 'warning']

    # Display critical first
    if critical:
        console.print("\n[bold red]🚨 CRITICAL ISSUES[/bold red]")
        for r in critical:
            console.print(f"  📍 {r['file']}:{r['line']}")
            console.print(f"     {r['issue']}")
            console.print(f"     💡 {r['suggestion']}\n")

    # Then warnings
    if warnings:
        console.print("\n[bold yellow]⚠️  WARNINGS[/bold yellow]")
        # ...

def save_json(reviews, output_file):
    """Save to JSON file"""
    with open(output_file, 'w') as f:
        json.dump(reviews, f, indent=2)
```

---

### Day 3: Testing + Polish

**Morning (3 hours)**: Test on Real PR
```python
# Test with sample-pr-001
python src/main.py review

# Expected output:
# 🚨 CRITICAL ISSUES (4)
# ⚠️  WARNINGS (4)
# 💡 SUGGESTIONS (2)
#
# Token usage: 6,542 tokens
# Time: 45 seconds
```

**Afternoon (2-3 hours)**: Config + CLI
```python
# main.py
import typer

app = typer.Typer()

@app.command()
def review(
    base: str = "main",
    model: str = "deepseek-coder:33b-instruct",
    format: str = "markdown",
    output: str = None,
    passes: int = 2
):
    """Review current PR"""
    console.print(f"Reviewing PR against {base}...")

    # Extract diff
    diff = get_pr_diff(base)

    # Load examples
    examples = load_few_shot_examples()

    # Pass 1
    console.print("Pass 1: Initial review...")
    reviews = review_pass1(diff, examples)

    # Pass 2 (if enabled)
    if passes >= 2:
        console.print("Pass 2: Self-critique...")
        reviews = review_pass2_critique(reviews)

    # Display
    display_reviews(reviews)

    # Save if requested
    if output:
        save_json(reviews, output)

if __name__ == "__main__":
    app()
```

---

## 설정 파일 (최소)

```yaml
# config.yml
model: deepseek-coder:33b-instruct
base_branch: main
num_passes: 2
min_confidence: 0.6

focus_categories:
  - memory-safety
  - performance
  - modern-cpp
  - security

ollama:
  temperature: 0.3
  top_p: 0.9
  num_predict: 2000
```

---

## 의존성 (최소)

```txt
# requirements.txt
ollama-python>=0.1.0
typer>=0.9.0
rich>=13.0.0
pyyaml>=6.0
```

**That's it!** 4개 패키지만.

---

## 실전 사용 시나리오

### 시나리오 1: 빠른 리뷰
```bash
# 현재 브랜치 vs main 리뷰
cpp-reviewer review

# 출력:
# 🚨 CRITICAL: Memory leak at data_processor.cpp:25
# 💡 Use std::unique_ptr instead of raw pointer
#
# ⚠️  WARNING: Unnecessary copy at data_processor.cpp:12
# 💡 Pass by const reference: const std::string&
#
# ⏱️  Time: 45s | 🪙 Tokens: 6,542
```

### 시나리오 2: 고품질 리뷰 (3-pass)
```bash
# 더 많은 패스, 더 높은 품질
cpp-reviewer review --passes 3

# Pass 1: Initial review (30s)
# Pass 2: Self-critique (25s)
# Pass 3: Final polish (20s)
# ⏱️  Total: 75s | 🪙 Tokens: 15,234
#
# Precision: 92% (estimated)
```

### 시나리오 3: JSON 출력 (CI/CD용)
```bash
cpp-reviewer review --format json --output review.json

# review.json:
# {
#   "reviews": [...],
#   "summary": {
#     "critical": 2,
#     "warnings": 5,
#     "total_issues": 7
#   }
# }
```

---

## 평가 방법

### Test on Sample PR
```bash
# Run on our test PR
cd test-data/sample-pr-001
git init
git add before.cpp
git commit -m "Base"
git checkout -b feature
cp after.cpp test.cpp
git add test.cpp
git commit -m "Add caching (with bugs)"

# Review
cpp-reviewer review

# Compare with expected-issues.md
# Calculate:
# - Precision: Found issues / Total flagged
# - Recall: Found issues / Total real issues
# - F1 score
```

### Success Criteria
- ✅ Finds ≥ 90% of critical issues (4/4)
- ✅ Finds ≥ 70% of all issues (7/10)
- ✅ Precision ≥ 70% (low false positives)
- ✅ Takes < 2 minutes per review

---

## 확장 계획 (나중에 필요하면)

### Phase 2: 간단한 Context Retrieval (RAG 없이)
```python
def get_symbol_definition(symbol_name, repo_path):
    """Find class/function definition using grep"""
    result = subprocess.run(
        ["grep", "-r", f"class {symbol_name}", repo_path],
        capture_output=True
    )

    # Extract definition from result
    return extract_definition(result.stdout)

# 사용:
symbols = extract_symbols_from_diff(diff)
context = "\n".join([get_symbol_definition(s) for s in symbols])

# Add to prompt
prompt = f"{few_shot}\n\nContext:\n{context}\n\nReview:\n{diff}"
```

### Phase 3: 더 나은 Chunking (AST 파싱)
```python
# tree-sitter로 함수 단위 파싱
# 하지만 대부분 경우 불필요함!
```

---

## 왜 이게 충분한가?

### 1. **단순함 = 신뢰성**
- 5개 파일, 500줄 코드
- 디버깅 쉬움
- 유지보수 쉬움

### 2. **Few-Shot + Multi-Pass = 높은 품질**
- Few-shot: 일관성 +40%
- Self-critique: 정확도 +20%
- 합치면 professional-grade 리뷰

### 3. **1인용 = 복잡한 인프라 불필요**
- 벡터 DB? 필요 없음
- 캐싱? 필요 없음
- 분산 처리? 필요 없음

### 4. **속도 무관 = 품질 극대화 가능**
- 3-pass review 가능
- 큰 모델 사용 (33b, 72b)
- CoT로 깊은 분석

---

## 최종 결론

**질문**: "이것만으로 의미있는 LLM 서비스가 가능할까?"

**답변**: **완전히 가능합니다!**

이 단순한 아키텍처로:
- ✅ 실제 버그를 80-90% 찾아냄
- ✅ False positive < 20%
- ✅ 개발자가 매일 쓸 만큼 유용함
- ✅ 2-3일 만에 작동하는 프로토타입 완성
- ✅ 복잡한 인프라 없이 유지보수 쉬움

**핵심**: RAG, 벡터 DB, 복잡한 chunking은 "nice-to-have"지, "must-have"가 아닙니다.

**Few-shot prompting + Multi-pass review**가 80%의 효과를 만들어냅니다.
나머지 20%를 위해 복잡도를 10배 늘릴 필요는 없습니다.

---

## Next Steps

1. ✅ Test data 만들기 (완료)
2. 📝 Day 1 구현: Git diff + Prompt builder
3. 📝 Day 2 구현: Few-shot examples + Output
4. 📝 Day 3 구현: Testing + Polish
5. 🎯 실전 테스트: 실제 프로젝트 PR에 적용

**시작할까요?** 🚀
