# -*- coding: utf-8 -*-
"""WISS2026 の公式のプログラムのページ（https://www.wiss.org/WISS2026/program.html）から、
data/2026.tsv と、登壇発表の時刻つきの一覧を作る。

2026年11月12日に公式のプログラムが公開された。それまでは、参加者向けの仮プログラムの PDF から
pipeline/parse_wiss2026_pdf.py で表を作っていた。公式のページは、ほかの年と同じく取得し直せるので、こちらを正とする。

使い方: python3 pipeline/parse_wiss2026_html.py [取得したページのファイル] [出力する表のファイル]
ファイルを省くと、wiss.org から取得して raw/wiss2026/program.html に保存してから読む。
発表の時刻は、セッションの時間を発表の件数で均等に割って求める（ページの記載は「登壇：1件12分（質疑含む）」）。
"""
import csv, datetime as dt, html, os, re, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = "https://www.wiss.org/WISS2026/program.html"
if len(sys.argv) > 1:
    page = open(sys.argv[1], encoding="utf-8").read()
else:
    page = urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": "wiss-talk-stats"}), timeout=60).read().decode("utf-8")
    os.makedirs(os.path.join(ROOT, "raw", "wiss2026"), exist_ok=True)
    open(os.path.join(ROOT, "raw", "wiss2026", "program.html"), "w", encoding="utf-8").write(page)


def text(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()


rows, sched = [], []
for sec in re.findall(r'<section class="program-session[^"]*"[^>]*>(.*?)</section>', page, re.S):
    head = text(re.sub(r"</span>\s*<span", "</span> <span", re.search(r"<h3[^>]*>(.*?)</h3>", sec, re.S).group(1)))
    m = re.search(r'<time datetime="([\d-]+)">([^<]*)</time><span>([\d:]+)–([\d:]+)</span>', sec)
    oral = head.startswith("セッション")
    kind = "登壇（区別なし）" if oral else "国際学会招待発表"
    arts = re.findall(r'<article class="presentation-info"[^>]*>(.*?)</article>', sec, re.S)
    items = []
    for a in arts:
        num = text(re.search(r'class="presentation-number"[^>]*>(.*?)</a>', a, re.S).group(1))
        t = re.search(r'<h4 class="presentation-title"[^>]*>(.*?)</h4>', a, re.S).group(1)
        tags = [text(x) for x in re.findall(r'<span class="presentation-tag[^"]*">(.*?)</span>', t, re.S)]
        title = text(re.sub(r'<span class="presentation-tag[^"]*">.*?</span>', "", t, flags=re.S))
        au = text(re.search(r'<p class="authors">(.*?)</p>', a, re.S).group(1))
        au = re.sub(r"\([^()]*\)", "", au)  # 所属を除く
        names = [n.strip() for n in re.split(r"[，,]", au) if n.strip()]
        names = [re.sub(r"\s+", "", n) if re.search(r"[぀-ヿ㐀-鿿]", n) else re.sub(r"\s+", " ", n) for n in names]
        items.append((num, title, names, tags))
        rows.append([2026, kind, title, ";".join(names), names[0]])
    if oral and m:
        sched.append((head, m.group(1), m.group(2), m.group(3), m.group(4), items))

out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "data", "2026.tsv")
with open(out, "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh, delimiter="\t", lineterminator="\n")
    w.writerow(["year", "kind", "title", "authors", "first_author"])
    w.writerows(rows)

lines = []
for head, date, label, st, en, items in sched:
    lines.append(f"■ {label} {st}–{en} {head}")
    t0, t1 = dt.datetime.strptime(st, "%H:%M"), dt.datetime.strptime(en, "%H:%M")
    d = (t1 - t0) / len(items)
    for k, (num, title, names, tags) in enumerate(items):
        b, e = t0 + d * k, t0 + d * (k + 1)
        tag = f"　［{'・'.join(tags)}］" if tags else ""
        lines.append(f"{num} {b:%H:%M}–{e:%H:%M} {title}{tag}\n    {'、'.join(names)}")
    lines.append("")
open(os.path.join(ROOT, "raw", "wiss2026", "wiss2026_oral_schedule.txt"), "w", encoding="utf-8").write("\n".join(lines))
print(f"{len(rows)} 件を書いた（登壇発表 {sum(r[1].startswith('登壇') for r in rows)} 件）")
