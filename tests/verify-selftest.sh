#!/usr/bin/env bash
# scripts/verify.py の自己テスト: 合格フィクスチャが通り、不合格フィクスチャで各ルールが発火するかを確かめる
# 使い方: bash tests/verify-selftest.sh
set -eu
cd "$(dirname "$0")/.."

fail=0
if ! out=$(python3 scripts/verify.py --strict --output tests/fixtures/verify/ok); then
  echo "NG: ok フィクスチャが通らない"; echo "$out"; fail=1
fi

set +e
out=$(python3 scripts/verify.py --output tests/fixtures/verify/ng); code=$?
set -e
[ "$code" -eq 1 ] || { echo "NG: ng フィクスチャの終了コードが1でない(実際: $code)"; fail=1; }
for rule in C01 C02 C03 C04 C05 C06 C07 F01 L01 M01 M02 W01 W02 W03 W04 W05 P01 P02 P03 P04; do
  echo "$out" | grep -q " $rule " || { echo "NG: $rule が発火しない"; fail=1; }
done

# 雛形のままの output/(init直後)はエラーにならないこと
python3 scripts/verify.py --output bootstrap/output >/dev/null || { echo "NG: 初期状態の雛形でエラーになる"; fail=1; }

[ "$fail" -eq 0 ] && echo "verify-selftest: OK"
exit "$fail"
