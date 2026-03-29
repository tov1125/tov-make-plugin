---
name: init-free
description: "새 프로젝트의 초기 환경을 자동으로 셋업하는 스킬. CLAUDE.md 생성과 .claude/settings.local.json 권한 설정을 한 번에 처리하여 승인피로 없이 바로 개발을 시작할 수 있게 해준다. 사용자가 '/init-free', '프로젝트 초기화', '프로젝트 셋업', '새 프로젝트 시작', 'init', '세팅해줘', '환경설정', '승인피로', 'settings 만들어줘' 등을 언급하면 이 스킬을 사용한다."
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch
---

# init-free

새 프로젝트 디렉토리에 CLAUDE.md와 .claude/settings.local.json을 생성하여, Claude Code가 승인 프롬프트 없이 바로 작업할 수 있는 환경을 만드는 스킬이다.

## 중요: .claude/ 경로 쓰기 제한

Claude Code는 보안상 `.claude/` 디렉토리 내 파일(settings.local.json 등)을 Write/Edit 도구로 직접 생성하지 못할 수 있다. 이 경우 다음 순서로 시도한다:

1. **먼저 Write 도구로 직접 생성을 시도**한다.
2. 실패하면 **Bash로 디렉토리 생성 후 파일 쓰기**를 시도한다:
   ```bash
   mkdir -p .claude && cat > .claude/settings.local.json << 'SETTINGS_EOF'
   { ... JSON 내용 ... }
   SETTINGS_EOF
   ```
3. 그래도 실패하면 **사용자에게 내용을 보여주고 직접 붙여넣기를 안내**한다:
   ```
   아래 내용을 .claude/settings.local.json에 저장해주세요:
   (JSON 내용 출력)

   터미널에서 바로 실행하려면:
   ! mkdir -p .claude && cat > .claude/settings.local.json << 'EOF'
   (JSON 내용)
   EOF
   ```

이 3단계 접근법은 어떤 환경에서든 settings 파일을 생성할 수 있게 해준다.

## 실행 흐름

### Step 1: 프로젝트 분석

현재 작업 디렉토리를 분석한다.

1. 기존 파일 확인:
   - `CLAUDE.md` 이미 존재하는지
   - `.claude/settings.local.json` 이미 존재하는지
   - `README.md`, `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod` 등 프로젝트 메타 파일
   - `.cursorrules`, `.cursor/rules/`, `.github/copilot-instructions.md` 등 기존 AI 룰

2. 프로젝트 종류 판별:
   - 파일이 전혀 없으면 → **빈 프로젝트**
   - 메타 파일이 있으면 → 해당 언어/프레임워크 기반 프로젝트

3. 이미 존재하는 파일이 있으면 사용자에게 알리고 덮어쓸지 확인한다. 절대 무단으로 기존 파일을 덮어쓰지 않는다.

### Step 2: CLAUDE.md 생성

프로젝트 분석 결과를 바탕으로 CLAUDE.md를 생성한다.

**반드시 포함할 헤더:**
```markdown
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
```

**프로젝트에 코드가 있는 경우** 다음을 분석하여 포함한다:
- 빌드/테스트/린트 명령어 (package.json scripts, Makefile 등에서 추출)
- 고수준 아키텍처 (여러 파일을 읽어야 이해되는 구조적 특징)
- 기존 AI 룰(.cursorrules 등)의 중요한 부분

**빈 프로젝트인 경우** 최소한의 내용만 포함한다:
```markdown
## Project Overview

This is the `{project-name}` project.

## Status

This project is in its initial setup phase. Update this file as the codebase evolves.
```

**포함하지 않을 것:**
- 파일 구조 전체 나열 (Glob으로 쉽게 확인 가능)
- 일반적인 개발 관행 ("테스트를 작성하세요" 같은 당연한 말)
- 매 컴포넌트/모듈 설명 (코드를 읽으면 알 수 있는 것)
- 꾸며낸 정보 (실제 파일에서 확인되지 않은 내용)

### Step 3: settings.local.json 생성

`.claude/settings.local.json`에 범용 개발 허용 규칙을 설정한다. 이 파일은 git에 커밋되지 않는 개인 설정이다.

**범용 허용 규칙 (모든 프로젝트 공통) — 아래 JSON을 그대로 사용한다:**

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Edit",
      "Write",
      "Glob",
      "Grep",
      "Bash(ls:*)",
      "Bash(cat:*)",
      "Bash(wc:*)",
      "Bash(mkdir:*)",
      "Bash(cp:*)",
      "Bash(mv:*)",
      "Bash(head:*)",
      "Bash(tail:*)",
      "Bash(git:*)",
      "Bash(node:*)",
      "Bash(npm:*)",
      "Bash(npx:*)",
      "Bash(python3:*)",
      "Bash(pip3:*)",
      "Bash(jq:*)",
      "Bash(echo:*)",
      "Bash(which:*)",
      "Bash(open:*)",
      "WebSearch",
      "WebFetch(domain:*)"
    ]
  }
}
```

**허용 규칙 형식이 중요하다.** 도구 이름은 접미사 없이 그대로 쓴다:
- `"Read"` (O) — `"Read(*)"` (X)
- `"Edit"` (O) — `"Edit(*)"` (X)
- `"Bash(git:*)"` (O) — `"Bash(git *)"` (X, 콜론 필수)

**프로젝트 종류에 따라 추가할 규칙:**

| 감지 파일 | 프로젝트 종류 | 추가 규칙 |
|-----------|-------------|----------|
| `package.json`에 yarn | Node (yarn) | `Bash(yarn:*)` |
| `pnpm-lock.yaml` | Node (pnpm) | `Bash(pnpm:*)` |
| `bun.lockb` | Node (bun) | `Bash(bun:*)` |
| `pyproject.toml`, `setup.py` | Python | `Bash(pip:*)`, `Bash(pytest:*)` |
| `venv/`, `.venv/` | Python (venv) | `Bash(./venv/bin/*:*)` 또는 `Bash(./.venv/bin/*:*)` |
| `Cargo.toml` | Rust | `Bash(cargo:*)` |
| `go.mod` | Go | `Bash(go:*)` |
| `docker-compose.yml` | Docker | `Bash(docker:*)`, `Bash(docker-compose:*)` |

**절대 allow에 넣지 않는 명령어** — 파일 삭제, 프로세스 종료, 권한 변경은 되돌리기 어렵기 때문에 사용자가 건별로 승인해야 한다:
- `rm`, `rm -rf` — 파일/디렉토리 삭제
- `kill`, `pkill` — 프로세스 종료
- `chmod`, `chown` — 파일 권한 변경
- `sudo` — 관리자 권한 실행

### Step 4: 기존 settings와 병합

`.claude/settings.local.json`이 이미 존재하면 기존 설정을 덮어쓰지 않고 **병합**한다.

1. 기존 파일을 Read로 읽는다
2. 기존 JSON 구조를 파싱한다
3. `permissions.allow` 배열: 기존 규칙을 유지하면서 새 규칙을 추가한다 (중복 제거)
4. `permissions.deny` 배열: 기존 deny 규칙을 그대로 보존한다 (절대 삭제하지 않는다)
5. 그 외 설정 (`hooks`, `env`, `enabledPlugins` 등): 기존 값을 그대로 유지한다

**병합 예시:**
```
기존:  allow: ["Bash(git:*)", "Read"], deny: ["Bash(rm -rf:*)"]
추가:  allow: ["Read", "Edit", "Write", "Glob", "Grep", ...]
결과:  allow: ["Bash(git:*)", "Read", "Edit", "Write", "Glob", "Grep", ...], deny: ["Bash(rm -rf:*)"]
```

### Step 5: 완료 리포트

생성/수정한 파일 목록과 내용 요약을 간결하게 보여준다:

```
완료! 다음 파일을 생성했습니다:

1. CLAUDE.md — 프로젝트 개요 및 개발 가이드
2. .claude/settings.local.json — 승인 없이 허용되는 도구/명령어 설정

| 카테고리 | 허용 항목 |
|---------|----------|
| 도구 | Read, Edit, Write, Glob, Grep |
| 파일 관리 | ls, cat, wc, mkdir, cp, mv, head, tail |
| Git | 모든 git 명령어 |
| 개발 | node, npm, npx, python3, pip3 |
| 유틸 | jq, echo, which, open |
| 웹 | WebSearch, WebFetch |

제외된 위험 명령어: rm, kill, sudo, chmod (필요시 수동 승인)
```
