# ダッシュボード(要Obsidian + Dataviewプラグイン)

## 最新Claim(直近20件)
```dataview
TABLE layer, confidence, date FROM "claims"
WHERE contains(tags, "claim")
SORT file.mtime DESC
LIMIT 20
```

## レイヤー別Claim数
```dataview
TABLE length(rows) AS count FROM "claims"
WHERE contains(tags, "claim")
GROUP BY layer
```

## 確度が低い要注意Claim
```dataview
LIST FROM "claims" WHERE confidence = "low"
```

## 矛盾(CONFLICT)
```dataview
LIST FROM "claims" WHERE contains(tags, "conflict")
```

## 主要ファイル
- [[synthesis/constraint-matrix|制約行列]] / [[synthesis/whitespace-candidates|Whitespace候補]]
- [[QUEUE|タスク]] / [[QUESTIONS|判断待ち]] / [[LOG|ログ]]
