#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hariana 機械検証: AGENTS.md の規律を、文章ではなく終了コードで判定する。

使い方:
  python3 scripts/verify.py                    # 既定(--gate all)
  python3 scripts/verify.py --gate claims      # Claimのみ(Matrix統合の前)
  python3 scripts/verify.py --gate all         # Claim+Matrix+候補台帳+企画書+リンク(企画書化の前後)
  python3 scripts/verify.py --gate graveyard   # リポジトリ側の死屍DB(メンテナ・PR用)
  オプション: --output <dir>(既定 output) / --strict(警告もエラー扱い)

終了コード: 0=合格(警告は可) / 1=エラーあり(次のフェーズへ進まない) / 2=使い方・環境の問題

方針:
- 新しい規律は足さない。AGENTS.md / GLOSSARY.md / core/red-team/SKILL.md に
  既に書かれているルールだけを検査する(各ルールIDの根拠は末尾の RULES 参照)
- 読み取り専用。ファイルを書き換えない。ネットワークに出ない
- 標準ライブラリのみ(追加インストール不要)
- 書式の揺れには寛容に読み、確実に判定できるものだけを ERROR にする。
  判定に自信が持てない項目は WARN に留める
"""
import argparse
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ルールID → (根拠となる文書, 内容)。メッセージと文書の対応を1か所で管理する
RULES = {
    "F01": ("AD-02", "frontmatterがファイル先頭にない(Obsidian/Dataviewが読めない)"),
    "C01": ("AGENTS.md ワークスペース", "Claimにfrontmatterがない"),
    "C02": ("AGENTS.md Phase 1", "出典URLがない"),
    "C03": ("GLOSSARY.md falsifiable_by", "falsifiable_by(反証条件)がない"),
    "C04": ("AGENTS.md Phase 1", "negative resultに検索式がない"),
    "C05": ("AGENTS.md 禁止事項", "主張の数値が抜粋(quote)に見当たらない"),
    "C06": ("GLOSSARY.md Claim", "ClaimのIDが重複している"),
    "C07": ("bootstrap/output/INDEX.md", "ダッシュボード用の項目(layer/confidence/date)が欠けている"),
    "L01": ("AD-02", "wikilinkのリンク先が存在しない"),
    "M01": ("AGENTS.md Phase 2", "PASS/FAILのマスに脚注(根拠)がない"),
    "M02": ("AGENTS.md Phase 2", "脚注記号に対応する脚注本文がない"),
    "W00": ("whitespace-candidates.md 書式", "候補台帳の書式を解釈できない(「## WS-01: 名前」の見出し形式で書く)"),
    "W01": ("whitespace-candidates.md 書式", "候補のtype/statusが無いか不正"),
    "W02": ("AGENTS.md 禁止事項", "SURVIVEなのにred-team記録がない"),
    "W03": ("core/red-team/SKILL.md 判定と出力契約", "SURVIVEなのに残存リスクが0件(審査不備)"),
    "W04": ("whitespace-candidates.md 書式", "候補に根拠Claimがない"),
    "W05": ("AGENTS.md Phase 5", "REJECTEDに蘇生条件の記載がない"),
    "P01": ("templates/", "企画書にwhitespace_idがない"),
    "P02": ("AD-05 / AD-06", "red-teamをSURVIVEしていない候補の企画書がある"),
    "P03": ("templates/", "企画書のred_team欄(通過日と残存リスク数)が空"),
    "P04": ("AGENTS.md Phase 4", "企画書の類型が候補台帳の類型と一致しない"),
    "G01": ("core/red-team/graveyard/README.md", "死屍事例の必須項目が無いか不正"),
    "G02": ("CONTRIBUTING.md", "死屍事例に出典URLがない"),
    "G03": ("core/red-team/graveyard/README.md", "蘇生可能な事例に蘇生条件の記載がない"),
}

SOURCE_KEYS = ("source", "source_url", "url", "sources", "出典")
FALSIFY_KEYS = ("falsifiable_by", "反証条件")
QUERY_KEYS = ("search_query", "query", "検索式")
QUOTE_KEYS = ("quote", "excerpt", "抜粋", "原文")
URL_RE = re.compile(r"https?://[^\s<>\"'))\]]+")
WIKILINK_RE = re.compile(r"!?\[\[([^\]\|#]+)(?:#[^\]\|]*)?(?:\|[^\]]*)?\]\]")
FOOTNOTE_RE = re.compile(r"\(([a-z]{1,2})\)|\[\^([^\]]+)\]")


class Report:
    def __init__(self):
        self.items = []  # (severity, rule, path, message)

    def add(self, severity, rule, path, detail=""):
        msg = RULES[rule][1] + (f" — {detail}" if detail else "")
        self.items.append((severity, rule, str(path), msg))

    def count(self, severity):
        return sum(1 for i in self.items if i[0] == severity)


# ---------- 読み取りの道具 ----------

def read(path):
    return path.read_text(encoding="utf-8-sig", errors="replace")


def strip_code(text):
    """コードブロックとインラインコードを消す(dataviewクエリ等を検査対象から外す)。"""
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return re.sub(r"`[^`\n]*`", "", text)


def clean_scalar(v):
    v = v.strip()
    if v[:1] in ("\"", "'"):
        end = v.find(v[0], 1)
        if end > 0:
            return v[1:end]
    return re.sub(r"\s+#.*$", "", v).strip()


def parse_yaml_subset(lines):
    """frontmatterで使う範囲のYAMLだけを読む(key: value / インライン配列 / 箇条書き配列 / 複数行)。"""
    data, key, mode = {}, None, None
    for raw in lines:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        top = re.match(r"^([^\s:#\-][^:]*?)\s*:\s*(.*)$", raw)
        if top:
            key, val = top.group(1).strip().strip("\"'"), top.group(2).strip()
            if val in ("|", ">", "|-", ">-", "|+", ">+"):
                data[key], mode = "", "block"
            elif val == "":
                data[key], mode = "", "pending"
            elif val.startswith("[") and val.endswith("]"):
                data[key] = [clean_scalar(x) for x in val[1:-1].split(",") if x.strip()]
                mode = None
            else:
                data[key], mode = clean_scalar(val), None
            continue
        if key is None:
            continue
        s = raw.strip()
        if s.startswith("- ") and mode in ("pending", "list"):
            if not isinstance(data[key], list):
                data[key] = []
            data[key].append(clean_scalar(s[2:]))
            mode = "list"
        elif raw[:1].isspace() and mode in ("pending", "block"):
            data[key] = (str(data[key]) + " " + s).strip()
            mode = "block"
    return data


def split_frontmatter(text):
    """戻り値: (frontmatter dict または None, 本文, 先頭にあるか)。
    企画書テンプレのように見出しの後ろに置かれた場合も読む(先頭でなければF01で警告)。"""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines[:15]):
        s = line.strip()
        if s == "---":
            start = i
            break
        if s and not s.startswith("#") and not s.startswith("<!--"):
            return None, text, False
    if start is None:
        return None, text, False
    for j in range(start + 1, min(len(lines), start + 41)):
        if lines[j].strip() == "---":
            fm = parse_yaml_subset(lines[start + 1:j])
            body = "\n".join(lines[:start] + lines[j + 1:])
            return fm, body, start == 0
    return None, text, False


def as_list(v):
    if v is None or v == "":
        return []
    return [str(x) for x in v] if isinstance(v, list) else [str(v)]


def is_blank(v):
    """空欄・テンプレの括弧書きのまま・プレースホルダを「未記入」とみなす。"""
    if isinstance(v, list):
        return all(is_blank(x) for x in v) if v else True
    s = str(v or "").strip().strip("*_`").strip()
    if not s or s in ("-", "…", "...", "TODO", "TBD", "未記入"):
        return True
    return bool(re.fullmatch(r"[((][^))]*[))]", s))


def get_any(fm, keys):
    for k in keys:
        if k in fm and not is_blank(fm[k]):
            return fm[k]
    return None


def body_field(body, labels):
    """本文中の「出典: ...」「検索式: ...」のような行の値を拾う。"""
    pat = re.compile(r"^\s*[-*]?\s*\**(?:%s)\**\s*[::]\s*(.+)$" % "|".join(map(re.escape, labels)), re.I)
    for line in body.splitlines():
        m = pat.match(line)
        if m and not is_blank(m.group(1)):
            return m.group(1).strip()
    return None


def numbers(text):
    t = unicodedata.normalize("NFKC", str(text))
    return {n.replace(",", "") for n in re.findall(r"\d+(?:[.,]\d+)*", t)}


def md_files(directory):
    if not directory.is_dir():
        return []
    return sorted(p for p in directory.rglob("*.md")
                  if not p.name.startswith(("_", ".")) and p.stem.upper() != "README"
                  and ".obsidian" not in p.parts)


# ---------- Claim ----------

def is_negative(fm):
    tags = [t.lower() for t in as_list(fm.get("tags"))]
    if any(t in ("negative", "negative-result", "negative_result", "不在") for t in tags):
        return True
    if any(str(fm.get(k, "")).lower().startswith("negative") for k in ("type", "kind", "result")):
        return True
    return str(fm.get("negative", "")).lower() in ("true", "yes")


def check_claims(vault, rep, stats):
    seen = {}
    files = md_files(vault / "claims")
    stats["Claim"] = len(files)
    numeric = quoted = 0
    for p in files:
        rel = p.relative_to(vault)
        fm, body, at_top = split_frontmatter(read(p))
        if fm is None:
            rep.add("ERROR", "C01", rel)
            continue
        if not at_top:
            rep.add("WARN", "F01", rel)

        cid = str(fm.get("id") or p.stem)
        if cid in seen:
            rep.add("ERROR", "C06", rel, f"{cid} は {seen[cid]} と重複")
        seen[cid] = rel

        negative = is_negative(fm)
        if negative:
            stats["うちnegative result"] = stats.get("うちnegative result", 0) + 1
            if not (get_any(fm, QUERY_KEYS) or body_field(body, QUERY_KEYS + ("検索クエリ",))):
                rep.add("ERROR", "C04", rel, "search_query に使った検索式を書く")
        else:
            src = " ".join(as_list(get_any(fm, SOURCE_KEYS)))
            if not URL_RE.search(src):
                src = body_field(body, ("出典", "source", "ソース")) or ""
            if not URL_RE.search(src):
                rep.add("ERROR", "C02", rel, "source に一次情報のURLを書く")

        if not (get_any(fm, FALSIFY_KEYS) or body_field(body, FALSIFY_KEYS)):
            rep.add("ERROR", "C03", rel)

        missing = [k for k in ("layer", "confidence", "date") if is_blank(fm.get(k))]
        if missing:
            rep.add("WARN", "C07", rel, "欠落: " + ", ".join(missing))

        # 数値の裏付け: 主張(見出し)の数値が抜粋に現れるか。抜粋が無いClaimは件数だけ集計する
        heading = re.search(r"^#\s+(.+)$", body, flags=re.M)
        statement = str(fm.get("claim") or (heading.group(1) if heading else ""))
        nums = numbers(statement)
        if nums and not negative:
            numeric += 1
            quote = get_any(fm, QUOTE_KEYS)
            if quote:
                quoted += 1
                lost = sorted(nums - numbers(" ".join(as_list(quote))))
                if lost:
                    rep.add("WARN", "C05", rel, "抜粋に無い数値: " + ", ".join(lost))
    if numeric:
        stats["数値を含むClaim"] = numeric
        stats["うち抜粋(quote)つき"] = quoted


# ---------- wikilink ----------

def check_links(vault, rep):
    index = set()
    for p in vault.rglob("*"):
        if p.is_file() and ".obsidian" not in p.parts:
            rel = p.relative_to(vault).as_posix().lower()
            for name in (rel, p.name.lower()):
                index.add(name)
                if name.endswith(".md"):
                    index.add(name[:-3])
    for p in md_files(vault):
        rel = p.relative_to(vault)
        strict_zone = rel.parts[0] in ("synthesis", "proposals")
        for m in WIKILINK_RE.finditer(strip_code(read(p))):
            target = m.group(1).strip().rstrip("\\").strip().lower().replace("\\", "/")
            local = (rel.parent / target).as_posix().lower()
            if target in index or local in index or target.split("/")[-1] in index:
                continue
            rep.add("ERROR" if strict_zone else "WARN", "L01", rel, f"[[{m.group(1).strip()}]]")


# ---------- Matrix ----------

def check_matrix(vault, rep, stats):
    path = vault / "synthesis" / "constraint-matrix.md"
    if not path.is_file():
        return
    rel = path.relative_to(vault)
    text = strip_code(read(path))
    used, defined, counts, bare = set(), set(), {"PASS": 0, "FAIL": 0, "UNKNOWN": 0}, 0
    lines = [l.strip() for l in text.splitlines()]
    is_sep = [bool(l.startswith("|") and re.fullmatch(r"[|\s:\-]+", l)) for l in lines]
    for i, s in enumerate(lines):
        if s.startswith("|"):
            if is_sep[i] or (i + 1 < len(lines) and is_sep[i + 1]):
                continue
            row = WIKILINK_RE.sub(lambda m: m.group(0).replace("|", "/"), s)
            for cell in row.strip("|").split("|")[1:]:
                value = re.search(r"(?<![A-Za-z])(PASS|FAIL|UNKNOWN)(?![A-Za-z])", cell)
                if not value:
                    continue
                counts[value.group(1)] += 1
                marks = FOOTNOTE_RE.findall(cell)
                used.update(a or b for a, b in marks)
                if value.group(1) != "UNKNOWN" and not marks and "[[" not in cell:
                    bare += 1
        else:
            d = re.match(r"^[-*]?\s*(?:\(([a-z]{1,2})\)|\[\^([^\]]+)\]:)\s*(.*)$", s)
            if d and not is_blank(d.group(3)):
                defined.add(d.group(1) or d.group(2))
    stats.update({f"Matrixの{k}マス": v for k, v in counts.items() if sum(counts.values())})
    if bare:
        rep.add("WARN", "M01", rel, f"{bare}マス")
    undefined = sorted(used - defined)
    if undefined:
        rep.add("WARN", "M02", rel, "未定義: " + ", ".join(f"({u})" for u in undefined))


# ---------- Whitespace候補台帳 ----------

LEDGER_FIELDS = [
    ("type", r"type"),
    ("status", r"status"),
    ("claims", r"根拠(?:\s*Claim(?:\s*ID)?)?"),
    ("redteam", r"red[-_ ]?team\s*(?:記録|レビュー|判定)?"),
    ("risks", r"残存リスク"),
    ("revive", r"蘇生条件(?:\s*[((][^))]*[))])?"),
]
LEDGER_RE = re.compile(
    r"(?:^|[\s/、,\-*])(?P<key>%s)\s*[::]" % "|".join(f"(?:{p})" for _, p in LEDGER_FIELDS), re.I | re.M)


def parse_ledger(text):
    blocks, cur = {}, None
    for line in strip_code(text).splitlines():
        head = re.match(r"^#{2,4}\s+(WS-\d+)\b[::]?\s*(.*)$", line)
        if head:
            cur = head.group(1).upper()
            blocks[cur] = {"name": head.group(2).strip(), "lines": []}
        elif re.match(r"^#{1,2}\s", line):
            cur = None
        elif cur:
            blocks[cur]["lines"].append(line)
    for b in blocks.values():
        raw = re.sub(r"[*`]", "", "\n".join(b["lines"]))
        hits = list(LEDGER_RE.finditer(raw))
        fields = {}
        for i, m in enumerate(hits):
            end = hits[i + 1].start() if i + 1 < len(hits) else len(raw)
            value = re.sub(r"\s*/\s*$", "", raw[m.end():end].strip()).strip(" -\n")
            for name, pat in LEDGER_FIELDS:
                if re.fullmatch(pat, m.group("key"), flags=re.I):
                    fields.setdefault(name, value)
                    break
        b["fields"] = fields
        st = re.search(r"CANDIDATE|SURVIVE|REJECTED|CONDITIONAL|KILL", fields.get("status", "").upper())
        b["status"] = st.group(0) if st else None
        b["type"] = norm_type(fields.get("type", ""))
    return blocks


def norm_type(v):
    v = str(v).lower()
    if "design" in v or "設計座標" in v:
        return "design-coordinate"
    if "research" in v or "研究ギャップ" in v:
        return "research-gap"
    return None


def check_ledger(vault, rep, stats):
    path = vault / "synthesis" / "whitespace-candidates.md"
    if not path.is_file():
        return {}
    rel = path.relative_to(vault)
    text = read(path)
    blocks = parse_ledger(text)
    if not blocks and re.search(r"WS-\d+", strip_code(text)):
        # 表形式など想定外の書き方。誤って企画書を止めないよう、判定不能として警告に留める
        rep.add("WARN", "W00", rel)
        return None
    for ws, b in blocks.items():
        f = b["fields"]
        if not b["type"] or not b["status"]:
            rep.add("ERROR", "W01", rel, f"{ws}: type={f.get('type') or '無'} / status={f.get('status') or '無'}")
            continue
        stats[f"候補 {b['status']}"] = stats.get(f"候補 {b['status']}", 0) + 1
        if b["status"] == "SURVIVE":
            if is_blank(f.get("redteam")):
                rep.add("ERROR", "W02", rel, ws)
            risks = f.get("risks", "")
            if is_blank(risks) or re.match(r"^(0\s*件|0(?![\d.])|なし|無し|ゼロ|none|n/a)", risks.strip(), flags=re.I):
                rep.add("ERROR", "W03", rel, ws)
        if is_blank(f.get("claims")):
            rep.add("ERROR" if b["status"] == "SURVIVE" else "WARN", "W04", rel, ws)
        if b["status"] in ("REJECTED", "KILL") and is_blank(f.get("revive")):
            rep.add("WARN", "W05", rel, f"{ws}: 蘇生不可なら「なし」と明記する")
    return blocks


# ---------- 企画書 ----------

def check_proposals(vault, rep, stats, ledger):
    files = md_files(vault / "proposals")
    stats["企画書"] = len(files)
    for p in files:
        rel = p.relative_to(vault)
        fm, _, at_top = split_frontmatter(read(p))
        fm = fm or {}
        if fm and not at_top:
            rep.add("WARN", "F01", rel)
        raw_id = " ".join(as_list(get_any(fm, ("whitespace_id", "whitespace-id", "whitespace", "ws_id"))))
        m = re.search(r"WS-\d+", raw_id.upper())
        if not m:
            rep.add("ERROR", "P01", rel)
            continue
        if ledger is None:
            rep.add("WARN", "P02", rel, f"{m.group(0)}: 候補台帳を解釈できず判定不能")
            continue
        entry = ledger.get(m.group(0))
        if entry is None:
            rep.add("ERROR", "P02", rel, f"{m.group(0)} が候補台帳にない")
        elif entry["status"] != "SURVIVE":
            rep.add("ERROR", "P02", rel, f"{m.group(0)} の status は {entry['status'] or '不明'}")
        elif norm_type(fm.get("type", "")) and norm_type(fm.get("type", "")) != entry["type"]:
            rep.add("WARN", "P04", rel, f"企画書={fm.get('type')} / 台帳={entry['type']}")
        if is_blank(get_any(fm, ("red_team", "red-team", "redteam"))):
            rep.add("ERROR", "P03", rel)


# ---------- 死屍DB(リポジトリ側) ----------

def check_graveyard(rep, stats):
    files = sorted((ROOT / "core" / "red-team" / "graveyard").glob("GY-*.md"))
    stats["死屍事例"] = len(files)
    for p in files:
        rel = p.relative_to(ROOT)
        fm, body, _ = split_frontmatter(read(p))
        fm = fm or {}
        bad = [k for k in ("id", "domain") if is_blank(fm.get(k))]
        if str(fm.get("death_cause", "")).lower() not in ("technical", "economic", "timing"):
            bad.append("death_cause")
        if str(fm.get("revivable", "")).lower() not in ("true", "false"):
            bad.append("revivable")
        if bad:
            rep.add("ERROR", "G01", rel, ", ".join(bad))
        src = body_field(body, ("出典", "source")) or ""
        tail = body[body.find("出典"):] if "出典" in body else ""
        if not URL_RE.search(src) and not URL_RE.search(tail):
            rep.add("ERROR", "G02", rel)
        revivable = str(fm.get("revivable", "")).lower() == "true"
        if (revivable or str(fm.get("death_cause", "")).lower() == "timing") and "蘇生条件" not in body:
            rep.add("WARN", "G03", rel)


# ---------- 実行 ----------

def main():
    ap = argparse.ArgumentParser(description="hariana 機械検証(読み取り専用)")
    ap.add_argument("--gate", choices=("claims", "all", "graveyard"), default="all")
    ap.add_argument("--output", default="output", help="探索データのフォルダ(既定: output)")
    ap.add_argument("--strict", action="store_true", help="警告(WARN)もエラーとして扱う")
    args = ap.parse_args()

    rep, stats = Report(), {}
    if args.gate == "graveyard":
        where = "core/red-team/graveyard"
        check_graveyard(rep, stats)
    else:
        vault = Path(args.output)
        if not vault.is_dir() and not vault.is_absolute():
            vault = ROOT / vault
        if not vault.is_dir():
            print(f"[verify] {vault} がありません。先に bash scripts/init.sh <プロファイル名> を実行してください")
            return 2
        where = args.output
        check_claims(vault, rep, stats)
        if args.gate == "all":
            check_matrix(vault, rep, stats)
            ledger = check_ledger(vault, rep, stats)
            check_proposals(vault, rep, stats, ledger)
            check_links(vault, rep)

    print(f"[verify] gate={args.gate} 対象={where}")
    order = {"ERROR": 0, "WARN": 1}
    for sev, rule, path, msg in sorted(rep.items, key=lambda i: (order[i[0]], i[2], i[1])):
        print(f"{sev:5} {rule} {path}: {msg}  (根拠: {RULES[rule][0]})")
    if stats:
        print("[verify] 集計: " + " / ".join(f"{k} {v}" for k, v in stats.items()))
    errors, warns = rep.count("ERROR"), rep.count("WARN")
    failed = errors > 0 or (args.strict and warns > 0)
    if failed:
        advice = "出典URLを補うこと" if args.gate == "graveyard" else "解消するまで次のフェーズへ進まないこと"
        print(f"[verify] 結果: NG(エラー {errors} / 警告 {warns})。{advice}")
    else:
        print(f"[verify] 結果: OK(エラー 0 / 警告 {warns})")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
