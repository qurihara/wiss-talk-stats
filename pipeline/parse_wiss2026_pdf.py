# -*- coding: utf-8 -*-
"""WISS2026 のプログラム（登壇発表と国際学会招待発表）の PDF から、data/2026.tsv を作る。

WISS2026 のプログラムは、2026年11月5日の時点で wiss.org の公開の場所からは辿れなかったので、
栗原が参加者として受け取ったプログラムのページを PDF にしたものを入力にした。
PDF は論文の概要を含むので、リポジトリには入れていない（raw/wiss2026/wiss2026_program.pdf に置いて使う）。

PDF の日本語は、この PDF の書体の都合で pdftotext では取り出せないので、macOS の PDFKit で取り出す。
PDFKit の出力は、文字の間に余計な空白が入り、行の途中で改行されるので、それを直してから題名と著者に分ける。

使い方（macOS）: python3 pipeline/parse_wiss2026_pdf.py
"""
import csv, os, re, subprocess, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(ROOT, "raw", "wiss2026", "wiss2026_program.pdf")
TXT = os.path.join(ROOT, "raw", "wiss2026", "wiss2026_program_pdfkit.txt")

SWIFT = r'''
import PDFKit
let doc = PDFDocument(url: URL(fileURLWithPath: CommandLine.arguments[1]))!
for i in 0..<doc.pageCount { print("=====PAGE \(i+1)"); print(doc.page(at: i)?.string ?? "") }
'''
if not os.path.exists(TXT):
    with tempfile.NamedTemporaryFile("w", suffix=".swift", delete=False) as f:
        f.write(SWIFT); sw = f.name
    open(TXT, "w", encoding="utf-8").write(subprocess.run(["swift", sw, PDF], capture_output=True, text=True, check=True).stdout)

CJK = r"　-ヿ㐀-鿿＀-￯"


def tidy(s):
    """PDFKit が入れた余計な空白を除く。日本語の文字に接する空白を消し、英字の空白は1つにそろえる。"""
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(rf"(?<=[{CJK}]) (?=[{CJK}])", "", s)
    s = re.sub(rf"(?<=[{CJK}]) (?=[A-Za-z0-9(])", "", s)
    s = re.sub(rf"(?<=[A-Za-z0-9)]) (?=[{CJK}])", "", s)
    s = re.sub(r"T ([a-z])", r"T\1", s)  # 「T asteFlow」「DuoT ouch」のような、T の直後の空白
    return s


lines = open(TXT, encoding="utf-8").read().split("\n")
noise = re.compile(r"^(=====PAGE|WISS 2026 著者の方へ|国際学会 ・ 国際論文誌|名$|INT 国際学会招待発表|座長|-- チャ|--$)")
starts = [i for i, l in enumerate(lines) if re.match(r"^\d{3}(?![\d.])", l) and not re.match(r"^\d{3}\s*本", l)]  # 「2026 (UIST2026)」や「108本」を除く
# PDFKit が第一著者の名前の途中で改行した発表。名前の前半が、著者の行の何行前から始まるかを書く（2026年11月5日に目で確かめた）
NAME_STARTS_EARLIER = {"005": 1, "013": 2, "042": 1}
rows = []
for i in starts:
    num = lines[i][:3]
    blk, j = [], i
    while j < len(lines) and not lines[j].startswith("要旨"):
        if not noise.match(lines[j].strip()):
            blk.append(lines[j])
        j += 1
    blk[0] = blk[0][3:]
    # 著者の行の始まり：「名前 (所属)」の形を最初に含む行
    k = next(n for n, l in enumerate(blk) if re.search(r"\S \(", l) and n > 0 or (n == 0 and re.search(r"\S \([^)]*\)\s*[，,]", l)))
    k -= NAME_STARTS_EARLIER.get(num, 0)
    title = tidy(" ".join(blk[:k]))
    title = re.sub(r"\s*★?\s*（WISS Challenge\)", "", title).replace("★", "").strip()
    au = " ".join(blk[k:])
    au = re.sub(r"\([^()]*\)", "", au)  # 所属を除く
    names = [tidy(a) for a in re.split(r"[，,]", au)]
    names = [re.sub(r"\s+", "", a) if re.search(rf"[{CJK}]", a) else a for a in names if a.strip()]
    kind = "登壇（区別なし）" if int(num) <= 35 else "国際学会招待発表"
    rows.append([2026, kind, title, ";".join(names), names[0], num])

out = os.path.join(ROOT, "data", "2026.tsv")
with open(out, "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh, delimiter="\t", lineterminator="\n")
    w.writerow(["year", "kind", "title", "authors", "first_author"])
    for r in rows:
        w.writerow(r[:5])
print(f"{len(rows)} 件を書いた（登壇発表 {sum(r[1].startswith('登壇') for r in rows)} 件）")
for r in rows:
    print(r[5], r[1][:2], r[2][:40], "|", r[3][:80])
