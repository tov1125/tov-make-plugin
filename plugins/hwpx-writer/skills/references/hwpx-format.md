# HWPX 포맷 상세 레퍼런스

## 목차
1. [ZIP 구조](#zip-구조)
2. [네임스페이스](#네임스페이스)
3. [XML 구조](#xml-구조)
4. [python-hwpx 라이브러리](#python-hwpx-라이브러리)
5. [DIY 저장 방법](#diy-저장-방법)
6. [호환성 주의사항](#호환성-주의사항)

## ZIP 구조

```
document.hwpx (ZIP)
├── mimetype                     # 첫 번째 항목, ZIP_STORED, "application/hwp+zip"
├── META-INF/
│   ├── container.xml            # rootfile → Contents/content.hpf
│   ├── container.rdf
│   └── manifest.xml             # 모든 Contents 파일 등록
├── settings.xml
├── version.xml                  # major="5" minor="1"
├── Contents/
│   ├── content.hpf              # OPF 매니페스트 + spine (섹션 순서)
│   ├── header.xml               # fontfaces, charPr, paraPr, styles
│   ├── section0.xml             # 본문 (문단, 표, 이미지)
│   └── section1.xml ...         # 추가 섹션
├── BinData/                     # 첨부 이미지, OLE 객체
├── Scripts/                     # 매크로
└── Preview/
    ├── PrvText.txt              # 텍스트 미리보기 (빠른 내용 파악)
    └── PrvImage.png             # 이미지 미리보기
```

## 네임스페이스

```python
NS_MAP = {
    "hp":          "http://www.hancom.co.kr/hwpml/2011/paragraph",   # 본문/표/셀
    "hs":          "http://www.hancom.co.kr/hwpml/2011/section",     # 섹션
    "hh":          "http://www.hancom.co.kr/hwpml/2011/head",        # 헤더
    "hc":          "http://www.hancom.co.kr/hwpml/2011/core",        # 공통
    "ha":          "http://www.hancom.co.kr/hwpml/2011/app",         # 앱 설정
    "hp10":        "http://www.hancom.co.kr/hwpml/2016/paragraph",   # 2016 확장
    "hhs":         "http://www.hancom.co.kr/hwpml/2011/history",
    "hm":          "http://www.hancom.co.kr/hwpml/2011/master-page",
    "hpf":         "http://www.hancom.co.kr/schema/2011/hpf",
    "dc":          "http://purl.org/dc/elements/1.1/",
    "opf":         "http://www.idpf.org/2007/opf/",
    "ooxmlchart":  "http://www.hancom.co.kr/hwpml/2016/ooxmlchart",
    "hwpunitchar": "http://www.hancom.co.kr/hwpml/2016/HwpUnitChar",
    "epub":        "http://www.idpf.org/2007/ops",
    "config":      "urn:oasis:names:tc:opendocument:xmlns:config:1.0",
}
```

`ET.tostring()` 호출 전에 모든 prefix를 등록해야 `ns0`/`ns1` 자동 생성을 방지할 수 있다.

## XML 구조

### 문단 (paragraph)

```xml
<hp:p paraPrIDRef="..." styleIDRef="...">
  <hp:run charPrIDRef="...">
    <hp:t>텍스트 내용</hp:t>
  </hp:run>
  <hp:linesegarray>       <!-- 줄 레이아웃 고정 — 텍스트 변경 시 반드시 제거 -->
    <hp:lineseg .../>
  </hp:linesegarray>
</hp:p>
```

### 테이블

```xml
<hp:tbl rowCnt="..." colCnt="...">
  <hp:tr>
    <hp:tc>
      <hp:cellAddr colAddr="0" rowAddr="0"/>    <!-- 논리적 좌표 -->
      <hp:cellSpan colSpan="1" rowSpan="1"/>    <!-- 병합 범위 -->
      <hp:cellSz ... />
      <hp:cellMargin ... />
      <hp:subList>
        <hp:p><hp:run><hp:t>셀 내용</hp:t></hp:run></hp:p>
      </hp:subList>
    </hp:tc>
  </hp:tr>
</hp:tbl>
```

병합 셀: 물리적 `<hp:tc>` 개수가 줄어든다. 셀을 찾을 때 `cellAddr` 기반 매핑 필수.

### MEMO 필드

```xml
<hp:p>
  <hp:run>
    <hp:fieldBegin type="MEMO" .../>
  </hp:run>
  <hp:run><hp:t>□ 목적</hp:t></hp:run>
  <hp:run>
    <hp:fieldEnd type="MEMO"/>
    <hp:subList>
      <hp:p><hp:run><hp:t>맑은 고딕 13. 진하게</hp:t></hp:run></hp:p>  <!-- 안내문 -->
    </hp:subList>
  </hp:run>
</hp:p>
```

MEMO 내부 subList는 **작성 안내문(주석)**. 실제 내용은 이 paragraph 다음의 빈 paragraph에 입력.

## python-hwpx 라이브러리

```python
from hwpx import HwpxDocument
import warnings
warnings.filterwarnings('ignore')

doc = HwpxDocument.open("문서.hwpx")

# 구조 탐색
print(f"섹션: {len(doc.sections)}, 문단: {len(doc.paragraphs)}")

# 테이블 접근
for para in doc.paragraphs:
    for table in para.tables:
        print(f"테이블: {table.row_count}x{table.column_count}")

# 셀 읽기/쓰기
cell = table.cell(row_idx, col_idx)
print(cell.text)

# 빈 셀 쓰기 (TypeError 우회)
def safe_set_text(cell, value):
    try:
        cell.text = value
    except TypeError:
        from lxml import etree as lxml_etree
        HP = "{http://www.hancom.co.kr/hwpml/2011/paragraph}"
        elem = cell.element
        t = elem.find(f".//{HP}t")
        if t is not None:
            t.text = value
        else:
            sublist = elem.find(f".//{HP}subList")
            if sublist is None:
                return
            p = sublist.find(f"{HP}p")
            if p is None:
                p = lxml_etree.SubElement(sublist, f"{HP}p")
            run = p.find(f"{HP}run")
            if run is None:
                run = lxml_etree.SubElement(p, f"{HP}run", {"charPrIDRef": "0"})
            t = lxml_etree.SubElement(run, f"{HP}t")
            t.text = value
        elem.set("dirty", "1")
        cell.table.mark_dirty()

# 앵커 셀 매핑 (병합 셀 고려)
for entry in table.iter_grid():
    if entry.anchor == (entry.row, entry.column):
        span = entry.span
        text = entry.cell.text
        print(f"[{entry.row},{entry.column}] span={span} = {text}")

doc.save_to_path("출력.hwpx")
doc.close()
```

설치: `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14`에 설치됨.

## DIY 저장 방법

```python
import zipfile
import xml.etree.ElementTree as ET

# 네임스페이스 등록 (hwpx_utils.py의 register_namespaces() 사용 권장)
for prefix, uri in NS_MAP.items():
    ET.register_namespace(prefix, uri)

# 수정된 XML을 바이트로 변환
modified_bytes = ET.tostring(root, encoding="unicode", xml_declaration=True).encode("utf-8")

# 원본 ZIP에서 수정 대상만 교체하여 새 ZIP 생성
with zipfile.ZipFile("원본.hwpx", "r") as zin:
    with zipfile.ZipFile("출력.hwpx", "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.namelist():
            if item == "Contents/section0.xml":
                zout.writestr(item, modified_bytes)
            else:
                zout.writestr(zin.getinfo(item), zin.read(item))
```

## 호환성 주의사항

1. **mimetype**: ZIP 내 첫 번째 항목, `ZIP_STORED` (비압축), 값 `application/hwp+zip` (공백/줄바꿈 없이)
2. **경로 구분자**: ZIP 내부 경로에 `\` 사용 금지, 반드시 `/`
3. **ZIP64 미사용**: 구형 한글 호환성 문제 가능, 일반 ZIP 유지
4. **UTF-8 BOM 없음**: BOM 포함 시 파서 오류 가능
5. **줄바꿈**: LF (`\n`) 사용, CRLF 혼재 금지
6. **XML declaration**: 모든 XML 파일에 `encoding="UTF-8"` 명시
7. **특수문자 이스케이프**: `&`, `<`, `>` 등 XML 이스케이프 필수 (lxml 자동 처리)
