"""Yi Constellationの構造を、原典の卦序と六十四卦の対応から検算する。

対象は docs/yi-constellation/01-64卦のシステム地図.md と
docs/yi-constellation/09-変爻の分析.md である。番号、卦名、上下卦、
八×八の配置、三十六の変爻、之卦の象の引用、綜卦の対、序卦の連続を
機械的に確かめる。象の意味の解釈は検算しない。

使い方:
    python evaluations/audit-yi-constellation.py
    python evaluations/audit-yi-constellation.py --json <path>
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "docs" / "yi-constellation"

HEX = [
    (1, "乾", "111111"), (2, "坤", "000000"), (3, "屯", "100010"), (4, "蒙", "010001"),
    (5, "需", "111010"), (6, "訟", "010111"), (7, "師", "010000"), (8, "比", "000010"),
    (9, "小畜", "111011"), (10, "履", "110111"), (11, "泰", "111000"), (12, "否", "000111"),
    (13, "同人", "101111"), (14, "大有", "111101"), (15, "謙", "001000"), (16, "豫", "000100"),
    (17, "隨", "100110"), (18, "蠱", "011001"), (19, "臨", "110000"), (20, "觀", "000011"),
    (21, "噬嗑", "100101"), (22, "賁", "101001"), (23, "剝", "000001"), (24, "復", "100000"),
    (25, "无妄", "100111"), (26, "大畜", "111001"), (27, "頤", "100001"), (28, "大過", "011110"),
    (29, "坎", "010010"), (30, "離", "101101"), (31, "咸", "001110"), (32, "恆", "011100"),
    (33, "遯", "001111"), (34, "大壯", "111100"), (35, "晉", "000101"), (36, "明夷", "101000"),
    (37, "家人", "101011"), (38, "睽", "110101"), (39, "蹇", "001010"), (40, "解", "010100"),
    (41, "損", "110001"), (42, "益", "100011"), (43, "夬", "111110"), (44, "姤", "011111"),
    (45, "萃", "000110"), (46, "升", "011000"), (47, "困", "010110"), (48, "井", "011010"),
    (49, "革", "101110"), (50, "鼎", "011101"), (51, "震", "100100"), (52, "艮", "001001"),
    (53, "漸", "001011"), (54, "歸妹", "110100"), (55, "豐", "101100"), (56, "旅", "001101"),
    (57, "巽", "011011"), (58, "兌", "110110"), (59, "渙", "010011"), (60, "節", "110010"),
    (61, "中孚", "110011"), (62, "小過", "001100"), (63, "既濟", "101010"), (64, "未濟", "010101"),
]
BY_NUM = {n: (name, bits) for n, name, bits in HEX}
BY_NAME = {name: (n, bits) for n, name, bits in HEX}
BY_BITS = {bits: (n, name) for n, name, bits in HEX}
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "yi-64-hexagrams.json"
XIANG = {item["name"]: item["xiang"] for item in json.loads(FIXTURE.read_text(encoding="utf-8"))["hexagrams"]}
TRIGRAM = {"111": "乾", "110": "兌", "101": "離", "100": "震", "011": "巽", "010": "坎", "001": "艮", "000": "坤"}
PRODUCTS = {"TAI": "泰", "SUI": "萃", "SHO": "升", "SEI": "井", "TEI": "鼎", "EKI": "益"}
SHADOWS = {12, 41, 47, 49}
LINE_POSITIONS = ["初", "二", "三", "四", "五", "上"]


def trigrams(bits: str) -> tuple[str, str]:
    return TRIGRAM[bits[0:3]], TRIGRAM[bits[3:6]]


def check_64_table(doc: str) -> list[str]:
    errors: list[str] = []
    rows = []
    for line in doc.splitlines():
        match = re.match(r"^\| (\d{1,2}) \| ([^|]+?) \| ([^|]+?) \| ([^|]+?) \| (.+?) \| (.+?) \|$", line)
        if match:
            rows.append((int(match.group(1)), match.group(2).strip(), match.group(3).strip(), match.group(4).strip(), match.group(6).strip()))
    if len(rows) != 64:
        errors.append(f"64-table rows: {len(rows)}")
    expected_positions = {11: "TAI", 45: "SUI", 46: "SHO", 48: "SEI", 50: "TEI", 42: "EKI"}
    for number, name, upper, lower, position in rows:
        if number not in BY_NUM:
            errors.append(f"64-table: unknown number {number}")
            continue
        canonical_name, bits = BY_NUM[number]
        if name != canonical_name:
            errors.append(f"64-table {number}: name {name} != {canonical_name}")
        canonical_lower, canonical_upper = trigrams(bits)
        if upper != canonical_upper:
            errors.append(f"64-table {number} {name}: upper {upper} != {canonical_upper}")
        if lower != canonical_lower:
            errors.append(f"64-table {number} {name}: lower {lower} != {canonical_lower}")
        if number in expected_positions:
            if expected_positions[number] not in position:
                errors.append(f"64-table {number} {name}: position {position} lacks {expected_positions[number]}")
        elif number in SHADOWS:
            if "影" not in position:
                errors.append(f"64-table {number} {name}: shadow position {position}")
        elif position != "空白":
            errors.append(f"64-table {number} {name}: position {position} != 空白")
    return errors


def check_matrix(doc: str) -> list[str]:
    errors: list[str] = []
    section = doc.split("### 5.1 配置")[1].split("### 5.2")[0]
    lines = [line for line in section.splitlines() if re.match(r"^\| (乾|兌|離|震|巽|坎|艮|坤) \|", line)]
    if len(lines) != 8:
        errors.append(f"matrix rows: {len(lines)}")
    columns = ["乾", "兌", "離", "震", "巽", "坎", "艮", "坤"]
    for line in lines:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        upper = cells[0]
        if len(cells) != 9:
            errors.append(f"matrix row {upper}: {len(cells)} cells")
            continue
        for lower, cell in zip(columns, cells[1:]):
            match = re.match(r"^(\d{1,2}) ([^★☆]+)([★☆]?)$", cell)
            if not match:
                errors.append(f"matrix {upper}/{lower}: bad cell {cell}")
                continue
            number, name = int(match.group(1)), match.group(2).strip()
            if name not in BY_NAME:
                errors.append(f"matrix {upper}/{lower}: unknown name {name}")
                continue
            canonical_number, bits = BY_NAME[name]
            canonical_lower, canonical_upper = trigrams(bits)
            if upper != canonical_upper:
                errors.append(f"matrix {upper}/{lower}: {name} upper {canonical_upper}")
            if lower != canonical_lower:
                errors.append(f"matrix {upper}/{lower}: {name} lower {canonical_lower}")
            if number != canonical_number:
                errors.append(f"matrix {upper}/{lower}: number {number} for {name}")
    return errors


def changed(bits: str, index: int) -> str:
    new = list(bits)
    new[index] = "1" if new[index] == "0" else "0"
    return "".join(new)


def check_changes(doc: str) -> list[str]:
    errors: list[str] = []
    summary = {}
    for line in doc.splitlines():
        match = re.match(r"^\| (TAI|SUI|SHO|SEI|TEI|EKI) [^|]+ \| (.+) \|$", line)
        if match:
            summary[match.group(1)] = [cell.strip() for cell in match.group(2).split("|")]
    if len(summary) != 6:
        errors.append(f"summary rows: {len(summary)}")
    for product, cells in summary.items():
        bits = BY_NAME[PRODUCTS[product]][1]
        if len(cells) != 6:
            errors.append(f"summary {product}: {len(cells)} cells")
        for index, cell in enumerate(cells[:6]):
            match = re.match(r"^([^（]+)（([^）]+)）$", cell)
            if not match:
                errors.append(f"summary {product} line {index + 1}: bad cell {cell}")
                continue
            expected = BY_BITS[changed(bits, index)][1]
            if match.group(2) != expected:
                errors.append(f"summary {product} line {index + 1}: {match.group(2)} != {expected}")

    current = None
    seen = {product: 0 for product in PRODUCTS}
    for line in doc.splitlines():
        heading = re.match(r"^## \d+\. (TAI|SUI|SHO|SEI|TEI|EKI) ", line)
        if heading:
            current = heading.group(1)
            continue
        if not current or not re.match(r"^\| (初九|初六|九二|六二|九三|六三|九四|六四|九五|六五|上九|上六) \|", line):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        label, zhigua = cells[0], cells[2]
        position = label[0] if label[0] in ("初", "上") else label[1]
        index = LINE_POSITIONS.index(position)
        bits = BY_NAME[PRODUCTS[current]][1]
        if ("九" in label) != (bits[index] == "1"):
            errors.append(f"detail {current} {label}: polarity mismatch (bit {bits[index]})")
        expected = BY_BITS[changed(bits, index)][1]
        if zhigua != expected:
            errors.append(f"detail {current} {label}: {zhigua} != {expected}")
        seen[current] += 1
    for product, count in seen.items():
        if count != 6:
            errors.append(f"detail {product}: {count} rows")
    return errors


def check_pairs() -> list[str]:
    errors: list[str] = []
    for first, second in [(11, 12), (41, 42), (45, 46), (47, 48), (49, 50)]:
        if BY_NUM[first][1][::-1] != BY_NUM[second][1]:
            errors.append(f"zonggua {first}/{second}: not reversed")
    for first, second in [(11, 12), (41, 42), (42, 43), (45, 46), (46, 47), (47, 48), (48, 49), (49, 50)]:
        if second != first + 1:
            errors.append(f"xugua {first}->{second}: not consecutive")
    return errors


def normalize(text: str) -> str:
    return re.sub(r"[\s，、；。：,.;:（）()「」『』]", "", text)


def check_xiang(doc: str) -> list[str]:
    errors: list[str] = []
    current = None
    count = 0
    for line in doc.splitlines():
        heading = re.match(r"^## \d+\. (TAI|SUI|SHO|SEI|TEI|EKI) ", line)
        if heading:
            current = heading.group(1)
            continue
        if not current or not re.match(r"^\| (初九|初六|九二|六二|九三|六三|九四|六四|九五|六五|上九|上六) \|", line):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        label, zhigua, quote = cells[0], cells[2], cells[3]
        count += 1
        expected = XIANG.get(zhigua)
        if expected is None:
            errors.append(f"xiang {current} {label}: no canonical text for {zhigua}")
            continue
        if normalize(quote) not in normalize(expected):
            errors.append(f"xiang {current} {label} {zhigua}: quote mismatch")
    if count != 36:
        errors.append(f"xiang rows: {count}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", help="write the audit result to this path")
    args = parser.parse_args()

    doc01 = (BASE / "01-64卦のシステム地図.md").read_text(encoding="utf-8")
    doc09 = (BASE / "09-変爻の分析.md").read_text(encoding="utf-8")

    errors: list[str] = []
    errors += check_64_table(doc01)
    errors += check_matrix(doc01)
    errors += check_changes(doc09)
    errors += check_xiang(doc09)
    errors += check_pairs()

    result = {
        "schema": "tai.evaluation.yi-constellation-structure/v0",
        "checkedAt": datetime.now(timezone.utc).isoformat(),
        "documents": [
            "docs/yi-constellation/01-64卦のシステム地図.md",
            "docs/yi-constellation/09-変爻の分析.md",
        ],
        "checks": {
            "64table": "number, name, upper/lower trigram, position",
            "matrix": "8x8 upper/lower placement",
            "changes": "36 summary and detailed line changes, polarity labels",
            "xiang": "36 daisho quotes against the fixture",
            "pairs": "5 zonggua pairs and 8 xugua transitions",
        },
        "errors": errors,
        "passed": not errors,
        "scope": "構造と大象の引用。意味の解釈と製品割当の理由は検算しない。",
    }
    print(f"errors: {len(errors)}")
    for error in errors[:60]:
        print(f"- {error}")
    if args.json:
        Path(args.json).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {args.json}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
