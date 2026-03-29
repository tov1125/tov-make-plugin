# tov-make-market

Claude Code 플러그인 마켓플레이스

## 플러그인 목록

### hwpx-writer

HWPX(한글 워드프로세서) 문서를 분석, 읽기, 쓰기, 양식 채우기하는 통합 스킬입니다.

#### 주요 기능

- **문서 분석**: HWPX 파일의 내부 구조(섹션, 테이블, 셀, MEMO 필드) 분석 및 텍스트 추출
- **양식 채우기**: JSON/XML 데이터를 HWPX 양식의 빈 셀에 자동 입력, 체크박스 처리(□ → ☑)
- **참조문서 기반 작성**: 소스 HWPX(참조문서)를 분석하여 타겟 HWPX(양식)에 맞게 내용을 자동 작성. 분석 → 생성 → 검증 → 피드백 루프의 4단계 오케스트레이션 지원

#### 번들 스크립트

| 스크립트 | 용도 |
|----------|------|
| `scripts/hwpx_analyzer.py` | HWPX 파일 구조 분석기 |
| `scripts/hwpx_utils.py` | HWPX 편집 공통 유틸리티 (20+ 함수) |

#### HWPX 편집 시 핵심 주의사항

- **linesegarray 제거**: 텍스트 삽입 후 반드시 제거해야 글자 겹침 방지
- **MEMO 필드**: `fieldBegin type="MEMO"`는 주석이며, 실제 내용은 다음 빈 paragraph에 입력
- **테이블 행 추가**: deepcopy로 행 복제 후 rowAddr/rowCnt 갱신 필수
- **병합 셀**: cellAddr 기반 논리적 좌표로 매핑

#### 설치 방법

```
/plugin marketplace add tov1125/tov-make-market
/plugin install hwpx-writer@tov-make-market
```

---

### agent-team-creator

Multi-agent 팀 아키텍처를 설계하고 코드 스캐폴딩을 생성하는 플러그인입니다. Anthropic의 harness design 원칙에 기반하며, **"가장 단순한 구조에서 시작하고, 필요할 때만 복잡도를 추가하라"**는 철학을 따릅니다.

#### 주요 기능

- **4단계 설계 프로세스**: 분석(Analysis) → 수집(Collection) → 계획(Plan) → 구현(Build) → 검증(Verify)의 체계적 워크플로우
- **도메인별 맞춤 설계**: 소프트웨어 개발, 데이터 분석/ML, 콘텐츠 생성, 연구/리서치, 디자인/크리에이티브 등 도메인별 가이드 내장
- **복잡도 자동 판단**: 태스크 특성에 따라 단일 agent / Generator+Evaluator / Planner+Generator+Evaluator 중 적절한 패턴 선택
- **코드 스캐폴딩 생성**: 설계 문서(`architecture.md`, `evaluation-criteria.md`)와 실행 가능한 코드 구조 자동 생성

#### 핵심 설계 패턴

```
[Planner] → [Generator] → [Evaluator]
    ↑                          │
    └──────── feedback ────────┘
```

- **Planner** (선택적): 짧은 요청을 포괄적 스펙으로 확장
- **Generator**: 실제 작업 수행, Evaluator 피드백 기반 수정
- **Evaluator**: 정의된 기준으로 결과물 평가, 구체적 피드백 제공

#### 생성되는 프로젝트 구조

```
agents/
├── orchestrator.py      # agent 간 흐름 제어, 반복 로직
├── planner.py           # 스펙 생성 (필요시)
├── generator.py         # 작업 수행 agent
├── evaluator.py         # 평가 agent
├── shared/              # context, criteria, contracts 관리
├── prompts/             # agent별 system prompt (.md)
└── workspace/           # agent 간 파일 기반 통신
```

#### 비용/시간 트레이드오프

| 구성 | 예상 시간 | 예상 비용 | 적합한 경우 |
|------|----------|----------|------------|
| 단일 agent | ~20분 | ~$9 | 기본 기능, 빠른 프로토타이핑 |
| 풀 harness (3-agent) | ~4-6시간 | ~$125-200 | 완성도 높은 결과물, edge case 처리 |

#### 설치 방법

```
/plugin marketplace add tov1125/tov-make-market
/plugin install agent-team-creator@tov-make-market
```

---

### init-free

새 프로젝트의 초기 환경을 자동으로 셋업하는 플러그인입니다. CLAUDE.md 생성과 `.claude/settings.local.json` 권한 설정을 한 번에 처리하여, 승인 피로 없이 바로 개발을 시작할 수 있게 해줍니다.

#### 주요 기능

- **프로젝트 자동 분석**: 기존 파일, 언어/프레임워크 자동 감지 (Node, Python, Rust, Go, Docker 등)
- **CLAUDE.md 생성**: 프로젝트 종류에 맞는 빌드/테스트 명령어, 아키텍처 가이드 자동 작성
- **settings.local.json 생성**: 범용 개발 허용 규칙 자동 설정 (Read, Edit, Write, Git, npm, python3 등)
- **기존 설정 병합**: 이미 settings가 있으면 덮어쓰지 않고 기존 규칙을 보존하며 병합
- **안전한 기본값**: rm, kill, sudo, chmod 등 위험 명령어는 자동 허용에서 제외

#### 실행 흐름

```
프로젝트 분석 → CLAUDE.md 생성 → settings.local.json 생성 → 완료 리포트
```

#### 프로젝트별 추가 허용 규칙

| 감지 파일 | 프로젝트 종류 | 추가 허용 규칙 |
|-----------|-------------|---------------|
| `package.json` (yarn) | Node (yarn) | `Bash(yarn:*)` |
| `pnpm-lock.yaml` | Node (pnpm) | `Bash(pnpm:*)` |
| `pyproject.toml` | Python | `Bash(pip:*)`, `Bash(pytest:*)` |
| `Cargo.toml` | Rust | `Bash(cargo:*)` |
| `go.mod` | Go | `Bash(go:*)` |
| `docker-compose.yml` | Docker | `Bash(docker:*)` |

#### 설치 방법

```
/plugin marketplace add tov1125/tov-make-market
/plugin install init-free@tov-make-market
```

---

### slide-hdml

순수 HTML/CSS/JS 단일 파일로 완결되는 웹 슬라이드 프레젠테이션을 생성하는 플러그인입니다. 외부 라이브러리 없이 브라우저에서 바로 열면 동작합니다.

#### 주요 기능

- **자연어 → 슬라이드**: "발표자료 만들어줘"로 바로 생성
- **문서 변환**: Markdown, 텍스트, PDF, URL, PPTX, HWPX → HTML 슬라이드
- **전환 효과**: fade, slide, zoom 3종 전환
- **빌드 애니메이션**: fade-up, grow-in 등 순차 등장 효과
- **코드 하이라이트**: 라인별 하이라이트 + 단계별 진행
- **2단 컬럼 레이아웃**: 비교/대조 슬라이드
- **발표자 노트 / 터치 스와이프 / 풀스크린** 지원

#### 테마

| 테마 | 용도 |
|------|------|
| `theme-dark` | 타이틀, 마무리 슬라이드 |
| `theme-light` | 본문 슬라이드 |
| `theme-accent` | 강조, 핵심 메시지 |
| `theme-code` | 코드 블록 슬라이드 |

#### 설치 방법

```
/plugin marketplace add tov1125/tov-make-market
/plugin install slide-hdml@tov-make-market
```
