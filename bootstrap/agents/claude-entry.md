# hariana — 入口(Claude Code用)

実行手順の正本は AGENTS.md です。以下でその全文を取り込みます。
本ファイルに手順を複製・追記しないでください(分岐禁止)。

@AGENTS.md

## Claude Code 固有の補足
- AGENTS.md の「書き込み境界」は .claude/settings.json でも強制されている
  (deny優先)。書き込みが拒否されたらそれは境界違反なので、リトライせず
  output/QUESTIONS.md に回すこと
