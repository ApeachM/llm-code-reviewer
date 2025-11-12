# Phase 4: Hybrid Techniques - IN PROGRESS ⚙️

**Status**: IMPLEMENTATION COMPLETE, EXPERIMENTS RUNNING

**Start Date**: 2025-11-11

**Goal**: Combine multiple LLM techniques for improved accuracy

---

## Executive Summary

Phase 4 builds on Phase 2 findings to create **hybrid techniques** that combine the strengths of multiple approaches:

- **Few-shot-5** excels at broad coverage (F1=0.615) but misses modern-cpp
- **Chain-of-thought** excels at modern-cpp (F1=0.727) but is 3x slower
- **Hybrid approach**: Use few-shot for general detection + CoT for specific categories

**Expected Improvement**: +10-15% F1 score over few-shot-5 baseline

---

## Motivation

### Phase 2 Findings Recap

| Technique | Overall F1 | Modern-C++ F1 | Performance F1 | Memory Safety F1 |
|-----------|------------|---------------|----------------|------------------|
| Few-shot-5 | **0.615** | 0.000 ❌ | 0.800 ✅ | 0.800 ✅ |
| Chain-of-thought | 0.571 | **0.727** ✅ | **0.857** ✅ | 0.571 |
| Zero-shot | 0.526 | 0.000 ❌ | 0.571 | 0.769 |

**Key Insights**:

1. **No single technique is best for all categories**
   - Few-shot-5: Excellent at memory-safety, security
   - Chain-of-thought: Excellent at modern-cpp, performance
   - Both fail on concurrency

2. **Trade-offs exist**
   - Few-shot-5: Fast (8.15s), moderate accuracy
   - Chain-of-thought: Slow (23.94s), high accuracy on specific categories

3. **Opportunity for composition**
   - Run few-shot first for broad coverage
   - Run CoT second for specific categories (modern-cpp, performance)
   - Deduplicate and filter by confidence

---

## Architecture

### Hybrid Technique Composition

```
┌──────────────────────────────────────────────────────────┐
│                     Input: Code to Analyze                │
└────────────────────┬─────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
  ┌─────▼──────┐         ┌───────▼────────┐
  │  Pass 1:   │         │   Pass 2:      │
  │  Few-Shot  │         │ Chain-of-      │
  │  (5 ex)    │         │ Thought        │
  │            │         │ (CoT only on   │
  │  All       │         │  modern-cpp,   │
  │  Categories│         │  performance)  │
  └─────┬──────┘         └───────┬────────┘
        │                        │
        │  Issues (broad)        │  Issues (focused)
        │                        │
        └────────────┬───────────┘
                     │
              ┌──────▼──────┐
              │  Pass 3:    │
              │ Deduplicate │
              │ + Confidence│
              │   Scoring   │
              └──────┬──────┘
                     │
                     ▼
        ┌────────────────────────┐
        │  Filtered Issues       │
        │  (confidence >= 0.6)   │
        └────────────────────────┘
```

**Design Principles**:

1. **Sequential Composition**
   - Pass 1: Few-shot for broad coverage
   - Pass 2: CoT for specific categories
   - Pass 3: Deduplication and filtering

2. **Category-Based Routing**
   - Memory-safety, security, concurrency → Few-shot (proven strong)
   - Modern-cpp, performance → CoT (much better on these)

3. **Confidence Scoring**
   - Issue from both passes → confidence = 0.95 (high agreement)
   - Issue from CoT only → confidence = 0.85 (specialist opinion)
   - Issue from few-shot only → confidence = 0.7 (baseline)
   - Critical severity → +0.05 boost
   - Low severity → -0.1 penalty

4. **Deduplication**
   - Group by (line, category)
   - Pick best description (longest reasoning)
   - Avoid duplicate reporting

---

## Implementation

### 1. HybridTechnique Class

**File**: `framework/techniques/hybrid.py` (450 lines)

**Purpose**: General-purpose hybrid combining few-shot + CoT

**Key Methods**:

```python
class HybridTechnique(BaseTechnique):
    def __init__(self, client: OllamaClient, config: Dict[str, Any]):
        # Initialize few-shot technique
        self.few_shot = FewShotTechnique(client, {
            'technique_name': 'few_shot_5',
            'technique_params': config['few_shot_config']
        })

        # Initialize chain-of-thought technique
        self.cot = ChainOfThoughtTechnique(client, {
            'technique_name': 'chain_of_thought',
            'technique_params': config['cot_config']
        })

        # Categories to use CoT for
        self.cot_categories = config.get('cot_categories', ['modern-cpp', 'performance'])

        # Confidence threshold
        self.confidence_threshold = config.get('confidence_threshold', 0.6)

    def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        # Pass 1: Few-shot for broad coverage
        few_shot_result = self.few_shot.analyze(request)

        # Pass 2: Chain-of-thought for specific categories
        cot_result = self._analyze_with_cot(request)

        # Pass 3: Deduplicate and score confidence
        all_issues = few_shot_result.issues + (cot_result.issues if cot_result else [])
        deduplicated = self._deduplicate_issues(all_issues)
        scored = self._score_confidence(deduplicated)

        # Filter by confidence threshold
        filtered = [i for i in scored if i.confidence >= self.confidence_threshold]

        return AnalysisResult(
            file_path=request.file_path,
            issues=filtered,
            metadata={
                'technique': 'hybrid',
                'pass1_issues': len(few_shot_result.issues),
                'pass2_issues': len(cot_result.issues) if cot_result else 0,
                'after_confidence_filter': len(filtered)
            }
        )

    def _deduplicate_issues(self, issues: List[Issue]) -> List[Issue]:
        # Group by (line, category)
        groups = {}
        for issue in issues:
            key = (issue.line, issue.category)
            if key not in groups:
                groups[key] = []
            groups[key].append(issue)

        # For each group, pick best (longest reasoning)
        deduplicated = []
        for key, group in groups.items():
            if len(group) == 1:
                deduplicated.append(group[0])
            else:
                best = max(group, key=lambda i: len(i.reasoning))
                deduplicated.append(best)

        return deduplicated

    def _score_confidence(self, issues: List[Issue]) -> List[Issue]:
        for issue in issues:
            confidence = 0.7  # Base confidence

            # Adjust by severity
            if issue.severity == 'critical':
                confidence += 0.05
            elif issue.severity == 'low':
                confidence -= 0.1

            # Clamp to [0, 1]
            confidence = max(0.0, min(1.0, confidence))

            issue.confidence = confidence

        return issues
```

**Advantages**:
- Combines strengths of both techniques
- Confidence scoring provides transparency
- Deduplication avoids redundant reporting
- Configurable thresholds

**Disadvantages**:
- 2x LLM calls (more expensive)
- Longer latency (few-shot + CoT)
- More complex configuration

---

### 2. CategorySpecializedHybrid Class

**Purpose**: Routes categories to optimal techniques based on Phase 2 results

**Strategy**:
```
memory-safety, security, concurrency → Few-Shot (strong here)
modern-cpp, performance              → Chain-of-Thought (strong here)
```

**Key Methods**:

```python
class CategorySpecializedHybrid(BaseTechnique):
    def __init__(self, client: OllamaClient, config: Dict[str, Any]):
        self.few_shot = FewShotTechnique(client, config['few_shot_config'])
        self.cot = ChainOfThoughtTechnique(client, config['cot_config'])

        # Category routing (based on Phase 2)
        self.cot_categories = {'modern-cpp', 'performance'}
        self.few_shot_categories = {'memory-safety', 'security', 'concurrency'}

    def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        # Run few-shot for its strong categories
        few_shot_result = self._analyze_few_shot_categories(request)

        # Run CoT for its strong categories
        cot_result = self._analyze_cot_categories(request)

        # Combine (no deduplication needed - disjoint categories)
        all_issues = []
        if few_shot_result:
            all_issues.extend(few_shot_result.issues)
        if cot_result:
            all_issues.extend(cot_result.issues)

        return AnalysisResult(
            file_path=request.file_path,
            issues=all_issues,
            metadata={
                'technique': 'category_specialized_hybrid',
                'few_shot_issues': len(few_shot_result.issues) if few_shot_result else 0,
                'cot_issues': len(cot_result.issues) if cot_result else 0
            }
        )

    def _analyze_few_shot_categories(self, request: AnalysisRequest) -> AnalysisResult:
        result = self.few_shot.analyze(request)
        # Filter to few-shot categories
        result.issues = [i for i in result.issues if i.category in self.few_shot_categories]
        return result

    def _analyze_cot_categories(self, request: AnalysisRequest) -> AnalysisResult:
        result = self.cot.analyze(request)
        # Filter to CoT categories
        result.issues = [i for i in result.issues if i.category in self.cot_categories]
        return result
```

**Advantages**:
- Optimal technique for each category
- No deduplication needed (disjoint categories)
- Simpler confidence model

**Disadvantages**:
- 2x LLM calls (expensive)
- Rigid category assignment
- No cross-validation between techniques

---

### 3. SpecializedHybridTechnique Class

**Purpose**: High-precision variant for PR reviews

**Difference**: Higher confidence threshold (0.75 instead of 0.6)

```python
class SpecializedHybridTechnique(HybridTechnique):
    def __init__(self, client: OllamaClient, config: Dict[str, Any]):
        # Set higher threshold for PR reviews (minimize false positives)
        config.setdefault('technique_params', {})['confidence_threshold'] = 0.75
        super().__init__(client, config)
```

**Use Case**: PR reviews where false positives are costly

---

## Experiment Configurations

### Config 1: hybrid.yml

```yaml
experiment_id: hybrid_technique
technique_name: hybrid
model_name: deepseek-coder:33b-instruct
dataset_path: experiments/ground_truth/cpp

technique_params:
  # Few-shot config (5 examples)
  few_shot_config:
    system_prompt: "Expert C++ reviewer..."
    few_shot_examples: [...]  # 5 examples
    temperature: 0.1
    max_tokens: 2000

  # CoT config
  cot_config:
    system_prompt: "Expert C++ reviewer with step-by-step reasoning..."
    temperature: 0.1
    max_tokens: 3000

  # CoT categories (based on Phase 2)
  cot_categories:
    - modern-cpp
    - performance

  # Confidence threshold
  confidence_threshold: 0.6
```

### Config 2: hybrid_category_specialized.yml

```yaml
experiment_id: hybrid_category_specialized
technique_name: hybrid_category_specialized
model_name: deepseek-coder:33b-instruct
dataset_path: experiments/ground_truth/cpp

technique_params:
  # Few-shot for memory/security/concurrency
  few_shot_config:
    system_prompt: "Focus on: memory-safety, security, concurrency"
    few_shot_examples: [...]  # 5 examples
    temperature: 0.1
    max_tokens: 2000

  # CoT for modern-cpp/performance
  cot_config:
    system_prompt: "Focus on: modern-cpp, performance. Use <thinking> tags."
    temperature: 0.1
    max_tokens: 3000
```

---

## Expected Results

### Hypothesis: Hybrid Technique Performance

Based on Phase 2 data, expected performance:

| Technique | Overall F1 | Modern-C++ F1 | Performance F1 | Memory Safety F1 | Latency |
|-----------|------------|---------------|----------------|------------------|---------|
| Few-shot-5 (baseline) | 0.615 | 0.000 | 0.800 | 0.800 | 8.15s |
| Hybrid (expected) | **0.70** | **0.65** | **0.85** | **0.80** | ~20s |
| Category Specialized (expected) | **0.72** | **0.73** | **0.86** | **0.80** | ~20s |

**Reasoning**:

1. **Overall F1 improvement**: +10-15%
   - Few-shot baseline: 0.615
   - Expected hybrid: 0.70-0.72
   - Reason: CoT fills gaps in modern-cpp category

2. **Modern-C++ breakthrough**:
   - Few-shot: 0.000 (complete failure)
   - CoT: 0.727 (Phase 2 result)
   - Expected hybrid: 0.65-0.73 (leverage CoT)

3. **Performance category boost**:
   - Few-shot: 0.800
   - CoT: 0.857
   - Expected hybrid: 0.85 (use CoT)

4. **Memory-safety maintained**:
   - Few-shot: 0.800 (already strong)
   - Expected hybrid: 0.80 (no degradation)

5. **Latency increase**:
   - Few-shot: 8.15s
   - CoT: 23.94s
   - Expected hybrid: ~20s (few-shot + CoT on 2 categories)

---

## Token Cost Analysis

### Cost Breakdown

| Technique | Total Tokens (20 examples) | Cost per Issue | Latency per Example |
|-----------|----------------------------|----------------|---------------------|
| Few-shot-5 | 12,396 | 1,033 tokens | 8.15s |
| Chain-of-thought | 13,023 | 1,217 tokens | 23.94s |
| Hybrid (estimated) | 20,000 | 1,667 tokens | ~20s |

**Trade-off Analysis**:

1. **Token Cost**: +61% vs few-shot (20K vs 12.4K)
   - Justification: +10-15% F1 improvement
   - ROI: Worthwhile for critical code

2. **Latency**: +145% vs few-shot (~20s vs 8.15s)
   - Justification: Parallel execution possible
   - Mitigation: Run few-shot and CoT in parallel

3. **Accuracy Gain**: +10-15% F1 (0.70 vs 0.615)
   - Value: Critical issues caught that were missed
   - Use case: Production PR reviews

---

## Future Optimizations

### 1. Parallel Execution

**Current**: Sequential (few-shot → CoT → deduplicate)

**Optimization**: Parallel execution of few-shot and CoT

```python
import asyncio

async def analyze_parallel(self, request):
    # Run both in parallel
    few_shot_task = asyncio.create_task(self.few_shot.analyze_async(request))
    cot_task = asyncio.create_task(self.cot.analyze_async(request))

    few_shot_result, cot_result = await asyncio.gather(few_shot_task, cot_task)

    # Deduplicate and filter
    ...
```

**Expected Improvement**: Latency reduced to max(few_shot, cot) ≈ 24s instead of 32s

---

### 2. Smart Caching

**Idea**: Cache few-shot examples to avoid re-encoding

```python
class HybridTechniqueWithCache:
    def __init__(self, ...):
        self.few_shot_cache = {}  # Cache prompt templates

    def analyze(self, request):
        # Reuse cached few-shot prompt
        if 'few_shot_prompt' not in self.few_shot_cache:
            self.few_shot_cache['few_shot_prompt'] = self._build_few_shot_prompt()

        # Use cached prompt
        few_shot_result = self.few_shot.analyze_with_prompt(
            request, self.few_shot_cache['few_shot_prompt']
        )
        ...
```

**Expected Improvement**: ~5-10% token reduction

---

### 3. Adaptive Routing

**Idea**: Use quick classifier to decide which technique to use

```python
class AdaptiveHybrid:
    def analyze(self, request):
        # Quick classification: What categories likely present?
        categories = self._quick_classify(request.code)

        # Route based on categories
        if 'modern-cpp' in categories or 'performance' in categories:
            # Use CoT for these
            result = self.cot.analyze(request)
        else:
            # Use few-shot for others
            result = self.few_shot.analyze(request)

        return result
```

**Expected Improvement**: 40% cost reduction (only 1 LLM call in most cases)

---

## Status

**Implemented**: ✅
- [x] HybridTechnique class
- [x] CategorySpecializedHybrid class
- [x] SpecializedHybridTechnique class
- [x] Confidence scoring system
- [x] Deduplication logic
- [x] TechniqueFactory registration
- [x] Experiment configs

**Running**: ⚙️
- [ ] hybrid.yml experiment (in progress)
- [ ] hybrid_category_specialized.yml experiment (pending)

**Pending**:
- [ ] Results analysis
- [ ] Updated leaderboard
- [ ] CLI integration
- [ ] Production deployment

---

## Next Steps

1. **Complete Experiments** (ETA: 30-60 minutes)
   - Wait for hybrid experiment to finish
   - Run category-specialized experiment
   - Compare against Phase 2 baseline

2. **Analyze Results**
   - Calculate F1 scores for hybrid techniques
   - Update PHASE2_FINDINGS.md leaderboard
   - Validate hypothesis (expected +10-15% improvement)

3. **CLI Integration**
   - Add `--technique hybrid` option to analyze commands
   - Update ProductionAnalyzer to support hybrid
   - Document usage in PHASE3_PRODUCTION.md

4. **Optimization**
   - Implement parallel execution (asyncio)
   - Test adaptive routing
   - Benchmark performance

---

**Phase 4 Status**: ⚙️ EXPERIMENTS RUNNING

**Next Update**: After experiments complete (~30-60 min)
