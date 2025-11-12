# Domain-Agnostic LLM Engineering Framework

**An LLM engineering research platform** that discovers, measures, and documents which prompting techniques work best for code analysis.

## Core Value Proposition

This is **NOT** just another code analysis tool. This is a **research platform** where the primary value is systematic experimentation proving which LLM techniques (few-shot learning, multi-pass review, chain-of-thought, self-critique) are most effective.

**Research findings with statistical evidence** (precision, recall, F1, token efficiency) are the primary deliverable, not just "another code review tool."

## Key Differentiators

- **Experiment-First Architecture**: Evaluation infrastructure built BEFORE features
- **Technique Modularity**: Each LLM technique (few-shot, multi-pass, CoT) is independently testable
- **Statistical Rigor**: A/B testing with t-tests, p-values, significance testing
- **Complete Reproducibility**: Timestamped experiment runs with full prompt history
- **Domain-Agnostic**: Plugin architecture for C++, RTL, Power, Design analysis

## Research Results (Phase 2)

*Placeholder for leaderboard and findings after experiments complete*

Expected findings:
- Few-shot learning: +40% accuracy over zero-shot
- Multi-pass self-critique: -20% false positives
- Chain-of-thought: +30% complex bug detection
- Diff-focused prompting: -50% token consumption

## Quick Start

### Prerequisites

1. **Python 3.11+**
2. **Ollama** installed and running:
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ollama pull deepseek-coder:33b
   ollama pull qwen2.5:14b
   ```

### Installation

```bash
pip install -r requirements.txt
```

### Run Your First Experiment

```bash
# Run single experiment
llm-framework experiment run --config experiments/configs/few_shot_5.yml

# Compare techniques
llm-framework experiment compare --techniques few_shot_3,few_shot_5

# Generate leaderboard
llm-framework experiment leaderboard
```

## Project Structure

```
framework/              # Core LLM engineering infrastructure
├── evaluation.py       # GroundTruthDataset, MetricsCalculator
├── experiment_runner.py # A/B testing framework
├── prompt_logger.py    # Log all LLM interactions
├── statistical_analyzer.py # Significance testing
└── techniques/         # Modular technique implementations
    ├── few_shot.py
    ├── multi_pass.py
    ├── chain_of_thought.py
    └── ...

experiments/            # Research artifacts (FIRST-CLASS!)
├── ground_truth/       # Annotated examples (version controlled)
├── configs/            # Experiment configurations
├── runs/               # Timestamped results (gitignored)
└── leaderboard.md      # Research findings

plugins/                # Domain-specific plugins
└── cpp/                # C++ code review plugin

cli/                    # Command-line interface

docs/                   # Documentation
├── README.md           # This file
├── QUICKSTART.md       # Quick start guide
├── phases/             # Phase completion documents (0-5)
├── architecture/       # Architecture & technical guides
├── experiments/        # Experiment methodologies
├── guides/             # User guides (Spec-kit, etc)
└── specs/              # Spec-kit specifications

tests/                  # Unit and integration tests
```

## Architecture

**Experiment-First**: Measurement infrastructure → Techniques → Plugins → Analysis

```
ExperimentRunner → Technique (few-shot, multi-pass, CoT) → Plugin (C++, RTL) → Ollama
                ↓
         MetricsCalculator (precision, recall, F1)
                ↓
         StatisticalAnalyzer (t-test, p-values)
                ↓
         Leaderboard (research findings)
```

## Development Status

- [x] Phase 0: Experimental Infrastructure
- [x] Phase 1: Framework Core + Few-shot Techniques (F1: 0.615)
- [x] Phase 2: Multi-technique Experiments
- [x] Phase 3: Production C++ Plugin
- [x] Phase 4: Hybrid Analysis (Few-shot + Chain-of-Thought)
- [x] Phase 5: Large File Support (AST-based Chunking)

**Current Status**: Production-ready for C++ code analysis with PR support

## Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Get started in 5 minutes
- **[Architecture Overview](architecture/ARCHITECTURE.md)** - System design and components
- **[Developer Guide](architecture/DEVELOPER_GUIDE.md)** - Contributing and extending
- **[AST Chunking Explained](architecture/AST_CHUNKING_EXPLAINED.md)** - Deep dive into large file handling
- **[Phase Documents](phases/)** - Detailed phase completion reports
- **[Experiment Guides](experiments/)** - How to run experiments

## License

MIT License - See [LICENSE](../LICENSE) for details

## Contributing

This is a research platform emphasizing systematic LLM engineering. Contributions should include:
- Quantitative evaluation results
- Statistical significance testing
- Reproducible experiment configs
- Documented findings (what works and why)
