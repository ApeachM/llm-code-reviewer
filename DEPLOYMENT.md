# Deployment Guide

This guide covers deploying the Semantic PR Review Bot in production environments.

## Prerequisites

### Hardware Requirements
- **CPU**: 8+ cores recommended for parallel chunk analysis
- **RAM**: 32GB+ (model dependent)
- **GPU**: NVIDIA GPU with 24GB+ VRAM (recommended for faster inference)
- **Storage**: 50GB+ for models

### Software Requirements
- Python 3.11+
- Ollama (latest version)
- Git 2.0+
- Docker (optional, for containerized deployment)

## Installation

### 1. Install Ollama

```bash
# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# macOS
brew install ollama

# Start Ollama service
ollama serve
```

### 2. Pull Models

```bash
# Recommended production model (18GB, best accuracy)
ollama pull deepseek-coder:33b-instruct

# Alternative: Smaller model (9GB, faster, lower accuracy)
ollama pull qwen2.5:14b

# Verify model is available
ollama list
```

### 3. Install the Package

```bash
# Clone repository
git clone https://github.com/your-org/semantic-pr-reviewer.git
cd semantic-pr-reviewer

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install package
pip install -e .

# Verify installation
llm-framework --help
```

## Configuration

### Environment Variables

```bash
# Ollama configuration
export OLLAMA_HOST="http://localhost:11434"
export OLLAMA_MODEL="deepseek-coder:33b-instruct"

# GitLab integration (for CI/CD)
export GITLAB_API_TOKEN="glpat-xxxxxxxxxxxx"
export CI_SERVER_URL="https://gitlab.example.com"
export CI_PROJECT_ID="123"
```

### GitLab CI Setup

1. **Create API Token**:
   - Go to GitLab → Settings → Access Tokens
   - Create token with `api` scope
   - Save as `GITLAB_API_TOKEN` CI variable

2. **Configure Runner**:
   - Ensure runner has access to Ollama service
   - Add `ollama` tag to runner
   - Allocate sufficient resources (8+ CPU, 32GB+ RAM)

3. **Add CI Configuration**:
   - Copy `.gitlab-ci.yml` to your repository
   - Commit and push
   - MR reviews will trigger automatically

### Model Selection

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| deepseek-coder:33b-instruct | 18GB | Slow | High | Production default |
| qwen2.5:14b | 9GB | Medium | Medium | Resource-constrained |
| starcoder2:15b | 9GB | Medium | Medium | Alternative |

## Usage

### Local Analysis

```bash
# Analyze single file
llm-framework analyze file src/main.cpp

# Analyze directory
llm-framework analyze dir src/ --output report.md

# Analyze PR changes
llm-framework analyze pr --base main --head feature-branch
```

### CI/CD Integration

The bot automatically triggers on merge requests when `.gitlab-ci.yml` is configured.

**Customization options** (set as CI variables):

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_MODEL` | qwen2.5:14b | Model to use |
| `MIN_SEVERITY` | medium | Minimum severity to report |
| `MAX_ISSUES` | 20 | Maximum issues per MR |

### API Integration

```python
from integrations.gitlab_client import GitLabClient

client = GitLabClient(
    gitlab_url="https://gitlab.example.com",
    project_id=123,
    private_token="glpat-xxx"
)

# Get MR info
mr = client.get_merge_request(42)

# Post review comment
client.post_mr_comment(42, "Review summary...")
```

## Performance Tuning

### Chunk Size

For large files (300+ lines), chunking improves analysis quality:

```bash
# Default: 200 lines per chunk
llm-framework analyze file large.cpp --chunk

# Custom chunk size
llm-framework analyze file large.cpp --chunk --chunk-size 150
```

### Parallelization

The chunk analyzer uses ThreadPoolExecutor with 4 workers by default.
Adjust based on available resources:

```python
# In code: ChunkAnalyzer uses max_workers parameter
analyzer.analyze_chunks_parallel(chunks, max_workers=8)
```

### Memory Management

- Each analysis uses ~2-4GB RAM for model inference
- Parallel analysis multiplies memory usage
- Monitor with: `ollama ps` and system tools

## Monitoring

### Logs

The bot logs to stdout by default. For production:

```bash
# Redirect to file
llm-framework analyze pr --base main --head feature 2>&1 | tee review.log

# Or configure logging in code
import logging
logging.basicConfig(level=logging.INFO, filename='review.log')
```

### Metrics

Track these metrics for production monitoring:

- **Analysis latency**: Time per file/chunk
- **Token usage**: Tokens per analysis
- **Issue detection rate**: Issues found per file
- **False positive rate**: Manual tracking via feedback

### Health Checks

```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Check model availability
ollama list

# Test analysis
echo 'int x = 0;' | llm-framework analyze file /dev/stdin
```

## Troubleshooting

### Common Issues

**1. Model not found**
```
Error: Model 'xxx' not available in Ollama
Solution: Run 'ollama pull xxx'
```

**2. Connection refused**
```
Error: Connection to Ollama failed
Solution: Ensure 'ollama serve' is running
```

**3. Out of memory**
```
Error: CUDA out of memory
Solution: Use smaller model or reduce chunk parallelization
```

**4. Slow analysis**
- Check GPU utilization: `nvidia-smi`
- Reduce chunk size for faster processing
- Use smaller model

### Debug Mode

```bash
# Verbose output
llm-framework analyze file src/main.cpp -v

# Save prompts for debugging
# Set environment variable:
export LLM_DEBUG=1
```

## Security Considerations

1. **API Tokens**: Store securely, never commit to repository
2. **Code Exposure**: Analyzed code is sent to local Ollama only
3. **Results**: Review results may contain sensitive code snippets
4. **Network**: Keep Ollama on internal network only

## Scaling

### Horizontal Scaling

For high-volume environments:

1. Deploy multiple Ollama instances
2. Use load balancer for distribution
3. Configure runners per Ollama instance

### Caching

Consider caching for:
- Repeated file analysis (hash-based)
- Common code patterns
- Model responses (careful with cache invalidation)

## Support

- Issues: https://github.com/your-org/semantic-pr-reviewer/issues
- Documentation: See CLAUDE.md for architecture details
- Migration: See MIGRATION.md for version upgrades
