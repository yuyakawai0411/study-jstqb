#!/usr/bin/env python3
"""records/answers.jsonlに回答記録を1行追記する。

標準入力からJSONオブジェクトを1件受け取り、answered_at(ISO8601, JST)を
付与した上でrecords/answers.jsonlに1行追記する。ファイル・ディレクトリが
無ければ新規作成する。実行時のカレントディレクトリはリポジトリルート
(syllabus/・records/の親)であることを前提とする。

使い方:
    python3 .claude/skills/jstqb-study/scripts/append_answer.py <<'EOF'
    {"chapter_id": "1.2", "cognitive_level": "理解", "learning_objective": "...",
     "question_text": "...", "user_answer": "...", "model_answer": "...",
     "understanding_level": "△"}
    EOF
"""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REQUIRED_FIELDS = [
    "chapter_id",
    "cognitive_level",
    "learning_objective",
    "question_text",
    "user_answer",
    "model_answer",
    "understanding_level",
]
VALID_COGNITIVE_LEVELS = {"記憶", "理解", "適用"}
VALID_UNDERSTANDING_LEVELS = {"◎", "△", "×"}
JST = timezone(timedelta(hours=9))
RECORDS_PATH = Path("records/answers.jsonl")


def main() -> None:
    raw = sys.stdin.read()
    try:
        record = json.loads(raw)
    except json.JSONDecodeError as e:
        sys.exit(f"標準入力が正しいJSONではありません: {e}")

    missing = [f for f in REQUIRED_FIELDS if f not in record]
    if missing:
        sys.exit(f"必須フィールドが不足しています: {', '.join(missing)}")

    if record["cognitive_level"] not in VALID_COGNITIVE_LEVELS:
        sys.exit(
            f"cognitive_levelは{sorted(VALID_COGNITIVE_LEVELS)}のいずれかである必要があります"
        )
    if record["understanding_level"] not in VALID_UNDERSTANDING_LEVELS:
        sys.exit(
            f"understanding_levelは{sorted(VALID_UNDERSTANDING_LEVELS)}のいずれかである必要があります"
        )

    record["answered_at"] = datetime.now(JST).isoformat(timespec="seconds")

    RECORDS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with RECORDS_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"記録しました: {RECORDS_PATH}")


if __name__ == "__main__":
    main()
