"""
CLI interface for LLM framework.

Commands:
- experiment run: Run a single experiment
- experiment compare: Compare two techniques
- experiment leaderboard: Show technique rankings
"""

import click
import yaml
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.progress import track

from framework.models import ExperimentConfig
from framework.experiment_runner import ExperimentRunner
from framework.techniques import TechniqueFactory, OllamaClientFactory
from framework.statistical_analyzer import StatisticalAnalyzer

console = Console()


@click.group()
def cli():
    """LLM Framework - Research platform for LLM code analysis techniques."""
    pass


@cli.group()
def experiment():
    """Experiment management commands."""
    pass


@experiment.command()
@click.option('--config', '-c', required=True, type=click.Path(exists=True),
              help='Path to experiment config YAML file')
@click.option('--output', '-o', default='experiments/runs',
              help='Output directory for results')
def run(config: str, output: str):
    """
    Run a single experiment.

    Example:
        llm-framework experiment run --config experiments/configs/zero_shot.yml
    """
    console.print(f"\n[bold cyan]Loading experiment config:[/bold cyan] {config}")

    # Load config
    with open(config) as f:
        config_data = yaml.safe_load(f)

    experiment_id = config_data['experiment_id']
    technique_name = config_data['technique_name']
    model_name = config_data['model_name']

    console.print(f"[bold]Experiment:[/bold] {experiment_id}")
    console.print(f"[bold]Technique:[/bold] {technique_name}")
    console.print(f"[bold]Model:[/bold] {model_name}\n")

    # Check model availability
    console.print("[yellow]Checking model availability...[/yellow]")
    client_factory = OllamaClientFactory()
    models_status = client_factory.check_all_models_available([model_name])

    if not models_status.get(model_name, False):
        console.print(f"[bold red]Error:[/bold red] Model '{model_name}' not available in Ollama")
        console.print(f"\n[yellow]Available models:[/yellow]")
        # List available models
        import ollama
        try:
            models = ollama.Client().list()
            for model in models.get('models', []):
                console.print(f"  - {model.model}")
        except:
            pass
        console.print(f"\n[yellow]To pull the model, run:[/yellow]")
        console.print(f"  ollama pull {model_name}")
        return

    console.print(f"[green]✓[/green] Model available\n")

    # Create Ollama client
    client = client_factory.create_from_config(config_data)

    # Create technique
    try:
        technique = TechniqueFactory.create(technique_name, client, config_data)
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        console.print(f"\n[yellow]Available techniques:[/yellow]")
        for tech in TechniqueFactory.available_techniques():
            console.print(f"  - {tech}")
        return

    # Create experiment config
    exp_config = ExperimentConfig(
        experiment_id=experiment_id,
        technique_name=technique_name,
        model_name=model_name,
        technique_params=config_data.get('technique_params', {}),
        dataset_path=config_data['dataset_path'],
        seed=config_data.get('seed')
    )

    # Run experiment
    console.print("[bold green]Starting experiment...[/bold green]\n")

    runner = ExperimentRunner(
        config=exp_config,
        technique=technique,
        output_dir=output
    )

    try:
        metrics = runner.run()

        # Display summary
        console.print("\n[bold green]✓ Experiment complete![/bold green]")
        console.print(f"\n[bold]Results saved to:[/bold] {Path(output) / exp_config.run_id}")

        # Create results table
        table = Table(title="Experiment Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Precision", f"{metrics.precision:.3f}")
        table.add_row("Recall", f"{metrics.recall:.3f}")
        table.add_row("F1 Score", f"{metrics.f1:.3f}")
        table.add_row("Token Efficiency", f"{metrics.token_efficiency:.2f} issues/1K tokens")
        table.add_row("Avg Latency", f"{metrics.latency:.2f}s")
        table.add_row("Total Tokens", str(metrics.total_tokens))

        console.print(table)

    except KeyboardInterrupt:
        console.print("\n[yellow]Experiment interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        import traceback
        console.print(traceback.format_exc())


@experiment.command()
@click.option('--techniques', '-t', required=True,
              help='Comma-separated list of technique names (e.g., zero_shot,few_shot_5)')
@click.option('--output', '-o', default='experiments/runs',
              help='Output directory for results')
def compare(techniques: str, output: str):
    """
    Compare two or more techniques.

    Example:
        llm-framework experiment compare --techniques zero_shot,few_shot_5
    """
    technique_list = [t.strip() for t in techniques.split(',')]

    if len(technique_list) < 2:
        console.print("[bold red]Error:[/bold red] Need at least 2 techniques to compare")
        return

    console.print(f"\n[bold cyan]Comparing techniques:[/bold cyan]")
    for tech in technique_list:
        console.print(f"  - {tech}")

    console.print("\n[yellow]Note:[/yellow] This feature requires running experiments first.")
    console.print("Use 'llm-framework experiment run' to generate results, then implement comparison.")


@experiment.command()
@click.option('--output', '-o', default='experiments/runs',
              help='Results directory to analyze')
def leaderboard(output: str):
    """
    Show technique leaderboard.

    Ranks all techniques by F1 score, token efficiency, and overall score.
    """
    console.print("\n[bold cyan]Technique Leaderboard[/bold cyan]")
    console.print("\n[yellow]Note:[/yellow] This feature analyzes all experiment results.")
    console.print("Run experiments first with 'llm-framework experiment run'")

    # Check if results directory exists
    results_dir = Path(output)
    if not results_dir.exists():
        console.print(f"\n[red]Results directory not found:[/red] {results_dir}")
        return

    # Find all metrics.json files
    import json
    metrics_files = list(results_dir.glob("*/metrics.json"))

    if not metrics_files:
        console.print("\n[yellow]No experiment results found.[/yellow]")
        console.print("Run some experiments first!")
        return

    console.print(f"\nFound {len(metrics_files)} experiment results\n")

    # Load and display results
    table = Table(title="Experiment Results")
    table.add_column("Experiment", style="cyan")
    table.add_column("F1", style="green")
    table.add_column("Precision", style="blue")
    table.add_column("Recall", style="magenta")
    table.add_column("Token Eff", style="yellow")

    results = []
    for metrics_file in metrics_files:
        with open(metrics_file) as f:
            metrics_data = json.load(f)
            results.append(metrics_data)

    # Sort by F1 score
    results.sort(key=lambda x: x['f1'], reverse=True)

    for metrics_data in results:
        table.add_row(
            metrics_data['experiment_id'],
            f"{metrics_data['f1']:.3f}",
            f"{metrics_data['precision']:.3f}",
            f"{metrics_data['recall']:.3f}",
            f"{metrics_data['token_efficiency']:.2f}"
        )

    console.print(table)


@cli.group()
def analyze():
    """Production code analysis commands."""
    pass


@analyze.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--model', '-m', default='deepseek-coder:33b-instruct',
              help='Ollama model to use')
@click.option('--output', '-o', type=click.Path(), help='Output file (markdown)')
def file(file_path: str, model: str, output: Optional[str]):
    """
    Analyze a single file.

    Example:
        llm-framework analyze file src/main.cpp
        llm-framework analyze file src/main.cpp --output report.md
    """
    from plugins.production_analyzer import ProductionAnalyzer

    console.print(f"\n[bold cyan]Analyzing file:[/bold cyan] {file_path}")
    console.print(f"[bold]Model:[/bold] {model}\n")

    # Create analyzer
    analyzer = ProductionAnalyzer(model_name=model)

    # Analyze
    file_path_obj = Path(file_path)
    result = analyzer.analyze_file(file_path_obj)

    if not result:
        console.print("[yellow]File not analyzed (filtered out)[/yellow]")
        return

    # Display results
    if not result.issues:
        console.print("[green]✅ No issues found![/green]")
    else:
        console.print(f"[yellow]Found {len(result.issues)} issue(s):[/yellow]\n")

        for issue in result.issues:
            severity_color = {
                'critical': 'red',
                'high': 'yellow',
                'medium': 'blue',
                'low': 'green'
            }.get(issue.severity, 'white')

            console.print(f"[{severity_color}]● Line {issue.line}[/{severity_color}] "
                         f"[{issue.category}] {issue.description}")
            console.print(f"  {issue.reasoning}\n")

    # Save to file if requested
    if output:
        markdown = analyzer.format_results_markdown({file_path_obj: result})
        Path(output).write_text(markdown)
        console.print(f"\n[green]Report saved to:[/green] {output}")


@analyze.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--model', '-m', default='deepseek-coder:33b-instruct',
              help='Ollama model to use')
@click.option('--output', '-o', type=click.Path(), help='Output file (markdown)')
@click.option('--recursive/--no-recursive', default=True,
              help='Recurse into subdirectories')
def dir(directory: str, model: str, output: Optional[str], recursive: bool):
    """
    Analyze all files in a directory.

    Example:
        llm-framework analyze dir src/
        llm-framework analyze dir src/ --output report.md
    """
    from plugins.production_analyzer import ProductionAnalyzer

    console.print(f"\n[bold cyan]Analyzing directory:[/bold cyan] {directory}")
    console.print(f"[bold]Model:[/bold] {model}")
    console.print(f"[bold]Recursive:[/bold] {recursive}\n")

    # Create analyzer
    analyzer = ProductionAnalyzer(model_name=model)

    # Analyze
    dir_path = Path(directory)
    with console.status("[bold green]Analyzing files...") as status:
        results = analyzer.analyze_directory(dir_path, recursive=recursive)

    # Display statistics
    if not results:
        console.print("[yellow]No files analyzed[/yellow]")
        return

    stats = analyzer.get_statistics(results)

    table = Table(title="Analysis Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Files Analyzed", str(stats['total_files']))
    table.add_row("Total Issues", str(stats['total_issues']))
    table.add_row("Critical Issues", str(stats['severity_counts']['critical']))
    table.add_row("High Issues", str(stats['severity_counts']['high']))
    table.add_row("Medium Issues", str(stats['severity_counts']['medium']))
    table.add_row("Low Issues", str(stats['severity_counts']['low']))

    console.print(table)

    # Category breakdown
    if stats['category_counts']:
        console.print("\n[bold]Issues by Category:[/bold]")
        for category, count in sorted(stats['category_counts'].items(), key=lambda x: -x[1]):
            console.print(f"  {category}: {count}")

    # Save to file if requested
    if output:
        markdown = analyzer.format_results_markdown(results)
        Path(output).write_text(markdown)
        console.print(f"\n[green]Report saved to:[/green] {output}")


@analyze.command()
@click.option('--repo', '-r', type=click.Path(exists=True), default='.',
              help='Path to git repository')
@click.option('--base', '-b', default='main',
              help='Base branch to compare against')
@click.option('--head', '-h', default='HEAD',
              help='Head branch/commit')
@click.option('--model', '-m', default='deepseek-coder:33b-instruct',
              help='Ollama model to use')
@click.option('--output', '-o', type=click.Path(), help='Output file (markdown)')
def pr(repo: str, base: str, head: str, model: str, output: Optional[str]):
    """
    Analyze changes in a pull request.

    Only analyzes files that changed between base and head branches.

    Example:
        llm-framework analyze pr --base main --head feature-branch
        llm-framework analyze pr --output pr-review.md
    """
    from plugins.production_analyzer import ProductionAnalyzer

    console.print(f"\n[bold cyan]Analyzing PR:[/bold cyan] {base}...{head}")
    console.print(f"[bold]Repository:[/bold] {repo}")
    console.print(f"[bold]Model:[/bold] {model}\n")

    # Create analyzer
    analyzer = ProductionAnalyzer(model_name=model)

    # Analyze git diff
    repo_path = Path(repo)
    with console.status("[bold green]Analyzing changed files...") as status:
        results = analyzer.analyze_git_diff(repo_path, base, head)

    if not results:
        console.print("[green]✅ No issues found in changed files![/green]")
        return

    # Display results
    stats = analyzer.get_statistics(results)

    console.print(f"[yellow]Analyzed {stats['total_files']} changed file(s)[/yellow]")
    console.print(f"[yellow]Found {stats['total_issues']} issue(s)[/yellow]\n")

    # Show issues by file
    for file_path, result in results.items():
        if not result.issues:
            continue

        console.print(f"[bold]📄 {file_path.name}:[/bold]")
        for issue in result.issues:
            severity_color = {
                'critical': 'red',
                'high': 'yellow',
                'medium': 'blue',
                'low': 'green'
            }.get(issue.severity, 'white')

            console.print(f"  [{severity_color}]● Line {issue.line}[/{severity_color}] {issue.description}")

        console.print()

    # Save to file if requested
    if output:
        markdown = analyzer.format_results_markdown(results)
        Path(output).write_text(markdown)
        console.print(f"[green]PR review saved to:[/green] {output}")
        console.print("\n💡 Tip: Copy this markdown to your PR comment!")


if __name__ == '__main__':
    cli()
