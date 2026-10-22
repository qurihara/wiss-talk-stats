# -*- coding: utf-8 -*-
"""README に載せる図と数値を data/<年>.tsv から作り直す。

使い方: python3 make_figures.py
出力: figs/<名前>_light.png と figs/<名前>_dark.png、figs/stats.json
年の範囲は data/ にある年から決まるので、data/2026.tsv を足せば2026年までの図になる。
"""
import csv, glob, json, os, collections
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from rank import norm, COUNTED

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "figs")
os.makedirs(FIGS, exist_ok=True)

for f in ("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc", "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"):
    if os.path.exists(f):
        font_manager.fontManager.addfont(f)
plt.rcParams["font.family"] = ["Hiragino Sans", "Hiragino Kaku Gothic Pro", "sans-serif"]

# 既定の配色（dataviz スキルの reference palette の1番目と2番目）
THEMES = {
    "light": dict(surface="#fcfcfb", text="#0b0b0b", text2="#52514e", grid="#e4e3df",
                  s1="#2a78d6", s2="#eb6834", muted="#b9b8b2"),
    "dark": dict(surface="#1a1a19", text="#f0efec", text2="#c3c2b7", grid="#34332f",
                 s1="#3987e5", s2="#d95926", muted="#5b5a55"),
}

# ---- データを読む ----
talks, demos = [], collections.Counter()
for f in sorted(glob.glob(os.path.join(HERE, "data", "*.tsv"))):
    for r in csv.DictReader(open(f, encoding="utf-8"), delimiter="\t"):
        y = int(r["year"])
        if r["kind"] in COUNTED:
            talks.append((y, norm(r["first_author"])))
        elif r["kind"] in ("デモ", "ポスター"):
            demos[y] += 1
years = sorted({y for y, _ in talks})
Y0, Y1 = years[0], years[-1]
per_year = collections.Counter(y for y, _ in talks)
unknown = [(y, a) for y, a in talks if a in ("", "（不明）")]
known = [(y, a) for y, a in talks if a not in ("", "（不明）")]
cnt = collections.Counter(a for _, a in known)
years_of = collections.defaultdict(list)
for y, a in known:
    years_of[a].append(y)
dist = collections.Counter(cnt.values())

# 各年の登壇発表のうち、その第一著者にとって初めての登壇であるものの割合
seen, first_share = set(), {}
for y in years:
    ys = [a for yy, a in known if yy == y]
    new = sum(1 for a in ys if a not in seen)
    first_share[y] = new / len(ys) if ys else None
    seen.update(ys)

ranked = sorted(cnt.items(), key=lambda kv: (-kv[1], min(years_of[kv[0]])))
stats = {
    "years": [Y0, Y1], "talks": len(talks), "talks_known": len(known), "talks_unknown": len(unknown),
    "authors": len(cnt), "dist": {str(k): dist[k] for k in sorted(dist)},
    "once": dist[1], "once_share": round(dist[1] / len(cnt), 3),
    "talks_by_repeaters_share": round(sum(c for c in cnt.values() if c >= 2) / len(known), 3),
    "top": [[a, c, min(years_of[a]), max(years_of[a])] for a, c in ranked if c >= 4],
    "per_year": {str(y): per_year[y] for y in years},
    "first_share_mean": round(sum(v for v in first_share.values() if v is not None) / len(years), 3),
    "first_share": {str(y): round(v, 3) for y, v in first_share.items() if v is not None and y != Y0},
    "demos": {str(y): demos[y] for y in sorted(demos)},
}
json.dump(stats, open(os.path.join(FIGS, "stats.json"), "w"), ensure_ascii=False, indent=1)


def frame(ax, t):
    ax.set_facecolor(t["surface"])
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(t["grid"])
    ax.tick_params(which="both", colors=t["text2"], labelsize=9, length=0)
    ax.grid(axis="y", color=t["grid"], linewidth=0.8)
    ax.set_axisbelow(True)


def save(fig, name, mode, t):
    fig.patch.set_facecolor(t["surface"])
    fig.savefig(os.path.join(FIGS, f"{name}_{mode}.png"), dpi=200, facecolor=t["surface"], bbox_inches="tight")
    plt.close(fig)


def title(fig, t, main, sub, ax=None):
    # 題と副題を、描画領域の上端から一定の距離（ポイント単位）に置く。左端は図の左端にそろえる。
    ax = ax or fig.axes[0]
    from matplotlib.transforms import blended_transform_factory, offset_copy
    base = blended_transform_factory(fig.transFigure, ax.transAxes)
    fig.text(0.0, 1.0, main, color=t["text"], fontsize=13, fontweight="bold", ha="left", va="bottom",
             transform=offset_copy(base, fig=fig, y=26, units="points"))
    fig.text(0.0, 1.0, sub, color=t["text2"], fontsize=9, ha="left", va="bottom",
             transform=offset_copy(base, fig=fig, y=10, units="points"))


for mode, t in THEMES.items():
    # 1. 登壇回数の多い第一著者（5回以上）
    top = [(a, c) for a, c in ranked if c >= 5][::-1]
    fig, ax = plt.subplots(figsize=(7.2, 0.32 * len(top) + 0.9))
    frame(ax, t); ax.grid(axis="y", visible=False); ax.grid(axis="x", color=t["grid"], linewidth=0.8)
    ax.barh(range(len(top)), [c for _, c in top], height=0.62, color=t["s1"])
    for i, (a, c) in enumerate(top):
        ax.text(c + 0.15, i, f"{c}", va="center", ha="left", color=t["text"], fontsize=9)
    ax.set_yticks(range(len(top))); ax.set_yticklabels([a for a, _ in top], color=t["text"], fontsize=9.5)
    ax.set_xlim(0, max(c for _, c in top) + 1.2); ax.set_xlabel("登壇発表の回数（第一著者として）", color=t["text2"], fontsize=9)
    title(fig, t, "登壇回数の多い第一著者", f"WISS {Y0}–{Y1}、5回以上の{len(top)}人")
    save(fig, "ranking", mode, t)

    # 2. 回数ごとの人数（縦軸は対数）
    ks = list(range(1, max(dist) + 1))
    fig, ax = plt.subplots(figsize=(7.2, 3.3))
    frame(ax, t)
    ax.bar(ks, [dist[k] for k in ks], width=0.7, color=t["s1"])
    ax.set_yscale("log"); ax.set_ylim(0.7, dist[1] * 2.2)
    for k in ks:
        if dist[k]:
            ax.text(k, dist[k] * 1.12, f"{dist[k]}", ha="center", va="bottom", color=t["text"], fontsize=9)
    ax.set_xticks(ks); ax.set_xlabel("登壇発表の回数（第一著者として）", color=t["text2"], fontsize=9)
    ax.set_ylabel("人数（対数目盛）", color=t["text2"], fontsize=9)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
    title(fig, t, "登壇回数ごとの第一著者の人数", f"WISS {Y0}–{Y1}、第一著者{len(cnt)}人のうち{dist[1]}人（{dist[1]/len(cnt):.0%}）が1回")
    save(fig, "distribution", mode, t)

    # 3. 年ごとの登壇発表とデモ・ポスターの件数
    fig, ax = plt.subplots(figsize=(7.6, 3.4))
    frame(ax, t)
    xs = list(range(Y0, Y1 + 1))
    ax.plot(xs, [demos.get(y, None) or float("nan") for y in xs], color=t["s2"], linewidth=2, marker="o", markersize=4, label="デモ・ポスター")
    ax.plot(xs, [per_year.get(y, 0) for y in xs], color=t["s1"], linewidth=2, marker="o", markersize=4, label="登壇発表")
    ax.text(Y1 + 0.4, per_year[Y1], "登壇発表", color=t["text"], fontsize=9, va="center")
    ax.text(Y1 + 0.4, demos[Y1], "デモ・ポスター", color=t["text"], fontsize=9, va="center")
    ax.legend(loc="upper left", frameon=False, fontsize=9, labelcolor=t["text"])
    ax.set_xlim(Y0 - 0.5, Y1 + 4.5); ax.set_ylim(0, None)
    ax.set_ylabel("件数", color=t["text2"], fontsize=9)
    title(fig, t, "年ごとの発表件数", "デモ・ポスターは、予稿集かプログラムに一覧が残っている年だけを示す")
    save(fig, "per_year", mode, t)

    # 4. 初めて第一著者として登壇する人の割合
    fig, ax = plt.subplots(figsize=(7.6, 3.0))
    frame(ax, t)
    ys = [y for y in years if y != Y0]
    ax.plot(ys, [first_share[y] * 100 for y in ys], color=t["s1"], linewidth=2, marker="o", markersize=4)
    ax.set_ylim(0, 100); ax.set_ylabel("割合（%）", color=t["text2"], fontsize=9)
    ax.set_xlim(Y0, Y1 + 0.5)
    title(fig, t, "初登壇の第一著者による発表の割合", f"各年の登壇発表のうち、第一著者がWISSで初めて登壇するもの（{Y0}年は全員が初登壇なので除く）")
    save(fig, "first_timers", mode, t)

    # 5. 登壇回数の多い第一著者の登壇年（6回以上）
    tl = [(a, sorted(years_of[a])) for a, c in ranked if c >= 6]
    fig, ax = plt.subplots(figsize=(7.6, 0.36 * len(tl) + 1.0))
    frame(ax, t); ax.grid(axis="y", visible=False); ax.grid(axis="x", color=t["grid"], linewidth=0.8)
    for i, (a, ys_) in enumerate(tl[::-1]):
        c = collections.Counter(ys_)
        ax.plot([min(ys_), max(ys_)], [i, i], color=t["muted"], linewidth=1, zorder=1)
        ax.scatter(list(c), [i] * len(c), s=[30 + 45 * (n - 1) for n in c.values()], color=t["s1"],
                   edgecolors=t["surface"], linewidths=1.5, zorder=2)
    ax.set_yticks(range(len(tl))); ax.set_yticklabels([a for a, _ in tl[::-1]], color=t["text"], fontsize=9.5)
    ax.set_xlim(Y0 - 1, Y1 + 1)
    title(fig, t, "登壇回数の多い第一著者が登壇した年", "6回以上の人。大きい点は同じ年に複数件")
    save(fig, "timeline", mode, t)

print(json.dumps({k: stats[k] for k in ("years", "talks", "talks_known", "talks_unknown", "authors", "once", "once_share", "talks_by_repeaters_share", "first_share_mean")}, ensure_ascii=False))


# ================= 著者全員の分析 =================
# 1994年以降は著者全員、1993年は分かっている第一著者だけを数える（1993年は共著者が分からない）。
papers = []  # (年, [著者...])
for f in sorted(glob.glob(os.path.join(HERE, "data", "*.tsv"))):
    for r in csv.DictReader(open(f, encoding="utf-8"), delimiter="\t"):
        if r["kind"] not in COUNTED:
            continue
        y = int(r["year"])
        if y == 1993:
            fa = norm(r["first_author"])
            if fa and fa != "（不明）":
                papers.append((y, [fa]))
            continue
        al = [norm(a) for a in r["authors"].split(";") if a.strip()]
        papers.append((y, al))
anyc, firstc, lastc = collections.Counter(), collections.Counter(), collections.Counter()
yrs = collections.defaultdict(set)
pairs = collections.Counter()
for y, al in papers:
    for a in dict.fromkeys(al):  # 重複を除き、並び順は保つ（集合は実行ごとに順が変わる）
        anyc[a] += 1; yrs[a].add(y)
    firstc[al[0]] += 1
    if len(al) >= 2 and y != 1993:
        lastc[al[-1]] += 1
    u = sorted(set(al))
    for i in range(len(u)):
        for j in range(i + 1, len(u)):
            pairs[(u[i], u[j])] += 1
mean_authors = {}
for y in years:
    if y == Y0:
        continue
    ns = [len(al) for yy, al in papers if yy == y]
    mean_authors[y] = sum(ns) / len(ns)
rank_any = sorted(anyc.items(), key=lambda kv: (-kv[1], -firstc[kv[0]], min(yrs[kv[0]])))
with open(os.path.join(HERE, "ranking_authors.tsv"), "w", encoding="utf-8") as out:
    out.write("著者\t著者として関わった登壇発表の数\t第一著者の回数\t最終著者の回数\t最初の年\t最後の年\n")
    for a, c in rank_any:
        out.write(f"{a}\t{c}\t{firstc[a]}\t{lastc[a]}\t{min(yrs[a])}\t{max(yrs[a])}\n")
stats["authors_all"] = {
    "people": len(anyc), "appearances": sum(len(set(al)) for _, al in papers if _ != 1993),
    "top_any": [[a, c, firstc[a], lastc[a], min(yrs[a]), max(yrs[a])] for a, c in rank_any[:30]],
    "top_last": [[a, c, anyc[a]] for a, c in lastc.most_common(15)],
    "top_pairs": [[a, b, c] for (a, b), c in pairs.most_common(15)],
    "mean_authors": {str(y): round(v, 2) for y, v in mean_authors.items()},
}
json.dump(stats, open(os.path.join(FIGS, "stats.json"), "w"), ensure_ascii=False, indent=1)

for mode, t in THEMES.items():
    # 6. 著者として関わった登壇発表の数（上位20人）。第一著者とそれ以外に分ける
    top = rank_any[:20][::-1]
    fig, ax = plt.subplots(figsize=(7.4, 0.32 * len(top) + 1.1))
    frame(ax, t); ax.grid(axis="y", visible=False); ax.grid(axis="x", color=t["grid"], linewidth=0.8)
    f_ = [firstc[a] for a, _ in top]; o_ = [c - firstc[a] for a, c in top]
    ax.barh(range(len(top)), f_, height=0.62, color=t["s1"], label="第一著者として", edgecolor=t["surface"], linewidth=1)
    ax.barh(range(len(top)), o_, left=f_, height=0.62, color=t["s2"], label="共著者として", edgecolor=t["surface"], linewidth=1)
    for i, (a, c) in enumerate(top):
        ax.text(c + 0.6, i, f"{c}", va="center", ha="left", color=t["text"], fontsize=9)
    ax.set_yticks(range(len(top))); ax.set_yticklabels([a for a, _ in top], color=t["text"], fontsize=9.5)
    ax.set_xlim(0, top[-1][1] * 1.1)
    ax.set_xlabel("著者として関わった登壇発表の数", color=t["text2"], fontsize=9)
    ax.legend(loc="lower right", frameon=False, fontsize=9, labelcolor=t["text"])
    title(fig, t, "著者として関わった登壇発表の多い人", f"WISS {Y0}–{Y1}、上位20人。1993年は第一著者だけを数えた")
    save(fig, "authors_any", mode, t)

    # 7. 1件あたりの著者の数の推移
    fig, ax = plt.subplots(figsize=(7.6, 3.0))
    frame(ax, t)
    xs = sorted(mean_authors)
    ax.plot(xs, [mean_authors[y] for y in xs], color=t["s1"], linewidth=2, marker="o", markersize=4)
    ax.set_ylim(0, 5); ax.set_ylabel("人", color=t["text2"], fontsize=9); ax.set_xlim(xs[0] - 0.5, xs[-1] + 0.5)
    title(fig, t, "登壇発表1件あたりの著者の数", f"WISS {xs[0]}–{xs[-1]} の各年の平均（1993年は著者が分からないので除く）")
    save(fig, "mean_authors", mode, t)

print(json.dumps({k: stats["authors_all"][k] for k in ("people", "appearances", "top_last", "top_pairs")}, ensure_ascii=False))


# ================= 発表速度 =================
# デビュー年 = 第一著者として初めて登壇した年。経過年数 = 集計の最後の年 - デビュー年 + 1（デビュー年を1年目と数える）。
# 発表速度 = 第一著者としての登壇回数 / 経過年数。
# 経過年数が短い人ほど、少ない回数でも値が大きく振れる。そこで、登壇回数がポアソン分布に従うと考え、
# 発表速度の95%信頼区間（Garwood の正確な区間）の下限で並べる。年数が短いほど区間が広がり、下限が下がる。
# 補助として、デビューから10年間の登壇回数も数える（デビュー年が集計の最後の年の9年前までの人に限る）。
from poisson_ci import ci
WINDOW = 10
speed = []
for a, c in cnt.items():
    d = min(years_of[a]); el = Y1 - d + 1
    lo, hi = ci(c)
    w = sum(1 for y in years_of[a] if y < d + WINDOW) if d <= Y1 - WINDOW + 1 else None
    speed.append(dict(name=a, n=c, debut=d, years=el, rate=c / el, lower=lo / el, upper=hi / el, window=w))
speed.sort(key=lambda x: (-x["lower"], -x["n"], x["debut"]))
with open(os.path.join(HERE, "ranking_speed.tsv"), "w", encoding="utf-8") as out:
    out.write("順位\t第一著者\t発表速度の95%信頼区間の下限（回/年）\t発表速度（回/年）\t発表速度の95%信頼区間の上限（回/年）\t登壇回数\tデビュー年\t経過年数\tデビューから10年間の登壇回数\n")
    prev, rk = None, 0
    for i, x in enumerate(speed, 1):
        if round(x["lower"], 9) != prev:
            rk, prev = i, round(x["lower"], 9)
        x["rank"] = rk
        out.write(f"{rk}\t{x['name']}\t{x['lower']:.3f}\t{x['rate']:.3f}\t{x['upper']:.3f}\t{x['n']}\t{x['debut']}\t{x['years']}\t{'' if x['window'] is None else x['window']}\n")
win = sorted([x for x in speed if x["window"] is not None], key=lambda x: (-x["window"], x["debut"]))
prev, rk = None, 0
for i, x in enumerate(win, 1):
    if x["window"] != prev:
        rk, prev = i, x["window"]
    x["wrank"] = rk
stats["speed"] = {
    "end_year": Y1, "people": len(speed),
    "top": [[x["rank"], x["name"], round(x["lower"], 3), round(x["rate"], 3), round(x["upper"], 3), x["n"], x["debut"], x["years"]] for x in speed[:20]],
    "window": WINDOW, "window_people": len(win), "window_last_debut": Y1 - WINDOW + 1,
    "window_top": [[x["wrank"], x["name"], x["window"], x["debut"], x["n"]] for x in win if x["window"] >= 4],
}
json.dump(stats, open(os.path.join(FIGS, "stats.json"), "w"), ensure_ascii=False, indent=1)

for mode, t in THEMES.items():
    # 8. 発表速度の下限の上位20人（点は発表速度、線は95%信頼区間）
    top = speed[:20][::-1]
    fig, ax = plt.subplots(figsize=(7.6, 0.34 * len(top) + 1.2))
    frame(ax, t); ax.grid(axis="y", visible=False); ax.grid(axis="x", color=t["grid"], linewidth=0.8)
    for i, x in enumerate(top):
        ax.plot([x["lower"], min(x["upper"], 1.6)], [i, i], color=t["muted"], linewidth=2, solid_capstyle="round", zorder=1)
        ax.scatter([x["lower"]], [i], s=46, color=t["s1"], edgecolors=t["surface"], linewidths=1.5, zorder=3, marker="D")
        ax.scatter([x["rate"]], [i], s=30, color=t["s2"], edgecolors=t["surface"], linewidths=1.2, zorder=3)
        ax.text(1.62, i, f"{x['lower']:.2f}（{x['n']}回／{x['years']}年）", va="center", ha="left", color=t["text"], fontsize=8.5)
    ax.set_yticks(range(len(top))); ax.set_yticklabels([x["name"] for x in top], color=t["text"], fontsize=9.5)
    ax.set_xlim(0, 2.25); ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5])
    ax.scatter([], [], s=46, color=t["s1"], marker="D", label="95%信頼区間の下限（順位の基準）")
    ax.scatter([], [], s=30, color=t["s2"], label="発表速度（回数÷年数）")
    ax.plot([], [], color=t["muted"], linewidth=2, label="95%信頼区間（1.6以上は省略）")
    ax.set_xlabel("回/年", color=t["text2"], fontsize=9)
    ax.legend(loc="upper center", bbox_to_anchor=(0.45, -0.09), ncol=3, frameon=False, fontsize=8.5, labelcolor=t["text"])
    title(fig, t, "発表速度の下限で並べた第一著者", f"WISS {Y0}–{Y1}、上位20人。経過年数はデビュー年から{Y1}年まで。右の数字は下限（登壇回数／経過年数）")
    save(fig, "speed", mode, t)

    # 9. デビュー年と発表速度：割り算の値と、下限の比較（2回以上の人）
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.9), sharey=True)
    sub = [x for x in speed if x["n"] >= 2]
    for ax, key, lab in ((axes[0], "rate", "発表速度（回数÷年数）"), (axes[1], "lower", "95%信頼区間の下限")):
        frame(ax, t); ax.grid(axis="x", color=t["grid"], linewidth=0.8)
        ax.scatter([x["debut"] for x in sub], [x[key] for x in sub], s=[14 * x["n"] for x in sub], color=t["s1"],
                   alpha=0.8, edgecolors=t["surface"], linewidths=1, zorder=3)
        ax.set_xlim(Y0 - 1, Y1 + 1); ax.set_ylim(0, 1.05)
        ax.set_xlabel("デビュー年", color=t["text2"], fontsize=9)
        ax.text(0.02, 0.97, lab, transform=ax.transAxes, color=t["text"], fontsize=9.5, va="top")
    axes[0].set_ylabel("回/年", color=t["text2"], fontsize=9)
    title(fig, t, "デビュー年と発表速度", f"登壇2回以上の{len(sub)}人。点の大きさは登壇回数。左の割り算の値では最近のデビューほど高く出るが、右の下限ではその偏りが小さくなる", ax=axes[0])
    save(fig, "speed_debut", mode, t)

    # 10. デビューから10年間の登壇回数（上位）
    wt = [x for x in win if x["window"] >= 4][::-1]
    fig, ax = plt.subplots(figsize=(7.2, 0.32 * len(wt) + 1.1))
    frame(ax, t); ax.grid(axis="y", visible=False); ax.grid(axis="x", color=t["grid"], linewidth=0.8)
    ax.barh(range(len(wt)), [x["window"] for x in wt], height=0.62, color=t["s1"])
    for i, x in enumerate(wt):
        ax.text(x["window"] + 0.12, i, f"{x['window']}（{x['debut']}年デビュー）", va="center", ha="left", color=t["text"], fontsize=8.5)
    ax.set_yticks(range(len(wt))); ax.set_yticklabels([x["name"] for x in wt], color=t["text"], fontsize=9.5)
    ax.set_xlim(0, max(x["window"] for x in wt) + 3.2)
    ax.set_xlabel(f"デビュー年から{WINDOW}年間の登壇回数（第一著者として）", color=t["text2"], fontsize=9)
    title(fig, t, f"デビューから{WINDOW}年間の登壇回数", f"{Y1 - WINDOW + 1}年までにデビューした{len(win)}人のうち、4回以上の人")
    save(fig, "speed_window", mode, t)
print("発表速度", [(x["rank"], x["name"], round(x["lower"], 3), x["n"], x["years"]) for x in speed[:12]])
print("10年間", [(x["wrank"], x["name"], x["window"], x["debut"]) for x in win[:15]])
