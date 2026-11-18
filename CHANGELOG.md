# Changelog

## 未リリース
- 規律の機械検証: scripts/verify.py(標準ライブラリのみ・読み取り専用)。
  既存の規律(Claimの出典URL・falsifiable_by・negative resultの検索式、
  SURVIVE候補のred-team記録と残存リスク、red-team未通過候補の企画書化禁止、
  wikilink切れ)を終了コードで判定する。新しい規律は足していない。
  AGENTS.md「機械検証(フェーズの関所)」節、templates/claim.md(Claim雛形)、
  tests/verify-selftest.sh とフィクスチャを追加
- 既知の課題: `python3 scripts/verify.py --gate graveyard` は初期4件を
  出典URLなしとして検出する(CONTRIBUTING.md の「出典URL必須」に未対応)
- profiles/individual.yml のしきい値コメントのずれを修正

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
