# Agent Team Creator

Multi-agent 팀 아키텍처를 설계하고 코드 스캐폴딩을 생성하는 Claude Code 플러그인.

## 개요

새로운 agent 시스템을 처음부터 설계하거나, 기존 multi-agent 시스템을 개선할 때 사용한다.
Anthropic의 harness design 원칙에 기반하며, **분석 → 수집 → 계획 → 구현 → 검증** 5단계 프로세스를 따른다.

## 핵심 철학

> "가장 단순한 구조에서 시작하고, 필요할 때만 복잡도를 추가하라."

모든 설계 결정에서 항상 물어야 할 질문: **"이 agent를 빼면 어떤 문제가 생기는가?"**

## 워크플로우

```
분석(Analysis) → 수집(Collect) → 계획(Plan) → 구현(Build) → 검증(Verify)
```

1. **분석**: 도메인과 태스크의 본질을 이해하고, 필요한 agent 구조 판단
2. **수집**: 레퍼런스, 패턴, 도메인 지식 확보
3. **계획**: 아키텍처 설계 및 평가 기준 정의
4. **구현**: 설계 문서와 코드 스캐폴딩 생성
5. **검증**: 불필요한 복잡도 제거 및 일관성 확인

## 트리거 키워드

`agent 설계`, `agent team`, `multi-agent`, `harness 설계`, `agent 아키텍처`, `evaluator 추가`, `generator-evaluator`, `agent 역할 분리`, `agent 시스템 개선`, `agent 파이프라인`

## 플러그인 구조

```
agent-team-creator/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── SKILL.md
│   ├── evals/
│   │   └── evals.json
│   └── references/
│       └── domain-guides.md
└── README.md
```

## 설치

이 폴더를 Claude Code 플러그인 디렉토리에 배치하면 자동으로 인식된다.

## 작성자

tov
