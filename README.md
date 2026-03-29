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

AI 에이전트 팀을 자동으로 생성하는 플러그인입니다.

- 다양한 역할의 에이전트를 팀으로 구성
- 프로젝트에 맞는 에이전트 팀 자동 생성

#### 설치 방법

```
/plugin marketplace add tov1125/tov-make-market
/plugin install agent-team-creator@tov-make-market
```
