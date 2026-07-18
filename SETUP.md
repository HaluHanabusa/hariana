# セットアップガイド

分からない言葉が出てきたら GLOSSARY.md を見てください。

## 用意するもの
- ローカルAIエージェントが動く環境。要件は「ファイルの読み書き」と
  「Web検索」の2つだけです:
  - **Claude Code**(書き込み禁止領域の強制まで効く推奨環境)
  - **Codex CLI / Cursor**(実行手順 AGENTS.md を自動で読む)
  - その他のエージェント(AGENTS.md 非対応でも、ファイルが読めれば動く)
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
bash scripts/init.sh individual          # Claude Code の場合(第2引数省略)
bash scripts/init.sh individual codex    # Codex の場合
bash scripts/init.sh individual cursor   # Cursor の場合
bash scripts/init.sh individual other    # その他のエージェントの場合
```
初期化ですることは3つ:
- 作業場所 `output/` が雛形から作られる(2回目以降は上書きしません)
- プロファイルの default_skills が `Active_Skills/` にコピーされる
- 第2引数のエージェント用の入口ファイルが生成される
  (claude→`CLAUDE.md`、cursor→`.cursor/rules/hariana.mdc`。中身はどちらも
  正本 AGENTS.md へのポインタ。codex / other は AGENTS.md を直接読むので生成なし)

つまり **Codex や Cursor 用に初期化したフォルダには、Claude Code 用の
ファイルはそもそも作られません**(逆も同じ。両方使いたい場合は
第2引数を変えて init を2回実行すればよい)。

### 4. エージェントを起動して話しかける
実行手順の正本は、どのエージェントでも **AGENTS.md** です
(CLAUDE.md と .cursor/rules/ は、init が生成するそこへの入口)。

**Claude Code**
```bash
claude
```

**Codex CLI**
```bash
codex
```
Phase 1(調査)にはWeb検索が必要です。Web検索を有効にして起動してください
(有効化の方法はバージョンで変わるため `codex --help` で確認)。

**Cursor**
このフォルダをCursorで開き、Agentチャットで話しかけます。
init が生成した`.cursor/rules/hariana.mdc` が入口になります。

**その他のエージェント**
AGENTS.md を自動で読まないエージェントでは、最初のメッセージでこう伝えます:
> 「AGENTS.md を読み、その手順に従ってください」

最初の一言の例(どのエージェントでも共通):
> 「〇〇というテーマで探索を始めたい。Phase 0の壁打ちからお願いします」

AIが質問を返してきます。答えていくとテーマと条件(制約)が固まり、
そこから先(調査→行列→針通し→企画書)は自動で進みます。

### 5. 結果を眺める
Obsidianで「Open folder as vault」→ `output/` を選ぶと、
集めた事実(Claim)とアイデアの系譜がリンクの網として見えます。

## エージェントによる違い(重要)

| | Claude Code | Codex / Cursor / その他 |
|---|---|---|
| 実行手順の読み込み | init が生成する CLAUDE.md 経由で AGENTS.md | AGENTS.md を直接 |
| 書き込み禁止領域の守り | `.claude/settings.json` で**強制** | AGENTS.md「書き込み境界」の指示 + git履歴(強制なし) |
| Web検索 | 内蔵 | エージェント側で有効化が必要な場合あり |

強制機構の無いエージェントでは、まれにAIが仕組み側(core/ 等)を
書き換える事故があり得ます。git管理下で使い、`git status` をときどき確認して
ください(変更されていても `git checkout -- <ファイル>` で戻せます)。

## 無人運転したい場合(任意)
夜間や不在時に回し続けたい場合は AUTOPILOT.md を読み、
起動後に「AUTOPILOT.mdに従ってoutput/QUEUE.mdの処理を開始してください」と
伝えてください。サブスクの利用上限で止まった後の自動再開には
claude-auto-retry(Claude Code用)などの外部ツールが使えます
(導入は各ツールの説明に従う)。

## うまくいかないとき
- **Claude Codeなのに手順が読み込まれない** → 入口 `CLAUDE.md` が生成されて
  いない可能性。`bash scripts/init.sh <プロファイル名>`(第2引数なし)で生成される
- **AIがファイルを書けないと言う(Claude Code)** → `.claude/settings.json` の
  許可設定を確認。書き込みが許されているのは output/ と Active_Skills/ だけです(仕様)
- **AIが手順に従わない(Codex / Cursor / その他)** → 最初のメッセージで
  「AGENTS.md を読み、その手順に従ってください」と明示する。仕組み側の
  ファイルを書き換えられてしまったら `git checkout -- <ファイル>` で戻す
- **Phase 1 の調査が進まない** → そのエージェントでWeb検索が有効かを確認する
- **Skillが読まれていない** → Active_Skills/ にコピーされているか確認
  (`ls Active_Skills/`)。空なら手順3をやり直す
- **red-teamを外したい** → 外せません(設計上の意図です。DESIGN_CHARTER.md AD-06)
