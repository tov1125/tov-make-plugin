#!/usr/bin/env python3
"""HWPX 문서 구조 분석기

HWPX 파일의 테이블 구조, 셀 내용, MEMO 필드, 서브섹션 패턴을 분석하여 출력한다.

사용법:
    python3.14 hwpx_analyzer.py "문서.hwpx"
    python3.14 hwpx_analyzer.py "문서.hwpx" --section 0
    python3.14 hwpx_analyzer.py "문서.hwpx" --verbose
"""

import argparse
import sys
import zipfile
import xml.etree.ElementTree as ET

HP = "{http://www.hancom.co.kr/hwpml/2011/paragraph}"


def get_all_text(elem):
    return "".join(t.text or "" for t in elem.iter(f"{HP}t")).strip()


def get_direct_text(p_elem):
    texts = []
    for run in p_elem.findall(f"{HP}run"):
        for t in run.findall(f"{HP}t"):
            if t.text:
                texts.append(t.text)
    return "".join(texts).strip()


def has_memo_field(p_elem):
    return p_elem.find(f".//{HP}fieldBegin[@type='MEMO']") is not None


def has_table(p_elem):
    return p_elem.find(f".//{HP}tbl") is not None


def analyze_table(tbl, table_idx, verbose=False):
    """테이블 구조 분석"""
    row_cnt = tbl.get("rowCnt", "?")
    col_cnt = tbl.get("colCnt", "?")
    print(f"\n=== 테이블 #{table_idx} ({row_cnt}행 x {col_cnt}열) ===")

    for tr in tbl.findall(f"{HP}tr"):
        for tc in tr.findall(f"{HP}tc"):
            addr = tc.find(f".//{HP}cellAddr")
            span = tc.find(f".//{HP}cellSpan")
            if addr is not None:
                row = addr.get("rowAddr", "?")
                col = addr.get("colAddr", "?")
                text = get_all_text(tc)
                span_info = ""
                if span is not None:
                    rs = span.get("rowSpan", "1")
                    cs = span.get("colSpan", "1")
                    if rs != "1" or cs != "1":
                        span_info = f" (span:{rs}x{cs})"
                display = text[:60] if text else "(빈 셀)"
                print(f"  [{row:>2s},{col:>2s}]{span_info} {display}")


def analyze_section(root, section_name, verbose=False):
    """섹션 구조 분석"""
    children = list(root)
    print(f"\n{'='*60}")
    print(f"  {section_name}: 직접 자식 {len(children)}개")
    print(f"{'='*60}")

    table_idx = 0
    subsection_count = 0

    for i, child in enumerate(children):
        tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        text = get_all_text(child)
        memo = " [MEMO]" if has_memo_field(child) else ""
        tbl_flag = " [TABLE]" if has_table(child) else ""

        if has_memo_field(child) and "목적" in text:
            subsection_count += 1
            print(f"\n  --- 서브섹션 {subsection_count} ---")

        if text or tbl_flag or verbose:
            display = text[:80] if text else ""
            print(f"  [{i:3d}] <{tag}>{memo}{tbl_flag} {display}")

        if has_table(child):
            for tbl in child.iter(f"{HP}tbl"):
                analyze_table(tbl, table_idx, verbose)
                table_idx += 1

    print(f"\n  요약: 테이블 {table_idx}개, 서브섹션 {subsection_count}개")


def analyze_hwpx(hwpx_path, target_section=None, verbose=False):
    """HWPX 파일 전체 분석"""
    print(f"분석 대상: {hwpx_path}")

    with zipfile.ZipFile(hwpx_path, "r") as zf:
        # 파일 목록
        names = zf.namelist()
        print(f"ZIP 내 파일 {len(names)}개")

        # 미리보기 텍스트
        for name in names:
            if "PrvText" in name:
                preview = zf.read(name).decode("utf-8", errors="replace")
                print(f"\n--- Preview ({name}) ---")
                print(preview[:500])
                if len(preview) > 500:
                    print(f"  ... ({len(preview)}자 중 500자만 표시)")
                break

        # 섹션 분석
        sections = sorted(n for n in names if n.startswith("Contents/section") and n.endswith(".xml"))
        print(f"\n섹션 파일: {sections}")

        for sec in sections:
            sec_num = sec.replace("Contents/section", "").replace(".xml", "")
            if target_section is not None and sec_num != str(target_section):
                continue
            root = ET.fromstring(zf.read(sec))
            analyze_section(root, sec, verbose)


def main():
    parser = argparse.ArgumentParser(description="HWPX 문서 구조 분석기")
    parser.add_argument("hwpx_path", help="분석할 HWPX 파일 경로")
    parser.add_argument("--section", "-s", type=int, default=None, help="특정 섹션만 분석 (예: 0, 1)")
    parser.add_argument("--verbose", "-v", action="store_true", help="빈 요소도 모두 표시")
    args = parser.parse_args()

    analyze_hwpx(args.hwpx_path, args.section, args.verbose)


if __name__ == "__main__":
    main()
