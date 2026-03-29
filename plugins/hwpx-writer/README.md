# HWPX Writer

HWPX(한글 워드프로세서) 문서를 분석, 읽기, 쓰기, 양식 채우기하는 Claude Code 플러그인.

## 개요

HWPX는 한컴오피스 한글의 XML 기반 문서 포맷으로, 실체는 ZIP 파일 안에 XML들이 들어있는 구조다.
이 플러그인은 HWPX 파일을 다루는 모든 작업을 지원한다.

## 주요 기능

- **문서 분석**: HWPX 파일의 구조(테이블, 셀, MEMO 필드 등) 파악
- **단순 읽기/수정**: 텍스트 추출, 특정 셀 값 변경
- **양식 채우기**: JSON/XML 데이터를 HWPX 양식의 빈 셀에 매핑하여 채우기
- **참조문서 기반 작성**: 소스 HWPX의 내용을 분석하여 타겟 양식에 맞게 작성 (4단계 오케스트레이션)

## 트리거 키워드

`hwpx`, `한글 파일`, `hwpx 분석`, `hwpx 작성`, `hwpx 수정`, `양식 채우기`, `한글 문서 작성`, `참조문서로 양식 작성`, `hwpx 템플릿`

## 번들 스크립트

| 스크립트 | 용도 |
|----------|------|
| `scripts/hwpx_analyzer.py` | HWPX 구조 분석 |
| `scripts/hwpx_utils.py` | 공통 유틸리티 (import용) |

## 플러그인 구조

```
hwpx-writer/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── SKILL.md
│   ├── references/
│   │   └── hwpx-format.md
│   └── scripts/
│       ├── hwpx_analyzer.py
│       └── hwpx_utils.py
└── README.md
```

## Python 환경

- Python 경로: `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14`
- DIY 방식(zipfile + ElementTree)으로 세밀한 제어 가능

## 설치

이 폴더를 Claude Code 플러그인 디렉토리에 배치하면 자동으로 인식된다.

## 작성자

tov
