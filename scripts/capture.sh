#!/usr/bin/env bash
# 視覚的証拠の取得: Webページ(または特定要素)のスクリーンショットを output/assets/ に保存する
# 使い方: bash scripts/capture.sh <URL> <出力名> [CSSセレクタ]
#   出力名: 英数字とハイフンのみ・拡張子なし。例: ws01-patent-fig1
#   セレクタを指定するとその要素だけを切り取る(例: "figure#drawing" )
# 前提: shot-scraper(導入は SETUP.md「画像キャプチャ」参照)。無ければ uvx で代替実行
# 保存先は output/assets/ 固定。出典は output/assets/SOURCES.md に自動追記される
set -eu
cd "$(dirname "$0")/.."

URL="${1:-}"
NAME="${2:-}"
SELECTOR="${3:-}"

if [ -z "$URL" ] || [ -z "$NAME" ]; then
  echo "使い方: bash scripts/capture.sh <URL> <出力名> [CSSセレクタ]"
  echo "  例: bash scripts/capture.sh 'https://patents.google.com/patent/US1234567' ws01-patent-fig1"
  exit 1
fi

# 出力名の検証: 保存先を output/assets/ の外に出さないため、パス区切り等を拒否する
case "$NAME" in
  *[!a-zA-Z0-9._-]* | .* )
    echo "[capture] エラー: 出力名は英数字・ハイフン・アンダースコアのみ(先頭ドット不可): $NAME"
    exit 1 ;;
esac

# shot-scraper の解決: PATH に無ければ uvx(あれば)で都度実行する
if command -v shot-scraper >/dev/null 2>&1; then
  SS="shot-scraper"
elif command -v uvx >/dev/null 2>&1; then
  SS="uvx shot-scraper"
else
  echo "[capture] エラー: shot-scraper がありません。導入方法:"
  echo "  pip install shot-scraper && shot-scraper install   (SETUP.md「画像キャプチャ」参照)"
  exit 1
fi

mkdir -p output/assets
OUT="output/assets/${NAME}.png"

if [ -n "$SELECTOR" ]; then
  if ! $SS shot "$URL" -o "$OUT" --selector "$SELECTOR" --wait 2000; then
    echo "[capture] エラー: 撮影失敗。セレクタ '$SELECTOR' がページに無い可能性が高い"
    echo "          (getBoundingClientRectのエラーはセレクタ不一致の典型)"
    echo "          対処: まずセレクタ無しで全体を撮り、構造を確認してから絞り込む"
    exit 1
  fi
else
  if ! $SS shot "$URL" -o "$OUT" --wait 2000 --width 1280; then
    echo "[capture] エラー: 撮影失敗。URLの到達性、またはshot-scraperの導入状態を確認"
    exit 1
  fi
fi

# 出典台帳への追記(証拠のトレーサビリティ。手で消さないこと)
SOURCES="output/assets/SOURCES.md"
if [ ! -f "$SOURCES" ]; then
  printf '# assets出典台帳(capture.shが自動追記。画像の出所はここで辿る)\n\n' > "$SOURCES"
fi
{
  printf -- '- %s `%s.png` ← %s' "$(date +%F)" "$NAME" "$URL"
  [ -n "$SELECTOR" ] && printf ' (selector: `%s`)' "$SELECTOR"
  printf '\n'
} >> "$SOURCES"

echo "[capture] 保存: $OUT"
echo "[capture] 次にやること: 画像を開いて目的の内容が写っているか確認してから引用する"
