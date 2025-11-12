================================================================================
SPEC-KIT 사용 가이드 (GitHub Spec-Kit)
================================================================================

프로젝트: LLM Engineering Framework for C++ → RTL → Chip Design
목표: 확장 가능한 도메인 독립적 LLM 프레임워크 구축

================================================================================
1. /speckit.constitution
================================================================================

용도: 프로젝트의 핵심 원칙과 거버넌스 정의

입력 예시:
-----------
/speckit.constitution

또는 구체적 원칙 제시:

/speckit.constitution Our project has 6 core principles:
1. Privacy-First: All processing must use local LLM via Ollama
2. Domain-Agnostic: Plugin architecture supporting multiple domains (C++, RTL, Power)
3. LLM Engineering Excellence: Few-shot, multi-pass, self-critique
4. Data-Driven: Comprehensive evaluation framework with A/B testing
5. Token Efficiency: Smart context selection and prompt optimization
6. Production Ready: Extensible, testable, maintainable code

입력 내용 (우리 프로젝트용):
----------------------------
We are building an extensible LLM engineering framework that will:

Core Principles:
1. Domain-Agnostic Architecture
   - Plugin-based system where domain logic is separated from LLM techniques
   - Core framework provides: few-shot prompting, multi-pass review, self-critique, evaluation
   - Plugins provide: domain examples, parsing, issue categories, validation

2. LLM Engineering Best Practices
   - Few-shot learning with 5-10 expert examples per domain
   - Multi-pass review: initial → self-critique → refinement
   - Chain-of-thought for complex analysis
   - Structured JSON output with schema validation
   - Token budget management and monitoring

3. Experimental Rigor
   - Every technique must be measured (precision, recall, F1, token efficiency)
   - A/B testing framework for comparing approaches
   - Continuous improvement through feedback loops
   - Document what works and what doesn't

4. Domain Expansion Path
   - Phase 1: C++ code review (validation)
   - Phase 2: RTL/Verilog analysis (extension)
   - Phase 3: Power optimization (high-value)
   - Phase 4: Design methodology (premium service)

5. Privacy and Local-First
   - All LLM processing via local Ollama
   - No cloud API dependencies
   - On-premise deployment ready

Technology Stack:
- Python 3.11+ with Pydantic for type safety
- Ollama for local LLM inference
- Evaluation framework with metrics tracking
- Plugin interface for domain extension

================================================================================
2. /speckit.specify
================================================================================

용도: 기능 명세 작성 (User Stories, Acceptance Criteria)

입력 예시:
-----------
/speckit.specify Build a domain-agnostic LLM engineering framework with plugin architecture

상세 입력 (우리 프로젝트용):
----------------------------
/speckit.specify

Feature: Domain-Agnostic LLM Engineering Framework

Description:
Build a reusable framework that implements LLM engineering best practices
(few-shot learning, multi-pass review, self-critique) in a domain-agnostic way.
The framework should work across multiple code analysis domains: C++ review,
RTL analysis, power optimization, and chip design methodology.

Primary Goals:
1. Create plugin interface that allows easy domain extension
2. Implement core LLM techniques as reusable components
3. Build comprehensive evaluation framework to measure technique effectiveness
4. Start with C++ code review as pilot domain
5. Demonstrate clear path to RTL and power optimization

User Stories (Priority Order):

P1 - Framework Core:
- As a developer, I want to implement domain-specific analysis by writing
  a plugin, so that I can reuse proven LLM techniques without reimplementing them

P1 - C++ Plugin (Pilot):
- As a C++ developer, I want to get meaningful PR reviews from local LLM,
  so that I can catch bugs early without sending code to cloud services

P1 - Evaluation System:
- As a framework developer, I want to measure the effectiveness of different
  LLM techniques, so that I can optimize for quality and token efficiency

P2 - RTL Extension:
- As a hardware engineer, I want to analyze Verilog/SystemVerilog code for
  timing/power/CDC issues, demonstrating the framework extends to new domains

P3 - Experimental Platform:
- As an LLM researcher, I want to A/B test prompting strategies,
  so that I can discover which techniques work best for code analysis

Success Criteria:
- Framework supports at least 2 domains (C++, RTL)
- C++ plugin achieves >75% precision, >85% critical recall
- Token efficiency >0.5 issues per 1K tokens
- Clear documentation of which LLM techniques work best

Out of Scope (for now):
- CI/CD integration (user will handle)
- GitHub/GitLab API integration (user will handle)
- Web UI or dashboard
- Multi-user deployment

================================================================================
3. /speckit.plan
================================================================================

용도: 기술 스택, 아키텍처, 구현 계획 수립

⚠️  중요: 우리는 LLM ENGINEERING RESEARCH PLATFORM을 만들고 있습니다!
단순한 코드 분석 도구가 아니라, "어떤 LLM 기법이 최고인지" 발견하고 문서화하는 것이 목표입니다.

입력 예시:
-----------
/speckit.plan

상세 입력 (우리 프로젝트용 - 복사해서 사용):
--------------------------------------------
/speckit.plan

This is an LLM ENGINEERING RESEARCH PLATFORM, not just a code analysis tool.
The primary goal is to discover, measure, and document which LLM techniques work best for code analysis.

Architecture:

Core Components:
1. Experimental Infrastructure (Phase 0 - FIRST!)
   - GroundTruthDataset: Annotated examples with expected issues
   - ExperimentRunner: A/B testing framework
   - MetricsCalculator: Precision, recall, F1, token efficiency
   - PromptLogger: Track all prompts and results
   - StatisticalAnalyzer: Significance testing

2. Technique Library (Modular, swappable)
   - FewShotTechnique(num_examples: int)
   - MultiPassTechnique(num_passes: int)
   - ChainOfThoughtTechnique(depth: str)
   - DiffFocusedTechnique(context_lines: int)
   - Each technique is independently testable

3. Domain-Agnostic Core
   - LLMEngine: Orchestrates techniques
   - DomainPlugin: Abstract interface
   - Configuration: YAML-based per-experiment

4. Domain Plugins (Secondary to research)
   - CppPlugin (pilot for validation)
   - RtlPlugin (proves extensibility)

Project Structure:
```
framework/
  domain_plugin.py      # ABC
  llm_engine.py         # Orchestration
  evaluation.py         # Metrics
  techniques/           # NEW! Modular techniques
    base.py
    few_shot.py
    multi_pass.py
    chain_of_thought.py
    diff_focused.py
  experiment_runner.py  # NEW! A/B testing

plugins/
  cpp_plugin.py         # Minimal first, full later
  rtl_plugin.py         # Future

experiments/
  ground_truth/         # NEW! Annotated examples
    cpp/
      example_001.json  # {code, expected_issues}
      ...
  configs/              # NEW! Experiment configs
    baseline.yml
    few_shot_3.yml
    few_shot_5.yml
    multi_pass_2.yml
  runs/                 # NEW! Timestamped results
    2025-11-11_001_baseline/
      results.json
      prompts.log
  leaderboard.md        # Best techniques ranking

prompts/
  cpp/
    few_shot_examples.json
    system_prompt.txt

test-data/
  cpp/sample-pr-001/    # Already exists
```

Technology Stack:
- Python 3.11+ (type hints, modern features)
- Pydantic 2.0+ (validation, settings)
- ollama-python (LLM interface)
- pytest (testing)
- rich (terminal UI)
- numpy/pandas (metrics calculation)
- scipy (statistical significance)
- pyyaml (config)

Implementation Phases:

Phase 0 (Day 1-2): Experimental Infrastructure FIRST
- Create GroundTruthDataset class
- Implement MetricsCalculator (precision, recall, F1, tokens)
- Build ExperimentRunner (run config, save results)
- Implement PromptLogger (log all LLM interactions)
- Create 20 annotated C++ examples manually
- Deliverable: Can run experiment and get metrics

Phase 1 (Day 3-5): Framework Core + Minimal Plugin
- Implement DomainPlugin ABC (minimal interface)
- Implement LLMEngine (basic orchestration)
- Implement Technique base class and FewShotTechnique
- Minimal CppPlugin (just enough to test)
- Deliverable: Can run one technique on ground truth

Phase 2 (Day 6-10): Technique Experiments (CORE VALUE!)
- Implement remaining techniques (MultiPass, CoT, DiffFocused)
- Create experiment configs (10+ variations)
- Run full experiment matrix:
  * Few-shot: 0, 3, 5, 10 examples
  * Multi-pass: 1, 2, 3 passes
  * Chain-of-thought: shallow, deep
  * Combinations
- Statistical analysis of results
- Generate comparison report
- Document findings: "What worked and why"
- Deliverable: Leaderboard of techniques with data

Phase 3 (Day 11-14): Production C++ Plugin
- Full C++ plugin with winning techniques
- 10+ high-quality few-shot examples
- Comprehensive prompt templates
- Test on sample-pr-001
- Deliverable: Production-ready C++ reviewer

Phase 4 (Week 3+): RTL Extension
- RTL plugin proving extensibility
- RTL few-shot examples
- Measure domain transfer
- Deliverable: Multi-domain validation

Dependencies:
- CRITICAL: Ground truth dataset (20+ annotated C++ examples)
  → Blocks all experiments
  → Requires manual annotation by domain expert
- Ollama running with deepseek-coder:33b, qwen2.5:14b
- sample-pr-001 for integration testing

Performance Goals:

PRIMARY (Research):
- Identify technique(s) with highest F1 on ground truth (statistically significant)
- Quantify improvement: "Technique X beats baseline by Y% (p < 0.05)"
- Token efficiency: Measure issues per 1K tokens per technique
- Reproducibility: Same experiment → same ranking

SECONDARY (Product):
- Analysis time: <60 seconds for 500-line PR
- Usable precision: >75%, Critical recall: >85%
- Token efficiency: >0.5 issues per 1K tokens

Key Design Decisions:
1. **Experiment-first**: Build measurement before features
2. **Technique modularity**: Each technique is swappable, testable
3. **Prompt logging**: Track everything for analysis
4. **Version control**: Prompts, examples, configs versioned
5. **Comparative analysis**: Always A/B test, measure significance
6. **Plugin over inheritance**: Domain logic separate from framework
7. **Evaluation-first**: Metrics before optimization
8. **Document learnings**: Research findings = product value
9. **Simple before complex**: Start basic, add complexity with data
10. **Local-only**: Privacy and control

Success Criteria:

RESEARCH SUCCESS (Primary):
- Successfully rank 5+ techniques by effectiveness
- Quantify improvements with statistical significance
- Reproducible experiments (run twice, same results)
- Documented findings suitable for publication/blog

PRODUCT SUCCESS (Secondary):
- Framework supports 2+ domains (C++, RTL)
- C++ plugin achieves precision >75%, recall >85%
- Token efficiency >0.5 issues per 1K tokens
- Developer can build new plugin in <8 hours

OUT OF SCOPE:
- CI/CD integration (user handles)
- Web UI
- Multi-user deployment
- RAG/vector DB (unless experiments prove needed)

The plan emphasizes that discovering which LLM techniques work best IS the product value, not just building another code review tool.

================================================================================
4. /speckit.tasks
================================================================================

용도: 실행 가능한 작업 목록 생성 (체크리스트 형식)

⚠️  중요: Phase 0 (Experimental Infrastructure)이 최우선입니다!
측정 인프라 없이는 "어떤 기법이 좋은지" 알 수 없습니다.

입력 예시:
-----------
/speckit.tasks

상세 입력 (우리 프로젝트용 - 복사해서 사용):
--------------------------------------------
/speckit.tasks

Generate implementation tasks for the LLM Engineering Research Platform.

CRITICAL UNDERSTANDING:
This is a RESEARCH platform where experiments are the core value.
The task order MUST reflect the 4-phase plan:
- Phase 0: Experimental Infrastructure (FIRST!)
- Phase 1: Framework Core + Minimal Plugin
- Phase 2: Experiments (CORE VALUE!)
- Phase 3: Production C++ Plugin

PHASE ORGANIZATION (STRICT ORDER):

Phase 0 (Day 1-2): Experimental Infrastructure
BLOCKING TASK - MANUAL WORK REQUIRED:
- [ ] Create ground truth dataset (20+ annotated C++ examples)
  - This is 4-6 hours of MANUAL annotation work
  - Each example: code snippet + list of expected issues (category, severity, line)
  - Cannot proceed to experiments without this!
  - File: experiments/ground_truth/cpp/example_001.json to example_020.json

THEN implement evaluation infrastructure:
- [ ] Create GroundTruthDataset class (framework/ground_truth.py)
- [ ] Implement MetricsCalculator (framework/evaluation.py)
  - precision, recall, F1, token efficiency
- [ ] Implement ExperimentRunner (framework/experiment_runner.py)
  - Load config, run technique, save results
- [ ] Implement PromptLogger (framework/prompt_logger.py)
  - Log every LLM interaction with timestamp
- [ ] Implement StatisticalAnalyzer (framework/statistical_analyzer.py)
  - t-test, significance testing, p-values
- [ ] Create experiment config templates (experiments/configs/)
  - baseline.yml, few_shot_3.yml, few_shot_5.yml, etc.

EXIT GATE: Can run dummy experiment end-to-end and get metrics

Phase 1 (Day 3-7): Framework Core + Technique Library
- [ ] Implement DomainPlugin interface (framework/domain_plugin.py)
- [ ] Implement BaseTechnique interface (framework/techniques/base.py)
- [ ] Implement FewShotTechnique (framework/techniques/few_shot.py)
- [ ] Implement MultiPassTechnique (framework/techniques/multi_pass.py)
- [ ] Implement ChainOfThoughtTechnique (framework/techniques/chain_of_thought.py)
- [ ] Implement DiffFocusedTechnique (framework/techniques/diff_focused.py)
- [ ] Implement SelfCritiqueTechnique (framework/techniques/self_critique.py)
- [ ] Implement LLMEngine (framework/llm_engine.py)
  - Orchestrates techniques, calls Ollama
- [ ] Minimal CppPlugin (plugins/cpp_plugin.py)
  - Just enough to test: parse C++, provide 3 examples, basic prompts

EXIT GATE: Can run FewShotTechnique on one ground truth example, get valid result

Phase 2 (Day 8-12): EXPERIMENTS - CORE VALUE! ⭐⭐⭐
- [ ] Create 12 experiment configurations (experiments/configs/)
  - baseline, few_shot_3, few_shot_5, few_shot_10
  - multi_pass_2, multi_pass_3
  - chain_of_thought_shallow, chain_of_thought_deep
  - diff_focused
  - combinations: few_shot_5_multi_pass_2, few_shot_5_cot_critique
  - best_of_all
- [ ] Run full experiment matrix (12 configs × 20 examples = 240 LLM calls)
- [ ] Generate results for each run (experiments/runs/TIMESTAMP_CONFIG/)
- [ ] Implement leaderboard generator (framework/leaderboard_generator.py)
  - Rank techniques by F1 score
  - Show statistical significance
  - Generate markdown report
- [ ] Generate leaderboard (experiments/leaderboard.md)
- [ ] Document findings (experiments/findings.md)
  - What worked and WHY
  - Quantified improvements: "5-shot +42% over baseline (p<0.001)"
  - Recommendations for production use

EXIT GATE: Leaderboard with statistically significant rankings, reproducible results

Phase 3 (Day 13-16): Production C++ Plugin
- [ ] Create 15+ curated few-shot examples (prompts/cpp/few_shot_examples.json)
  - Based on Phase 2 learnings
  - Cover all categories: memory, performance, modern-cpp, security, concurrency
- [ ] Implement full C++ parser (plugins/cpp/parser.py)
  - Use tree-sitter for AST parsing
- [ ] Implement diff-focused prompting (plugins/cpp/diff_prompt.py)
- [ ] Apply winning technique configuration from Phase 2
- [ ] Test on sample-pr-001 (10 intentional bugs)
- [ ] Validate: ≥75% precision, ≥85% critical recall

EXIT GATE: Production-ready C++ reviewer that meets quality thresholds

TASK ORGANIZATION:
- Group by Phase (not by user story!)
- Mark parallel tasks with [P] ONLY within same phase
- Include exact file paths
- Specify dependencies explicitly
- Emphasize manual work (ground truth annotation!)

CRITICAL DEPENDENCIES:
1. Ground truth annotation BLOCKS everything (manual work!)
2. Phase 0 BLOCKS Phase 1 (need evaluation infrastructure)
3. Phase 1 BLOCKS Phase 2 (need techniques to test)
4. Phase 2 results INFORM Phase 3 (apply winning techniques)

SUCCESS METRICS TO TRACK:
- Precision, Recall, F1 per technique
- Token consumption per technique
- Statistical significance (p-values)
- Reproducibility (run same config twice, get same ranking)

RESEARCH ARTIFACTS TO GENERATE:
- experiments/leaderboard.md (main research output!)
- experiments/findings.md (documented learnings)
- experiments/runs/ (all timestamped results)
- experiments/configs/ (all technique configs)

Request detailed tasks with:
- Exact file paths
- Expected lines of code (rough estimate)
- Clear dependencies (BLOCKS / BLOCKED BY)
- Manual work clearly marked
- Research outputs emphasized

The tasks should make it crystal clear:
Phase 0 → Phase 1 → Phase 2 (experiments!) → Phase 3

================================================================================
5. /speckit.implement
================================================================================

용도: 작업 실행 (Claude가 tasks.md를 따라 구현)

⚠️  중요: Phase 0 (Experimental Infrastructure)부터 시작합니다!

입력 예시:
-----------
/speckit.implement

상세 입력 (우리 프로젝트용 - 복사해서 사용):
--------------------------------------------
/speckit.implement

Start implementation following the 5-phase plan in tasks.md (209 tasks total).

📊 TASK OVERVIEW:
- Phase 0: 68 tasks (T001-T068) - Experimental Infrastructure
- Phase 1: 35 tasks (T069-T103) - Framework Core + Techniques
- Phase 2: 33 tasks (T104-T136) - Experiments ⭐ CORE VALUE
- Phase 3: 46 tasks (T137-T182) - Production C++ Plugin
- Phase 4: 27 tasks (T183-T209) - Polish & Documentation

💡 MVP RECOMMENDATION: Complete Phase 0-2 only (136 tasks)
   = Research proof with statistical evidence in <50% of total tasks!

PHASE 0 (Day 1-2, T001-T068): Experimental Infrastructure
This is the FOUNDATION. Cannot skip this!

START IMMEDIATELY:
- T001: Create project structure
- T002: Initialize Python package (requirements.txt, pyproject.toml)
- T012: Verify Ollama installed (deepseek-coder:33b, qwen2.5:14b)
- T013-T033: Ground Truth Annotation (21 MANUAL TASKS, 4-6 HOURS!)
  → BLOCKS EVERYTHING
  → Each example: JSON with code + expected_issues
  → Format: {category, severity, line, description, reasoning}
  → Use test-data/sample-pr-001 as starting point

THEN build evaluation infrastructure:
- T040: GroundTruthDataset class (load and validate)
- T042: MetricsCalculator (precision, recall, F1, token efficiency)
- T048: ExperimentRunner (run config, save results)
- T045: PromptLogger (log all LLM interactions)
- T052: StatisticalAnalyzer (t-test, p-values, significance)
- T055-T066: Create experiment config templates (11 configs)

EXIT GATE Phase 0 (T068): Run dummy experiment, get metrics output

PHASE 1 (Day 3-7, T069-T103): Framework Core + Technique Library
- T069-T073: DomainPlugin interface (ABC with 5 methods)
- T074-T083: 5 Technique implementations (ALL parallelizable!)
  - T074: FewShotTechnique(num_examples: int)
  - T076: MultiPassTechnique(num_passes: int)
  - T078: ChainOfThoughtTechnique(depth: str)
  - T080: DiffFocusedTechnique(context_lines: int)
  - T082: SelfCritiqueTechnique(confidence_threshold: float)
- T084-T092: LLMEngine (orchestrate, call Ollama, handle errors)
- T093-T103: Minimal CppPlugin (3 examples, basic prompts)

EXIT GATE Phase 1 (T103): Run FewShotTechnique(5) on one example with real Ollama

PHASE 2 (Day 8-12, T104-T136): EXPERIMENTS ⭐⭐⭐ THIS IS THE GOAL!
- T104-T114: Run 11 experiment configs on 20 examples (240 LLM calls!)
  - baseline, few_shot_3, few_shot_5, few_shot_10
  - multi_pass_2, multi_pass_3
  - chain_of_thought_shallow, chain_of_thought_deep
  - diff_focused
  - few_shot_5_multi_pass_2, best_of_all
- T119-T123: Generate leaderboard (ranking, significance, recommendations)
- T126: Document findings (experiments/findings.md)
  - "Few-shot +40%, multi-pass -20% FP, CoT +30% complex bugs"
- T133-T135: Validate reproducibility (re-run → same rankings)

EXIT GATE Phase 2 (T136): Leaderboard with statistically significant rankings
→ THIS IS THE PRIMARY DELIVERABLE! Research value proven!

🎯 MVP COMPLETE AT THIS POINT! (Phase 0-2 = 136 tasks)
Phase 3-4 are OPTIONAL for research proof.

PHASE 3 (Day 13-16, T137-T182): Production C++ Plugin [OPTIONAL]
- T138-T142: Curate 15+ few-shot examples (based on Phase 2 learnings)
- T146: Tree-sitter C++ parser (AST-based)
- T151: DiffFormatter (diff-focused prompting)
- T177-T180: Validate ≥75% precision, ≥85% critical recall
- T181-T182: Test on sample-pr-001

EXIT GATE Phase 3 (T182): Production-ready C++ reviewer

PHASE 4 (Day 17+, T183-T209): Polish & Documentation [OPTIONAL]
- T183-T195: User documentation (README, examples, troubleshooting)
- T196-T202: Error handling and user experience
- T203-T209: Performance optimization

STOP POINTS FOR REVIEW:
- After T068 (Phase 0): Verify evaluation infrastructure works
- After T103 (Phase 1): Verify one technique runs successfully
- After T136 (Phase 2): Review leaderboard and findings ⭐ PRIMARY VALUE!
- After T182 (Phase 3): Validate quality metrics (if doing production plugin)

CRITICAL NOTES:
- DO NOT skip Phase 0! Measurement infrastructure is essential
- T013-T033 (Ground truth annotation) is 4-6 hours MANUAL work - START NOW!
- Phase 2 (T104-T136) is where research value is created
- MVP = Phase 0-2 only (136 tasks = research proof with statistical evidence)
- Phase 3-4 optional for MVP (production polish)
- Timeline: 12 days for MVP (Phase 0-2), 18-19 days for full implementation

The implementation prioritizes discovering which techniques work best (Phase 2)
over building a polished tool (Phase 3-4).

================================================================================
6. 추가 명령어 (Optional)
================================================================================

/speckit.analyze
- 모든 artifacts 분석하고 일관성 체크
- 사용 시점: 구현 중간에 문서와 코드가 맞는지 확인

/speckit.checklist
- 품질 체크리스트 생성
- 사용 시점: 구현 완료 후 최종 검증

/speckit.clarify
- 불명확한 요구사항 질문 생성
- 사용 시점: specify 이후, plan 이전

================================================================================
현재 프로젝트 상태 (2025-11-11 - Updated)
================================================================================

완료:
✅ Git 설정 (Minjae Kim <develop.minjae@gmail.com>)
✅ Initial commit (30 files, 6914 lines)
✅ /speckit.constitution 실행 완료 (검증됨, v2.0.0)
   - 6개 핵심 원칙 → LLM Engineering Excellence 중심으로 재정의
✅ /speckit.specify 실행 완료 (LLM feedback 반영)
   - US2 (Experimental Platform) P3 → P1로 상향 ⭐
   - Few-shot importance 강조 (+40% accuracy)
   - Input/Output engineering requirements 추가
✅ /speckit.plan 실행 완료 ⭐⭐⭐
   - Revolutionary: Phase 0 (Experimental Infrastructure) FIRST!
   - 4-Phase implementation (16 days)
   - 12 experiment configurations defined
   - Research Success > Product Success (priority flip!)
✅ 테스트 데이터 준비 (sample-pr-001 with 10 bugs)
✅ SPECKIT_USAGE_GUIDE.txt 작성 및 업데이트

다음 단계:
1. ⏭️  /speckit.tasks 실행 (위의 입력 사용) ← 다음 할 일!
2. 🔜 /speckit.implement 실행 (Phase 0부터 시작)
3. 🔜 Ground Truth Annotation (MANUAL - 4-6 hours!)
4. 🔜 Phase 0-3 구현 및 실험

핵심 포인트:
- Spec-kit은 우리가 작성한 문서를 참고하되, 자신의 형식에 맞게 재구성함
- 기존에 작성한 004-extensible-llm-framework.md는 참고 자료로 유용함
- 각 단계에서 생성된 문서는 .specify/ 디렉토리에 구조화되어 저장됨
- 우리의 목표는 LLM engineering 정수를 담은 확장 가능한 프레임워크 구축

================================================================================
권장 워크플로우 (현재 진행 상황 반영)
================================================================================

✅ 1-3. Spec-kit 문서화 단계 완료
   - Constitution ✅
   - Specify ✅
   - Plan ✅

⏭️  4. Tasks 생성 (다음 단계!)
   /speckit.tasks
   [위의 상세 입력 복사 - Phase 0 강조]

🔜 5. 구현 시작 (Phase 0부터!)
   /speckit.implement

   중요: Phase 0 (Experimental Infrastructure) 먼저!
   - Ground truth annotation (4-6시간 수동 작업)
   - Evaluation infrastructure
   - Experiment runner

🔜 6. Phase별 진행 및 검증
   Phase 0: Evaluation infrastructure 작동 확인
   Phase 1: 1개 technique 실행 성공
   Phase 2: 12 configs 실험 → Leaderboard ⭐⭐⭐ (핵심!)
   Phase 3: Production C++ plugin

🔜 7. 연구 결과 문서화
   - experiments/leaderboard.md (최고 기법 ranking)
   - experiments/findings.md (무엇이 왜 작동했는가)
   - 블로그/논문 수준의 분석

🔜 8. RTL 확장 (Phase 4)
   - Domain transfer 측정
   - RTL few-shot examples
   - Extensibility 검증

================================================================================
