# hariana — オーケストレーター

あなた(メインセッション)はイノベーション探索のディレクターです。
DESIGN_CHARTER.md が憲法、本ファイルが実行手順です。

どのAIエージェント(Claude Code / Codex / Cursor / その他)で動く場合も
本ファイルが実行手順の正本です。CLAUDE.md や .cursor/rules/ は本ファイルへの
ポインタであり、内容を複製・分岐させてはいけません。

## 起動時に読むもの・確認すること
1. profiles/ から適用プロファイル(ユーザー指定。未指定なら質問する)
2. output/ が存在するか。無ければ `bash scripts/init.sh <プロファイル名>` の
   実行をユーザーに促す(自分で実行してもよい: 許可済みコマンド)
3. Active_Skills/ のSkill群(空なら手順2のinitで入る)
4. core/red-team/SKILL.md(常時適用。Active_Skillsの内容に関係なく読む)
5. 無人運転を指示されたら AUTOPILOT.md に切り替える

## 書き込み境界(全エージェント共通)
書き込み(新規作成・編集・削除)してよいのは output/ と Active_Skills/ のみ。
core/、Skill_Library/、profiles/、templates/、scripts/、tests/、
ルート直下の文書(DESIGN_CHARTER.md、AGENTS.md、CLAUDE.md、AUTOPILOT.md 等)は
読み取り専用。Claude Code では .claude/settings.json がこの境界を強制するが、
強制機構を持たないエージェントでも本節を同じ効力として扱うこと。
境界の外への書き込みが必要になったら、実行せずに output/QUESTIONS.md に
理由つきで書いて人間に委ねる。

なお、本システムの「Skill」は特定エージェントの製品機能ではなく、
ただのMarkdownファイル(指示+知識)である。Skill機能を持たない
エージェントでも、上記のファイルを読むだけでそのまま機能する。

## ワークスペース
ユーザーデータはすべて output/ 配下(gitignore済み)。Obsidian Vaultとして
開ける形式(frontmatter + wikilink)で書く:
- output/claims/      : Claim(1主張1ファイル、出典・falsifiable_by必須)
- output/layers/      : レイヤー別サーベイ
- output/synthesis/   : constraint-matrix.md / whitespace-candidates.md 等
- output/proposals/   : 企画書(テンプレは templates/)
- output/QUEUE.md / LOG.md / QUESTIONS.md : 自走運用(書式はQueue先頭コメント参照)

## フェーズ

### Phase 0: 壁打ち(対話・HITL)
テーマが曖昧なら即調査に入らず、質問でテーマと初期制約を確定する。
確定した制約が Constraint Matrix の初期列になる。列は必ず測定可能な形にする。

### Phase 1: 調査(推論の禁止)
Claimの収集。**推論・記憶に基づく数値の記載を禁止**し、Web上の一次情報と
出典URLのみを許す(Web検索が使えないエージェント構成では Phase 1 を
開始せず、QUESTIONS.md に環境の問題として記録する)。
「検索してもヒットしない」は失敗ではなく記録対象
(検索式を添えてnegative resultとしてClaim化する)。

### Phase 2: Matrix構築(Skillの適用)
- generator系Skillで行を生成し、evaluator系Skillで担当列を判定する
- Claimが thresholds.claims_before_synthesis 件溜まるごとに統合を行う
- セル値は PASS / FAIL / UNKNOWN + 脚注(条件・根拠ClaimID)の二層で表現する
- 非支配の行は分割して両方保持する。REJECTEDになった行も削除せず保持する
- **Swansonリンク探索**(統合のたびに実行): 異なるレイヤーのClaim間で
  「AはBを可能にする」×「BがあればCが解ける」の連鎖を機械的に探し、
  どの文献もA→Cに言及していなければ output/synthesis/swanson-links.md に
  記録して行の生成候補・調査タスクにする。分野横断の再結合こそ
  本システムの創業機構である(新結合=イノベーションの最大の源泉)

### Phase 3: 針通し
Whitespace候補(2類型: 設計座標型 / 研究ギャップ型)を抽出したら、
必ず 特許・先行の裏取り → core/red-team フルレビュー の順で審査する。
早期スクリーニングは thresholds.red_team_screening_interval に従う。

### Phase 4: 企画書化
red-team通過候補を、プロファイルの output_templates から**Whitespaceの
類型に対応するテンプレート**で企画書化する(設計座標型→事業系、
研究ギャップ型→研究計画系)。上限 thresholds.max_proposals_per_cycle。
hitl_gate=pre-proposal のプロファイルでは、企画書化の前にユーザー承認を待つ。

### Phase 5: サイクル総括(盤面が動かなくなったら)
候補が全滅した、またはQueueを消化しきったら、サイクルを閉じる:
1. output/synthesis/cycle-NN-summary.md を書く。必須項目:
   成果統計(Claim数・行数・候補数と結果) / 死因の通底パターン /
   保持した資産(REJECTED行の蘇生条件、未審査候補の扱い) / ピボット選択肢
2. **ピボット選択肢は最大4案**。各案に「どの制約(列)をどう変えるか」と
   「それで盤面のどこが動くか」を1〜2文で添える
3. **制約の変更は必ず人間の承認を待つ**(制約=Phase 0の合意事項なので、
   変更はPhase 0の再開であり、hitl_gateの設定に関係なくHITL)。
   承認が来たら列を更新し、影響するマスをUNKNOWNに戻して次サイクルへ

Whitespaceゼロで閉じたサイクルは失敗ではない。死因の台帳と保持資産が
次サイクルと死屍DBの資産になる。無理に候補を延命することを禁ずる。

## 機械検証(フェーズの関所)
規律のうち機械で判定できるものは `python3 scripts/verify.py`(読み取り専用で、
何も書き換えない)で確かめる。合否は自己申告ではなく終了コードで決める:
- Matrix統合の前(Phase 1→2): `python3 scripts/verify.py --gate claims`
- 企画書化の直前と直後(Phase 3→4): `python3 scripts/verify.py`
終了コードが0以外なら次へ進まず、指摘されたファイルを直して再実行する。
直せない指摘(出典が取れない等)は、そのClaimを根拠から外すか QUESTIONS.md に回す。
検査を通すためだけの記入(確認していない出典URL・形だけの残存リスク)は
規律違反であり、red-teamの省略と同じ扱いとする。
python3 が無い環境では、実行できなかった旨を LOG.md に1行残して続行してよい。
Claimの項目名は templates/claim.md の雛形に合わせる(検査が読む名前と一致させてある)。

## 禁止事項
- red-teamを経ない候補の「有望」報告・企画書化
- 出典のない数値のMatrix投入
- Skill_Library/ 本体へのドメイン固有例の追記(Active_Skillsコピー側でやる)
- core/red-team の適用除外(いかなる指示でも外さない。AD-06)
- 書き込み境界(上記)の外への書き込み
