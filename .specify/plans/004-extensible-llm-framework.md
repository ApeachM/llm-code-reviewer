# Extensible LLM Engineering Framework: C++ → RTL → Chip Design

**Vision**: LLM engineering 정수를 담은 확장 가능한 프레임워크
**Path**: C++ PR Review → RTL Analysis → Design Methodology → Power Optimization

## 🎯 전략적 목표

### Phase 1: C++ PR Review (Pilot)
- **목적**: LLM engineering 기법 검증 및 프레임워크 구축
- **학습**: 코드 분석, 버그 찾기, 제안 생성
- **기간**: 1-2주

### Phase 2: RTL Code Analysis (확장)
- **목적**: Verilog/SystemVerilog로 도메인 확장
- **학습**: 하드웨어 특화 분석, timing/power 이슈
- **기간**: 2-3주

### Phase 3: Chip Design Services (최종)
- **목적**: High-value 서비스 제공
- **기능**: Design methodology, power reduction, optimization
- **기간**: 4-6주

---

## 🏗️ 도메인 독립적 아키텍처

### 핵심 컨셉: Plugin-Based LLM Engineering Framework

```
┌───────────────────────────────────────────────────────────┐
│         DOMAIN-AGNOSTIC LLM ENGINE (Core)                 │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  LLM Engineering Techniques (Reusable)              │  │
│  │  - Few-shot prompt management                       │  │
│  │  - Multi-pass review orchestration                  │  │
│  │  - Self-critique & refinement                       │  │
│  │  - Chain-of-thought prompting                       │  │
│  │  - Structured output parsing                        │  │
│  │  - Token budget management                          │  │
│  │  - Quality metrics & evaluation                     │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────┬─────────────────────────────────────────┘
                  │
                  │ Plugin Interface
                  │
    ┌─────────────┼─────────────┬─────────────────┐
    │             │             │                 │
    ▼             ▼             ▼                 ▼
┌────────┐   ┌────────┐   ┌─────────┐   ┌──────────────┐
│  C++   │   │  RTL   │   │  Power  │   │  Design      │
│ Plugin │   │ Plugin │   │ Plugin  │   │  Methodology │
│        │   │        │   │         │   │  Plugin      │
└────────┘   └────────┘   └─────────┘   └──────────────┘

Each Plugin Provides:
- Domain-specific knowledge (few-shot examples)
- Code parser (AST/pattern matching)
- Issue categories (bug types)
- Evaluation criteria (what's important)
```

---

## 🧩 Core Framework Components

### 1. Domain Plugin Interface

```python
# framework/domain_plugin.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any

class DomainPlugin(ABC):
    """
    Domain-specific plugin interface.
    Each domain (C++, RTL, Power, etc.) implements this.
    """

    @abstractmethod
    def get_few_shot_examples(self) -> List[Dict]:
        """Return domain-specific few-shot examples"""
        pass

    @abstractmethod
    def parse_code(self, code: str) -> Dict[str, Any]:
        """Parse code into analyzable units (functions, modules, etc.)"""
        pass

    @abstractmethod
    def get_issue_categories(self) -> List[str]:
        """Return domain-specific issue categories"""
        # C++: ["memory-safety", "performance", "modern-cpp"]
        # RTL: ["timing", "power", "cdc", "synthesis", "formal"]
        pass

    @abstractmethod
    def get_evaluation_metrics(self) -> Dict[str, callable]:
        """Return domain-specific evaluation functions"""
        pass

    @abstractmethod
    def format_prompt(self, code: str, context: Dict) -> str:
        """Format code and context into domain-specific prompt"""
        pass

    @abstractmethod
    def validate_suggestion(self, suggestion: str) -> bool:
        """Validate if suggestion is reasonable for this domain"""
        pass
```

### 2. LLM Technique Engine (Reusable)

```python
# framework/llm_engine.py

class LLMEngine:
    """
    Domain-agnostic LLM engineering techniques.
    Reusable across all domains.
    """

    def __init__(self, plugin: DomainPlugin):
        self.plugin = plugin
        self.ollama = OllamaClient()

    def multi_pass_review(self, code: str, num_passes: int = 3):
        """
        Multi-pass review with progressive refinement.
        Works for ANY domain.
        """
        results = []

        # Pass 1: Initial analysis
        prompt1 = self._build_initial_prompt(code)
        response1 = self.ollama.generate(prompt1)
        results.append(self._parse_response(response1))

        # Pass 2: Self-critique
        prompt2 = self._build_critique_prompt(response1)
        response2 = self.ollama.generate(prompt2)
        results.append(self._parse_response(response2))

        # Pass 3: Domain expert validation
        prompt3 = self._build_expert_prompt(response2)
        response3 = self.ollama.generate(prompt3)
        results.append(self._parse_response(response3))

        return self._aggregate_results(results)

    def few_shot_learning(self, code: str, focus: str = None):
        """
        Few-shot prompting with domain examples.
        Examples come from plugin.
        """
        examples = self.plugin.get_few_shot_examples()
        if focus:
            examples = [e for e in examples if e['category'] == focus]

        prompt = self._build_few_shot_prompt(examples, code)
        return self.ollama.generate(prompt)

    def chain_of_thought(self, code: str, complexity: str = "high"):
        """
        CoT prompting for complex analysis.
        Depth depends on complexity.
        """
        if complexity == "high":
            prompt = f"""
Analyze this code step-by-step:

Step 1: What is the purpose of this code?
Step 2: What are potential issues?
Step 3: For each issue, why is it problematic?
Step 4: What are specific fixes?

Code:
{code}
"""
        else:
            prompt = f"Analyze this code:\n{code}"

        return self.ollama.generate(prompt)

    def structured_output(self, code: str, schema: Dict):
        """
        Force structured output with validation.
        Schema comes from plugin.
        """
        prompt = f"""
Output MUST be valid JSON matching this schema:
{json.dumps(schema, indent=2)}

Code to analyze:
{code}

Output JSON:
"""
        max_retries = 3
        for i in range(max_retries):
            response = self.ollama.generate(prompt)
            try:
                parsed = json.loads(response)
                jsonschema.validate(parsed, schema)
                return parsed
            except:
                if i < max_retries - 1:
                    prompt += f"\n\nERROR: Invalid JSON. Try again."
                else:
                    raise ValueError("Failed to get valid JSON")
```

### 3. Evaluation Framework

```python
# framework/evaluation.py

class EvaluationFramework:
    """
    Measure effectiveness of LLM techniques.
    Track improvements across iterations.
    """

    def __init__(self, plugin: DomainPlugin):
        self.plugin = plugin
        self.results_db = []

    def run_experiment(self, technique: str, test_cases: List):
        """
        Run specific LLM technique on test cases.
        Measure: precision, recall, token usage, time.
        """
        results = {
            "technique": technique,
            "test_cases": [],
            "metrics": {}
        }

        for test in test_cases:
            ground_truth = test['expected_issues']

            # Run technique
            start_time = time.time()
            found_issues = self._apply_technique(technique, test['code'])
            elapsed = time.time() - start_time

            # Calculate metrics
            precision = self._calc_precision(found_issues, ground_truth)
            recall = self._calc_recall(found_issues, ground_truth)
            f1 = 2 * (precision * recall) / (precision + recall)

            results['test_cases'].append({
                "name": test['name'],
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "time": elapsed,
                "tokens": found_issues['token_usage']
            })

        # Aggregate
        results['metrics'] = {
            "avg_precision": np.mean([t['precision'] for t in results['test_cases']]),
            "avg_recall": np.mean([t['recall'] for t in results['test_cases']]),
            "avg_f1": np.mean([t['f1'] for t in results['test_cases']]),
            "total_time": sum([t['time'] for t in results['test_cases']]),
            "total_tokens": sum([t['tokens'] for t in results['test_cases']])
        }

        self.results_db.append(results)
        return results

    def compare_techniques(self, techniques: List[str]):
        """
        A/B test multiple techniques.
        Generate comparison report.
        """
        comparison = {}
        for tech in techniques:
            results = [r for r in self.results_db if r['technique'] == tech]
            if results:
                comparison[tech] = results[-1]['metrics']

        # Generate report
        self._generate_comparison_report(comparison)
        return comparison

    def track_improvements(self):
        """
        Track how techniques improve over time.
        Useful for RLHF-style iteration.
        """
        timeline = {}
        for result in sorted(self.results_db, key=lambda x: x.get('timestamp', 0)):
            tech = result['technique']
            if tech not in timeline:
                timeline[tech] = []
            timeline[tech].append(result['metrics'])

        return timeline
```

---

## 🔌 Domain-Specific Plugins

### Plugin 1: C++ Code Review

```python
# plugins/cpp_plugin.py

class CppPlugin(DomainPlugin):
    def get_few_shot_examples(self):
        return [
            {
                "category": "memory-safety",
                "code": "int* p = new int(10); // no delete",
                "issue": "Memory leak",
                "suggestion": "Use std::unique_ptr<int> p = std::make_unique<int>(10);"
            },
            {
                "category": "performance",
                "code": "void foo(std::string s) { }",
                "issue": "Unnecessary copy",
                "suggestion": "void foo(const std::string& s) { }"
            },
            # ... more examples
        ]

    def get_issue_categories(self):
        return [
            "memory-safety",
            "performance",
            "modern-cpp",
            "concurrency",
            "security",
            "const-correctness"
        ]

    def parse_code(self, code: str):
        # Use tree-sitter or simple regex
        functions = self._extract_functions(code)
        classes = self._extract_classes(code)
        return {"functions": functions, "classes": classes}

    def format_prompt(self, code: str, context: Dict):
        examples = self.get_few_shot_examples()
        return f"""
You are a C++ expert. Review code for: {', '.join(self.get_issue_categories())}.

Examples of good reviews:
{self._format_examples(examples)}

Code to review:
{code}

Output JSON with: file, line, category, severity, issue, suggestion
"""
```

### Plugin 2: RTL Code Analysis (Future)

```python
# plugins/rtl_plugin.py

class RTLPlugin(DomainPlugin):
    def get_few_shot_examples(self):
        return [
            {
                "category": "timing",
                "code": """
always @(posedge clk) begin
    data_out <= data_in + other_data + third_data + fourth_data;
end
""",
                "issue": "Long combinational path - may fail timing",
                "suggestion": "Pipeline the addition:\nalways @(posedge clk) begin\n  stage1 <= data_in + other_data;\n  stage2 <= stage1 + third_data;\n  data_out <= stage2 + fourth_data;\nend",
                "reasoning": "Multiple additions in one cycle create long critical path. Pipelining spreads computation across cycles."
            },
            {
                "category": "cdc",
                "code": """
always @(posedge clk_a) begin
    signal_a <= data_in;
end

always @(posedge clk_b) begin
    data_out <= signal_a;  // CDC violation!
end
""",
                "issue": "Clock domain crossing without synchronizer",
                "suggestion": "Add 2-flop synchronizer:\nreg [1:0] sync;\nalways @(posedge clk_b) begin\n  sync <= {sync[0], signal_a};\n  data_out <= sync[1];\nend",
                "reasoning": "Crossing clock domains without synchronization causes metastability. Two-stage synchronizer required."
            },
            {
                "category": "power",
                "code": """
always @(posedge clk) begin
    counter <= counter + 1;  // Always toggles
end
""",
                "issue": "Excessive switching activity - high dynamic power",
                "suggestion": "Add enable signal:\nalways @(posedge clk) begin\n  if (counter_enable)\n    counter <= counter + 1;\nend",
                "reasoning": "Counter toggles every cycle even when not needed. Clock gating or enable reduces power."
            },
            {
                "category": "synthesis",
                "code": """
assign result = (sel == 0) ? a :
                (sel == 1) ? b :
                (sel == 2) ? c :
                (sel == 3) ? d : 0;
""",
                "issue": "Priority mux - inefficient for FPGA",
                "suggestion": "Use case statement for parallel mux:\nalways @(*) begin\n  case(sel)\n    2'd0: result = a;\n    2'd1: result = b;\n    2'd2: result = c;\n    2'd3: result = d;\n    default: result = 0;\n  endcase\nend",
                "reasoning": "Nested ternary creates priority chain. Case statement synthesizes to parallel mux with better timing."
            },
            {
                "category": "formal",
                "code": """
always @(posedge clk) begin
    if (reset)
        state <= IDLE;
    else
        state <= next_state;
end
// No default case in next_state logic
""",
                "issue": "FSM may enter undefined state",
                "suggestion": "Add default case:\nalways @(*) begin\n  case(state)\n    IDLE: ...\n    BUSY: ...\n    default: next_state = IDLE;  // Safety\n  endcase\nend",
                "reasoning": "Without default, state could become X or enter invalid encoding. Formal verification will flag this."
            }
        ]

    def get_issue_categories(self):
        return [
            "timing",           # Timing violations, critical paths
            "power",            # Dynamic/static power issues
            "cdc",              # Clock domain crossing
            "synthesis",        # Synthesis inefficiencies
            "formal",           # Formal verification hints
            "area",             # Resource utilization
            "linting",          # RTL style/best practices
            "functionality"     # Logical bugs
        ]

    def parse_code(self, code: str):
        # Parse Verilog/SystemVerilog
        modules = self._extract_modules(code)
        always_blocks = self._extract_always_blocks(code)
        signals = self._extract_signals(code)

        return {
            "modules": modules,
            "always_blocks": always_blocks,
            "signals": signals,
            "clock_domains": self._identify_clock_domains(always_blocks)
        }

    def format_prompt(self, code: str, context: Dict):
        examples = self.get_few_shot_examples()
        return f"""
You are an RTL design expert specializing in: {', '.join(self.get_issue_categories())}.

Examples of expert RTL reviews:
{self._format_examples(examples)}

Module to review:
{code}

Focus on:
- Timing: Will this meet timing? Any long combinational paths?
- Power: Unnecessary switching? Missing clock gating?
- CDC: Any clock domain crossings? Are they synchronized?
- Synthesis: Will this synthesize efficiently? Any problematic constructs?

Output JSON with: module, line, category, severity, issue, reasoning, suggestion
"""
```

### Plugin 3: Power Optimization (Future)

```python
# plugins/power_plugin.py

class PowerOptimizationPlugin(DomainPlugin):
    def get_few_shot_examples(self):
        return [
            {
                "category": "clock-gating",
                "code": "// High-activity datapath always clocking",
                "issue": "Missing clock gating opportunity",
                "suggestion": "Implement automatic clock gating with enable signals",
                "impact": "30-40% dynamic power reduction in datapath"
            },
            {
                "category": "voltage-scaling",
                "code": "// All blocks at same voltage",
                "issue": "No multi-voltage design",
                "suggestion": "Use low-Vt for critical paths, high-Vt for non-critical",
                "impact": "15-25% leakage power reduction"
            },
            # ... more power optimization patterns
        ]

    def get_issue_categories(self):
        return [
            "clock-gating",
            "power-gating",
            "voltage-scaling",
            "frequency-scaling",
            "operand-isolation",
            "memory-optimization",
            "switching-activity"
        ]
```

---

## 📊 Experimental Design (LLM Engineering 정수)

### Experiment Matrix: Measure Everything

```python
# experiments/experiment_matrix.py

TECHNIQUES = [
    "baseline",              # Zero-shot, single pass
    "few_shot_3",           # 3 examples
    "few_shot_5",           # 5 examples
    "few_shot_10",          # 10 examples
    "multi_pass_2",         # 2-pass review
    "multi_pass_3",         # 3-pass review
    "chain_of_thought",     # CoT prompting
    "self_critique",        # Self-refinement
    "multi_agent",          # Specialized agents
    "few_shot_3 + multi_pass_2",  # Combination
    "few_shot_5 + cot + self_critique",  # Best combo
]

MODELS = [
    "deepseek-coder:7b",
    "deepseek-coder:33b",
    "qwen2.5:14b",
    "qwen2.5:72b",
    "starcoder2:15b"
]

DOMAINS = [
    "cpp",
    "rtl",    # Later
    "power"   # Later
]

def run_full_experiment():
    """
    Run every technique x model x domain combination.
    Generate comprehensive report.
    """
    results = []

    for domain in DOMAINS:
        plugin = load_plugin(domain)
        test_cases = load_test_cases(domain)

        for model in MODELS:
            for technique in TECHNIQUES:
                print(f"Running: {domain} / {model} / {technique}")

                result = {
                    "domain": domain,
                    "model": model,
                    "technique": technique,
                    "metrics": {}
                }

                # Run on all test cases
                for test in test_cases:
                    metrics = evaluate(plugin, model, technique, test)
                    result['metrics'][test['name']] = metrics

                results.append(result)

    # Generate comprehensive report
    generate_report(results)
    find_best_combinations(results)

    return results
```

### Metrics to Track

```python
METRICS = {
    # Accuracy
    "precision": "% of flagged issues that are real",
    "recall": "% of real issues that are flagged",
    "f1_score": "Harmonic mean of precision and recall",
    "critical_recall": "% of critical issues found",

    # Efficiency
    "token_efficiency": "Issues found per 1K tokens",
    "time_per_review": "Seconds to complete review",
    "cost_per_review": "Token cost (if using paid API)",

    # Quality
    "actionability": "% of suggestions that are implementable",
    "suggestion_quality": "Human rating of suggestion quality (1-5)",
    "false_positive_rate": "% of flagged issues that are false",

    # Robustness
    "parsing_success_rate": "% of outputs that parse correctly",
    "consistency": "Agreement across multiple runs (same code)",
    "coverage": "% of code that receives feedback"
}
```

---

## 🛣️ Development Roadmap

### Week 1-2: Framework + C++ Plugin

**Goal**: Build reusable framework, validate with C++

**Tasks**:
1. Implement core framework
   - `DomainPlugin` interface
   - `LLMEngine` with techniques
   - `EvaluationFramework`

2. Implement C++ plugin
   - Few-shot examples (10+)
   - Issue categories
   - Prompt templates

3. Run experiments
   - Test all techniques on sample-pr-001
   - Measure metrics
   - Find best combinations

**Deliverable**: Working C++ reviewer + experimental data

---

### Week 3-4: RTL Plugin + Domain Transfer

**Goal**: Extend to RTL, measure transfer learning

**Tasks**:
1. Create RTL test dataset
   - 10 Verilog modules with known issues
   - Timing, power, CDC, synthesis bugs
   - Ground truth annotations

2. Implement RTL plugin
   - RTL-specific few-shot examples (15+)
   - Verilog parser (tree-sitter-verilog)
   - RTL-specific prompt engineering

3. Measure domain transfer
   - Which techniques transfer well C++ → RTL?
   - What's RTL-specific?
   - Update framework based on learnings

**Deliverable**: RTL code analyzer + transfer learning insights

---

### Week 5-6: Power Optimization Plugin

**Goal**: High-value chip design service

**Tasks**:
1. Power optimization knowledge base
   - Clock gating patterns
   - Voltage scaling strategies
   - Memory optimization techniques
   - 50+ few-shot examples

2. Implement power plugin
   - Power-specific analysis
   - Multi-level suggestions (RTL, arch, tools)
   - ROI estimation (% power reduction)

3. Advanced LLM techniques
   - Multi-agent: Architecture expert + RTL expert + Tools expert
   - Retrieval: Search IEEE papers for state-of-art techniques
   - Synthesis: Generate optimized RTL from specs

**Deliverable**: Power optimization service

---

### Week 7-8: Design Methodology Service

**Goal**: Ultimate high-value service

**Capabilities**:
- Analyze entire chip design flow
- Suggest methodology improvements
- Recommend EDA tool settings
- Generate design checklists
- Predict potential issues early

**This is where the real value is!**

---

## 🎓 LLM Engineering Techniques Showcase

### 1. Progressive Refinement

```
Pass 1: Broad analysis (find obvious issues)
Pass 2: Deep dive (complex interactions)
Pass 3: Self-critique (reduce false positives)
Pass 4: Expert validation (domain-specific checks)
```

### 2. Multi-Agent Collaboration

```
Agent 1 (Timing Expert): Focuses on timing closure
Agent 2 (Power Expert): Focuses on power optimization
Agent 3 (Formal Expert): Focuses on correctness
Moderator: Aggregates and prioritizes
```

### 3. RAG with Domain Knowledge

```
Vector DB:
- IEEE papers on power optimization
- Internal design guidelines
- Best practice examples
- Known bug patterns

Retrieval: Find most relevant knowledge for each analysis
```

### 4. Active Learning

```
1. Review code
2. User provides feedback (good/bad suggestions)
3. Update few-shot examples
4. Improve prompts
5. Re-run evaluation
6. Repeat
```

### 5. Confidence-Based Filtering

```
LLM outputs confidence scores:
- 0.9-1.0: High confidence, show immediately
- 0.7-0.9: Medium, flag for review
- <0.7: Low, filter out or mark as uncertain
```

---

## 📈 Success Metrics

### C++ Phase (Week 1-2)
- ✅ Precision >75%
- ✅ Critical recall >90%
- ✅ Token efficiency >0.5 issues/1K tokens
- ✅ Framework supports plugin architecture

### RTL Phase (Week 3-4)
- ✅ RTL precision >70%
- ✅ Finds timing/power/CDC issues
- ✅ Techniques transfer with <10% quality loss
- ✅ Framework works for multiple domains

### Power Phase (Week 5-6)
- ✅ Suggests actionable power optimizations
- ✅ Estimates ROI (% power reduction)
- ✅ Multi-agent improves quality >20%
- ✅ Production-ready service

### Design Methodology Phase (Week 7-8)
- ✅ Provides high-level design guidance
- ✅ Integrated with EDA tools
- ✅ Used by real chip designers
- ✅ Demonstrates LLM engineering mastery

---

## 💎 Unique Value Propositions

### For Investors/Users:
"AI-powered chip design assistant that gets smarter over time"

### For Engineers:
"Framework demonstrating state-of-art LLM engineering techniques"

### For Academia:
"Comprehensive study of LLM techniques in hardware design domain"

### For You:
"Portfolio piece showing deep LLM engineering expertise, ready for RTL/chip design scaling"

---

## 🚀 Next Steps

1. **Start with Framework** (Day 1-3)
   - Build plugin architecture
   - Implement LLM technique engine
   - Create evaluation framework

2. **C++ Plugin + Experiments** (Day 4-7)
   - Implement C++ plugin
   - Run experiments on sample-pr-001
   - Document findings

3. **Plan RTL Extension** (Day 8-10)
   - Design RTL plugin interface
   - Collect RTL examples
   - Prepare test dataset

이제 "단순한 도구"가 아니라 **"확장 가능한 LLM engineering 프레임워크"**입니다.

시작할까요?
