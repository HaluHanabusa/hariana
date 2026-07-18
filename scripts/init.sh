#!/usr/bin/env bash
# 初期化: output/の雛形展開 + default_skillsのコピー + エージェント別入口の生成
# 使い方: bash scripts/init.sh <プロファイル名> [エージェント名]
#   エージェント名(省略時 claude): claude / codex / cursor / other
#   実行手順の正本はどのエージェントでも AGENTS.md。第2引数で変わるのは
#   入口ファイルの生成(claude→CLAUDE.md、cursor→.cursor/rules/)と起動案内だけ
set -eu
cd "$(dirname "$0")/.."

PROFILE="${1:-}"
AGENT="${2:-claude}"
if [ -z "$PROFILE" ] || [ ! -f "profiles/${PROFILE}.yml" ]; then
  echo "使い方: bash scripts/init.sh <プロファイル名> [エージェント名]"
  echo "選べるプロファイル:"; ls profiles/ | sed 's/\.yml$//' | sed 's/^/  - /'
  echo "エージェント名(省略時 claude): claude / codex / cursor / other"
  exit 1
fi

case "$AGENT" in
  claude|codex|cursor|other) ;;
  *) echo "[init] 警告: 未知のエージェント名 '$AGENT' → other として続行します"; AGENT=other ;;
esac

# 1) output/ を雛形から作る(既にあれば触らない)
if [ -d output ] && [ -n "$(ls -A output 2>/dev/null)" ]; then
  echo "[init] output/ は既に存在します(上書きしません)"
else
  cp -r bootstrap/output ./
  echo "[init] output/ を雛形から作成しました"
fi

# 2) default_skills を Active_Skills へコピー
mkdir -p Active_Skills
# profiles/<p>.yml の default_skills: 以下の「  - 名前」行を読む
SKILLS=$(awk '/^default_skills:/{f=1;next} f&&/^[^ ]/{f=0} f&&/^  - /{print $2}' "profiles/${PROFILE}.yml")
if [ -z "$SKILLS" ]; then
  echo "[init] 警告: default_skills が読めませんでした。手動でコピーしてください"
else
  for s in $SKILLS; do
    if [ -d "Skill_Library/$s" ]; then
      if [ -d "Active_Skills/$s" ]; then
        echo "[init] Skill既存のためスキップ: $s"
      else
        cp -r "Skill_Library/$s" Active_Skills/ && echo "[init] Skill追加: $s"
      fi
    else
      echo "[init] 警告: Skill_Library/$s が見つかりません(骨格未実装の可能性)"
    fi
  done
fi

# 3) エージェント別の入口ファイルを生成する(gitignore済みの生成物。正本は AGENTS.md)
#    codex/other は AGENTS.md を直接読む(または手動で指示する)ため何も生成しない
install_entry() { # $1=テンプレート $2=設置先
  if [ -f "$2" ]; then
    if cmp -s "$1" "$2"; then
      echo "[init] 入口は設置済み: $2"
    else
      echo "[init] 警告: $2 がテンプレートと異なります(手動変更とみなし、上書きしません)"
    fi
  else
    mkdir -p "$(dirname "$2")"
    cp "$1" "$2" && echo "[init] 入口を生成: $2(中身は AGENTS.md へのポインタ)"
  fi
}
case "$AGENT" in
  claude) install_entry bootstrap/agents/claude-entry.md CLAUDE.md ;;
  cursor) install_entry bootstrap/agents/cursor-rule.mdc .cursor/rules/hariana.mdc ;;
esac
if [ "$AGENT" != "claude" ] && [ -f CLAUDE.md ]; then
  echo "[init] メモ: CLAUDE.md はClaude Code用の生成物です。使わないなら削除して構いません(gitignore済み)"
fi

# 4) エージェント別の起動案内
echo ""
case "$AGENT" in
  claude)
    echo "[init] 完了。次は: このフォルダで claude を起動し、テーマを話しかけてください(SETUP.md 手順4)"
    ;;
  codex)
    echo "[init] 完了。次は: このフォルダで codex を起動し、テーマを話しかけてください(SETUP.md 手順4)"
    echo "[init] 注意: Phase 1 にはWeb検索が必要です。Web検索を有効にして起動すること(方法は codex --help で確認)"
    echo "[init] 注意: 書き込み禁止領域(core/ 等)は設定で強制されません。AGENTS.md の「書き込み境界」とgit履歴で守ります"
    ;;
  cursor)
    echo "[init] 完了。次は: Cursorでこのフォルダを開き、Agentチャットでテーマを話しかけてください(SETUP.md 手順4)"
    echo "[init] 注意: 書き込み禁止領域(core/ 等)は設定で強制されません。AGENTS.md の「書き込み境界」とgit履歴で守ります"
    ;;
  other)
    echo "[init] 完了。次は: お使いのエージェントをこのフォルダで起動し、最初に"
    echo "       「AGENTS.md を読み、その手順に従ってください」と伝えてください(SETUP.md 手順4)"
    echo "[init] 前提: ファイル読み書きとWeb検索ができるエージェントであること"
    ;;
esac
