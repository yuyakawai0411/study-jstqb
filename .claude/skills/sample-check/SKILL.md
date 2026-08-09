---
name: sample-check
description: モバイルアプリからこのリポジトリのSkillが検出・呼び出せるかを確認するための動作確認用Skill。「サンプルチェックして」「skillの動作確認して」と言われたら使う。
---

# サンプルチェックSkill

このSkillは `study-jstqb` リポジトリの `.claude/skills/` がモバイルアプリ(Claude Code on the web/モバイル)から検出できるかを確認するための、動作確認専用のSkillです。

呼び出されたら、他には何もせず、次のメッセージだけをそのまま返してください。

```
✅ study-jstqbリポジトリのSkillが正しく呼び出されました(sample-check)
```
