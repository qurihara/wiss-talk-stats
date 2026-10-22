# -*- coding: utf-8 -*-
"""1997年のプログラムは著者が姓だけで書かれているので、昔のデータベース（紙の予稿集で補ったもの）の
姓名で、登壇発表の著者と第一著者を置き換える。題名で対応づける。

昔のデータベースは第4著者までしか持っていない。ウェブの表で5人目以降がいる場合は、
その姓を、同じ年の昔のデータベースに出てくる姓名に引き当てて足す。

入力: raw/web/y1997 から作ったウェブの表（extraction/1994-2004 の出力。data/1997.tsv の元の版）
使い方: python3 fix1997_from_legacy.py <ウェブから作った1997年の表> [出力先。省略すると data/1997.tsv]
"""
import csv, os, re, sys, unicodedata, difflib, openpyxl
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1]
def key(t): return re.sub(r"[\s\W_]", "", unicodedata.normalize("NFKC", t or "")).lower()
def surname(a): return re.sub(r"[（(].*", "", re.sub(r"\s", "", a))
wb = openpyxl.load_workbook(os.path.join(HERE, "legacy", "wiss_stats2.xlsx"), read_only=True)
leg, fullnames = {}, set()
for r in wb["SpaceAndBracketErased"].iter_rows(values_only=True):
    if r[0] == 1997:
        names = [a for a in r[2:] if a]
        leg[key(r[1])] = names
        fullnames.update(names)
def to_full(s):
    c = [n for n in fullnames if n.startswith(s)]
    return c[0] if len(c) == 1 else s
rows = list(csv.DictReader(open(SRC, encoding="utf-8"), delimiter="\t"))
n = 0
for r in rows:
    if not r["kind"].startswith("登壇"): continue
    k = key(r["title"]); m = leg.get(k) or leg.get((difflib.get_close_matches(k, list(leg), 1, 0.6) or [None])[0])
    if not m: continue
    web = [a for a in r["authors"].split(";") if a.strip()]
    extra = [to_full(surname(a)) for a in web[len(m):]] if len(web) > len(m) else []
    r["authors"] = ";".join(m + extra)
    r["first_author"] = m[0]; n += 1
OUTP = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "data", "1997.tsv")
with open(OUTP, "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), delimiter="\t", lineterminator="\n"); w.writeheader(); w.writerows(rows)
print("置き換えた件数:", n)
