# Changelog

## v0.1.1 (2026-07-18)
マルチエージェント対応(Claude Code 専用 → AGENTS.md 標準)。

- 実行手順の正本を AGENTS.md に一本化(AD-07)。エージェント別の入口
  (claude→CLAUDE.md、cursor→.cursor/rules/hariana.mdc)は init が
  bootstrap/agents/ のテンプレートから生成する gitignore 済みポインタに変更
  (Codex / Cursor 用に初期化したフォルダには Claude Code 用ファイルを作らない)
- AGENTS.md に「書き込み境界」を明文化(権限強制の無いエージェント向けの
  指示ベース防壁。Claude Code では従来どおり .claude/settings.json で強制)
- scripts/init.sh に第2引数(claude/codex/cursor/other)を追加。
  エージェント別の入口生成と起動案内を切り替え(output/ とSkillの初期化は共通)
- SETUP.md / README.md / GLOSSARY.md をマルチエージェント前提に更新
- 修正: .gitignore の `output/` が雛形 bootstrap/output/ まで無視して
  未コミットになっていた問題(新規クローンで init 手順1が失敗する)。
  `/output/` にアンカーして解消

## v0.1.0 (2026-07-18)
初回リリース。

- 思想・設計: DESIGN_CHARTER(制約充足 / Whitespace 2類型 / 3値判定 /
  AD-01〜06)、FRAMEWORKS体系(Tier 1/2 + generator/evaluator/gateの3役割)
- Skill: triz / first-principles / jobs-to-be-done / blue-ocean /
  frugal-innovation / morphological-analysis の6本を完全実装
  (複数ドメイン検証問題 計13問 全通過)
- core: red-team(5本柱・着脱不可・別セッション並列で有効性実証済み)+
  graveyard(死屍DB、初期4件)
- 実行系: CLAUDE.md(Phase 0〜5)/ AUTOPILOT.md(無人運転)/
  scripts/init.sh / bootstrap雛形 / 権限設定(.claude/settings.json)
- プロファイル: individual / academic(しきい値・hitl_gate・企画書類型分岐)
- E2E: 乾式運転1周・全チェック合格(成熟市場でのWhitespaceゼロを正直に報告)
- ライセンス: Apache-2.0 / 名称検証: GitHub/npm/PyPI/J-PlatPat クリア

## 予定(v0.2)
- sme / enterprise プロファイルと PR-FAQ / ステージゲート系テンプレート
- Tier 2 Skill(scamper / analogy-biomimicry 等。初フィードバックで順位決定)
- 事例第2弾: 研究ギャップ型の実事例の追加
- 英語README(海外からの反応次第で繰り上げ)
