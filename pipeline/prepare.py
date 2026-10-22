# -*- coding: utf-8 -*-
"""手順2：raw/ の元のページから、抜き出しのスクリプトが読む中間のファイルを作る。

- raw/u8/y<年>.html と raw/w9404/*.html.u8 … 文字コードを UTF-8 にそろえた写し（1994–2004年）
- raw/web/*.txt … タグを除いて文字だけにした写し
- raw/prog/prog<年>.txt … 2006–2012年のプログラムの文字だけの写し
- raw/web2/prog_<年>.txt … 2020–2025年のプログラムの文字だけの写し

古いページは文字コードがまちまちなので、ファイルごとに文字コードを決めてある。

使い方: python3 pipeline/prepare.py
"""
import glob, html, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "raw")

# 1994–2004年のプログラムと、デモのページの文字コード
ENC = {1994: "euc_jp", 1995: "euc_jp", 1996: "euc_jp", 1997: "iso2022_jp", 1998: "euc_jp", 1999: "euc_jp",
       2000: "shift_jis", 2001: "shift_jis", 2002: "iso2022_jp", 2003: "iso2022_jp", 2004: "cp932"}
ENC_DEMO = {"WISS99_demo": "euc_jp", "WISS2001_wiss2001demo": "cp932", "WISS2002_Wiss2002demo": "cp932",
            "WISS2003_demoprogram": "cp932", "WISS2004_wiss-challenge": "iso2022_jp"}


def guess_decode(b, encs=("utf-8", "cp932", "euc_jp", "iso2022_jp")):
    for e in encs:
        try:
            return b.decode(e)
        except Exception:
            pass
    return b.decode("utf-8", "replace")


def to_text_web(path):
    """raw/web/*.txt を作る（予稿集の目次やプログラムのページ）"""
    t = guess_decode(open(path, "rb").read())
    t = re.sub(r"<(script|style).*?</\1>", "", t, flags=re.S | re.I)
    t = re.sub(r"<br\s*/?>|</(p|li|tr|div|h\d|dt|dd)>", "\n", t, flags=re.I)
    t = re.sub(r"<[^>]+>", " ", t); t = html.unescape(t)
    t = re.sub(r"[ \t　]+", " ", t); t = re.sub(r"\n\s*\n+", "\n", t)
    return t


def to_text_prog(path):
    """raw/prog/*.txt を作る（2006–2012年のプログラム）"""
    s = guess_decode(open(path, "rb").read(), ("utf-8", "cp932", "euc_jis_2004"))
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"<script.*?</script>", "", s, flags=re.S | re.I)
    s = re.sub(r"<(br|p|li|tr|h\d|div|dt|dd)\b[^>]*>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s); s = html.unescape(s)
    s = re.sub(r"[ \t\r]+", " ", s); s = re.sub(r"\n\s*\n+", "\n", s)
    return s + "\n"


def to_text_lines(path):
    """raw/web2/prog_<年>.txt を作る（2020–2025年のプログラム）"""
    s = open(path, encoding="utf-8").read()
    s = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", "", s)
    s = re.sub(r"(?i)<br\s*/?>", "\n", s)
    s = re.sub(r"(?i)</(p|div|li|h\d|tr|td|th|dt|dd)>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s); s = html.unescape(s)
    return "".join(l.strip() + "\n" for l in s.split("\n") if l.strip())


os.makedirs(os.path.join(RAW, "u8"), exist_ok=True)
for y, enc in ENC.items():
    b = open(os.path.join(RAW, "web", f"y{y}.html"), "rb").read()
    open(os.path.join(RAW, "u8", f"y{y}.html"), "w", encoding="utf-8").write(b.decode(enc, "replace"))
for name, enc in ENC_DEMO.items():
    b = open(os.path.join(RAW, "w9404", f"{name}.html"), "rb").read()
    open(os.path.join(RAW, "w9404", f"{name}.html.u8"), "w", encoding="utf-8").write(b.decode(enc, "replace"))
for p in glob.glob(os.path.join(RAW, "web", "*.html")):
    open(p[:-5] + ".txt", "w", encoding="utf-8").write(to_text_web(p))
for p in glob.glob(os.path.join(RAW, "prog", "prog*.html")):
    open(p[:-5] + ".txt", "w", encoding="utf-8").write(to_text_prog(p))
for p in glob.glob(os.path.join(RAW, "web2", "program_*.html")):
    y = re.search(r"(\d{4})", os.path.basename(p)).group(1)
    open(os.path.join(RAW, "web2", f"prog_{y}.txt"), "w", encoding="utf-8").write(to_text_lines(p))
print("中間のファイルを作った")
