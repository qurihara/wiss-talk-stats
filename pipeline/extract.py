# -*- coding: utf-8 -*-
"""手順3と4：年代ごとの抜き出しのスクリプトを動かして年ごとの表を作り、data/ と照合する。

抜き出しのスクリプト（extraction/）は、作業したときのまま「WORK」という名前のフォルダを読み書きする。
ここでは build/WORK を組み立て、raw/ の各フォルダをそこへつなげてから動かす。
できた表は build/WORK/out/<年>.tsv に出る。1997年は昔のデータベースで姓名を補い、1993年は書籍の目次から作る。
最後に、公開している data/<年>.tsv と1件ずつ照合し、違いを表示する。

使い方: python3 pipeline/fetch_raw.py; python3 pipeline/prepare.py; python3 pipeline/extract.py
"""
import csv, filecmp, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
W = os.path.join(BUILD, "WORK")
shutil.rmtree(BUILD, ignore_errors=True)
os.makedirs(os.path.join(W, "out")); os.makedirs(os.path.join(W, "debug2020s"))
for d in ("web", "u8", "w9404", "web2", "prog"):
    os.symlink(os.path.join(ROOT, "raw", d), os.path.join(W, d))
os.symlink(os.path.join(ROOT, "extraction", "2005-2012"), os.path.join(W, "wiss_script"))
os.symlink(os.path.join(ROOT, "extraction", "2013-2019"), os.path.join(W, "scripts_1319"))

def run(script, *args):
    r = subprocess.run([sys.executable, os.path.join(ROOT, "extraction", script), *args], cwd=BUILD, capture_output=True, text=True)
    print(f"{script}: 終了コード {r.returncode}")
    if r.returncode:
        print(r.stderr[-2000:]); sys.exit(1)

run("1994-2004/build9404.py")
run("2005-2012/build.py")
run("2013-2019/build.py", *[str(y) for y in range(2013, 2020)])  # 作る年を引数で渡す
run("2020-2025/build.py")
OUT = os.path.join(W, "out")

# 1997年：昔のデータベースの姓名で補う
shutil.copy(os.path.join(OUT, "1997.tsv"), os.path.join(OUT, "1997_web.tsv"))
subprocess.run([sys.executable, os.path.join(ROOT, "fix1997_from_legacy.py"), os.path.join(OUT, "1997_web.tsv"), os.path.join(OUT, "1997.tsv")], check=True)
os.remove(os.path.join(OUT, "1997_web.tsv"))

# 1993年：書籍の目次（題名だけ）から表の骨組みを作り、fill1993.py で第一著者と根拠を書き込む
txt = open(os.path.join(ROOT, "raw", "web", "k1993.txt"), encoding="utf-8").read()
titles = [l.strip().lstrip("*").strip() for l in txt.split("\n") if l.strip().startswith("*") or l.strip() == "並列論理型言語GHCのビジュアル化の試み"]
with open(os.path.join(OUT, "1993.tsv"), "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh, delimiter="\t", lineterminator="\n")
    w.writerow(["year", "kind", "title", "authors", "first_author"])
    for t in titles:
        w.writerow([1993, "登壇（区別なし）", t, "", "（不明）"])
subprocess.run([sys.executable, os.path.join(ROOT, "fill1993.py"), os.path.join(OUT, "1993.tsv")], check=True)

# data/ と照合する
same, diff = [], []
for f in sorted(os.listdir(os.path.join(ROOT, "data"))):
    a, b = os.path.join(ROOT, "data", f), os.path.join(OUT, f)
    (same if os.path.exists(b) and filecmp.cmp(a, b, shallow=False) else diff).append(f)
print(f"data/ と一致した年 {len(same)} 件、違う年 {len(diff)} 件", diff)
for f in diff:
    b = os.path.join(OUT, f)
    if not os.path.exists(b):
        print("  作られなかった:", f); continue
    A = open(os.path.join(ROOT, "data", f), encoding="utf-8").read().splitlines()
    B = open(b, encoding="utf-8").read().splitlines()
    print(f"  {f}: data/ {len(A)} 行、作り直し {len(B)} 行、違う行 {len(set(A) ^ set(B))} 行")
sys.exit(0 if not diff else 2)
