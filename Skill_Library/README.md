# Skill_Library

思考フレームワークのSkill置き場。使うものだけを Active_Skills/ にコピーする。
体系と採用規律は FRAMEWORKS.md を参照。

## 各Skillが守る契約
1. frontmatterで role(generator/evaluator/both)と column(担当列)を宣言する
2. PASS/FAIL/UNKNOWNの判定基準、または行生成の方式を本文に明記する
3. **汎用性規約**: Skill本文の例は必ず2つ以上の異なるドメインに跨ること。
   単一ドメインの例・数値・固有名詞をライブラリ本体に埋め込まない。
   ドメイン固有のfew-shotは Active_Skills/ へのコピー側に注釈する
   (コピー+gitignore方式はこのカスタマイズのためにある)
4. 完全実装の前に tests/validation-problems.md へ最低2ドメイン分の
   「答えの分かっている問題」を追加する(テストファースト)

収録Skill(v0.1.0時点、全6本とも完全実装・検証通過):
1. triz/                   — 40発明原理 + 分離原理
2. first-principles/       — 第一原理思考
3. jobs-to-be-done/        — ジョブ理論
4. blue-ocean/             — ブルーオーシャン戦略(戦略キャンバス+ERRC)
5. frugal-innovation/      — フルーガル革新(BOM概算+削る順番)
6. morphological-analysis/ — 形態分析(設計軸の直積で行を網羅生成)
