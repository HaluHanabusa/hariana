# Claim雛形(1主張1ファイル。output/claims/ に置く)

下の `---` から先を写して使う。frontmatterは必ずファイルの先頭に置く
(先頭でないとObsidianのプロパティとDataviewが読めない)。
項目名は scripts/verify.py が検査する名前に合わせてある。

---
id: (一意なID。ファイル名と同じでよい)
tags: [claim]
layer: (レイヤー名)
date: (取得日 YYYY-MM-DD)
confidence: (high | medium | low)
source: (一次情報のURL。まとめ記事・SNSの又聞きは不可)
quote: (任意。出典の原文の抜粋。数値を含む主張は、その数値を含む一文を写す)
falsifiable_by: (この主張が誤りになる条件)
---
# (主張を1文で)

補足(条件・測定方法・注意点)。

## 書き分け
- **negative result**(探したが無かった): tags を `[claim, negative]` にし、
  source の代わりに `search_query: (使った検索式)` を書く
- **矛盾するClaim**: tags に `conflict` を足す(INDEX.md のダッシュボードが拾う)
- 括弧書きのまま残した項目は、scripts/verify.py では未記入として扱われる
