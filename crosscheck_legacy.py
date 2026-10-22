"""昔のデータベース（legacy/wiss_stats2.xlsx の SpaceAndBracketErased シート。Access の本体と同じ410件）と、
今回ウェブから作った data/<年>.tsv の登壇発表を、題名で対応づけて第一著者を照合する。"""
import csv, os, re, sys, unicodedata, difflib, openpyxl, collections
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "data")
def key(t): return re.sub(r"[\s\W_]", "", unicodedata.normalize("NFKC", t or "")).lower()
def nm(n): return re.sub(r"\s", "", unicodedata.normalize("NFKC", n or ""))
wb = openpyxl.load_workbook(os.path.join(HERE, "legacy", "wiss_stats2.xlsx"), read_only=True)
leg = collections.defaultdict(list)
for r in wb["SpaceAndBracketErased"].iter_rows(values_only=True):
    leg[int(r[0])].append((r[1], r[2]))
for y in sorted(leg):
    f = os.path.join(DATA, f"{y}.tsv")
    rows = [r for r in csv.DictReader(open(f, encoding="utf-8"), delimiter="\t")]
    talks = [r for r in rows if r["kind"].startswith("登壇")]
    others = [r for r in rows if not r["kind"].startswith("登壇")]
    keys = {key(r["title"]): r for r in others}
    keys.update({key(r["title"]): r for r in talks})  # 同じ題名なら登壇発表を優先する
    tkeys = {key(r["title"]): r for r in talks}
    unmatched = []; diff = []
    for t, a in leg[y]:
        k = key(t)
        tm = difflib.get_close_matches(k, list(tkeys), 1, 0.6)
        m = tkeys.get(k) or (tkeys[tm[0]] if tm else None) or keys.get(k) or (keys[difflib.get_close_matches(k, list(keys), 1, 0.6)[0]] if difflib.get_close_matches(k, list(keys), 1, 0.6) else None)
        if not m: unmatched.append(t); continue
        if not m["kind"].startswith("登壇"): diff.append(("区分", t, m["kind"]))
        if nm(m["first_author"]) != nm(a): diff.append(("第一著者", t[:30], f"web={m['first_author']} legacy={a}"))
    print(f"{y}: legacy={len(leg[y])} web登壇={len(talks)} 対応なし={len(unmatched)} 食い違い={len(diff)}")
    for u in unmatched: print("   対応なし:", u[:40])
    for d in diff: print("   ", d)
