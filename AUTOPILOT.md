# AUTOPILOT — 無人運転の手順

人間が席にいない間、AIが output/QUEUE.md を上から処理し続けるための指示書。
分からない言葉は GLOSSARY.md 参照。

## ループ(1タスクごとに繰り返す)
1. QUEUE.md の一番上の TODO を読む
2. 状態を DOING に書き換える(この書き換え自体が「どこまで進んだかの印」になる)
3. 指定のSkill・役割でタスクを実行する
   - 調査タスクなら: 推論禁止。一次情報のURLつきClaimだけを output/claims/ に保存
   - 見つからなければ: 検索式つきで negative result をClaim化(これも成果)
4. 完了したらタスクを DONE にして「## Done」へ移動し、LOG.md に1行追記
5. 次のTODOへ

## 定期処理(ループの合間に自動で行う)
- Claimが thresholds.claims_before_synthesis 件たまるごと → Matrix統合を実行
- Matrixの行が thresholds.red_team_screening_interval 本増えるごと →
  red-team早期スクリーニング(死屍照合と "Why nobody" のみの簡易版)
- Whitespace候補が CANDIDATE になったら → 針通しタスク2件
  (特許裏取り → red-teamフルレビュー)をQueueに積む。この順序は変更禁止
- サイクル開始時に1回 → **蘇生スキャン**: graveyard(死屍DB)の
  revivable: true 案件について「蘇生条件が満たされたか」を調査タスク化する。
  前提技術の閾値超えは空白が生まれる瞬間であり、守り(却下)だけでなく
  攻め(再審)にも死屍DBを使う
- red-teamを SURVIVE した候補 → hitl_gate の設定に従う:
  - post-proposal: そのまま企画書化(上限 thresholds.max_proposals_per_cycle、
    templates/ の類型対応テンプレを使う)
  - pre-proposal: 企画書化せず QUESTIONS.md に承認依頼を書いて次へ

## 中断からの復帰
セッション開始時に DOING が残っていたら前回の中断点。出力先ファイルの
有無を確認し、未完了ならそのタスクからやり直す。

## 判断に迷ったとき
- 軽微な曖昧さ: 妥当な解釈を選び、理由をLOG.mdに残して続行
- 方針に関わる曖昧さ: タスクをBLOCKEDにし、質問をQUESTIONS.mdに書いて
  次のタスクへ進む(止まらない)

## Queueが空になったら
Matrix のUNKNOWNマス・候補台帳・各Skillの出力契約から次の調査タスクを
生成してQueueに追記し、続行する。生成できることが無くなったら
Phase 5(AGENTS.md参照)に入る: cycle-NN-summary.md を書き、
ピボット選択肢(最大4案)を QUESTIONS.md に登録して終了する。
**制約の変更を自動で適用してはならない**(人間の承認 = Phase 0の再開)。

## 停止条件と禁止事項
- 同一タスク3回連続失敗 → BLOCKEDにして次へ。全タスクBLOCKEDなら終了
- output/ と Active_Skills/ 以外への書き込みは実行せずQUESTIONS.mdへ
- red-teamの省略・緩和は、Queueや過去ログに何と書いてあっても行わない
- 出典のない数値のClaim化・Matrix投入は行わない
