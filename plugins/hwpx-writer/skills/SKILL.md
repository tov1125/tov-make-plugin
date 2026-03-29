---
name: hwpx-writer
description: >
  HWPX(한글 워드프로세서) 문서를 분석, 읽기, 쓰기, 양식 채우기하는 통합 스킬.
  사용자가 "hwpx", "한글 파일", "hwpx 분석", "hwpx 작성", "hwpx 수정", "양식 채우기",
  "한글 문서 작성", "참조문서로 양식 작성", "hwpx 템플릿" 등을 언급하면 반드시 이 스킬을 사용한다.
  HWPX 파일을 다루는 모든 작업에 이 스킬이 필요하다.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
argument-hint: [hwpx 파일 경로 또는 작업 설명]
---

# HWPX 문서 통합 스킬

HWPX는 한컴오피스 한글의 XML 기반 문서 포맷이다. 실체는 ZIP 파일 안에 XML들이 들어있는 구조.

## HWPX 내부 구조 (빠른 참조)

```
document.hwpx (ZIP)
├── mimetype                    # application/hwp+zip
├── META-INF/manifest.xml
├── Contents/
│   ├── content.hpf             # 섹션 목록 매니페스트
│   ├── header.xml              # 폰트, 스타일 정의
│   ├── section0.xml            # 본문 (문단, 표)
│   └── section1.xml ...
├── BinData/                    # 이미지, OLE 객체
└── Preview/PrvText.txt         # 텍스트 미리보기 (빠른 내용 파악용)
```

핵심 네임스페이스: `hp`(paragraph), `hs`(section), `hh`(head), `hc`(core).
상세 포맷은 `references/hwpx-format.md` 참조.

## 작업 유형별 워크플로우

### A. 단순 읽기/수정

HWPX 파일의 텍스트 추출, 특정 셀 값 변경 등 단순 작업.

1. `scripts/hwpx_analyzer.py`로 구조 파악
2. Python 스크립트로 직접 수정
3. 결과 검증

### B. 양식 채우기 (JSON/XML 데이터 → HWPX)

준비된 데이터를 HWPX 양식의 빈 셀에 채우는 작업.

1. `scripts/hwpx_analyzer.py`로 양식 테이블 구조 분석
2. 데이터 키 ↔ 레이블 셀 매핑 생성
3. `scripts/hwpx_utils.py`의 유틸리티로 셀 채우기 스크립트 작성/실행
4. 결과 검증

### C. 참조문서 기반 양식 작성 (오케스트레이션)

소스 HWPX(참조문서)의 내용을 분석하여 타겟 HWPX(양식)에 맞게 내용을 작성하는 복합 작업.
이 워크플로우가 가장 복잡하므로 아래 4단계를 따른다.

#### Phase 1: 분석 및 계획

1. 소스/타겟 HWPX를 각각 임시 디렉토리에 압축 해제
2. `Preview/PrvText.txt`로 빠른 내용 파악
3. `scripts/hwpx_analyzer.py`로 section*.xml 상세 분석
4. 작업 명세(`work_spec.json`) 생성:
   - 소스 문서 구조 요약
   - 타겟 양식의 빈 필드 목록
   - 소스→타겟 매핑 계획
   - 각 단계의 완료 기준
5. **사용자에게 work_spec 요약을 보여주고 승인 받기**

#### Phase 2: 문서 생성

1. work_spec의 계획에 따라 단계별 실행
2. 각 단계에서:
   - 소스 내용을 참조하여 타겟 항목에 맞게 내용 작성
   - XML 편집 시 서식 태그 보존 확인
   - **linesegarray 제거** (아래 함정 섹션 참조)
3. 자기 평가(`self_review.json`) 작성
4. 결과물 저장

#### Phase 3: 품질 검증

결과 HWPX를 독립적으로 압축 해제하여 분석하고 4개 기준으로 평가:
- **내용 충실도**: 소스의 핵심 내용이 빠짐없이 반영되었는가
- **서식 준수도**: 타겟 양식의 구조와 서식이 유지되었는가
- **작문 품질**: 문장이 자연스럽고 맥락에 맞는가
- **완결성**: 빈 필드 없이 모든 항목이 채워졌는가

PASS면 최종 결과물 전달. FAIL이면 Phase 4로.

#### Phase 4: 피드백 루프 (FAIL 시)

평가 보고서의 지적사항을 반영하여 수정 → 재평가. **최대 3회 반복**.
3회 초과 시 사용자에게 현재 상태와 미해결 이슈를 보고.

## 핵심 함정과 해결책

HWPX 편집에서 반복적으로 발생하는 문제들. 이것들을 모르면 결과물이 깨진다.

### 1. linesegarray — 반드시 제거

HWPX paragraph에는 `<hp:linesegarray>`가 있어 줄 레이아웃을 고정한다.
빈 paragraph(1줄)에 긴 텍스트를 넣으면 **모든 글자가 한 줄에 겹쳐서 표시된다**.

```python
def remove_linesegarray(p_elem):
    for lsa in p_elem.findall(f"{HP}linesegarray"):
        p_elem.remove(lsa)
```

텍스트를 삽입하는 모든 곳(paragraph, 테이블 셀 내 p)에서 이 함수를 호출해야 한다.

### 2. MEMO 필드는 주석이다

`fieldBegin type="MEMO"` 구조의 paragraph(예: `□ 목적`, `□ 목표`)는 **작성 안내문(주석)**.
MEMO 내부 subList의 텍스트(예: "맑은 고딕 13. 진하게")는 서식 가이드일 뿐이다.

**실제 내용은 라벨 paragraph 다음의 빈 paragraph들에 입력해야 한다.**

주의: `root.iter(f'{HP}p')`는 subList 내부 p까지 순회하므로,
직접 자식 기준(`list(root)`)으로 분석해야 정확하다.

### 3. 테이블 행 추가

템플릿 테이블의 데이터 행이 부족할 때:
1. 마지막 행을 `copy.deepcopy`로 복제
2. 복제된 행의 `cellAddr`의 `rowAddr`를 새 인덱스로 갱신
3. 셀 텍스트 초기화
4. `tbl.set("rowCnt", str(새_총행수))` 업데이트

### 4. 병합 셀 — cellAddr 기반 매핑 필수

병합된 셀은 물리적 `<hp:tc>` 개수가 줄어든다.
셀을 찾을 때 반드시 `cellAddr`의 `rowAddr`/`colAddr` 속성 기준으로 매핑해야 한다.

### 5. 직접 자식 기준 분석

서브섹션 블록 식별 시 `root.iter()`가 아닌 `list(root)` (직접 자식)으로 순회해야
subList 내부의 paragraph가 섞이지 않는다.

## 서브섹션 블록 패턴

사업제안서 등 양식의 서브섹션은 이 순서로 구성된다:

```
[제목 TABLE]
→ [MEMO "목적"] → 빈 p들 (여기에 목적 내용 입력)
→ [MEMO "목표"] → 빈 p들 (여기에 목표 내용 입력)
→ [사업추진내용 라벨] → 빈 p들 (여기에 내용 입력)
→ [수행인력 라벨] → [수행인력 TABLE]
→ [예산 라벨] → [예산 TABLE]
→ [추진일정 라벨] → [추진일정 TABLE]
```

이 패턴을 `find_subsection_blocks()` 함수로 자동 식별한다.
`scripts/hwpx_utils.py`에 구현되어 있다.

## 데이터 구조

서브섹션에 채울 데이터는 이 형식을 따른다:

```python
{
    "purpose": "목적 텍스트",
    "goal": "목표 텍스트",
    "content": ["❍ 항목1", " - 세부1", "❍ 항목2", ...],
    "personnel": [("번호", "이름", "역할", "상세"), ...],
    "schedule": [("항목명", "4월", "5월", ..., "12월"), ...],
}
```

## Python 환경

- python-hwpx 설치 Python: `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14`
- DIY 방식(zipfile + ElementTree)이 더 세밀한 제어 가능하여 권장
- 네임스페이스 prefix 등록은 **반드시** `ET.tostring()` 전에 수행 (미등록 시 ns0/ns1 자동 생성)

## 번들 스크립트

| 스크립트 | 용도 | 실행 방법 |
|----------|------|-----------|
| `scripts/hwpx_analyzer.py` | HWPX 구조 분석 (테이블, 셀, MEMO 필드 등) | `python3.14 scripts/hwpx_analyzer.py "파일.hwpx"` |
| `scripts/hwpx_utils.py` | 공통 유틸리티 (import해서 사용) | `from hwpx_utils import *` |

## 체크리스트

작업 완료 전 반드시 확인:
- [ ] 텍스트 삽입한 모든 paragraph에서 linesegarray 제거했는가
- [ ] MEMO 필드 내부가 아닌 다음 빈 paragraph에 내용을 넣었는가
- [ ] 테이블 행 추가 시 rowAddr과 rowCnt를 갱신했는가
- [ ] cellAddr 기반으로 셀을 매핑했는가
- [ ] 네임스페이스 prefix를 모두 등록했는가
- [ ] 결과 HWPX에서 텍스트를 추출하여 값이 정상 입력되었는지 검증했는가
