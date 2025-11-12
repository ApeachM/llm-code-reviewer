"""
Production code analyzer.

Uses research findings from Phase 2 to provide production-ready code analysis.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
from framework.models import AnalysisRequest, AnalysisResult, Issue
from framework.ollama_client import OllamaClient
from framework.techniques import FewShotTechnique
from plugins.domain_plugin import DomainPlugin
from plugins.cpp_plugin import CppPlugin


class ProductionAnalyzer:
    """
    Production-ready code analyzer.

    Features:
    - Uses few-shot-5 (Phase 2 winner: +17% F1 over baseline)
    - Domain plugin architecture
    - Git integration ready
    - PR review ready
    """

    def __init__(
        self,
        plugin: Optional[DomainPlugin] = None,
        model_name: str = "deepseek-coder:33b-instruct",
        temperature: float = 0.1
    ):
        """
        Initialize production analyzer.

        Args:
            plugin: Domain plugin (defaults to CppPlugin)
            model_name: Ollama model name
            temperature: Sampling temperature
        """
        self.plugin = plugin or CppPlugin()
        self.model_name = model_name
        self.temperature = temperature

        # Create Ollama client
        self.client = OllamaClient(
            model_name=model_name,
            temperature=temperature,
            max_tokens=2000
        )

        # Create technique with plugin's examples
        self.technique = self._create_technique()

    def _create_technique(self) -> FewShotTechnique:
        """
        Create few-shot technique using plugin examples.

        Returns:
            Configured FewShotTechnique
        """
        config = {
            'technique_name': 'few_shot_5',
            'technique_params': {
                'system_prompt': self.plugin.get_system_prompt(),
                'few_shot_examples': self.plugin.get_few_shot_examples(num_examples=5),
                'temperature': self.temperature,
                'max_tokens': 2000
            }
        }

        return FewShotTechnique(self.client, config)

    def analyze_file(
        self,
        file_path: Path,
        chunk_mode: bool = False,
        max_chunk_lines: int = 200,
        max_workers: int = 4
    ) -> Optional[AnalysisResult]:
        """
        Analyze a single file.

        Args:
            file_path: Path to file
            chunk_mode: Enable chunking for large files
            max_chunk_lines: Maximum lines per chunk
            max_workers: Number of parallel workers for chunk analysis (default: 4)

        Returns:
            AnalysisResult or None if file should not be analyzed
        """
        # Check if file should be analyzed
        if not self.plugin.should_analyze_file(file_path):
            return None

        # Decide: chunked or whole-file analysis
        if chunk_mode and self._should_use_chunking(file_path):
            return self._analyze_chunked(file_path, max_chunk_lines, max_workers)
        else:
            return self._analyze_whole(file_path)

    def _should_use_chunking(self, file_path: Path) -> bool:
        """
        Determine if file should be chunked.

        Criteria: file > 300 lines

        Args:
            file_path: Path to file

        Returns:
            True if file should be chunked
        """
        try:
            code = file_path.read_text(encoding='utf-8')
            line_count = len(code.split('\n'))
            return line_count > 300
        except Exception:
            return False

    def _analyze_whole(self, file_path: Path) -> Optional[AnalysisResult]:
        """
        Analyze file as a whole (existing logic).

        Args:
            file_path: Path to file

        Returns:
            AnalysisResult or None on error
        """
        # Read file
        try:
            code = file_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None

        # Preprocess code
        code = self.plugin.preprocess_code(code, file_path)

        # Create analysis request
        request = AnalysisRequest(
            code=code,
            file_path=str(file_path),
            language=self.plugin.name
        )

        # Analyze
        result = self.technique.analyze(request)

        # Postprocess issues
        result.issues = self.plugin.postprocess_issues(result.issues)

        return result

    def _analyze_chunked(
        self, file_path: Path, max_chunk_lines: int, max_workers: int = 4
    ) -> AnalysisResult:
        """
        Analyze file using chunking strategy.

        Steps:
        1. Chunk file with FileChunker
        2. Analyze each chunk with ChunkAnalyzer
        3. Merge results with ResultMerger

        Args:
            file_path: Path to file
            max_chunk_lines: Maximum lines per chunk

        Returns:
            Merged AnalysisResult
        """
        from framework.chunker import FileChunker
        from framework.chunk_analyzer import ChunkAnalyzer
        from framework.result_merger import ResultMerger

        # Chunk file
        chunker = FileChunker(
            language=self.plugin.name,
            max_chunk_lines=max_chunk_lines
        )
        chunks = chunker.chunk_file(file_path)

        print(f"Chunked file into {len(chunks)} chunks")

        # Analyze chunks in parallel
        chunk_analyzer = ChunkAnalyzer(analyzer=self)

        print(f"Analyzing {len(chunks)} chunks in parallel (workers={max_workers})...")
        chunk_results = chunk_analyzer.analyze_chunks_parallel(chunks, max_workers=max_workers)

        # Merge results
        merger = ResultMerger()
        merged_result = merger.merge(chunk_results)

        # Postprocess (existing plugin logic)
        merged_result.issues = self.plugin.postprocess_issues(merged_result.issues)

        return merged_result

    def analyze_directory(
        self,
        directory: Path,
        recursive: bool = True
    ) -> Dict[Path, AnalysisResult]:
        """
        Analyze all files in a directory.

        Args:
            directory: Directory to analyze
            recursive: Whether to recurse into subdirectories

        Returns:
            Dictionary mapping file paths to analysis results
        """
        results = {}

        # Find all matching files
        if recursive:
            pattern = f"**/*"
        else:
            pattern = "*"

        for file_path in directory.glob(pattern):
            if not file_path.is_file():
                continue

            result = self.analyze_file(file_path)
            if result:
                results[file_path] = result

        return results

    def analyze_git_diff(
        self,
        repo_path: Path,
        base_branch: str = "main",
        head_branch: str = "HEAD"
    ) -> Dict[Path, AnalysisResult]:
        """
        Analyze only files changed in git diff.

        Args:
            repo_path: Path to git repository
            base_branch: Base branch to compare against
            head_branch: Head branch/commit

        Returns:
            Dictionary mapping changed files to analysis results
        """
        import subprocess

        # Get list of changed files
        try:
            result = subprocess.run(
                ['git', 'diff', '--name-only', f'{base_branch}...{head_branch}'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            changed_files = result.stdout.strip().split('\n')
        except subprocess.CalledProcessError as e:
            print(f"Git diff failed: {e}")
            return {}

        # Analyze each changed file
        results = {}
        for file_name in changed_files:
            if not file_name:
                continue

            file_path = repo_path / file_name
            if not file_path.exists():
                continue

            result = self.analyze_file(file_path)
            if result:
                results[file_path] = result

        return results

    def format_results_markdown(self, results: Dict[Path, AnalysisResult]) -> str:
        """
        Format analysis results as markdown (for PR comments).

        Args:
            results: Analysis results

        Returns:
            Markdown-formatted report
        """
        if not results:
            return "✅ No issues found!"

        report = "## Code Analysis Results\n\n"
        report += f"🤖 Analyzed {len(results)} file(s) using LLM-powered analysis\n\n"

        # Count issues by severity
        total_issues = sum(len(r.issues) for r in results.values())
        critical_count = sum(
            len([i for i in r.issues if i.severity == 'critical'])
            for r in results.values()
        )

        report += f"**Found {total_issues} issue(s)** "
        if critical_count > 0:
            report += f"({critical_count} critical ⚠️)\n\n"
        else:
            report += "\n\n"

        # Report by file
        for file_path, result in results.items():
            if not result.issues:
                continue

            report += f"### 📄 {file_path.name}\n\n"

            for issue in result.issues:
                # Severity emoji
                severity_emoji = {
                    'critical': '🔴',
                    'high': '🟠',
                    'medium': '🟡',
                    'low': '🔵'
                }.get(issue.severity, '⚪')

                report += f"{severity_emoji} **Line {issue.line}** [{issue.category}] {issue.description}\n\n"
                report += f"> {issue.reasoning}\n\n"

                if issue.suggested_fix:
                    report += f"**Suggested fix:** {issue.suggested_fix}\n\n"

            report += "---\n\n"

        # Add footer
        report += "_🤖 Generated by LLM Framework using few-shot-5 technique (F1: 0.615, tested on 20 examples)_\n"

        return report

    def get_statistics(self, results: Dict[Path, AnalysisResult]) -> Dict[str, Any]:
        """
        Get statistics about analysis results.

        Args:
            results: Analysis results

        Returns:
            Statistics dictionary
        """
        total_files = len(results)
        total_issues = sum(len(r.issues) for r in results.values())

        # Count by severity
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for result in results.values():
            for issue in result.issues:
                if issue.severity in severity_counts:
                    severity_counts[issue.severity] += 1

        # Count by category
        category_counts = {}
        for result in results.values():
            for issue in result.issues:
                category_counts[issue.category] = category_counts.get(issue.category, 0) + 1

        # Token usage
        total_tokens = sum(r.metadata.get('tokens_used', 0) for r in results.values())
        avg_latency = sum(r.metadata.get('latency', 0) for r in results.values()) / total_files if total_files > 0 else 0

        return {
            'total_files': total_files,
            'total_issues': total_issues,
            'severity_counts': severity_counts,
            'category_counts': category_counts,
            'total_tokens': total_tokens,
            'avg_latency': avg_latency
        }
