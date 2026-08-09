---
name: jstqb-study
description: JSTQB Foundation Levelの学習内容について、対話形式で自由記述の理解度チェック問題を出題・採点するSkill。学習者が「今日勉強した章・節と学んだこと」を話すと、公式シラバスの該当範囲から問題を生成し、回答を理解度レベル(◎/△/×)で採点して記録する。「JSTQBの理解度チェックをして」「今日勉強した内容の問題を出して」といった依頼で使う。JSTQB・FL学習の文脈で使う。
---

# JSTQB学習サポートSkill

自由記述の理解度チェック問題のみを出題する。4択形式の問題や反復ドリルは生成しない(テス友アプリが担当する領域のため)。弱点分析は別Skillが担当するため、このSkillでは行わない。

教材データ(`syllabus/chapters.json`)・回答記録(`records/answers.jsonl`)の構造は [references/data-schema.md](references/data-schema.md) を参照。以下のコマンド例は全てリポジトリルートで実行する前提。

## ワークフロー

### ステップ1: 学習内容のヒアリング

**ARGUMENT**: なし(このステップで学習者から聞き出す)

学習者に「今日勉強した章・節」と「学んだこと(内容の要点)」を聞く。聞き出した内容はそれぞれ `<chapter_or_section>`、`<learned_summary>` として以降のステップで使う。

成功条件: `<chapter_or_section>` と `<learned_summary>` の両方を学習者から得ている。

トラブルシューティング: `<learned_summary>` だけ話されて `<chapter_or_section>` に触れていない場合は、章・節を追加で尋ねる。

### ステップ2: 章・節の照合

**ARGUMENT**: `<chapter_or_section>`(ステップ1)

章・節一覧を取得し、`<chapter_or_section>` と意味的に照合する。

```bash
jq '[.[] | {chapter_id, level, title}]' syllabus/chapters.json
```

表記ゆれは許容し、柔軟に判断する。複数章・節にまたがる発話なら複数を対象にする。マッチした結果を `<chapter_id>` として以降のステップで使う。

成功条件: 1つ以上の `<chapter_id>` が確定している。

トラブルシューティング: 該当する章・節が見つからない場合は、近い候補を提示して再入力を促す(セッションを打ち切らない)。

### ステップ3: 出題数の確認

**ARGUMENT**: なし(このステップで学習者から聞き出す)

学習者に出題数を確認する。聞き出した数を `<question_count>` として以降のステップで使う。

成功条件: `<question_count>` が確定している。

トラブルシューティング: 学習者が数を明言しない場合は、3問程度をデフォルトとして提案し、確認を取ってから進める。

### ステップ4: 問題の生成

**ARGUMENT**: `<chapter_id>`(ステップ2)、`<learned_summary>`(ステップ1)

該当する章・節のレコードを取得する。

```bash
jq '.[] | select(.chapter_id=="<chapter_id>")' syllabus/chapters.json
```

取得した `content`・`learning_objectives` と `<learned_summary>` の3つを踏まえて、自由記述の理解度チェック問題を1問生成する。観点の選び方は [references/learning-objectives.md](references/learning-objectives.md) を参照。生成した問題文を `<question_text>`、参考にした`learning_objectives`の項目を `<referenced_objective>`(`cognitive_level` と `description`)として以降のステップで使う。

成功条件: `<question_text>` が1問生成され、`<referenced_objective>` を記録用に控えている。

トラブルシューティング: 該当節の`content`が短く出題材料に乏しい場合は、`learning_objectives`の別の項目を参考にして生成し直す。

### ステップ5: 採点とフィードバック

**ARGUMENT**: `<user_answer>`(学習者の回答、このステップで聞き出す)

学習者の回答を受け取り、`content` と照合して理解度レベル `<understanding_level>`(◎/△/×)を判定し、模範解答 `<model_answer>` と解説をフィードバックする。判定基準は [references/grading-criteria.md](references/grading-criteria.md) を参照。

成功条件: `<understanding_level>` が確定し、判定理由を`content`の該当箇所を引用しながら説明している。

トラブルシューティング: `<user_answer>` が的外れで`content`のどの箇所とも対応しない場合は×とし、該当箇所を示した上で読み直しを促す。

### ステップ6: 記録

**ARGUMENT**: `<chapter_id>`(ステップ2)、`<referenced_objective>`(ステップ4)、`<question_text>`(ステップ4)、`<user_answer>`(ステップ5)、`<model_answer>`(ステップ5)、`<understanding_level>`(ステップ5)

`scripts/append_answer.py` に標準入力でJSONを渡し、回答記録を追記する。ファイル・ディレクトリが無ければスクリプトが新規作成し、`answered_at`もスクリプトが自動付与する。

```bash
python3 .claude/skills/jstqb-study/scripts/append_answer.py <<'EOF'
{"chapter_id": "<chapter_id>", "cognitive_level": "<referenced_objectiveのcognitive_level>", "learning_objective": "<referenced_objectiveのdescription>", "question_text": "<question_text>", "user_answer": "<user_answer>", "model_answer": "<model_answer>", "understanding_level": "<understanding_level>"}
EOF
```

成功条件: スクリプトが正常終了し(`記録しました: records/answers.jsonl`と表示される)、`records/answers.jsonl`に1行追記されている。

トラブルシューティング: 必須フィールド不足や`cognitive_level`/`understanding_level`が許容値以外の場合、スクリプトはエラーメッセージを出して終了する。メッセージに従って値を修正し再実行する。

### ステップ7: 繰り返しと終了

**ARGUMENT**: `<question_count>`(ステップ3)

指定した問題数に達するまでステップ4〜6を繰り返し、達したらセッションを終える。

成功条件: `<question_count>` と、保存された回答記録の件数が一致している。

トラブルシューティング: 学習者が途中でセッションの終了を求めた場合は、その時点で終了してよい。

## 参考

詳細設計(課題の背景、ユースケース図、ER図、フローチャート)は [issuesリポジトリの設計.md](https://github.com/yuyakawai0411/issues/blob/main/設計.md) を参照。
