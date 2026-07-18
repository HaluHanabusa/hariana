# セットアップガイド

分からない言葉が出てきたら GLOSSARY.md を見てください。

## 用意するもの
- Claude Code(または同等のローカルAIエージェント)が動く環境
- Obsidian(無料のメモアプリ。結果を眺めるのに使う。無くても動作はする)

## 手順(5分)

### 1. このフォルダ一式を自分のPCに置く
```bash
git clone <このリポジトリのURL>
cd hariana
```

### 2. 自分の立場に合うプロファイルを選ぶ
`profiles/` の中を見て選びます。いまは2種類:
- `individual.yml` — 個人開発者(週末MVPが出口)
- `academic.yml` — 研究者(論文・レポートが出口)
中身はただの設定ファイルなので、金額などを自分の実情に書き換えてOKです。

### 3. 初期化スクリプトを実行する
```bash
bash scripts/init.sh individual   # ← 選んだプロファイル名
```
これで2つのことが起きます:
- 作業場所 `output/` が雛形から作られる(2回目以降は上書きしません)
- プロファイルの default_skills が `Active_Skills/` にコピーされる

### 4. Claude Codeを起動して話しかける
```bash
claude
```
最初の一言の例:
> 「〇〇というテーマで探索を始めたい。Phase 0の壁打ちからお願いします」

AIが質問を返してきます。答えていくとテーマと条件(制約)が固まり、
そこから先(調査→行列→針通し→企画書)は自動で進みます。

### 5. 結果を眺める
Obsidianで「Open folder as vault」→ `output/` を選ぶと、
集めた事実(Claim)とアイデアの系譜がリンクの網として見えます。

## 無人運転したい場合(任意)
夜間や不在時に回し続けたい場合は AUTOPILOT.md を読み、
起動後に「AUTOPILOT.mdに従ってoutput/QUEUE.mdの処理を開始してください」と
伝えてください。サブスクの利用上限で止まった後の自動再開には
claude-auto-retry などの外部ツールが使えます(導入は各ツールの説明に従う)。

## うまくいかないとき
- **AIがファイルを書けないと言う** → `.claude/settings.json` の許可設定を確認。
  書き込みが許されているのは output/ と Active_Skills/ だけです(仕様)
- **Skillが読まれていない** → Active_Skills/ にコピーされているか確認
  (`ls Active_Skills/`)。空なら手順3をやり直す
- **red-teamを外したい** → 外せません(設計上の意図です。DESIGN_CHARTER.md AD-06)
