"""WISS の登壇発表の第一著者の回数を数え、順位表を作る。

入力: data/<年>.tsv（year, kind, title, authors, first_author のタブ区切り）
出力: ranking_all.tsv（全員の回数）と、標準出力への上位の一覧
使い方: python3 rank.py [上位の人数]
"""
import csv, glob, os, re, sys, collections, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
COUNTED = {"登壇ロング", "登壇ショート", "登壇（区別なし）"}

# 表記の揺れをそろえる対応表（同一人物と確かめたものだけを書く）
ALIASES = {
    "歴本純一": "暦本純一",
    "髙橋伸": "高橋伸",
    "Jun Rekimoto": "暦本純一",
    "Takeo Igarashi": "五十嵐健夫",
    "森悠紀": "五十嵐悠紀",  # 旧姓。2006年と2007年
    "広津登志夫": "廣津登志夫",  # 字体の違い
}
# 異体字をそろえる（人名の取り違えを生まない範囲に限る）
VARIANTS = str.maketrans({"髙": "高", "﨑": "崎", "德": "徳", "濵": "濱", "塚": "塚"})


def norm(name: str) -> str:
    n = unicodedata.normalize("NFKC", name or "")
    n = re.sub(r"[（(].*?[)）]", "", n)  # 所属の括弧書き
    n = re.sub(r"[★☆○◯*＊†‡・]", "", n)
    if re.search(r"[A-Za-z]", n) and not re.search(r"[぀-ヿ一-鿿]", n):
        n = re.sub(r"\s+", " ", n).strip()  # 英字の名前は空白を1つに
    else:
        n = re.sub(r"\s+", "", n)  # 日本語の名前は空白を除く
    n = n.translate(VARIANTS)
    return ALIASES.get(n, n)


def load():
    rows = []
    for f in sorted(glob.glob(os.path.join(HERE, "data", "*.tsv"))):
        with open(f, encoding="utf-8") as fh:
            for r in csv.DictReader(fh, delimiter="\t"):
                r["fa"] = norm(r.get("first_author", ""))
                rows.append(r)
    return rows


def main():
    top = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    rows = load()
    talks = [r for r in rows if r["kind"] in COUNTED and r["fa"] and r["fa"] != "（不明）"]
    cnt = collections.Counter(r["fa"] for r in talks)
    years = collections.defaultdict(list)
    for r in talks:
        years[r["fa"]].append(r["year"])
    ranked = sorted(cnt.items(), key=lambda kv: (-kv[1], min(years[kv[0]])))
    with open(os.path.join(HERE, "ranking_all.tsv"), "w", encoding="utf-8") as out:
        out.write("順位\t第一著者\t登壇回数\t最初の年\t最後の年\t年の一覧\n")
        prev, rank = None, 0
        for i, (name, c) in enumerate(ranked, 1):
            if c != prev:
                rank, prev = i, c
            ys = sorted(years[name])
            out.write(f"{rank}\t{name}\t{c}\t{ys[0]}\t{ys[-1]}\t{','.join(ys)}\n")
    print("登壇発表の件数:", len(talks), " 第一著者の人数:", len(cnt))
    prev, rank = None, 0
    for i, (name, c) in enumerate(ranked, 1):
        if c != prev:
            rank, prev = i, c
        if rank > top:
            break
        print(rank, name, c, ",".join(sorted(years[name])))


if __name__ == "__main__":
    main()
