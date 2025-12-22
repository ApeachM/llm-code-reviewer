# Chapter 09: 문제 해결 (Troubleshooting)

---

## 🔍 문제 진단 체크리스트

문제가 발생하면 다음 순서로 확인하세요:

1. ☐ Ollama 실행 중인가? (`ollama list`)
2. ☐ 모델 다운로드 되었는가? (`ollama list | grep deepseek`)
3. ☐ 가상환경 활성화되었는가? (`which python`)
4. ☐ 패키지 설치되었는가? (`pip list | grep ollama`)
5. ☐ 디스크 공간 충분한가? (`df -h`)
6. ☐ 메모리 충분한가? (`free -h`)

---

## 설치 문제

### ❌ "ollama: command not found"

**증상**:
```bash
$ ollama list
bash: ollama: command not found
```

**원인**: Ollama가 설치되지 않았거나 PATH에 없음

**해결**:
```bash
# 재설치
curl https://ollama.ai/install.sh | sh

# PATH 확인
echo $PATH

# 수동 PATH 추가 (필요시)
export PATH=$PATH:/usr/local/bin
echo 'export PATH=$PATH:/usr/local/bin' >> ~/.bashrc
```

---

### ❌ "ModuleNotFoundError: No module named 'framework'"

**증상**:
```bash
$ python -m cli.main analyze file test.cpp
ModuleNotFoundError: No module named 'framework'
```

**원인**: 패키지가 설치되지 않았거나 가상환경이 활성화되지 않음

**해결**:
```bash
# 1. 가상환경 확인
which python
# 출력: /path/to/venv/bin/python (가상환경)
# 출력: /usr/bin/python (시스템) ← 문제!

# 2. 가상환경 활성화
source venv/bin/activate

# 3. 패키지 재설치
pip install -e .
```

---

### ❌ "Model not found: deepseek-coder:33b-instruct"

**증상**:
```
Error: model 'deepseek-coder:33b-instruct' not available in Ollama
```

**원인**: 모델 다운로드 안 됨

**해결**:
```bash
# 모델 다운로드
ollama pull deepseek-coder:33b-instruct

# 다운로드 확인
ollama list

# 다운로드 실패 시 (네트워크 문제)
# 더 작은 모델 시도
ollama pull qwen2.5-coder:14b
```

---

## 실행 문제

### ❌ "Cannot connect to Ollama"

**증상**:
```
ConnectionError: Cannot connect to Ollama at localhost:11434
```

**원인**: Ollama 서버가 실행 중이지 않음

**해결**:
```bash
# Ollama 서비스 시작
ollama serve &

# 확인
curl http://localhost:11434/api/tags
```

---

### ❌ "Out of Memory (OOM)"

**증상**:
```
Error: model requires more memory than available
Killed
```

**원인**: 33B 모델은 최소 16GB RAM 필요

**해결 옵션 1**: 더 작은 모델
```bash
ollama pull qwen2.5-coder:14b  # 8GB RAM으로 가능
python -m cli.main analyze file test.cpp --model qwen2.5-coder:14b
```

**해결 옵션 2**: Swap 메모리 늘리기 (Linux)
```bash
# 16GB swap 생성
sudo fallocate -l 16G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 영구 적용
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

**해결 옵션 3**: GPU 사용
```bash
# GPU 확인
nvidia-smi

# Ollama가 자동으로 GPU 감지
# GPU VRAM 사용 → 시스템 RAM 절약
```

---

### ❌ 분석이 너무 느림

**증상**: 파일당 5분 이상 소요

**원인**: GPU 미사용 또는 모델이 너무 큼

**해결**:
```bash
# 1. GPU 사용 확인
nvidia-smi  # GPU 프로세스에 ollama가 보여야 함

# 2. 더 작은 모델 사용
python -m cli.main analyze file test.cpp --model qwen2.5-coder:14b

# 3. 청킹 사용 (대용량 파일)
python -m cli.main analyze file large.cpp --chunk

# 4. CPU 코어 확인
nproc  # 코어 수 확인
# 병렬 워커 수를 코어 수에 맞게 조정 (코드 수정 필요)
```

---

## 결과 품질 문제

### ❌ False Positive가 너무 많음

**증상**: 버그가 아닌데 버그로 탐지됨

**해결**:
```bash
# 1. Hybrid 기법 사용 (정밀도 향상)
# plugins/production_analyzer.py 수정
technique_config = {'technique_name': 'hybrid'}

# 2. 신뢰도 필터링
# 결과에서 confidence < 0.7인 이슈 제외

# 3. Ground truth에 false positive 예시 추가
# experiments/ground_truth/cpp/example_XXX.json
```

---

### ❌ 버그를 못 찾음 (False Negative)

**증상**: 명백한 버그인데 탐지하지 못함

**해결**:
```bash
# 1. 더 큰 모델 시도
python -m cli.main analyze file test.cpp --model deepseek-coder:33b-instruct

# 2. Hybrid 기법 사용
# 더 많은 pass로 탐지 확률 증가

# 3. Ground truth에 놓친 버그 예시 추가
# 그리고 재실험
python -m cli.main experiment run --config experiments/configs/few_shot_5.yml
```

---

### ❌ Modern-cpp 이슈를 못 찾음

**증상**: 스마트 포인터 제안 등이 나오지 않음

**원인**: Modern-cpp는 Few-shot으로 탐지 어려움 (F1: 0.000)

**해결**:
```bash
# Chain-of-thought 기법 사용 (F1: 0.727)
# 또는 Hybrid 기법
```

---

## Git/PR 문제

### ❌ "Not a git repository"

**증상**:
```
Error: Not a git repository
```

**해결**:
```bash
# Git 저장소 초기화
git init
git add .
git commit -m "Initial commit"

# 또는 올바른 디렉토리에서 실행
cd /path/to/git/repo
```

---

### ❌ "No C++ files changed"

**증상**:
```
Analyzed 0 files
No issues found
```

**원인**: PR에 C++ 파일 변경이 없음

**해결**:
```bash
# 변경된 파일 확인
git diff --name-only main...feature-branch

# C++ 파일이 있는지 확인
git diff --name-only main...feature-branch | grep -E '\.(cpp|h|hpp)$'
```

---

## 실험 실행 문제

### ❌ "Ground truth file not found"

**증상**:
```
FileNotFoundError: experiments/ground_truth/cpp/example_001.json
```

**해결**:
```bash
# Ground truth 디렉토리 확인
ls experiments/ground_truth/cpp/

# 파일이 없으면 생성
# 또는 올바른 경로에서 실행
cd /path/to/llm-code-reviewer
```

---

### ❌ "Experiment failed: JSON parsing error"

**증상**:
```
JSONDecodeError: Expecting property name enclosed in double quotes
```

**원인**: LLM이 잘못된 형식의 JSON 반환

**해결**:
```bash
# 1. 프롬프트 로그 확인
cat experiments/runs/<run-id>/*_prompts.jsonl | tail -20

# 2. 온도(temperature) 낮추기
# experiments/configs/your_config.yml
technique_params:
  temperature: 0.0  # 더 결정적인 출력

# 3. 재시도
python -m cli.main experiment run --config experiments/configs/few_shot_5.yml
```

---

## 일반적인 팁

### 로그 확인

```bash
# 상세 로그 출력
python -m cli.main analyze file test.cpp --verbose

# 프롬프트 확인 (디버깅)
# framework/ollama_client.py에 print() 추가
```

### 환경 초기화

모든 것을 처음부터 다시 시작:

```bash
# 1. 가상환경 삭제
rm -rf venv

# 2. 가상환경 재생성
python -m venv venv
source venv/bin/activate

# 3. 재설치
pip install -e .

# 4. Ollama 재시작
pkill ollama
ollama serve &

# 5. 모델 재다운로드
ollama pull deepseek-coder:33b-instruct
```

---

## 도움 받기

위 방법으로 해결되지 않으면:

1. **GitHub Issues** 확인
   - 유사한 문제가 보고되었는지 검색

2. **로그 포함해서 이슈 생성**
   ```bash
   # 재현 가능한 최소 예제 포함
   # 에러 메시지 전체 복사
   # 환경 정보 포함 (OS, Python 버전, GPU 등)
   ```

3. **Slack에서 문의**
   - #llm-code-reviewer 채널

---

**이전**: [Chapter 08: FAQ](08-faq.md) ←
**목차로**: [Index](00-INDEX.md) ↑
