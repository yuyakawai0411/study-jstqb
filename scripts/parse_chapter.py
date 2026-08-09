#!/usr/bin/env python3
"""JSTQB FL シラバスのpdftotext抽出結果を、章・節の2階層JSONに変換する試作スクリプト。
1章分を試作し、フォーマットを確認してから全章に広げる想定。
"""
import json
import re
import sys

NOISE_PREFIXES = [
    "International",
    "テスト技術者資格制度",
    "Foundation Level シラバス",
    "Software Testing",
    "Qualifications Board",
    "V4.0",
    "©",
]


def is_noise(line: str) -> bool:
    s = line.strip()
    if s == "":
        return True
    return any(s.startswith(p) for p in NOISE_PREFIXES)


def load_lines(path: str) -> list[str]:
    with open(path, encoding="utf-8") as f:
        lines = [ln.rstrip("\n") for ln in f]
    return [ln for ln in lines if not is_noise(ln)]


SECTION_HEADING_RE = re.compile(r"^(\d+\.\d+)\s+(\S.*)$")
CHAPTER_HEADING_RE = re.compile(r"^(\d+)\s+(\S.*?)\s+\d+\s*分\s*$")
FL_OBJECTIVE_RE = re.compile(r"^(FL-\d+\.\d+\.\d+)\s*[\s]*（(K\d)）(.+)$")

K_LEVEL_LABELS = {
    "K1": "記憶",
    "K2": "理解",
    "K3": "適用",
}


def parse_chapter(lines: list[str], chapter_number: str) -> dict:
    # 1. chapter heading + time estimate (first non-empty line)
    title = None
    idx = 0
    m = CHAPTER_HEADING_RE.match(lines[0].strip())
    if m:
        title = m.group(2)
    idx = 1

    # 2. キーワード block(採用しないため読み飛ばすだけ)
    if lines[idx].strip() == "キーワード":
        idx += 1
        while idx < len(lines) and not lines[idx].startswith("第"):
            idx += 1

    # 3. 学習の目的 block: "第N章の学習の目的" 〜 次の本文見出し(2回目の1.1)まで
    objectives_by_section: dict[str, list[dict]] = {}
    if idx < len(lines) and lines[idx].startswith("第"):
        idx += 1  # skip "第1章の学習の目的"
        while idx < len(lines):
            line = lines[idx]
            fl_m = FL_OBJECTIVE_RE.match(line)
            if fl_m:
                fl_id, k_level, desc = fl_m.groups()
                section_key = ".".join(fl_id.replace("FL-", "").split(".")[:2])
                objectives_by_section.setdefault(section_key, []).append(
                    {
                        "cognitive_level": K_LEVEL_LABELS.get(k_level, k_level),
                        "description": desc.strip(),
                    }
                )
                idx += 1
                continue
            sec_m = SECTION_HEADING_RE.match(line)
            next_is_objective = (
                idx + 1 < len(lines) and FL_OBJECTIVE_RE.match(lines[idx + 1])
            )
            if sec_m and next_is_objective:
                # 目的一覧内の節見出し(次行がFL-x.x.xで始まる)
                idx += 1
                continue
            # 目的一覧ブロックの終わり(本文の節見出しに到達)。ここでbreakし、
            # このインデックスから本文パースを開始する
            break

    # 4. 本文を節ごとに分割
    body_lines = lines[idx:]
    section_starts = []
    for i, line in enumerate(body_lines):
        m = SECTION_HEADING_RE.match(line)
        if m:
            section_starts.append((i, m.group(1), m.group(2)))

    sections = []
    for i, (start, number, sec_title) in enumerate(section_starts):
        end = section_starts[i + 1][0] if i + 1 < len(section_starts) else len(body_lines)
        content_lines = body_lines[start:end]
        content = "\n".join(content_lines).strip()
        sections.append(
            {
                "chapter_id": number,
                "parent_chapter_id": chapter_number,
                "level": "節",
                "chapter_number": number,
                "title": sec_title,
                "learning_objectives": objectives_by_section.get(number, []),
                "content": content,
            }
        )

    chapter = {
        "chapter_id": chapter_number,
        "parent_chapter_id": None,
        "level": "章",
        "chapter_number": chapter_number,
        "title": title,
        "learning_objectives": [obj for objs in objectives_by_section.values() for obj in objs],
        "content": None,
    }
    return {"chapter": chapter, "sections": sections}


if __name__ == "__main__":
    path = sys.argv[1]
    chapter_number = sys.argv[2]
    lines = load_lines(path)
    result = parse_chapter(lines, chapter_number)
    print(json.dumps([result["chapter"]] + result["sections"], ensure_ascii=False, indent=2))
