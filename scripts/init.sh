#!/usr/bin/env bash
# 初期化: 作業場所output/の雛形展開 + プロファイルのdefault_skillsをActive_Skillsへコピー
set -eu
cd "$(dirname "$0")/.."

PROFILE="${1:-}"
if [ -z "$PROFILE" ] || [ ! -f "profiles/${PROFILE}.yml" ]; then
  echo "使い方: bash scripts/init.sh <プロファイル名>"
  echo "選べるプロファイル:"; ls profiles/ | sed 's/\.yml$//' | sed 's/^/  - /'
  exit 1
fi

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

echo ""
echo "[init] 完了。次は: claude を起動し、テーマを話しかけてください(SETUP.md 手順4)"
