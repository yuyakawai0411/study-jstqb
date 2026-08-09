# データ構造

## syllabus/chapters.json

公式シラバスを章・節の2階層(章:1〜6、節:1.1、1.2、…)で構造化したデータ。配列の各要素は以下のフィールドを持つ。

| フィールド | 内容 |
|---|---|
| `chapter_id` | 章・節のID(例: `"1"` = 章、`"1.1"` = 節) |
| `parent_chapter_id` | 節の場合、親の章ID。章の場合は`null` |
| `level` | `"章"` または `"節"` |
| `chapter_number` | 表示用の番号(`chapter_id`と同じ) |
| `title` | 章・節タイトル |
| `learning_objectives` | `{cognitive_level, description}` の配列。`cognitive_level`は`記憶`/`理解`/`適用`のいずれか |
| `content` | シラバス原文抜粋(章の場合は`null`、節にのみ本文が入る) |

ファイル全体で約180KBあるため、`Read`で全文を読み込まず`jq`で必要な範囲だけ抽出する(具体的なコマンドはSKILL.mdのワークフロー各ステップを参照)。

## records/answers.jsonl

回答記録。1行1レコードのJSONL形式で、末尾に1行ずつ追記する。`.claude/skills/jstqb-study/scripts/append_answer.py`で追記する(SKILL.mdのステップ6を参照)ため、直接編集する必要はない。各行は以下のフィールドを持つ。

| フィールド | 内容 |
|---|---|
| `chapter_id` | 出題対象の章・節ID |
| `answered_at` | 回答日時(ISO8601, JST)。スクリプトが自動付与する |
| `cognitive_level` | 出題時に参考にした`learning_objectives`の`cognitive_level` |
| `learning_objective` | 出題時に参考にした`learning_objectives`の`description` |
| `question_text` | 出題した問題文 |
| `user_answer` | 学習者の自由記述回答 |
| `model_answer` | 模範解答・解説 |
| `understanding_level` | 理解度レベル。`◎`/`△`/`×`のいずれか |

例:
```json
{"chapter_id": "1.2", "cognitive_level": "理解", "learning_objective": "テストと品質保証の関係を想起する。", "question_text": "...", "user_answer": "...", "model_answer": "...", "understanding_level": "△", "answered_at": "2026-08-09T14:32:00+09:00"}
```
