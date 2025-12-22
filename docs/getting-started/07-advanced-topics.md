# Chapter 07: 고급 주제

**예상 소요 시간**: 60분

---

## 🎯 학습 목표

- ✅ 새로운 언어 플러그인 만들기
- ✅ 커스텀 기법 구현
- ✅ GitHub Actions 통합

---

## 1. Python 플러그인 만들기

### Step 1: 플러그인 클래스 생성

```python
# plugins/python_plugin.py
from plugins.domain_plugin import DomainPlugin

class PythonPlugin(DomainPlugin):
    def get_file_extensions(self):
        return ['.py']
    
    def get_categories(self):
        return ['type-safety', 'imports', 'exception-handling']
    
    def get_few_shot_examples(self):
        return [
            {
                'code': 'x = None\nprint(x.upper())',
                'issues': [{
                    'category': 'type-safety',
                    'line': 2,
                    'description': 'AttributeError: NoneType'
                }]
            },
            # ... 4 more examples
        ]
```

### Step 2: Ground truth 생성

`experiments/ground_truth/python/` 디렉토리에 20개 예시 추가

### Step 3: 실험 실행

```bash
python -m cli.main experiment run --config experiments/configs/python_few_shot_5.yml
```

---

## 2. 커스텀 기법 구현

```python
# framework/techniques/my_technique.py
from framework.techniques.base import SinglePassTechnique

class MyTechnique(SinglePassTechnique):
    def analyze(self, request):
        # 1. 프롬프트 생성
        prompt = self._build_prompt(request.code)
        
        # 2. LLM 호출
        response = self.client.generate(prompt)
        
        # 3. 파싱
        issues = self.client.parse_issues_from_response(response)
        
        return AnalysisResult(issues=issues)
```

---

## 3. GitHub Actions 통합

```yaml
# .github/workflows/code-review.yml
name: AI Code Review
on: [pull_request]

jobs:
  review:
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
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const review = fs.readFileSync('review.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: review
            });
```

---

상세 내용은 [docs/architecture/DEVELOPER_GUIDE.md](../architecture/DEVELOPER_GUIDE.md) 참고.

---

**다음**: [Chapter 08: FAQ](08-faq.md) →
**이전**: [Chapter 06: 실험 실행](06-experiments.md) ←
