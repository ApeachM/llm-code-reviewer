#!/usr/bin/env python3
"""
Demo script to visualize AST-based chunking process.

This shows how the system:
1. Parses C++ code with tree-sitter
2. Extracts AST nodes (functions, classes)
3. Creates chunks with context
4. Prepares input for LLM
"""

from pathlib import Path
from framework.chunker import FileChunker

def main():
    # Create a sample C++ file
    sample_code = """#include <iostream>
#include <vector>
using namespace std;

class Calculator {
private:
    int value;

public:
    Calculator(int v) : value(v) {}

    int add(int x) {
        return value + x;
    }

    int multiply(int x) {
        return value * x;
    }
};

void helperFunction() {
    cout << "Helper" << endl;
}

int main() {
    Calculator calc(10);
    cout << calc.add(5) << endl;
    return 0;
}
"""

    # Write sample file
    sample_file = Path("sample_for_demo.cpp")
    sample_file.write_text(sample_code)

    print("=" * 80)
    print("AST-BASED CHUNKING DEMO")
    print("=" * 80)
    print("\n📄 Original File:")
    print("-" * 80)
    print(sample_code)
    print("-" * 80)

    # Create chunker
    chunker = FileChunker(language='cpp', max_chunk_lines=200)

    # Chunk the file
    print("\n🔪 Chunking file...")
    chunks = chunker.chunk_file(sample_file)

    print(f"\n✅ Created {len(chunks)} chunks\n")

    # Display each chunk
    for i, chunk in enumerate(chunks, 1):
        print("=" * 80)
        print(f"CHUNK {i}: {chunk.chunk_id}")
        print("=" * 80)

        print(f"\n📍 Location:")
        print(f"   File: {chunk.file_path.name}")
        print(f"   Lines: {chunk.start_line}-{chunk.end_line}")
        print(f"   Type: {chunk.metadata.get('node_type')}")
        print(f"   Name: {chunk.metadata.get('node_name')}")

        print(f"\n📦 Context (prepended to chunk):")
        print("-" * 80)
        if chunk.context:
            print(chunk.context)
        else:
            print("(no context)")
        print("-" * 80)

        print(f"\n💻 Chunk Code:")
        print("-" * 80)
        print(chunk.code)
        print("-" * 80)

        print(f"\n🤖 What gets sent to LLM:")
        print("-" * 80)
        if chunk.context:
            full_input = f"{chunk.context}\n\n{chunk.code}"
        else:
            full_input = chunk.code

        print(full_input)
        print("-" * 80)

        print(f"\n📏 Stats:")
        print(f"   Context lines: {len(chunk.context.split(chr(10))) if chunk.context else 0}")
        print(f"   Code lines: {chunk.end_line - chunk.start_line + 1}")
        print(f"   Total input lines: {len(full_input.split(chr(10)))}")
        print()

    # Cleanup
    sample_file.unlink()

    print("\n" + "=" * 80)
    print("KEY POINTS")
    print("=" * 80)
    print("""
1. tree-sitter parses C++ into AST
2. Each function/class becomes a separate chunk
3. Context (includes, usings) is prepended to each chunk
4. LLM analyzes each chunk independently
5. Line numbers are adjusted back to original file
6. Results are merged and deduplicated

This allows analyzing 1000+ line files without hitting token limits!
""")

if __name__ == "__main__":
    main()
