# Expected Issues for Sample PR 001

This document lists all intentional bugs that a good C++ reviewer should catch.

## Critical Issues (Must Find)

### 1. Memory Leak in DataProcessor::cachedSum
- **Location**: Line 19, 25
- **Issue**: `cachedSum` is allocated with `new int(0)` but never deleted in destructor
- **Severity**: Critical (memory leak)
- **Fix**: Use `std::unique_ptr<int>` or delete in destructor

### 2. Use-After-Free in getProcessor()
- **Location**: Line 76-80, 91-92
- **Issue**: Returns pointer to object inside local `DataManager` that gets destroyed
- **Severity**: Critical (undefined behavior, crash)
- **Fix**: Don't return pointers to local objects, use smart pointers or copy

### 3. Race Condition in processDataConcurrently()
- **Location**: Line 56-66
- **Issue**: Multiple threads calling `addData()` on same `DataProcessor` without synchronization
- **Severity**: Critical (data race, undefined behavior)
- **Fix**: Use mutex or make `addData()` thread-safe

### 4. Dangling Pointer Risk in currentProcessor
- **Location**: Line 39, 44-46
- **Issue**: `currentProcessor` points into `processors` vector, can dangle on reallocation
- **Severity**: Critical (dangling pointer)
- **Fix**: Use index instead of pointer, or ensure vector doesn't reallocate

## High Priority Issues

### 5. Unnecessary Copy in Constructor
- **Location**: Line 12
- **Issue**: `DataProcessor(std::string n)` passes string by value, causing unnecessary copy
- **Severity**: High (performance)
- **Fix**: `DataProcessor(const std::string& n)` or `std::string_view`

### 6. Raw Pointers Instead of Smart Pointers
- **Location**: Line 35 (DataManager::processors)
- **Issue**: Using `std::vector<DataProcessor*>` with manual new/delete
- **Severity**: High (error-prone, not modern C++)
- **Fix**: Use `std::vector<std::unique_ptr<DataProcessor>>`

### 7. Missing const Qualifier
- **Location**: Line 30
- **Issue**: `getName()` doesn't modify state but isn't marked `const`
- **Severity**: Medium (const-correctness)
- **Fix**: `std::string getName() const`

### 8. Return by Value Instead of const&
- **Location**: Line 30
- **Issue**: `getName()` returns string by value, causing copy
- **Severity**: Medium (performance)
- **Fix**: `const std::string& getName() const`

## Medium Priority Issues

### 9. Inefficient Temporary Vector
- **Location**: Line 50
- **Issue**: `std::vector<DataProcessor*> temp = processors;` creates unnecessary copy
- **Severity**: Medium (performance)
- **Fix**: Iterate directly over `processors`, or use `const auto&`

### 10. Non-idiomatic Range-for with Raw Pointers
- **Location**: Line 51
- **Issue**: `for (auto proc : temp)` copies pointers (though cheap)
- **Severity**: Low (style)
- **Fix**: `for (auto* proc : processors)` or `for (const auto& proc : processors)`

## Summary Statistics

- **Critical**: 4 issues (memory safety, concurrency, undefined behavior)
- **High**: 4 issues (performance, modern C++ practices)
- **Medium**: 2 issues (const-correctness, efficiency)

**Total**: 10 issues

## Review Quality Metrics

A **good** LLM reviewer should find:
- ≥ 90% of Critical issues (≥ 3-4 out of 4)
- ≥ 70% of High priority issues (≥ 3 out of 4)
- ≥ 50% of Medium priority issues (≥ 1 out of 2)

A **excellent** LLM reviewer should find:
- 100% of Critical issues (4 out of 4)
- ≥ 90% of High priority issues (≥ 3-4 out of 4)
- ≥ 75% of Medium priority issues (≥ 1-2 out of 2)

**False Positive Tolerance**: < 20% (no more than 2 false positives per 10 real issues)
