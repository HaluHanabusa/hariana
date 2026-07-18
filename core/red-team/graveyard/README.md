# Graveyard — 死屍DB

「試されて死んだ」事例の台帳。死屍攻撃(柱3)の照合先。
初期データはドメイン運用のEXTRACTION_PROTOCOL表3(KILL分類)から注入し、
以降はred-teamのKILL判定のたびに追記する。

## 記録形式(1事例1ファイル、Obsidian互換)
```markdown
---
id: GY-001
domain: (ドメイン名)
death_cause: technical | economic | timing
revivable: true | false
tags: [graveyard]
---
# 事例名
何が試され、なぜ死んだか(2〜4文)。
死因が timing の場合: どの前提技術が変われば蘇生しうるかを明記。
出典: (一次情報URL)
```

## 規律
- 死屍は削除しない(蘇生判断の履歴が資産になる)
- revivable: true の事例は、前提技術の変化を検知したら再審に回す
