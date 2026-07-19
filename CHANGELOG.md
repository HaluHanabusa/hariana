# Changelog

## 未リリース
- 視覚的証拠の自動取得: scripts/capture.sh(shot-scraperベース。CSSセレクタでの
  要素切り取り・出典台帳 output/assets/SOURCES.md への自動追記)。
  AGENTS.md「視覚的証拠(画像)の扱い」節と SETUP.md「画像キャプチャ(任意)」を追加、
  .claude/settings.json に capture.sh の許可を追加

## v0.1.0 (2026-07-18)
初回リリース。

- 思想・設計: DESIGN_CHARTER(制約充足 / Whitespace 2類型 / 3値判定 /
  AD-01〜07)、FRAMEWORKS体系(Tier 1/2 + generator/evaluator/gateの3役割)
- Skill: triz / first-principles / jobs-to-be-done / blue-ocean /
  frugal-innovation / morphological-analysis の6本を完全実装
  (複数ドメイン検証問題 計13問 全通過)
- core: red-team(5本柱・着脱不可・別セッション並列で有効性実証済み)+
  graveyard(死屍DB、初期4件)
- 実行系: AGENTS.md(実行手順の正本、Phase 0〜5。Claude Code / Codex /
  Cursor などエージェント非依存)/ AUTOPILOT.md(無人運転)/
  scripts/init.sh(output/雛形展開・Skillコピー・エージェント別入口の生成)/
  bootstrap雛形 / 権限設定(.claude/settings.json。強制機構の無い
  エージェントは AGENTS.md「書き込み境界」+ git履歴で防壁)
- プロファイル: individual / academic(しきい値・hitl_gate・企画書類型分岐)
- E2E: 乾式運転1周・全チェック合格(成熟市場でのWhitespaceゼロを正直に報告)
- ライセンス: Apache-2.0 / 名称検証: GitHub/npm/PyPI/J-PlatPat クリア

## 予定(v0.2)
- sme / enterprise プロファイルと PR-FAQ / ステージゲート系テンプレート
- Tier 2 Skill(scamper / analogy-biomimicry 等。初フィードバックで順位決定)
- 事例第2弾: 研究ギャップ型の実事例の追加
- 英語README(海外からの反応次第で繰り上げ)
