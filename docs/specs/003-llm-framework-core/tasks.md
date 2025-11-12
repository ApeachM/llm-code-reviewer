# Implementation Tasks: Domain-Agnostic LLM Engineering Framework

**Feature Branch**: `003-llm-framework-core`
**Created**: 2025-11-11
**Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](./spec.md)

## Overview

This is an **LLM engineering research platform** where discovering which prompting techniques work best IS the core value. Tasks are organized in strict phase order to emphasize experiment-first architecture.

**Critical Understanding**: Build evaluation infrastructure (Phase 0) BEFORE building anything to evaluate. The primary deliverable is research findings with statistical evidence, not just "another code review tool."

**Phase Structure**:
- **Phase 0** (Day 1-2): Experimental Infrastructure - BLOCKS everything
- **Phase 1** (Day 3-7): Framework Core + Technique Library
- **Phase 2** (Day 8-12): Experiments - THE CORE VALUE ⭐⭐⭐
- **Phase 3** (Day 13-16): Production C++ Plugin

---

## Phase 0: Setup & Experimental Infrastructure (Day 1-2)

**Goal**: Build measurement infrastructure BEFORE building anything to measure. This phase BLOCKS all subsequent work.

**Exit Gate**: Can run dummy experiment end-to-end (mocked LLM) and get precision/recall/F1 metrics.

### 0.1: Project Initialization

- [ ] T001 [P] Create project directory structure per implementation plan
- [ ] T002 [P] Initialize Python package with pyproject.toml (Python 3.11+, dependencies: ollama-python, pydantic 2.0+, pytest, rich, numpy, scipy, pandas, pyyaml)
- [ ] T003 [P] Create framework/ directory with __init__.py
- [ ] T004 [P] Create plugins/ directory with __init__.py
- [ ] T005 [P] Create experiments/ directory with subdirectories: ground_truth/, configs/, runs/
- [ ] T006 [P] Create cli/ directory with __init__.py
- [ ] T007 [P] Create tests/ directory with subdirectories: unit/, integration/, fixtures/
- [ ] T008 [P] Create prompts/ directory for few-shot example storage
- [ ] T009 [P] Create docs/ directory for user documentation
- [ ] T010 [P] Create .gitignore (ignore experiments/runs/, __pycache__/, .pytest_cache/, *.pyc)
- [ ] T011 [P] Create README.md with project overview emphasizing research platform nature
- [ ] T012 Verify Ollama is installed and running locally (ollama list, check for models)

### 0.2: Ground Truth Dataset (BLOCKING - MANUAL WORK)

**⚠️ CRITICAL PATH**: This is 4-6 hours of MANUAL annotation work by domain expert. Cannot proceed to experiments without this!

- [ ] T013 **[MANUAL]** Create experiments/ground_truth/cpp/ directory
- [ ] T014 **[MANUAL]** Annotate example_001.json: Memory leak (raw pointer never deleted) in experiments/ground_truth/cpp/
- [ ] T015 **[MANUAL]** Annotate example_002.json: Use-after-free bug in experiments/ground_truth/cpp/
- [ ] T016 **[MANUAL]** Annotate example_003.json: Buffer overflow in experiments/ground_truth/cpp/
- [ ] T017 **[MANUAL]** Annotate example_004.json: Double-free bug in experiments/ground_truth/cpp/
- [ ] T018 **[MANUAL]** Annotate example_005.json: Dangling pointer reference in experiments/ground_truth/cpp/
- [ ] T019 **[MANUAL]** Annotate example_006.json: Unnecessary copy (pass-by-value) in experiments/ground_truth/cpp/
- [ ] T020 **[MANUAL]** Annotate example_007.json: Missing const-correctness in experiments/ground_truth/cpp/
- [ ] T021 **[MANUAL]** Annotate example_008.json: Range-for loop opportunity (modern C++) in experiments/ground_truth/cpp/
- [ ] T022 **[MANUAL]** Annotate example_009.json: Auto type inference opportunity in experiments/ground_truth/cpp/
- [ ] T023 **[MANUAL]** Annotate example_010.json: Smart pointer usage (unique_ptr) in experiments/ground_truth/cpp/
- [ ] T024 **[MANUAL]** Annotate example_011.json: Race condition risk in experiments/ground_truth/cpp/
- [ ] T025 **[MANUAL]** Annotate example_012.json: Deadlock potential in experiments/ground_truth/cpp/
- [ ] T026 **[MANUAL]** Annotate example_013.json: Null pointer dereference in experiments/ground_truth/cpp/
- [ ] T027 **[MANUAL]** Annotate example_014.json: Integer overflow in experiments/ground_truth/cpp/
- [ ] T028 **[MANUAL]** Annotate example_015.json: Algorithmic complexity issue (O(n²) where O(n) possible) in experiments/ground_truth/cpp/
- [ ] T029 **[MANUAL]** Annotate example_016.json: Clean code (no issues) - negative example in experiments/ground_truth/cpp/
- [ ] T030 **[MANUAL]** Annotate example_017.json: Clean code with smart pointers - negative example in experiments/ground_truth/cpp/
- [ ] T031 **[MANUAL]** Annotate example_018.json: Complex multi-issue example (memory leak + race condition) in experiments/ground_truth/cpp/
- [ ] T032 **[MANUAL]** Annotate example_019.json: Subtle use-after-free in multi-threaded context in experiments/ground_truth/cpp/
- [ ] T033 **[MANUAL]** Annotate example_020.json: Modern C++ best practices example in experiments/ground_truth/cpp/

**JSON Schema** (each example):
```json
{
  "id": "example_NNN",
  "description": "Brief description",
  "code": "C++ code snippet",
  "file_path": "filename.cpp",
  "expected_issues": [
    {
      "category": "memory-safety|modern-cpp|performance|security|concurrency",
      "severity": "critical|high|medium|low",
      "line": 1,
      "description": "Specific issue description",
      "reasoning": "Why this is problematic"
    }
  ]
}
```

### 0.3: Pydantic Models (Foundation)

**BLOCKED BY**: T002 (project initialization)

- [ ] T034 Implement Issue model in framework/models.py (~50 lines: category, severity, line, description, reasoning, suggested_fix, confidence)
- [ ] T035 Implement AnalysisRequest model in framework/models.py (~30 lines: code, domain, technique, context)
- [ ] T036 Implement AnalysisResult model in framework/models.py (~40 lines: issues, token_count, latency, technique, metadata)
- [ ] T037 Implement GroundTruthExample model in framework/models.py (~40 lines: id, description, code, file_path, expected_issues)
- [ ] T038 Implement ExperimentConfig model in framework/models.py (~50 lines: technique, model, parameters, dataset)
- [ ] T039 Implement MetricsResult model in framework/models.py (~60 lines: precision, recall, f1, token_efficiency, latency, per_category_metrics)

### 0.4: Ground Truth Dataset Loader

**BLOCKED BY**: T033 (last manual annotation), T037 (GroundTruthExample model)

- [ ] T040 Implement GroundTruthDataset class in framework/evaluation.py (~100 lines: load_from_directory, validate_schema, get_examples, filter_by_category)
- [ ] T041 Add unit test for GroundTruthDataset in tests/unit/test_evaluation.py (~80 lines: test load, test validation, test filtering)

### 0.5: Metrics Calculator

**BLOCKED BY**: T036 (AnalysisResult model), T037 (GroundTruthExample model), T039 (MetricsResult model)

- [ ] T042 Implement MetricsCalculator class in framework/evaluation.py (~200 lines: calculate_precision, calculate_recall, calculate_f1, calculate_token_efficiency, classify_results as TP/FP/FN)
- [ ] T043 Implement per-category metrics breakdown in MetricsCalculator (~80 lines: memory-safety precision, performance recall, etc.)
- [ ] T044 Add unit test for MetricsCalculator in tests/unit/test_evaluation.py (~150 lines: test precision/recall/F1 calculation, test edge cases like zero TP)

### 0.6: Prompt Logger

**BLOCKED BY**: T034 (Issue model)

- [ ] T045 Implement PromptLogger class in framework/prompt_logger.py (~120 lines: log_prompt, log_response, save_to_jsonl, query_by_example_id, query_false_positives)
- [ ] T046 Add timestamp and metadata tracking to PromptLogger (~40 lines: technique name, model, example_id, tokens, latency)
- [ ] T047 Add unit test for PromptLogger in tests/unit/test_prompt_logger.py (~100 lines: test logging, test querying, test JSON lines format)

### 0.7: Experiment Runner

**BLOCKED BY**: T038 (ExperimentConfig model), T040 (GroundTruthDataset), T042 (MetricsCalculator), T045 (PromptLogger)

- [ ] T048 Implement ExperimentRunner class in framework/experiment_runner.py (~180 lines: load_config, run_experiment, save_results_to_timestamped_dir, generate_summary_report)
- [ ] T049 Implement timestamped result directory structure in ExperimentRunner (~60 lines: experiments/runs/{timestamp}_{technique_name}/ with config.yml, results.json, prompts.log, details/)
- [ ] T050 Add experiment reproduction capability in ExperimentRunner (~50 lines: save config snapshot, enable re-running exact experiment)
- [ ] T051 Add unit test for ExperimentRunner with mocked LLM in tests/unit/test_experiment_runner.py (~120 lines: test config loading, test result saving, test directory structure)

### 0.8: Statistical Analyzer

**BLOCKED BY**: T039 (MetricsResult model)

- [ ] T052 Implement StatisticalAnalyzer class in framework/statistical_analyzer.py (~150 lines: t_test_comparison, calculate_p_values, calculate_effect_size, calculate_confidence_intervals)
- [ ] T053 Implement comparison report generation in StatisticalAnalyzer (~100 lines: technique A vs B, statistical significance, recommendation)
- [ ] T054 Add unit test for StatisticalAnalyzer in tests/unit/test_statistical_analyzer.py (~100 lines: test t-test, test p-value calculation, test significance determination)

### 0.9: Experiment Configuration Templates

**BLOCKED BY**: T005 (experiments directory structure)

- [ ] T055 [P] Create baseline_zero_shot.yml in experiments/configs/ (zero-shot, single-pass)
- [ ] T056 [P] Create few_shot_3.yml in experiments/configs/ (3 examples per category)
- [ ] T057 [P] Create few_shot_5.yml in experiments/configs/ (5 examples per category)
- [ ] T058 [P] Create few_shot_10.yml in experiments/configs/ (10 examples per category)
- [ ] T059 [P] Create multi_pass_2.yml in experiments/configs/ (initial + self-critique)
- [ ] T060 [P] Create multi_pass_3.yml in experiments/configs/ (initial + critique + refinement)
- [ ] T061 [P] Create chain_of_thought_shallow.yml in experiments/configs/ (basic CoT)
- [ ] T062 [P] Create chain_of_thought_deep.yml in experiments/configs/ (detailed step-by-step)
- [ ] T063 [P] Create diff_focused_3lines.yml in experiments/configs/ (3 lines context before/after)
- [ ] T064 [P] Create combo_5shot_2pass.yml in experiments/configs/ (few-shot 5 + multi-pass 2)
- [ ] T065 [P] Create combo_5shot_cot_critique.yml in experiments/configs/ (few-shot 5 + CoT deep + critique)
- [ ] T066 [P] Create best_all_techniques.yml in experiments/configs/ (placeholder for winning combo from Phase 2)

### 0.10: Phase 0 Integration Test

**BLOCKED BY**: T051 (ExperimentRunner with mocked LLM test)

- [ ] T067 Create end-to-end Phase 0 test in tests/integration/test_phase0_complete.py (~150 lines: load ground truth → run mocked experiment → verify metrics calculation → verify result storage → verify prompt logging)
- [ ] T068 Verify Phase 0 exit gate: Run dummy experiment (mocked LLM responses) and confirm precision/recall/F1 calculation works

---

## Phase 1: Framework Core + Technique Library (Day 3-7)

**Goal**: Implement domain-agnostic LLM techniques as modular, independently testable components.

**BLOCKED BY**: Phase 0 complete (T068)

**Exit Gate**: Can run FewShotTechnique(5) on one ground truth example with real Ollama, get valid AnalysisResult with metrics.

### 1.1: Core Interfaces

- [ ] T069 Implement DomainPlugin abstract base class in framework/domain_plugin.py (~80 lines: 5 abstract methods - get_few_shot_examples, parse_artifact, format_diff, validate_output, format_report)
- [ ] T070 Add comprehensive docstrings to DomainPlugin interface (~40 lines: explain each method's contract, expected inputs/outputs)
- [ ] T071 Implement TechniqueConfig Pydantic model in framework/techniques/base.py (~30 lines: name, version, parameters)
- [ ] T072 Implement BaseTechnique abstract base class in framework/techniques/base.py (~100 lines: build_prompt, process_response, execute methods)
- [ ] T073 Add unit test for BaseTechnique with mock subclass in tests/unit/test_techniques.py (~80 lines: test execute flow, test abstract method enforcement)

### 1.2: LLM Techniques Implementation

**BLOCKED BY**: T072 (BaseTechnique interface)

- [ ] T074 Implement FewShotTechnique in framework/techniques/few_shot.py (~120 lines: retrieve N examples from plugin, inject into prompt template, config parameter num_examples: int)
- [ ] T075 Add unit test for FewShotTechnique with mocked plugin/LLM in tests/unit/test_techniques.py (~100 lines: test 0-shot, 3-shot, 5-shot, 10-shot)
- [ ] T076 Implement MultiPassTechnique in framework/techniques/multi_pass.py (~180 lines: Pass 1 initial analysis, Pass 2 self-critique, Pass 3 refinement with confidence scores, config parameter num_passes: int)
- [ ] T077 Add unit test for MultiPassTechnique in tests/unit/test_techniques.py (~120 lines: test single-pass, 2-pass, 3-pass with mocked LLM)
- [ ] T078 Implement ChainOfThoughtTechnique in framework/techniques/chain_of_thought.py (~150 lines: prompt LLM for step-by-step reasoning, config parameter depth: "shallow"|"deep")
- [ ] T079 Add unit test for ChainOfThoughtTechnique in tests/unit/test_techniques.py (~100 lines: test shallow vs deep CoT with mocked LLM)
- [ ] T080 Implement DiffFocusedTechnique in framework/techniques/diff_focused.py (~140 lines: format diff with BEFORE/AFTER highlighting, omit unchanged code, config parameter context_lines: int)
- [ ] T081 Add unit test for DiffFocusedTechnique in tests/unit/test_techniques.py (~100 lines: test diff formatting with various context line counts)
- [ ] T082 Implement SelfCritiqueTechnique in framework/techniques/self_critique.py (~130 lines: ask LLM to rate confidence 0.0-1.0, filter issues below threshold, config parameter confidence_threshold: float)
- [ ] T083 Add unit test for SelfCritiqueTechnique in tests/unit/test_techniques.py (~100 lines: test confidence scoring and filtering)

### 1.3: LLM Engine Orchestration

**BLOCKED BY**: T069 (DomainPlugin interface), T072 (BaseTechnique interface), T036 (AnalysisResult model)

- [ ] T084 Implement OllamaClient wrapper in framework/llm_engine.py (~100 lines: generate method with streaming support, token counting, error handling)
- [ ] T085 Add retry logic and timeout handling to OllamaClient (~60 lines: max 3 retries, exponential backoff, 60s timeout)
- [ ] T086 Implement LLMEngine class in framework/llm_engine.py (~120 lines: analyze method orchestrates technique + plugin + Ollama, returns AnalysisResult)
- [ ] T087 Add integration test for LLMEngine with real Ollama in tests/integration/test_llm_engine.py (~100 lines: requires Ollama running, test end-to-end analysis)

### 1.4: Minimal C++ Plugin (Just Enough to Test)

**BLOCKED BY**: T069 (DomainPlugin interface)

**Goal**: Validate plugin interface with simplest possible implementation. Full production plugin comes in Phase 3.

- [ ] T088 Create plugins/cpp/ directory with __init__.py
- [ ] T089 Implement MinimalCppPlugin in plugins/cpp/plugin.py (~150 lines: implement 5 DomainPlugin methods with basic logic)
- [ ] T090 Add 3 hardcoded few-shot examples to MinimalCppPlugin (~60 lines: memory leak, unnecessary copy, modern C++ range-for)
- [ ] T091 Implement trivial parse_artifact in MinimalCppPlugin (~20 lines: return code as-is, no tree-sitter yet)
- [ ] T092 Implement basic format_diff in MinimalCppPlugin (~40 lines: simple BEFORE/AFTER text formatting)
- [ ] T093 Implement JSON parsing in validate_output in MinimalCppPlugin (~50 lines: parse LLM JSON response into Issue objects)
- [ ] T094 Implement markdown formatter in format_report in MinimalCppPlugin (~40 lines: basic markdown template)
- [ ] T095 Add plugin interface compliance test in tests/unit/test_plugins.py (~80 lines: verify MinimalCppPlugin implements all required methods)

### 1.5: CLI Foundation

**BLOCKED BY**: T086 (LLMEngine), T048 (ExperimentRunner)

- [ ] T096 Implement CLI entry point in cli/main.py using Click (~80 lines: main command group)
- [ ] T097 Implement `analyze` command in cli/main.py (~60 lines: analyze single file with specified technique)
- [ ] T098 Implement `evaluate` command in cli/main.py (~70 lines: run evaluation on ground truth dataset)
- [ ] T099 Implement `experiment run` command in cli/main.py (~60 lines: run single experiment config)
- [ ] T100 Implement `experiment compare` command in cli/main.py (~70 lines: compare two technique runs)
- [ ] T101 Add Rich progress bars and result tables in cli/ui.py (~100 lines: experiment progress, metrics display)

### 1.6: Phase 1 Integration Test

**BLOCKED BY**: T095 (MinimalCppPlugin), T087 (LLMEngine integration test)

- [ ] T102 Create Phase 1 integration test in tests/integration/test_phase1_complete.py (~150 lines: load ground truth example → run FewShotTechnique(5) with MinimalCppPlugin and real Ollama → verify AnalysisResult)
- [ ] T103 Verify Phase 1 exit gate: Run FewShotTechnique(5) on example_001.json with real Ollama, confirm precision/recall/F1 returned successfully

---

## Phase 2: Experiments - THE CORE VALUE! (Day 8-12) ⭐⭐⭐

**Goal**: DISCOVER which LLM techniques work best for code analysis. Generate research findings with statistical rigor. This is the PRIMARY DELIVERABLE.

**BLOCKED BY**: Phase 1 complete (T103)

**Exit Gate**: Leaderboard generated with statistically significant rankings (p<0.05), reproducible experiment results, documented findings.

### 2.1: Experiment Execution

**BLOCKED BY**: T103 (Phase 1 complete)

- [ ] T104 Run baseline_zero_shot.yml experiment on 20 ground truth examples with deepseek-coder:33b (~30 min runtime)
- [ ] T105 Run few_shot_3.yml experiment on 20 ground truth examples with deepseek-coder:33b (~35 min runtime)
- [ ] T106 Run few_shot_5.yml experiment on 20 ground truth examples with deepseek-coder:33b (~40 min runtime)
- [ ] T107 Run few_shot_10.yml experiment on 20 ground truth examples with deepseek-coder:33b (~50 min runtime)
- [ ] T108 Run multi_pass_2.yml experiment on 20 ground truth examples with deepseek-coder:33b (~60 min runtime, 2x LLM calls)
- [ ] T109 Run multi_pass_3.yml experiment on 20 ground truth examples with deepseek-coder:33b (~90 min runtime, 3x LLM calls)
- [ ] T110 Run chain_of_thought_shallow.yml experiment on 20 ground truth examples with deepseek-coder:33b (~40 min runtime)
- [ ] T111 Run chain_of_thought_deep.yml experiment on 20 ground truth examples with deepseek-coder:33b (~50 min runtime)
- [ ] T112 Run diff_focused_3lines.yml experiment on 20 ground truth examples with deepseek-coder:33b (~35 min runtime)
- [ ] T113 Run combo_5shot_2pass.yml experiment on 20 ground truth examples with deepseek-coder:33b (~60 min runtime)
- [ ] T114 Run combo_5shot_cot_critique.yml experiment on 20 ground truth examples with deepseek-coder:33b (~80 min runtime)

**Total Runtime Estimate**: ~10-12 hours for all experiments (can parallelize 2-3 at a time on powerful machine)

### 2.2: Results Verification

**BLOCKED BY**: T114 (all experiments complete)

- [ ] T115 Verify all 11 experiment runs have complete results.json files in experiments/runs/
- [ ] T116 Verify all 11 experiment runs have complete prompts.log files with all LLM interactions
- [ ] T117 Verify all 11 experiment runs have per-example result details in details/ subdirectories
- [ ] T118 Check for any failed experiments, re-run if necessary

### 2.3: Leaderboard Generator

**BLOCKED BY**: T052 (StatisticalAnalyzer), T115 (results verification)

- [ ] T119 Implement LeaderboardGenerator class in framework/leaderboard_generator.py (~200 lines: aggregate results from all runs, rank by F1 score, calculate statistical significance vs baseline)
- [ ] T120 Implement markdown leaderboard formatting in LeaderboardGenerator (~100 lines: generate tables with ranks, metrics, significance)
- [ ] T121 Implement per-category performance tables in LeaderboardGenerator (~80 lines: memory-safety, modern-cpp, performance, security, concurrency breakdowns)
- [ ] T122 Implement failure analysis section in LeaderboardGenerator (~100 lines: identify top false positive/negative causes, suggest fixes)
- [ ] T123 Implement recommendations section in LeaderboardGenerator (~80 lines: "For maximum quality use X", "For balanced quality/cost use Y", "For speed use Z")

### 2.4: Generate Research Artifacts

**BLOCKED BY**: T123 (LeaderboardGenerator complete)

- [ ] T124 Generate experiments/leaderboard.md from all experiment results (~500 lines expected: tables, findings, recommendations)
- [ ] T125 Review leaderboard.md for statistical significance - all rankings must have p-values relative to baseline
- [ ] T126 Create experiments/findings.md with publication-quality writeup (~800 lines: research question, methodology, results, discussion, limitations, future work)
- [ ] T127 Document key findings in findings.md: "Few-shot learning +40% over baseline (p<0.001)", "Multi-pass critique -20% false positives (p=0.02)", etc.
- [ ] T128 Add per-category analysis to findings.md: memory-safety precision/recall improvements, modern-cpp suggestions effectiveness
- [ ] T129 Add failure analysis to findings.md: why false positives occurred, which few-shot examples need refinement
- [ ] T130 Add token efficiency analysis to findings.md: issues per 1K tokens per technique, cost-quality trade-offs
- [ ] T131 Identify winning technique configuration for Phase 3 from leaderboard (likely combo_5shot_cot_critique.yml)
- [ ] T132 Update best_all_techniques.yml config with winning parameters from T131

### 2.5: Reproducibility Validation

**BLOCKED BY**: T124 (leaderboard generated)

- [ ] T133 Re-run winning technique (from T131) on ground truth dataset a second time
- [ ] T134 Verify second run produces same ranking (±5% metric variance acceptable)
- [ ] T135 Document reproducibility results in findings.md (confirm or note variance)

### 2.6: Phase 2 Exit Validation

**BLOCKED BY**: T135 (reproducibility validated)

- [ ] T136 Verify Phase 2 exit gate checklist:
  - ✅ All 11 experiment configs successfully run on 20 examples
  - ✅ Leaderboard generated with clear rankings (experiments/leaderboard.md)
  - ✅ Statistical comparison shows significant differences (p<0.05) between top/bottom techniques
  - ✅ Documented findings explain WHAT works and WHY (experiments/findings.md)
  - ✅ Failure analysis identifies improvement opportunities
  - ✅ Reproducibility verified (re-run yields same rankings ±5%)

---

## Phase 3: Production C++ Plugin (Day 13-16)

**Goal**: Build production-quality C++ plugin using winning techniques discovered in Phase 2 experiments.

**BLOCKED BY**: Phase 2 complete (T136)

**Exit Gate**: C++ plugin achieves precision ≥75%, critical recall ≥85% on ground truth, sample-pr-001 analysis succeeds in <3 minutes.

### 3.1: Curated Few-Shot Examples

**BLOCKED BY**: T129 (failure analysis - know which examples need improvement)

- [ ] T137 Create prompts/cpp/ directory with subdirectory few_shot_examples/
- [ ] T138 Create memory-safety examples set v1 in prompts/cpp/few_shot_examples/v1_memory_safety.json (~4 examples: leak, use-after-free, double-free, dangling pointer)
- [ ] T139 Create modern-cpp examples set v1 in prompts/cpp/few_shot_examples/v1_modern_cpp.json (~3 examples: range-for, auto, smart pointers)
- [ ] T140 Create performance examples set v1 in prompts/cpp/few_shot_examples/v1_performance.json (~3 examples: unnecessary copy, pass-by-value, algorithmic complexity)
- [ ] T141 Create security examples set v1 in prompts/cpp/few_shot_examples/v1_security.json (~2 examples: buffer overflow, null pointer dereference)
- [ ] T142 Create concurrency examples set v1 in prompts/cpp/few_shot_examples/v1_concurrency.json (~2 examples: race condition, deadlock risk)
- [ ] T143 Ensure all examples follow quality criteria from Phase 2 findings: specific code snippets, issue explanation, reasoning, suggested fix
- [ ] T144 Calibrate examples to reduce false positives based on Phase 2 failure analysis (e.g., show when const NOT needed)

**Total**: 15+ high-quality examples across all categories

### 3.2: Tree-sitter C++ Parsing

**BLOCKED BY**: T136 (Phase 2 complete)

- [ ] T145 Add tree-sitter and tree-sitter-cpp to dependencies in pyproject.toml
- [ ] T146 Implement CppParser class in plugins/cpp/parser.py (~200 lines: parse C++ file into AST, extract functions/classes/methods)
- [ ] T147 Implement extract_functions method in CppParser (~80 lines: return list of function definitions with line numbers)
- [ ] T148 Implement extract_classes method in CppParser (~80 lines: return list of class definitions)
- [ ] T149 Implement chunking logic for large files in CppParser (~100 lines: split file into analyzable units if >32k tokens)
- [ ] T150 Add unit test for CppParser in tests/unit/test_cpp_parser.py (~150 lines: test function/class extraction, test chunking)

### 3.3: Diff-Focused Prompting

**BLOCKED BY**: T146 (CppParser)

- [ ] T151 Implement DiffFormatter class in plugins/cpp/diff_prompt.py (~150 lines: format git diff with BEFORE/AFTER highlighting)
- [ ] T152 Implement changed line marking in DiffFormatter (~60 lines: mark added/removed/modified lines with ✅/❌ symbols)
- [ ] T153 Implement context line control in DiffFormatter (~40 lines: configurable N lines before/after changes)
- [ ] T154 Add unit test for DiffFormatter in tests/unit/test_diff_prompt.py (~100 lines: test diff formatting with various PR diffs)

### 3.4: Production C++ Plugin

**BLOCKED BY**: T144 (curated examples), T150 (CppParser tests), T154 (DiffFormatter tests)

- [ ] T155 Implement ProductionCppPlugin in plugins/cpp/plugin.py (~300 lines: full implementation of 5 DomainPlugin methods)
- [ ] T156 Implement get_few_shot_examples in ProductionCppPlugin (~80 lines: load from JSON files, filter by category)
- [ ] T157 Implement parse_artifact in ProductionCppPlugin (~60 lines: use CppParser to extract functions/classes)
- [ ] T158 Implement format_diff in ProductionCppPlugin (~50 lines: use DiffFormatter for BEFORE/AFTER highlighting)
- [ ] T159 Implement validate_output in ProductionCppPlugin (~100 lines: parse JSON, validate Issue schema, handle malformed output)
- [ ] T160 Implement format_report in ProductionCppPlugin (~100 lines: markdown, JSON, git-comment formats)
- [ ] T161 Add comprehensive unit test for ProductionCppPlugin in tests/unit/test_production_cpp_plugin.py (~200 lines: test all 5 methods, interface compliance)

### 3.5: Winning Technique Configuration

**BLOCKED BY**: T132 (best_all_techniques.yml with winning config)

- [ ] T162 Create production configuration file .llm-framework.yml in repo root (~50 lines: model deepseek-coder:33b, winning technique from Phase 2)
- [ ] T163 Set default technique to best_all_techniques (likely combo_5shot_cot_critique) in .llm-framework.yml
- [ ] T164 Configure token budget allocation in .llm-framework.yml (~30 lines: context 30%, analysis 70%)
- [ ] T165 Configure per-category analysis settings in .llm-framework.yml (~40 lines: memory-safety CRITICAL + CoT deep, performance HIGH, style LOW priority)

### 3.6: CLI Commands for Production Use

**BLOCKED BY**: T161 (ProductionCppPlugin complete), T165 (production config)

- [ ] T166 Implement `analyze-pr` command in cli/main.py (~100 lines: analyze PR diff, extract changed functions, produce line-referenced comments)
- [ ] T167 Add git diff extraction to analyze-pr command (~60 lines: run git diff base..head, parse output)
- [ ] T168 Add output format options to CLI commands (~40 lines: --format markdown|json|git-comment)
- [ ] T169 Add progress indication with Rich for long-running analysis (~50 lines: show "Analyzing... Pass 1/3")
- [ ] T170 Add summary statistics to CLI output (~40 lines: show issues found, token consumption, latency)

### 3.7: Integration Test on sample-pr-001

**BLOCKED BY**: T170 (CLI complete with all features)

- [ ] T171 Verify test-data/cpp/sample-pr-001/ exists with diff.patch and expected-issues.md
- [ ] T172 Run production C++ plugin on sample-pr-001 using analyze-pr command
- [ ] T173 Verify detects 3+ of 4 known critical issues from expected-issues.md
- [ ] T174 Verify false positive rate <20% (manual review of flagged issues)
- [ ] T175 Verify analysis completes in <3 minutes
- [ ] T176 Verify output is markdown report with line-referenced comments

### 3.8: Production Quality Validation

**BLOCKED BY**: T176 (sample-pr-001 test complete)

- [ ] T177 Run ProductionCppPlugin on all 20 ground truth examples with winning technique
- [ ] T178 Calculate final precision on ground truth dataset (target: ≥75%)
- [ ] T179 Calculate final critical recall on ground truth dataset (target: ≥85% for memory-safety and security categories)
- [ ] T180 Calculate final token efficiency (target: >0.5 issues per 1K tokens)
- [ ] T181 Verify all quality targets met, document results in specs/003-llm-framework-core/production_validation.md

### 3.9: Phase 3 Exit Validation

**BLOCKED BY**: T181 (production quality validated)

- [ ] T182 Verify Phase 3 exit gate checklist:
  - ✅ 15+ curated few-shot examples across all categories (T144)
  - ✅ Tree-sitter C++ parsing extracts functions/classes correctly (T150)
  - ✅ Diff-focused prompting formats PR diffs optimally (T154)
  - ✅ Production config uses winning techniques from Phase 2 (T165)
  - ✅ Achieves precision ≥75%, critical recall ≥85% on ground truth (T179)
  - ✅ sample-pr-001 analysis succeeds with actionable feedback in <3 min (T176)

---

## Phase 4: Polish & Documentation (Day 17+)

**Goal**: Final polish, user documentation, quickstart guide.

**BLOCKED BY**: Phase 3 complete (T182)

### 4.1: User Documentation

- [ ] T183 [P] Create docs/quickstart.md (~300 lines: installation, first analysis, running experiments)
- [ ] T184 [P] Create docs/plugin-development.md (~400 lines: implement DomainPlugin interface, example RTL plugin walkthrough)
- [ ] T185 [P] Create docs/experiment-guide.md (~350 lines: run A/B tests, interpret results, create custom configs)
- [ ] T186 [P] Create docs/technique-library.md (~300 lines: catalog of techniques with parameters, effectiveness data from Phase 2)
- [ ] T187 Update README.md with usage examples (~200 lines: analyze command, evaluate command, experiment workflow)
- [ ] T188 Add architecture diagram to README.md (~ASCII art or link to diagram: framework → techniques → plugins → LLM)

### 4.2: Type Hints & Documentation

- [ ] T189 [P] Add comprehensive type hints to all framework modules (mypy --strict passes)
- [ ] T190 [P] Add comprehensive docstrings to all public classes and methods (Google style)
- [ ] T191 [P] Generate API documentation with pydoc or Sphinx

### 4.3: Error Handling & Edge Cases

- [ ] T192 [P] Add error handling for Ollama unavailable in LLMEngine (~30 lines: clear error message, suggest `ollama serve`)
- [ ] T193 [P] Add error handling for invalid plugin in CLI (~20 lines: list available plugins)
- [ ] T194 [P] Add error handling for malformed config in ExperimentRunner (~30 lines: validate YAML schema)
- [ ] T195 [P] Add error handling for LLM timeout in OllamaClient (~20 lines: timeout after 60s, clear error)
- [ ] T196 [P] Add handling for file too large in CppParser (~40 lines: auto-chunk if >32k tokens, warn user)

### 4.4: Testing & CI

- [ ] T197 Add pytest configuration in pytest.ini (~20 lines: test discovery, coverage settings)
- [ ] T198 Add test fixtures for common test data in tests/fixtures/ (~100 lines: mock LLM responses, sample code snippets)
- [ ] T199 Achieve 80%+ unit test coverage for framework/ modules
- [ ] T200 Create integration test suite in tests/integration/ covering all CLI commands
- [ ] T201 Add GitHub Actions workflow (if using GitHub) for CI: run tests on push (~50 lines YAML)

### 4.5: Performance Optimization

- [ ] T202 [P] Profile experiment runs and identify bottlenecks
- [ ] T203 [P] Add parallel execution support for running multiple experiments simultaneously (pytest-xdist style)
- [ ] T204 [P] Optimize prompt construction to minimize token usage
- [ ] T205 [P] Add caching for ground truth dataset loading

### 4.6: Final Validation

- [ ] T206 Verify all Phase 0-3 exit gates still pass after polish
- [ ] T207 Run full experiment matrix one more time to confirm reproducibility
- [ ] T208 Review all documentation for accuracy and completeness
- [ ] T209 Create release checklist in specs/003-llm-framework-core/release_checklist.md

---

## Dependencies & Execution Strategy

### Critical Path (Strictly Sequential)

```
Phase 0 Manual Annotation (T013-T033)
  ↓ BLOCKS
Phase 0 Infrastructure (T034-T068)
  ↓ BLOCKS
Phase 1 Framework Core (T069-T103)
  ↓ BLOCKS
Phase 2 Experiments (T104-T136) ⭐ CORE VALUE
  ↓ BLOCKS
Phase 3 Production Plugin (T137-T182)
  ↓ BLOCKS
Phase 4 Polish (T183-T209)
```

### Parallel Execution Opportunities

**Within Phase 0**:
- T001-T012 (project setup) can all run in parallel
- T055-T066 (experiment configs) can all run in parallel
- T034-T039 (Pydantic models) can run in parallel

**Within Phase 1**:
- T074-T083 (technique implementations) can run in parallel after T072
- T088-T095 (MinimalCppPlugin) can run in parallel after T069

**Within Phase 2**:
- T104-T114 (experiment runs) can run 2-3 in parallel on powerful machine (10-12 hours → 4-6 hours with parallelism)

**Within Phase 3**:
- T138-T142 (few-shot example sets) can run in parallel

**Within Phase 4**:
- T183-T188 (documentation) can all run in parallel
- T189-T191 (type hints, docstrings, API docs) can run in parallel
- T192-T196 (error handling) can run in parallel
- T202-T205 (performance optimizations) can run in parallel

### MVP Recommendation

**Minimum Viable Research Platform** (Weeks 1-2):
- Phase 0: Complete (T001-T068) - MUST HAVE
- Phase 1: Complete (T069-T103) - MUST HAVE
- Phase 2: At least 5 experiment runs (T104-T108, T115, T119-T124) - CORE VALUE
- Phase 3: Skip (production plugin optional for research proof)
- Phase 4: Basic README only (T187)

This MVP proves the research concept with <50% of tasks.

**Full Production Platform** (Weeks 1-4):
- All phases complete (T001-T209)

---

## Task Summary

**Total Tasks**: 209
**Manual Tasks**: 21 (T013-T033 ground truth annotation)
**Automated Tasks**: 188

**Phase Breakdown**:
- Phase 0 (Setup & Experimental Infrastructure): 68 tasks (T001-T068)
- Phase 1 (Framework Core + Techniques): 35 tasks (T069-T103)
- Phase 2 (Experiments - CORE VALUE): 33 tasks (T104-T136)
- Phase 3 (Production C++ Plugin): 46 tasks (T137-T182)
- Phase 4 (Polish & Documentation): 27 tasks (T183-T209)

**Parallel Opportunities**: ~40 tasks can be parallelized within phases

**Estimated Timeline**:
- Phase 0: 2 days (including 4-6 hours manual annotation)
- Phase 1: 5 days
- Phase 2: 5 days (10-12 hours experiment runtime, analysis & writeup)
- Phase 3: 4 days
- Phase 4: 2-3 days
**Total**: 18-19 days (3.5-4 weeks)

**Critical Blockers**:
1. Ground truth annotation (T013-T033) - MUST complete first
2. Ollama installed with models (T012) - MUST verify
3. Each phase blocks the next (strict ordering)

---

## Success Metrics (Track Throughout)

### Research Metrics (PRIMARY)
- [ ] Technique leaderboard generated with F1 scores
- [ ] Statistical significance proven (p<0.05) between top/bottom techniques
- [ ] Reproducibility validated (±5% variance on re-run)
- [ ] Documented findings explaining WHAT works and WHY

### Product Metrics (SECONDARY)
- [ ] C++ plugin precision ≥75%
- [ ] Critical recall (memory-safety, security) ≥85%
- [ ] Token efficiency >0.5 issues per 1K tokens
- [ ] Analysis latency <60 seconds for 500-line PR

### Deliverables
- [ ] experiments/leaderboard.md (research artifact)
- [ ] experiments/findings.md (publication-quality writeup)
- [ ] experiments/runs/ (all timestamped results, reproducible)
- [ ] Production C++ plugin achieving quality targets
- [ ] User documentation (quickstart, plugin dev guide, experiment guide)

---

**The task list makes it crystal clear: Phase 0 → Phase 1 → Phase 2 (experiments = CORE VALUE!) → Phase 3 → Phase 4**

**Start with**: T001 (project setup) and T013 (begin ground truth annotation in parallel)
