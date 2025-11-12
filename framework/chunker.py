"""
File chunking for large code analysis.

This module provides functionality to split large files into manageable chunks
for LLM analysis, using AST parsing to maintain semantic boundaries.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import tree_sitter_cpp as ts_cpp
from tree_sitter import Language, Parser


@dataclass
class Chunk:
    """
    Represents a chunk of code to be analyzed.

    Attributes:
        chunk_id: Unique identifier (e.g., "large.cpp:MyClass::process:45-120")
        file_path: Original file path
        start_line: Starting line in original file (1-indexed)
        end_line: Ending line in original file (inclusive)
        code: The actual code chunk
        context: Necessary context (imports, class def, etc.)
        metadata: Additional metadata
    """
    chunk_id: str
    file_path: Path
    start_line: int
    end_line: int
    code: str
    context: str
    metadata: dict


class FileChunker:
    """
    Chunk large files into analyzable pieces.

    Strategy:
    1. Parse file with tree-sitter to get AST
    2. Extract top-level functions and class methods
    3. Create chunks with appropriate context
    4. Handle edge cases (templates, macros, nested classes)
    """

    def __init__(self, language: str = 'cpp', max_chunk_lines: int = 200):
        """
        Initialize chunker.

        Args:
            language: Programming language ('cpp', 'python', etc.)
            max_chunk_lines: Maximum lines per chunk
        """
        self.language = language
        self.max_chunk_lines = max_chunk_lines

        # Initialize tree-sitter parser
        CPP_LANGUAGE = Language(ts_cpp.language())
        self.parser = Parser(CPP_LANGUAGE)

    def chunk_file(self, file_path: Path) -> List[Chunk]:
        """
        Split file into chunks.

        Args:
            file_path: Path to file

        Returns:
            List of Chunk objects

        Raises:
            FileNotFoundError: If file doesn't exist
            ParseError: If file cannot be parsed
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Read file
        code_bytes = file_path.read_bytes()
        code_text = code_bytes.decode('utf-8')

        # Parse with tree-sitter
        try:
            tree = self.parser.parse(code_bytes)
        except Exception as e:
            # Fallback to line-based chunking
            print(f"Warning: Parse error ({e}), falling back to line-based chunking")
            return self._fallback_line_chunking(file_path, code_text)

        # Extract chunks
        chunks = []

        # Get file-level context (includes, namespaces)
        file_context = self._extract_file_context(tree, code_text)

        # Extract functions and classes
        for node in tree.root_node.children:
            if node.type in ['function_definition', 'class_specifier',
                            'struct_specifier', 'namespace_definition']:
                chunk = self._create_chunk_from_node(
                    node, file_path, code_text, file_context
                )

                if chunk:
                    # Check size
                    if self._get_chunk_line_count(chunk) <= self.max_chunk_lines:
                        chunks.append(chunk)
                    else:
                        # Split large chunk
                        sub_chunks = self._split_large_chunk(chunk)
                        chunks.extend(sub_chunks)

        # If no chunks extracted (e.g., global code only), fallback
        if not chunks:
            return self._fallback_line_chunking(file_path, code_text)

        return chunks

    def _extract_file_context(self, tree, code_text: str) -> str:
        """
        Extract file-level context (includes, using statements, etc.).

        Returns:
            String containing necessary context
        """
        context_lines = []

        for node in tree.root_node.children:
            if node.type in ['preproc_include', 'using_declaration',
                            'namespace_alias_definition']:
                # Extract line
                start_byte = node.start_byte
                end_byte = node.end_byte
                context_lines.append(code_text[start_byte:end_byte])

        return '\n'.join(context_lines)

    def _create_chunk_from_node(
        self, node, file_path: Path, code_text: str, file_context: str
    ) -> Optional[Chunk]:
        """Create Chunk from AST node."""
        start_line = node.start_point[0] + 1  # tree-sitter is 0-indexed
        end_line = node.end_point[0] + 1

        # Extract code
        start_byte = node.start_byte
        end_byte = node.end_byte
        code = code_text[start_byte:end_byte]

        # Generate chunk ID
        node_name = self._get_node_name(node)
        chunk_id = f"{file_path.name}:{node_name}:{start_line}-{end_line}"

        return Chunk(
            chunk_id=chunk_id,
            file_path=file_path,
            start_line=start_line,
            end_line=end_line,
            code=code,
            context=file_context,
            metadata={'node_type': node.type, 'node_name': node_name}
        )

    def _get_node_name(self, node) -> str:
        """Extract function/class name from node."""
        # Look for declarator or identifier child
        for child in node.children:
            if child.type == 'function_declarator':
                for subchild in child.children:
                    if subchild.type == 'identifier':
                        return subchild.text.decode('utf-8')
            elif child.type == 'type_identifier' or child.type == 'identifier':
                return child.text.decode('utf-8')

        return "unknown"

    def _get_chunk_line_count(self, chunk: Chunk) -> int:
        """Count lines in chunk (code + context)."""
        context_lines = len(chunk.context.split('\n')) if chunk.context else 0
        code_lines = len(chunk.code.split('\n'))
        return context_lines + code_lines

    def _split_large_chunk(self, chunk: Chunk) -> List[Chunk]:
        """
        Split a chunk that exceeds max_chunk_lines.

        Strategy: Split at statement boundaries (every N statements)
        Fallback: Split at line boundaries
        """
        # For now, simple line-based splitting
        lines = chunk.code.split('\n')
        sub_chunks = []

        for i in range(0, len(lines), self.max_chunk_lines):
            sub_code = '\n'.join(lines[i:i + self.max_chunk_lines])
            sub_start = chunk.start_line + i
            sub_end = min(chunk.start_line + i + self.max_chunk_lines - 1, chunk.end_line)

            sub_chunk = Chunk(
                chunk_id=f"{chunk.chunk_id}_part{i // self.max_chunk_lines + 1}",
                file_path=chunk.file_path,
                start_line=sub_start,
                end_line=sub_end,
                code=sub_code,
                context=chunk.context,
                metadata={**chunk.metadata, 'is_split': True}
            )
            sub_chunks.append(sub_chunk)

        return sub_chunks

    def _fallback_line_chunking(self, file_path: Path, code_text: str) -> List[Chunk]:
        """
        Fallback to simple line-based chunking when AST parsing fails.

        Args:
            file_path: Path to file
            code_text: File contents

        Returns:
            List of line-based chunks
        """
        lines = code_text.split('\n')
        chunks = []

        for i in range(0, len(lines), self.max_chunk_lines):
            sub_code = '\n'.join(lines[i:i + self.max_chunk_lines])
            sub_start = i + 1  # 1-indexed
            sub_end = min(i + self.max_chunk_lines, len(lines))

            chunk = Chunk(
                chunk_id=f"{file_path.name}:lines_{sub_start}-{sub_end}",
                file_path=file_path,
                start_line=sub_start,
                end_line=sub_end,
                code=sub_code,
                context='',  # No context extraction in fallback
                metadata={'is_fallback': True}
            )
            chunks.append(chunk)

        return chunks
