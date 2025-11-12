# Large PR Analysis Experiment

## Objective

Test the LLM Framework's PR analysis capability on real-world, large-scale pull requests from open-source projects to validate:

1. **Scalability** - Can handle PRs with 10+ files, 500+ lines changed
2. **Accuracy** - Finds meaningful issues vs. false positives
3. **Performance** - Completes within reasonable time (<10 minutes)
4. **Chunking** - Large file support works in PR context
5. **Practical value** - Issues found would be useful in code review

## Target Projects (C++ Open Source)

### Option A: LLVM Project
- **Repository**: https://github.com/llvm/llvm-project
- **Example PRs**:
  - Recent merged PRs with 10+ files
  - Focus on llvm/lib/ or clang/lib/ directories
- **Why**: Industry-standard, high-quality C++ codebase

### Option B: Bitcoin Core
- **Repository**: https://github.com/bitcoin/bitcoin
- **Example PRs**:
  - Wallet feature PRs
  - Consensus changes
- **Why**: Security-critical, well-reviewed code

### Option C: OpenCV
- **Repository**: https://github.com/opencv/opencv
- **Example PRs**:
  - Algorithm implementations
  - Performance optimizations
- **Why**: Complex algorithms, performance-sensitive

## Experiment Setup

### Step 1: Clone Target Repository

```bash
cd /tmp
git clone --depth=100 https://github.com/llvm/llvm-project.git
cd llvm-project
```

### Step 2: Find Suitable PR

**Criteria for PR selection**:
- Merged within last 6 months
- 10-30 files changed
- 300-1000 lines changed
- Mix of additions and modifications
- Not just documentation/tests

**Find PRs**:
```bash
# List recent merged branches
git log --oneline --merges --since="6 months ago" | head -20

# Pick a merge commit and inspect
git show --stat <commit-hash>

# Identify base and head commits
git log --oneline <commit-hash>^1..<commit-hash>^2
```

### Step 3: Run PR Analysis

```bash
cd /home/baum/workspace/claude-home/cpp-llm-reviewer
source venv/bin/activate

# Analyze the PR
python3 -m cli.main analyze pr \
  --repo /tmp/llvm-project \
  --base <base-commit> \
  --head <head-commit> \
  --chunk \
  --output experiments/large-pr-analysis-results.md

# With timeout for safety
timeout 600 python3 -m cli.main analyze pr \
  --repo /tmp/llvm-project \
  --base <base-commit> \
  --head <head-commit> \
  --chunk \
  --output experiments/large-pr-analysis-results.md
```

### Step 4: Evaluate Results

Manually review the generated report:

1. **Coverage**: How many files were analyzed?
2. **Relevance**: Are the issues meaningful?
3. **False Positives**: Any obvious incorrect findings?
4. **Critical Issues**: Any security/memory safety issues found?
5. **Performance**: Total execution time

## Alternative Approach: Create Synthetic Large PR

If cloning external repos is not feasible, create a synthetic large PR in the current repo:

### Synthetic PR Setup

```bash
cd /home/baum/workspace/claude-home/cpp-llm-reviewer

# Create a new branch with intentional issues
git checkout -b experiment/synthetic-large-pr

# Create multiple C++ test files with various issues
for i in {1..15}; do
  cat > test-data/synthetic-pr/file_${i}.cpp << 'EOF'
#include <iostream>
#include <vector>
#include <string>

class DataProcessor {
private:
    int* data;
    size_t size;

public:
    // Issue: Missing destructor - memory leak
    DataProcessor(size_t n) : size(n) {
        data = new int[n];
    }

    // Issue: No bounds checking
    int get(size_t index) {
        return data[index];
    }

    // Issue: Pass by value instead of const reference
    void processVector(std::vector<int> v) {
        for (size_t i = 0; i < v.size(); i++) {
            data[i % size] = v[i] * 2;
        }
    }

    // Issue: Raw pointer return without ownership clarity
    int* getData() {
        return data;
    }
};

// Issue: Using C-style array
void processArray(int arr[], int size) {
    for (int i = 0; i <= size; i++) {  // Issue: Off-by-one error
        std::cout << arr[i] << std::endl;
    }
}

// Issue: Division by zero not checked
double divide(int a, int b) {
    return static_cast<double>(a) / b;
}

int main() {
    DataProcessor* proc = new DataProcessor(10);  // Issue: new without delete

    std::vector<int> data = {1, 2, 3, 4, 5};
    proc->processVector(data);

    int arr[5] = {1, 2, 3, 4, 5};
    processArray(arr, 5);

    std::cout << divide(10, 0) << std::endl;  // Issue: Division by zero

    return 0;
}
EOF
done

# Commit the changes
git add test-data/synthetic-pr/
git commit -m "test: Add synthetic large PR with 15 files for experiment"

# Analyze this PR
python3 -m cli.main analyze pr \
  --base main \
  --head experiment/synthetic-large-pr \
  --chunk \
  --output experiments/synthetic-pr-analysis.md
```

## Success Criteria

### Minimum Requirements
- ✅ Analysis completes without crashing
- ✅ Finds at least 50% of known issues
- ✅ Completes within 10 minutes for 15 files
- ✅ Generates readable markdown report

### Ideal Outcome
- ✅ Finds 80%+ of known issues
- ✅ False positive rate < 20%
- ✅ Identifies critical issues (memory leaks, security)
- ✅ Completes within 5 minutes
- ✅ Report is actionable for developers

## Data to Collect

1. **Performance Metrics**:
   - Total execution time
   - Number of files analyzed
   - Number of chunks created
   - Tokens used (if tracked)

2. **Quality Metrics**:
   - Total issues found
   - Issues by severity (critical/warning)
   - Issues by category
   - False positive count (manual assessment)

3. **Coverage**:
   - Files analyzed vs. total files changed
   - Lines covered by analysis

## Expected Issues Template

For the synthetic PR, expected issues per file:

1. ❌ Memory leak - missing destructor (critical)
2. ❌ No bounds checking in `get()` (critical)
3. ⚠️ Pass by value instead of const reference (performance)
4. ⚠️ Off-by-one error in loop (critical)
5. ❌ Division by zero not checked (critical)
6. ⚠️ Manual memory management without RAII (modern-cpp)
7. ⚠️ Raw pointer return without ownership documentation (modern-cpp)
8. ⚠️ Using C-style array instead of std::array (modern-cpp)

**Total expected: ~8 issues per file × 15 files = 120 issues**

## Running the Experiment

### For Current Claude Session

```bash
# Option 1: Synthetic PR (faster, controlled)
cd /home/baum/workspace/claude-home/cpp-llm-reviewer
git checkout -b experiment/synthetic-large-pr
# [Create files as described above]
git add test-data/synthetic-pr/
git commit -m "test: Add synthetic large PR"
timeout 600 python3 -m cli.main analyze pr \
  --base main \
  --head experiment/synthetic-large-pr \
  --chunk \
  --output experiments/synthetic-pr-results.md

# Option 2: Real OSS PR (realistic, but slower)
cd /tmp
git clone --depth=100 https://github.com/bitcoin/bitcoin.git
cd bitcoin
git log --oneline --merges | head -10
# Pick a merge commit
git show --stat <commit-hash>
# Analyze
cd /home/baum/workspace/claude-home/cpp-llm-reviewer
timeout 600 python3 -m cli.main analyze pr \
  --repo /tmp/bitcoin \
  --base <base-commit> \
  --head <head-commit> \
  --chunk \
  --output experiments/bitcoin-pr-results.md
```

### For Spec-kit Claude Session

Provide this instruction:

```
I have an LLM-powered C++ code analysis framework at:
/home/baum/workspace/claude-home/cpp-llm-reviewer

Please run a large PR analysis experiment to validate the system works on realistic PRs.

Follow the guide at: docs/experiments/LARGE_PR_EXPERIMENT.md

Specifically:
1. Create a synthetic large PR with 15 C++ files containing common issues
2. Run PR analysis with chunking enabled
3. Evaluate the results against expected issues
4. Report performance metrics and quality assessment

The framework is already set up with:
- Virtual environment at venv/
- CLI command: python3 -m cli.main analyze pr
- All dependencies installed

Focus on the "Synthetic PR" approach since it's faster and more controlled.
```

## Post-Experiment Analysis

After running the experiment, analyze:

1. **What worked well?**
   - Which categories had high detection rate?
   - Was performance acceptable?
   - Did chunking work properly?

2. **What needs improvement?**
   - Which issues were missed?
   - Any false positives?
   - Performance bottlenecks?

3. **Recommendations**:
   - Should we adjust chunk size?
   - Do we need better prompts for certain categories?
   - Should we add more examples to few-shot?

## Integration with Existing Experiments

This experiment extends the existing Phase 0-5 tests:

- **Phase 0**: Single file analysis (baseline)
- **Phase 1**: Few-shot improvements
- **Phase 2-4**: Technique refinements
- **Phase 5**: Large file chunking
- **This experiment**: Large PR with multiple large files

Results should be tracked in `experiments/runs/` with timestamp.
