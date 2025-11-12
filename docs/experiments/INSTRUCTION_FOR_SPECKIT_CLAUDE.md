# Instruction for Spec-kit Claude: Large PR Analysis Experiment

## Context

You are working with an LLM-powered C++ code analysis framework located at:
```
/home/baum/workspace/claude-home/cpp-llm-reviewer
```

This framework has been fully developed through Phase 5 and includes:
- ✅ Domain-agnostic architecture with plugin system
- ✅ Multiple analysis techniques (zero-shot, few-shot, CoT, hybrid)
- ✅ Large file support via AST-based chunking
- ✅ PR analysis capability with git integration
- ✅ CLI interface for production use
- ✅ 83/84 tests passing (98.8% pass rate)

## Your Task

**Run a large-scale PR analysis experiment to validate the system works on realistic, multi-file pull requests with 10+ files and 300+ lines changed.**

This experiment will demonstrate:
1. The system can handle PRs larger than the test suite's sample PR (which was only 1 file)
2. Chunking works properly when multiple large files are analyzed
3. The analysis produces actionable results in reasonable time
4. The framework is ready for real-world use

## Step-by-Step Instructions

### Phase 1: Setup and Verification (5 minutes)

```bash
cd /home/baum/workspace/claude-home/cpp-llm-reviewer

# Verify virtual environment exists
ls venv/bin/activate

# Activate environment
source venv/bin/activate

# Verify CLI works
python3 -m cli.main --help

# Check current branch
git branch
git status
```

Expected: Clean working directory on `main` branch.

---

### Phase 2: Create Synthetic Large PR (10 minutes)

**Why Synthetic?**
- Faster than cloning external repos
- Controlled environment with known issues
- Easier to evaluate accuracy

**Create the branch:**
```bash
git checkout -b experiment/synthetic-large-pr-2024
```

**Create test directory:**
```bash
mkdir -p test-data/synthetic-pr
```

**Generate 15 C++ files with intentional issues:**

Each file should contain a mix of:
- ❌ Critical issues: memory leaks, buffer overflows, null pointer dereferences
- ⚠️ Warnings: performance issues, modernization opportunities
- Some correct code (to test false positive rate)

**Example file template** (create variations of this for all 15 files):

```cpp
#include <iostream>
#include <vector>
#include <string>
#include <memory>

// File: test-data/synthetic-pr/module_{N}.cpp
// Purpose: Test large PR analysis with file {N} of 15

class DataProcessor {
private:
    int* data;  // Issue: raw pointer
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

    // Issue: Using strcpy (unsafe)
    void setName(char* dest, const char* src) {
        strcpy(dest, src);  // Buffer overflow risk
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

// Issue: String concatenation in loop (inefficient)
std::string buildString(const std::vector<std::string>& parts) {
    std::string result;
    for (int i = 0; i < parts.size(); i++) {
        result = result + parts[i];  // Should use +=
    }
    return result;
}

int main() {
    DataProcessor* proc = new DataProcessor(10);  // Issue: new without delete

    std::vector<int> data = {1, 2, 3, 4, 5};
    proc->processVector(data);

    int arr[5] = {1, 2, 3, 4, 5};
    processArray(arr, 5);

    std::cout << divide(10, 0) << std::endl;  // Issue: Division by zero

    char buffer[10];
    proc->setName(buffer, "This is a very long string that will overflow");

    return 0;  // Issue: Memory leak - proc never deleted
}
```

**Generate all 15 files:**
Create variations by:
- Changing class names: `DataProcessor` → `FileHandler`, `NetworkManager`, etc.
- Changing function names
- Adding more or fewer issues per file
- Varying file length (100-300 lines each)

Use a script or loop to create them quickly:

```bash
for i in {1..15}; do
  cat > test-data/synthetic-pr/module_${i}.cpp << 'ENDOFFILE'
[Paste the template above with variations]
ENDOFFILE
done
```

**Verify file creation:**
```bash
ls -lh test-data/synthetic-pr/
wc -l test-data/synthetic-pr/*.cpp
```

Expected: 15 files, each ~100-200 lines.

---

### Phase 3: Commit the Synthetic PR (2 minutes)

```bash
git add test-data/synthetic-pr/
git status  # Should show 15 new files

git commit -m "test: Add synthetic large PR with 15 C++ files for experiment

This synthetic PR contains 15 C++ files with intentional issues:
- Memory leaks (missing destructors)
- Buffer overflows (unsafe string operations)
- Off-by-one errors
- Performance issues (pass by value)
- Modern C++ violations (raw pointers)

Expected issues: ~8-10 per file = 120-150 total issues

Purpose: Validate PR analysis on realistic multi-file changes."

git log --oneline -1  # Verify commit
```

---

### Phase 4: Run PR Analysis (10-20 minutes)

**Important**: This will take time because it analyzes 15 files with LLM.

```bash
cd /home/baum/workspace/claude-home/cpp-llm-reviewer
source venv/bin/activate

# Create output directory
mkdir -p experiments/large-pr

# Run the analysis with timeout (10 minutes max)
timeout 600 python3 -m cli.main analyze pr \
  --base main \
  --head experiment/synthetic-large-pr-2024 \
  --chunk \
  --output experiments/large-pr/synthetic-pr-analysis.md

echo "Exit code: $?"
```

**Expected output:**
- Analysis starts
- Files are processed one by one
- Each large file (>300 lines) gets chunked
- Progress messages printed
- Results written to markdown file

**If timeout occurs (exit code 124):**
- This is expected for 15 files
- Check partial results in the output file
- Consider reducing to 10 files and retry

**If errors occur:**
- Check Ollama is running: `ollama list`
- Check model exists: `ollama list | grep deepseek`
- Verify syntax of generated C++ files: `g++ -fsyntax-only test-data/synthetic-pr/module_1.cpp`

---

### Phase 5: Analyze Results (10 minutes)

**Read the generated report:**
```bash
cat experiments/large-pr/synthetic-pr-analysis.md
```

**Count metrics:**
```bash
# Total files analyzed
grep -c "^###.*\.cpp" experiments/large-pr/synthetic-pr-analysis.md

# Total issues found
grep -c "^🔴\|^🟡" experiments/large-pr/synthetic-pr-analysis.md

# Critical issues
grep -c "^🔴" experiments/large-pr/synthetic-pr-analysis.md

# Warnings
grep -c "^🟡" experiments/large-pr/synthetic-pr-analysis.md

# Issues by category
grep "\[.*\]" experiments/large-pr/synthetic-pr-analysis.md | \
  sed 's/.*\[\(.*\)\].*/\1/' | sort | uniq -c | sort -rn
```

**Manual evaluation:**

For each of the 15 files, check:
1. ✅ Was the file analyzed?
2. ✅ Were the intentional issues found?
3. ❌ Any false positives?
4. ⭐ Any surprising issues found (true positives we didn't expect)?

**Expected results:**
- **Coverage**: 15/15 files analyzed
- **Detection rate**: 60-80% of intentional issues found
- **False positives**: <20%
- **Categories**: memory-safety, performance, modern-cpp should be top 3

---

### Phase 6: Document Results (10 minutes)

Create a summary document:

```bash
cat > experiments/large-pr/EXPERIMENT_SUMMARY.md << 'EOF'
# Large PR Analysis Experiment Results

**Date**: $(date)
**Branch**: experiment/synthetic-large-pr-2024
**Analyzer**: Claude (Spec-kit session)

## Experiment Setup

- **PR Type**: Synthetic (controlled)
- **Files**: 15 C++ files
- **Lines changed**: ~2,000 lines
- **Intentional issues**: ~120-150 issues
- **Categories**: memory-safety, performance, modern-cpp, security

## Performance Metrics

- **Execution time**: [FILL IN] seconds
- **Timeout**: No / Yes (if yes, at which file?)
- **Files analyzed**: [FILL IN] / 15
- **Chunks created**: [FILL IN]

## Quality Metrics

- **Total issues found**: [FILL IN]
- **Critical issues**: [FILL IN]
- **Warnings**: [FILL IN]
- **False positives (estimated)**: [FILL IN]
- **Detection rate (estimated)**: [FILL IN]%

## Issues by Category

[Paste the output from grep category count above]

## Sample Issues Found

### Memory Safety
[Copy 2-3 example critical issues from report]

### Performance
[Copy 2-3 example warning issues from report]

### Modern C++
[Copy 2-3 example modernization suggestions from report]

## Evaluation

### What Worked Well
- [List positives]

### Issues Missed
- [List known issues that were not detected]

### False Positives
- [List any incorrect findings]

### Surprises
- [List unexpected findings or insights]

## Recommendations

Based on this experiment:
1. [Performance recommendation]
2. [Accuracy recommendation]
3. [Next steps]

## Conclusion

[Overall assessment: Is the system ready for production use?]

EOF
```

Fill in the placeholders based on actual results.

---

### Phase 7: Commit Results (2 minutes)

```bash
git add experiments/large-pr/

git commit -m "experiment: Add large PR analysis results

Analyzed synthetic PR with 15 C++ files:
- Found X issues (Y critical, Z warnings)
- Execution time: A seconds
- Detection rate: B%

Results demonstrate system can handle multi-file PRs."

# Return to main branch
git checkout main

# Optionally merge experiment results (not the test files)
git checkout experiment/synthetic-large-pr-2024 -- experiments/large-pr/
git add experiments/large-pr/
git commit -m "docs: Add large PR experiment results to main"
```

---

## Success Criteria

### Minimum (Must achieve)
- ✅ PR analysis completes (even if with timeout)
- ✅ At least 10/15 files analyzed
- ✅ At least 60 issues found
- ✅ Report generated in markdown format

### Target (Should achieve)
- ✅ All 15/15 files analyzed
- ✅ 80-100 issues found (60-70% detection rate)
- ✅ Completes within 10 minutes
- ✅ False positive rate <20%

### Stretch (Nice to have)
- ✅ 100+ issues found (70%+ detection rate)
- ✅ Completes within 5 minutes
- ✅ Identifies all critical issues (memory leaks, buffer overflows)
- ✅ Report is immediately actionable

---

## Troubleshooting

### Problem: Ollama not responding
```bash
# Check if Ollama is running
ps aux | grep ollama

# Start Ollama
ollama serve &

# Verify model
ollama list
ollama pull deepseek-coder:33b-instruct
```

### Problem: Python environment issues
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### Problem: Git issues
```bash
# If branch already exists
git branch -D experiment/synthetic-large-pr-2024
git checkout -b experiment/synthetic-large-pr-2024

# If merge conflicts
git checkout main
git branch -D experiment/synthetic-large-pr-2024
# Start over
```

### Problem: Analysis takes too long
- **Option 1**: Reduce to 10 files instead of 15
- **Option 2**: Use smaller model: `--model deepseek-coder:6.7b`
- **Option 3**: Disable chunking for files <200 lines

---

## Alternative: Real OSS PR (Optional)

If synthetic PR is too easy, try real open-source:

```bash
cd /tmp
git clone --depth=100 https://github.com/bitcoin/bitcoin.git
cd bitcoin

# Find a recent merged PR
git log --oneline --merges --since="3 months ago" | head -10

# Pick one and inspect
git show --stat <merge-commit>

# Analyze it
cd /home/baum/workspace/claude-home/cpp-llm-reviewer
source venv/bin/activate

timeout 600 python3 -m cli.main analyze pr \
  --repo /tmp/bitcoin \
  --base <base-commit> \
  --head <head-commit> \
  --chunk \
  --output experiments/large-pr/bitcoin-pr-analysis.md
```

This will be more realistic but less controlled.

---

## Final Deliverable

When complete, provide:

1. **Branch**: `experiment/synthetic-large-pr-2024` with 15 test files
2. **Report**: `experiments/large-pr/synthetic-pr-analysis.md` (full LLM output)
3. **Summary**: `experiments/large-pr/EXPERIMENT_SUMMARY.md` (your analysis)
4. **Metrics**: Execution time, detection rate, false positive rate
5. **Recommendation**: Is the system production-ready?

---

## Timeline Estimate

- Phase 1 (Setup): 5 min
- Phase 2 (Create files): 10 min
- Phase 3 (Commit): 2 min
- Phase 4 (Run analysis): 10-20 min
- Phase 5 (Analyze): 10 min
- Phase 6 (Document): 10 min
- Phase 7 (Commit): 2 min

**Total**: ~50-60 minutes

---

## Notes

- The framework is already fully implemented and tested
- This experiment is **validation**, not development
- Focus on **measuring and documenting** results
- If something doesn't work, debug it - the system is stable
- Results will inform future improvements (Phase 6+)

Good luck! This experiment will demonstrate the system's readiness for production use.
