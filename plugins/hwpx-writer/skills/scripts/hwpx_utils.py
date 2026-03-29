#!/usr/bin/env python3
"""HWPX 문서 편집 공통 유틸리티

이 모듈은 HWPX 파일을 zipfile + xml.etree.ElementTree로 다룰 때
반복적으로 필요한 함수들을 모아놓은 것이다.

사용법:
    import sys; sys.path.insert(0, "<이 파일이 있는 디렉토리>")
    from hwpx_utils import *
"""

import copy
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

# ── 네임스페이스 ──────────────────────────────────────────────────

NS_MAP = {
    "hp":          "http://www.hancom.co.kr/hwpml/2011/paragraph",
    "hs":          "http://www.hancom.co.kr/hwpml/2011/section",
    "hc":          "http://www.hancom.co.kr/hwpml/2011/core",
    "hh":          "http://www.hancom.co.kr/hwpml/2011/head",
    "ha":          "http://www.hancom.co.kr/hwpml/2011/app",
    "hp10":        "http://www.hancom.co.kr/hwpml/2016/paragraph",
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

def register_namespaces():
    """ET.tostring() 전에 호출하여 ns0/ns1 자동 생성을 방지"""
    for prefix, uri in NS_MAP.items():
        ET.register_namespace(prefix, uri)

# 모듈 로드 시 자동 등록
register_namespaces()

HP = f"{{{NS_MAP['hp']}}}"


# ── 텍스트 읽기 ──────────────────────────────────────────────────

def get_direct_text(p_elem):
    """paragraph의 직접 run 텍스트만 (subList 내부 제외)"""
    texts = []
    for run in p_elem.findall(f"{HP}run"):
        for t in run.findall(f"{HP}t"):
            if t.text:
                texts.append(t.text)
    return "".join(texts).strip()


def get_all_text(p_elem):
    """paragraph 내 모든 텍스트 (subList 포함)"""
    return "".join(t.text or "" for t in p_elem.iter(f"{HP}t")).strip()


def get_cell_text(tc_elem):
    """<hp:tc> 요소의 전체 텍스트"""
    return "".join(t.text or "" for t in tc_elem.iter(f"{HP}t")).strip()


# ── 텍스트 쓰기 ──────────────────────────────────────────────────

def remove_linesegarray(p_elem):
    """paragraph에서 linesegarray를 제거하여 한글이 줄바꿈을 재계산하도록 함.
    텍스트를 삽입하는 모든 곳에서 반드시 호출해야 한다.
    미제거 시 긴 텍스트가 한 줄에 겹쳐서 표시되는 치명적 문제 발생."""
    for lsa in p_elem.findall(f"{HP}linesegarray"):
        p_elem.remove(lsa)


def set_para_text(p_elem, new_text):
    """paragraph의 첫 번째 run > t에 텍스트 설정하고 linesegarray 제거"""
    for run in p_elem.findall(f"{HP}run"):
        for t in run.findall(f"{HP}t"):
            t.text = new_text
            remove_linesegarray(p_elem)
            return True
        t = ET.SubElement(run, f"{HP}t")
        t.text = new_text
        remove_linesegarray(p_elem)
        return True
    return False


def set_cell_text(table_elem, row, col, new_text):
    """테이블 셀에 텍스트 설정 (cellAddr 기반). linesegarray도 제거."""
    for tc in table_elem.iter(f"{HP}tc"):
        addr = tc.find(f".//{HP}cellAddr")
        if addr is not None:
            r = int(addr.get("rowAddr", "0"))
            c = int(addr.get("colAddr", "0"))
            if r == row and c == col:
                for t in tc.iter(f"{HP}t"):
                    t.text = new_text
                    for p in tc.iter(f"{HP}p"):
                        remove_linesegarray(p)
                    return True
                for run in tc.iter(f"{HP}run"):
                    t = ET.SubElement(run, f"{HP}t")
                    t.text = new_text
                    return True
    return False


# ── 테이블 유틸리티 ──────────────────────────────────────────────

def get_table_cells(table_elem):
    """cellAddr 기반 논리적 좌표 매핑. 병합 셀도 정확히 처리."""
    cells = {}
    for tr in table_elem.findall(f"{HP}tr"):
        for tc in tr.findall(f"{HP}tc"):
            addr = tc.find(f".//{HP}cellAddr")
            if addr is not None:
                row = int(addr.get("rowAddr", "0"))
                col = int(addr.get("colAddr", "0"))
                cells[(row, col)] = tc
    return cells


def ensure_table_rows(tbl, needed_data_rows, header_rows=1):
    """테이블에 필요한 만큼 데이터 행을 확보. 부족하면 마지막 행을 복제."""
    trs = tbl.findall(f"{HP}tr")
    current_data_rows = len(trs) - header_rows

    if current_data_rows >= needed_data_rows:
        return

    template_tr = trs[-1]

    for i in range(needed_data_rows - current_data_rows):
        new_row_idx = header_rows + current_data_rows + i
        new_tr = copy.deepcopy(template_tr)

        for tc in new_tr.findall(f"{HP}tc"):
            addr = tc.find(f".//{HP}cellAddr")
            if addr is not None:
                addr.set("rowAddr", str(new_row_idx))
            for t in tc.iter(f"{HP}t"):
                t.text = ""
            for p in tc.iter(f"{HP}p"):
                remove_linesegarray(p)

        tbl.append(new_tr)

    tbl.set("rowCnt", str(header_rows + needed_data_rows))


# ── 구조 분석 ────────────────────────────────────────────────────

def has_memo_field(p_elem):
    """MEMO 필드(fieldBegin type="MEMO") 포함 여부"""
    return p_elem.find(f".//{HP}fieldBegin[@type='MEMO']") is not None


def has_table(p_elem):
    """테이블 포함 여부"""
    return p_elem.find(f".//{HP}tbl") is not None


def get_first_table(p_elem):
    """첫 번째 테이블 반환"""
    return p_elem.find(f".//{HP}tbl")


def find_subsection_blocks(root):
    """섹션의 직접 자식을 분석하여 서브섹션 블록을 식별.
    패턴: [MEMO 목적] → 빈 p들 → [MEMO 목표] → 빈 p들 → [사업추진내용] → ...
    """
    children = list(root)
    blocks = []

    i = 0
    while i < len(children):
        child = children[i]
        text = get_all_text(child)

        if has_memo_field(child) and "목적" in text:
            block = {"purpose_label": i, "children_ref": children}

            # 목적 빈 paragraphs (다음 MEMO "목표"까지)
            purpose_blanks = []
            j = i + 1
            while j < len(children):
                t = get_all_text(children[j])
                if has_memo_field(children[j]) and "목표" in t:
                    block["goal_label"] = j
                    break
                purpose_blanks.append(j)
                j += 1
            block["purpose_blanks"] = purpose_blanks

            # 목표 빈 paragraphs (다음 "사업추진내용"까지)
            goal_blanks = []
            j = block.get("goal_label", i) + 1
            while j < len(children):
                t = get_all_text(children[j])
                if "사업추진내용" in t:
                    block["content_label"] = j
                    break
                goal_blanks.append(j)
                j += 1
            block["goal_blanks"] = goal_blanks

            # 사업추진내용 빈 paragraphs (다음 "수행인력"까지)
            content_blanks = []
            j = block.get("content_label", i) + 1
            while j < len(children):
                t = get_all_text(children[j])
                if "수행인력" in t:
                    block["personnel_label"] = j
                    break
                content_blanks.append(j)
                j += 1
            block["content_blanks"] = content_blanks

            # 수행인력 테이블
            j = block.get("personnel_label", i) + 1
            while j < len(children):
                if has_table(children[j]):
                    block["personnel_table"] = j
                    break
                j += 1

            # 추진일정 테이블
            j = block.get("personnel_table", i) + 1
            while j < len(children):
                t = get_all_text(children[j])
                if "추진일정" in t:
                    block["schedule_label"] = j
                    if j + 1 < len(children) and has_table(children[j + 1]):
                        block["schedule_table"] = j + 1
                    break
                j += 1

            blocks.append(block)

        i += 1

    return blocks


def fill_block(block, data):
    """서브섹션 블록에 데이터를 채움"""
    children = block["children_ref"]

    # 목적
    purpose_blanks = block.get("purpose_blanks", [])
    if purpose_blanks and data.get("purpose"):
        set_para_text(children[purpose_blanks[0]], data["purpose"])

    # 목표
    goal_blanks = block.get("goal_blanks", [])
    if goal_blanks and data.get("goal"):
        set_para_text(children[goal_blanks[0]], data["goal"])

    # 사업추진내용
    content_blanks = block.get("content_blanks", [])
    content_lines = data.get("content", [])
    for idx, blank_i in enumerate(content_blanks):
        if idx < len(content_lines):
            set_para_text(children[blank_i], content_lines[idx])

    # 수행인력 테이블
    personnel_table_idx = block.get("personnel_table")
    if personnel_table_idx and data.get("personnel"):
        tbl = get_first_table(children[personnel_table_idx])
        if tbl is not None:
            ensure_table_rows(tbl, len(data["personnel"]))
            for row_idx, (num, name, role, detail) in enumerate(data["personnel"]):
                set_cell_text(tbl, row_idx + 1, 0, num)
                set_cell_text(tbl, row_idx + 1, 1, name)
                set_cell_text(tbl, row_idx + 1, 2, role)
                set_cell_text(tbl, row_idx + 1, 3, detail)

    # 추진일정 테이블
    schedule_table_idx = block.get("schedule_table")
    if schedule_table_idx and data.get("schedule"):
        tbl = get_first_table(children[schedule_table_idx])
        if tbl is not None:
            ensure_table_rows(tbl, len(data["schedule"]))
            for row_idx, row_data in enumerate(data["schedule"]):
                period = row_data[0]
                months = row_data[1:]
                set_cell_text(tbl, row_idx + 1, 0, period)
                set_cell_text(tbl, row_idx + 1, 1, period)
                for col_idx, val in enumerate(months):
                    set_cell_text(tbl, row_idx + 1, col_idx + 2, val)


# ── HWPX 파일 I/O ────────────────────────────────────────────────

def read_section_xml(hwpx_path, section_name="Contents/section0.xml"):
    """HWPX에서 특정 섹션 XML을 파싱하여 root Element 반환"""
    with zipfile.ZipFile(hwpx_path, "r") as zf:
        return ET.fromstring(zf.read(section_name))


def list_sections(hwpx_path):
    """HWPX 내 섹션 파일 목록 반환"""
    with zipfile.ZipFile(hwpx_path, "r") as zf:
        return [n for n in zf.namelist() if n.startswith("Contents/section") and n.endswith(".xml")]


def save_hwpx(src_path, dst_path, section_updates):
    """수정된 섹션 XML을 반영하여 새 HWPX 파일 저장.

    Args:
        src_path: 원본 HWPX 경로
        dst_path: 출력 HWPX 경로
        section_updates: {섹션파일명: root_element} 딕셔너리
    """
    with zipfile.ZipFile(src_path, "r") as zin:
        with zipfile.ZipFile(dst_path, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.namelist():
                if item in section_updates:
                    modified = ET.tostring(
                        section_updates[item],
                        encoding="unicode",
                        xml_declaration=True
                    ).encode("utf-8")
                    zout.writestr(item, modified)
                else:
                    zout.writestr(zin.getinfo(item), zin.read(item))


def extract_all_text(hwpx_path):
    """HWPX에서 모든 텍스트를 추출 (검증용)"""
    texts = []
    sections = list_sections(hwpx_path)
    for sec in sections:
        root = read_section_xml(hwpx_path, sec)
        for t in root.iter(f"{HP}t"):
            if t.text and t.text.strip():
                texts.append(t.text.strip())
    return texts


def get_preview_text(hwpx_path):
    """Preview/PrvText.txt에서 미리보기 텍스트 추출 (빠른 내용 파악용)"""
    with zipfile.ZipFile(hwpx_path, "r") as zf:
        for name in zf.namelist():
            if "PrvText" in name or "Preview" in name:
                try:
                    return zf.read(name).decode("utf-8", errors="replace")
                except Exception:
                    pass
    return ""


# ── 체크박스 처리 ─────────────────────────────────────────────────

def toggle_checkbox(cell_text, target_value):
    """체크박스 텍스트에서 target_value에 해당하는 항목을 체크(□→☑)"""
    return cell_text.replace(f"□ {target_value}", f"☑ {target_value}")
