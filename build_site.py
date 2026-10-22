# -*- coding: utf-8 -*-
"""GitHub Pages に載せる HTML 版（index.html）とスライド版（slides.html）を、figs/stats.json から作る。

使い方: python3 make_figures.py のあとに python3 build_site.py
文章の中の数値と名前は stats.json から埋め込むので、2026年分を足して作り直せば、そのまま確定版になる。
"""
import html, json, os, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(HERE, "figs", "stats.json"), encoding="utf-8"))
VERSION = open(os.path.join(HERE, "VERSION"), encoding="utf-8").read().strip()
REPO = "https://github.com/qurihara/wiss-talk-stats"
SITE = "https://qurihara.github.io/wiss-talk-stats/"
Y0, Y1 = S["years"]
PROVISIONAL = Y1 < 2026  # 2026年分を足すまでは暫定版
STATUS = "暫定版" if PROVISIONAL else "確定版"

e = html.escape


def names_join(ns):
    return "さんと".join(ns) + "さん" if len(ns) <= 2 else "さん、".join(ns[:-1]) + "さん、" + ns[-1] + "さん"


top = S["top"]
max_n = top[0][1]
leaders = [a for a, c, *_ in top if c == max_n]
aa = S["authors_all"]
sp = S["speed"]
ma = {int(k): v for k, v in aa["mean_authors"].items()}
ma90 = statistics.mean(v for y, v in ma.items() if y < 2000)
ma20 = statistics.mean(v for y, v in ma.items() if y >= 2020)
fs = {int(k): v for k, v in S["first_share"].items()}
fs20 = [v for y, v in fs.items() if y >= 2020]
pyc = list(S["per_year"].values())
repeaters = S["authors"] - S["once"]
any1 = aa["top_any"][0]
any2 = aa["top_any"][1]
pair1 = aa["top_pairs"][0]
sp_top = sp["top"]
win_top = sp["window_top"]


def picture(name, alt, width=None):
    w = f' width="{width}"' if width else ""
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="figs/{name}_dark.png">'
            f'<img src="figs/{name}_light.png" alt="{e(alt)}"{w} loading="lazy"></picture>')


def table(head, rows, num_cols=()):
    th = "".join(f'<th class="{"num" if i in num_cols else ""}">{e(h)}</th>' for i, h in enumerate(head))
    trs = "".join("<tr>" + "".join(f'<td class="{"num" if i in num_cols else ""}">{e(str(c))}</td>' for i, c in enumerate(r)) + "</tr>" for r in rows)
    return f'<div class="tablewrap"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'


# 第一著者の順位（同じ回数は同順位）
first_rows, prev, rk = [], None, 0
for i, (a, c, y0, y1) in enumerate(top, 1):
    if c != prev:
        rk, prev = i, c
    first_rows.append([rk, a, c, y0, y1])

FACTS = [
    ("開催", f"{Y1 - Y0 + 1}回", f"{Y0}年の第1回から{Y1}年の第{Y1 - Y0 + 1}回まで"),
    ("登壇発表", f"{S['talks']}件", f"第一著者が分かっているのは{S['talks_known']}件"),
    ("第一著者", f"{S['authors']}人", f"{S['once']}人（{S['once_share']:.0%}）は1回だけ"),
    ("著者として関わった人", f"{aa['people']}人", f"{Y0}年は第一著者だけを数えた"),
]

CSS = """
:root{--bg:#fcfcfb;--fg:#0b0b0b;--fg2:#52514e;--line:#e4e3df;--accent:#2a78d6;--card:#f4f3f0;color-scheme:light}
@media (prefers-color-scheme: dark){:root{--bg:#1a1a19;--fg:#f0efec;--fg2:#c3c2b7;--line:#34332f;--accent:#3987e5;--card:#242422;color-scheme:dark}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font-family:"Noto Sans JP","Hiragino Sans","Hiragino Kaku Gothic ProN","Yu Gothic",sans-serif;line-height:1.85;font-size:16px}
a{color:var(--accent)}
img{max-width:100%;height:auto;display:block}
"""

PAGE_CSS = CSS + """
.wrap{max-width:860px;margin:0 auto;padding:32px 16px 80px}
header .badge{display:inline-block;font-size:13px;padding:2px 10px;border:1px solid var(--line);border-radius:999px;color:var(--fg2)}
h1{font-size:28px;line-height:1.4;margin:12px 0 8px}
h2{font-size:22px;margin:56px 0 12px;padding-top:12px;border-top:1px solid var(--line)}
h3{font-size:18px;margin:32px 0 8px}
.lead{color:var(--fg2)}
.note{background:var(--card);border-radius:8px;padding:12px 16px;margin:16px 0;font-size:15px}
.facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:24px 0}
.fact{background:var(--card);border-radius:10px;padding:14px 16px}
.fact .k{font-size:13px;color:var(--fg2)}.fact .v{font-size:30px;font-weight:700;line-height:1.3}.fact .s{font-size:13px;color:var(--fg2)}
figure{margin:24px 0}figcaption{font-size:14px;color:var(--fg2);margin-top:6px}
.tablewrap{overflow-x:auto;margin:12px 0}
table{border-collapse:collapse;font-size:14.5px;min-width:100%}
th,td{padding:6px 10px;border-bottom:1px solid var(--line);text-align:left;white-space:nowrap}
th{color:var(--fg2);font-weight:600}.num{text-align:right;font-variant-numeric:tabular-nums}
nav.toc{background:var(--card);border-radius:10px;padding:12px 20px;margin:24px 0;font-size:15px}
nav.toc ol{margin:0;padding-left:20px}
footer{margin-top:64px;font-size:13px;color:var(--fg2);border-top:1px solid var(--line);padding-top:16px}
"""


def intro_text():
    return (f"日本ソフトウェア科学会の「インタラクティブシステムとソフトウェアに関するワークショップ」（WISS）について、"
            f"第1回（{Y0}年）から第{Y1 - Y0 + 1}回（{Y1}年）までの登壇発表を全件集め、第一著者ごとの登壇回数を集計した調査である。")


def build_index():
    toc = [("summary", "調査の結果の概要"), ("first", "第一著者の登壇回数"), ("trend", "年ごとの推移"),
           ("authors", "著者全員で見た分析"), ("speed", "発表速度"), ("history", "経緯"), ("method", "方法"), ("limits", "この調査の限界")]
    body = []
    body.append(f'<header><span class="badge">{STATUS}・版 {e(VERSION)}</span><h1>WISS 登壇発表の第一著者の統計（{Y0}–{Y1}）</h1>'
                f'<p class="lead">{e(intro_text())}</p><p class="lead">調査と集計：栗原一貴（津田塾大学）　｜　<a href="slides.html">スライド版</a>　｜　<a href="{REPO}">データとスクリプト（GitHub）</a></p></header>')
    if PROVISIONAL:
        body.append('<p class="note"><b>暫定版である。</b> WISS2026（第34回）のプログラムが公開されたあとに2026年分を加え、確定版とする予定である。</p>')
    body.append('<nav class="toc"><b>目次</b><ol>' + "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in toc) + "</ol></nav>")

    body.append('<h2 id="summary">調査の結果の概要</h2><div class="facts">' + "".join(
        f'<div class="fact"><div class="k">{e(k)}</div><div class="v">{e(v)}</div><div class="s">{e(s)}</div></div>' for k, v, s in FACTS) + "</div>")
    body.append("<ul>"
                f"<li>第一著者の{S['once_share']:.0%}（{S['once']}人）は、登壇発表が1回だけである。2回以上登壇した{repeaters}人の発表が、全体の{S['talks_by_repeaters_share']:.0%}を占める。</li>"
                f"<li>最も多く登壇したのは、{e(names_join(leaders))}の{max_n}回である。</li>"
                f"<li>各年の登壇発表のうち、第一著者が WISS で初めて登壇する発表の割合は、平均で{S['first_share_mean']:.0%}である。2020年以降は{min(fs20):.0%}から{max(fs20):.0%}である。</li>"
                f"<li>登壇発表は毎年{min(pyc)}件から{max(pyc)}件でほぼ一定である。一方、デモ・ポスター発表は2020年以降に大きく増え、{Y1}年には{S['demos'][str(Y1)]}件になった。</li>"
                f"<li>著者全員で数えると、登壇発表に関わった人は{aa['people']}人である。最も多くの登壇発表に関わったのは{e(any1[0])}さんの{any1[1]}件である。</li>"
                f"<li>登壇回数をデビューからの経過年数で割った「発表速度」を、95%信頼区間の下限で並べると、{e(sp_top[0][1])}さん、{e(sp_top[1][1])}さん、{e(sp_top[2][1])}さんの順になる。</li>"
                "</ul>")

    body.append('<h2 id="first">第一著者の登壇回数</h2>')
    body.append(f'<figure>{picture("ranking", "登壇回数の多い第一著者の横棒グラフ")}</figure>')
    body.append(f'<figure>{picture("distribution", "登壇回数ごとの第一著者の人数の棒グラフ")}<figcaption>縦軸は対数目盛である。1回の人数（{S["once"]}人）と、それ以外の人数の差が大きいためである。</figcaption></figure>')
    body.append(f'<figure>{picture("timeline", "登壇回数の多い第一著者が登壇した年を示す点の図")}</figure>')
    body.append("<h3>登壇回数が4回以上の第一著者</h3>" + table(["順位", "第一著者", "登壇回数", "最初の年", "最後の年"], first_rows, (0, 2, 3, 4))
                + f'<p>同じ回数の人は、最初に登壇した年の順に並べた。全員分の表は <a href="{REPO}/blob/main/ranking_all.tsv">ranking_all.tsv</a> にある。</p>')

    body.append('<h2 id="trend">年ごとの推移</h2>')
    body.append(f'<figure>{picture("per_year", "年ごとの登壇発表とデモ・ポスター発表の件数の折れ線グラフ")}<figcaption>デモ・ポスター発表は、予稿集かプログラムに一覧が残っている分だけを数えた。1993年から1996年は一覧が無い。</figcaption></figure>')
    body.append(f'<figure>{picture("first_timers", "初登壇の第一著者による発表の割合の折れ線グラフ")}</figure>')

    body.append('<h2 id="authors">著者全員で見た分析</h2>')
    body.append(f"<p>第一著者だけでなく、登壇発表の著者として名前を連ねた人を全員数えた。{Y0 + 1}年以降は著者全員を数え、{Y0}年は共著者が分からないので、分かっている第一著者だけを数えた。</p><ul>"
                f"<li>登壇発表に著者として関わった人は {aa['people']}人 である。</li>"
                f"<li>最も多くの登壇発表に関わったのは {e(any1[0])}さんの{any1[1]}件 で、2位の{e(any2[0])}さん（{any2[1]}件）を大きく上回る。{e(any1[0])}さんの{any1[1]}件のうち{any1[3]}件は最終著者である。</li>"
                "<li>第一著者としての回数と、著者として関わった数は、別の人を浮かび上がらせる。第一著者の回数が少なくても、共著者として数十件に関わった人がいる。研究室や研究グループを率いて、学生や若手の研究者の発表を支えてきた人たちと考えられる。</li>"
                f"<li>登壇発表1件あたりの著者の数は、1990年代の平均の約{ma90:.1f}人から、2020年代の平均の約{ma20:.1f}人に増えた。</li></ul>")
    body.append(f'<figure>{picture("authors_any", "著者として関わった登壇発表の多い上位20人の積み上げ横棒グラフ")}</figure>')
    body.append(f'<figure>{picture("mean_authors", "登壇発表1件あたりの著者の数の推移")}</figure>')
    lr, prev, rk = [], None, 0
    for i, (a, c, n) in enumerate(aa["top_last"], 1):
        if c != prev:
            rk, prev = i, c
        lr.append([rk, a, c, n])
    body.append("<h3>最終著者としての回数（上位15人）</h3><p>著者が2人以上の登壇発表で、最後に名前がある回数である。研究室を主宰する人が最後に名前を連ねることが多いので、その目安になる。</p>"
                + table(["順位", "最終著者", "最終著者の回数", "著者として関わった数"], lr, (0, 2, 3)))
    body.append("<h3>共著の多い組（上位15組）</h3>" + table(["組", "回数"], [[f"{a}・{b}", c] for a, b, c in aa["top_pairs"]], (1,))
                + f'<p>全員分の表は <a href="{REPO}/blob/main/ranking_authors.tsv">ranking_authors.tsv</a> にある。</p>')

    body.append('<h2 id="speed">発表速度</h2>')
    body.append("<p>登壇回数の多さは、活動してきた年数の長さにも左右される。そこで、年数あたりの登壇の多さを表す指標として「発表速度」を定めた。</p><ul>"
                "<li><b>デビュー年</b>：第一著者として初めて登壇した年。</li>"
                f"<li><b>経過年数</b>：デビュー年を1年目として、集計の最後の年（{Y1}年）まで数えた年数。</li>"
                "<li><b>発表速度</b>：第一著者としての登壇回数を経過年数で割った値（回/年）。</li></ul>")
    body.append("<h3>発表速度の偏りと、その補正</h3><p>発表速度をそのまま比べると、デビューが最近の人ほど値が高く出る。経過年数が短いと少ない回数でも値が大きく振れること、デビュー年には必ず1回が入っていることが、その原因である。"
                f"そこで、登壇回数がポアソン分布に従うと考え、発表速度の<b>95%信頼区間の下限</b>で並べた（Garwood の正確な信頼区間）。経過年数が短く回数が少ない人ほど区間が広がり、下限が下がる。この方法なら足切りが要らないので、第一著者{sp['people']}人の全員を並べた。</p>")
    body.append(f'<figure>{picture("speed", "発表速度の95%信頼区間の下限で並べた上位20人の図")}</figure>')
    body.append(f'<figure>{picture("speed_debut", "デビュー年と発表速度の散布図。左が割り算の値、右が信頼区間の下限")}<figcaption>左の割り算の値では、デビューが最近の人ほど点が上に寄る。右の下限では、この偏りが小さくなる。</figcaption></figure>')
    body.append(table(["順位", "第一著者", "下限（回/年）", "発表速度（回/年）", "登壇回数", "デビュー年", "経過年数"],
                      [[r[0], r[1], f"{r[2]:.2f}", f"{r[5] / r[7]:.2f}", r[5], r[6], r[7]] for r in sp_top], (0, 2, 3, 4, 5, 6)))
    body.append(f"<h3>補助の指標：デビューから{sp['window']}年間の登壇回数</h3><p>期間を同じ長さにそろえて比べる指標である。{sp['window']}年間がそろう、{sp['window_last_debut']}年までにデビューした{sp['window_people']}人が対象である。</p>")
    body.append(f'<figure>{picture("speed_window", "デビューから10年間の登壇回数の横棒グラフ")}</figure>')
    body.append(table(["順位", "第一著者", f"デビューから{sp['window']}年間の登壇回数", "デビュー年", "登壇回数の合計"], win_top, (0, 2, 3, 4))
                + f'<p>全員分の表は <a href="{REPO}/blob/main/ranking_speed.tsv">ranking_speed.tsv</a> にある。</p>')

    body.append('<h2 id="history">経緯</h2><ol>'
                "<li><b>2011年に、1994年から2011年までの一覧を作った。</b> 栗原一貴が、WISS のウェブサイトのプログラムと紙の予稿集から、登壇発表410件の題名と著者（第4著者まで）を Microsoft Access のデータベースにまとめた。1997年のウェブのプログラムは著者の大半が姓だけで書かれているので、この年の姓名は紙の予稿集で補ったと考えられる。</li>"
                "<li><b>2026年10月に、全回を調べ直した。</b> 栗原一貴の WISS2026 の登壇発表が何回目にあたるかを確かめる目的で始め、全員の順位表を作る調査に広げた。wiss.org に残る各年のプログラムと予稿集の目次を取得し、生成AI（Anthropic の Claude Code）に年代ごとに分けて一覧の表を作らせた。表は、取得したページの本文と全件を機械で照合して確かめた。</li>"
                "<li><b>2011年のデータベースと突き合わせた。</b> 1994年から2011年までの410件を、題名で対応づけて第一著者を照合した。食い違いは、旧姓による表記の違いが1件と、データベースで名前が途中で切れていたものが2件だけであった。データベースに漏れていた登壇発表が3件見つかった。</li>"
                f"<li><b>{Y0}年（第1回）を再構成した。</b> {Y0}年だけは発表の一覧のページが作られておらず、出版社（近代科学社）の書籍のページに題名38件だけが残っている。CiNii の引用の書誌、学会誌「コンピュータソフトウェア」11巻6号（1994年）の特集への再録、本人の researchmap、同じ著者の後の論文から、24件の第一著者を補った。残る{S['talks_unknown']}件は分かっていない。</li></ol>")
    body.append('<h2 id="method">方法</h2><ul>'
                "<li><b>数えたもの</b>：論文を伴う口頭発表（登壇発表）の第一著者。ロング発表、ショート発表、議論枠の発表を含む。</li>"
                "<li><b>数えていないもの</b>：デモ・ポスター発表、招待講演、国際学会招待発表、ロングティザー発表、WISS Challenge、WISS Design。</li>"
                "<li><b>情報源</b>：1993年は近代科学社の書籍のページの目次、1994年から2004年は wiss.org の各年のプログラム、2005年以降は wiss.org の各年の予稿集の目次とプログラム。</li>"
                "<li><b>名前の表記の揺れ</b>：空白と異体字をそろえ、旧姓と字体の違いは対応表で同一人物として扱った。上位の人については、別の表記で数え漏れていないことを目で確かめた。</li></ul>")
    body.append('<h2 id="limits">この調査の限界</h2><ul>'
                f"<li>{Y0}年の{S['talks_unknown']}件は第一著者が分からない。紙の予稿集で確かめれば埋められる。</li>"
                f"<li>{Y0}年の第一著者のうち2件は、同じ時期に同じ主題の論文を書いていることからの推定である。</li>"
                "<li>同じ人が姓を変えた場合、対応表に載せた人だけを同一人物として扱っている。英字の名前は照合していない。</li>"
                "<li>デモ・ポスター発表は、一覧が残っている年だけを数えた。</li></ul>")
    body.append(f'<footer>版 {e(VERSION)}（{STATUS}）　｜　<a href="{REPO}/blob/main/CHANGELOG.md">変更履歴</a>　｜　<a href="{REPO}">GitHub</a>　｜　調査と集計：栗原一貴（津田塾大学）</footer>')
    return ("<!doctype html><html lang=\"ja\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            f"<title>WISS 登壇発表の統計</title><meta name=\"description\" content=\"{e(intro_text())}\">"
            '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;600;700&display=swap" rel="stylesheet">'
            f"<style>{PAGE_CSS}</style></head><body><div class=\"wrap\">" + "\n".join(body) + "</div></body></html>")


SLIDE_CSS = CSS + """
html,body{height:100%;overflow:hidden}
.deck{position:fixed;inset:0;display:flex;align-items:center;justify-content:center}
.slide{position:absolute;width:1280px;height:720px;padding:56px 72px 48px;display:none;flex-direction:column;background:var(--bg);transform-origin:center center}
.slide.on{display:flex}
.slide h2{font-size:38px;line-height:1.3;margin:0 0 20px}
.slide .sub{font-size:20px;color:var(--fg2);margin:-10px 0 18px}
.slide ul{font-size:24px;line-height:1.7;margin:0;padding-left:1.2em}.slide li{margin:6px 0}
.slide .fig{flex:1 1 0;min-height:0;display:flex;align-items:center;justify-content:center;margin-bottom:28px;overflow:hidden}
.slide .fig picture{display:flex;height:100%;width:100%;justify-content:center;align-items:center}
.slide .fig img{max-height:100%;max-width:100%;width:auto;height:auto;object-fit:contain}
.slide h2,.slide .sub,.slide ul,.slide .big{flex-shrink:0}
.slide .cols{display:flex;gap:40px;flex:1;min-height:0}.slide .cols>div{flex:1;min-width:0}
.slide table{font-size:19px;border-collapse:collapse;width:100%}.slide th,.slide td{padding:4px 10px;border-bottom:1px solid var(--line);text-align:left}
.slide .num{text-align:right;font-variant-numeric:tabular-nums}.slide th{color:var(--fg2)}
.big{display:grid;grid-template-columns:repeat(4,1fr);gap:20px;margin:16px 0 28px}
.big div{background:var(--card);border-radius:14px;padding:20px 22px}.big .k{font-size:18px;color:var(--fg2)}.big .v{font-size:52px;font-weight:700;line-height:1.2}.big .s{font-size:16px;color:var(--fg2)}
.title h1{font-size:54px;line-height:1.35;margin:120px 0 20px}.title .meta{font-size:24px;color:var(--fg2)}
.badge{display:inline-block;align-self:flex-start;font-size:18px;padding:2px 14px;border:1px solid var(--line);border-radius:999px;color:var(--fg2)}
.foot{position:absolute;left:72px;right:72px;bottom:18px;font-size:14px;color:var(--fg2);display:flex;justify-content:space-between}
.hint{position:fixed;right:16px;bottom:12px;font-size:13px;color:var(--fg2)}
@media print{html,body{overflow:visible;height:auto}.deck{position:static;display:block}.slide{position:relative;display:flex!important;transform:none!important;page-break-after:always}.hint{display:none}@page{size:1280px 720px;margin:0}}
"""


def slide(inner, cls=""):
    return f'<section class="slide {cls}">{inner}</section>'


def slide_fig(title_, sub, name, alt):
    return slide(f"<h2>{e(title_)}</h2>" + (f'<p class="sub">{e(sub)}</p>' if sub else "") + f'<div class="fig">{picture(name, alt)}</div>')


def slide_fig_table(title_, sub, name, alt, head, rows, num_cols=()):
    return slide(f"<h2>{e(title_)}</h2>" + (f'<p class="sub">{e(sub)}</p>' if sub else "")
                 + f'<div class="cols"><div class="fig">{picture(name, alt)}</div><div style="flex:0 0 46%">{mini_table(head, rows, num_cols)}</div></div>')


def mini_table(head, rows, num_cols=()):
    th = "".join(f'<th class="{"num" if i in num_cols else ""}">{e(h)}</th>' for i, h in enumerate(head))
    trs = "".join("<tr>" + "".join(f'<td class="{"num" if i in num_cols else ""}">{e(str(c))}</td>' for i, c in enumerate(r)) + "</tr>" for r in rows)
    return f"<table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>"


def build_slides():
    s = []
    s.append(slide(f'<span class="badge">{STATUS}・版 {e(VERSION)}</span><h1>WISS 登壇発表の<br>第一著者の統計（{Y0}–{Y1}）</h1>'
                   f'<p class="meta">栗原一貴（津田塾大学）</p><p class="meta" style="font-size:18px">HTML 版：{SITE}</p>', "title"))
    s.append(slide("<h2>何を数えたか</h2><div class=\"big\">" + "".join(
        f'<div><div class="k">{e(k)}</div><div class="v">{e(v)}</div><div class="s">{e(s_)}</div></div>' for k, v, s_ in FACTS) + "</div><ul>"
        "<li>数えたのは、論文を伴う口頭発表（登壇発表）の第一著者である。</li>"
        "<li>デモ・ポスター、招待講演、国際学会招待発表は数えていない。</li>"
        f"<li>情報源は wiss.org の各年のプログラムと予稿集の目次。{Y0}年は書籍の目次から再構成した。</li></ul>"))
    s.append(slide_fig("第一著者の8割は、登壇が1回だけである", f"{S['authors']}人のうち{S['once']}人（{S['once_share']:.0%}）が1回。2回以上の{repeaters}人の発表が全体の{S['talks_by_repeaters_share']:.0%}を占める", "distribution", "登壇回数ごとの人数"))
    s.append(slide_fig_table(f"最多は{names_join(leaders)}の{max_n}回", "第一著者としての登壇回数", "ranking", "登壇回数の多い第一著者",
                             ["順位", "第一著者", "回数", "期間"], [[r[0], r[1], r[2], f"{r[3]}–{r[4]}"] for r in first_rows[:10]], (0, 2)))
    s.append(slide_fig("登壇回数の多い人は、いつ登壇したか", "6回以上の人。大きい点は同じ年に複数件", "timeline", "登壇した年"))
    s.append(slide_fig("登壇発表はほぼ一定、デモ・ポスターは急増", f"登壇発表は毎年{min(pyc)}件から{max(pyc)}件。デモ・ポスターは{Y1}年に{S['demos'][str(Y1)]}件", "per_year", "年ごとの発表件数"))
    s.append(slide_fig("初登壇の第一著者による発表が増えている", f"平均は{S['first_share_mean']:.0%}。2020年以降は{min(fs20):.0%}から{max(fs20):.0%}", "first_timers", "初登壇の割合"))
    s.append(slide_fig_table("著者全員で数えると、別の人が浮かび上がる", f"登壇発表に関わった{aa['people']}人。青は第一著者として、橙は共著者として", "authors_any", "著者として関わった数",
                             ["著者", "関わった数", "うち第一著者"], [[r[0], r[1], r[2]] for r in aa["top_any"][:10]], (1, 2)))
    lr = aa["top_last"][:10]
    s.append(slide("<h2>最終著者と、共著の多い組</h2><div class=\"cols\"><div>"
                   + mini_table(["最終著者", "回数"], [[a, c] for a, c, n in lr], (1,)) + "</div><div>"
                   + mini_table(["共著の組", "回数"], [[f"{a}・{b}", c] for a, b, c in aa["top_pairs"][:10]], (1,)) + "</div></div>"))
    s.append(slide_fig("1件あたりの著者は増えている", f"1990年代の平均の約{ma90:.1f}人から、2020年代の平均の約{ma20:.1f}人へ", "mean_authors", "1件あたりの著者の数"))
    s.append(slide("<h2>発表速度：年数あたりの登壇の多さ</h2><ul>"
                   "<li><b>デビュー年</b>：第一著者として初めて登壇した年</li>"
                   f"<li><b>発表速度</b>：登壇回数 ÷ デビューから{Y1}年までの経過年数</li>"
                   "<li>そのままでは、デビューが最近の人ほど高く出る</li>"
                   "<li>そこで、ポアソン分布の<b>95%信頼区間の下限</b>で並べる</li></ul>"
                   f'<div class="fig">{picture("speed_debut", "デビュー年と発表速度の散布図")}</div>'))
    s.append(slide_fig_table(f"発表速度の下限では{sp_top[0][1]}さんが1位", "菱形が下限（順位の基準）、丸が割り算の値、線が95%信頼区間", "speed", "発表速度の下限",
                             ["順位", "第一著者", "下限", "回数／年数"], [[r[0], r[1], f"{r[2]:.2f}", f"{r[5]}回／{r[7]}年"] for r in sp_top[:10]], (0, 2, 3)))
    s.append(slide_fig(f"デビューから{sp['window']}年間の登壇回数", f"{sp['window_last_debut']}年までにデビューした{sp['window_people']}人が対象", "speed_window", "10年間の登壇回数"))
    s.append(slide("<h2>経緯と、この調査の限界</h2><ul>"
                   "<li>2011年に、1994年から2011年までの410件を Access のデータベースにまとめた</li>"
                   "<li>2026年10月に、wiss.org の全回のページから生成AI（Claude Code）で一覧を作り直し、2011年のデータベースと照合した</li>"
                   f"<li>{Y0}年は、CiNii、学会誌への再録、researchmap から第一著者を補った（{S['talks_unknown']}件は不明）</li>"
                   "<li>旧姓などの表記の揺れは、対応表に載せた人だけをそろえた</li>"
                   + ("<li><b>暫定版</b>：WISS2026 のプログラムの公開後に2026年分を加えて確定版とする</li>" if PROVISIONAL else "")
                   + f"</ul><p style=\"font-size:20px;margin-top:28px\">データとスクリプト：{REPO}</p>"))
    n = len(s)
    s = [x.replace("</section>", f'<div class="foot"><span>WISS 登壇発表の統計（{STATUS}・版 {e(VERSION)}）</span><span>{i + 1} / {n}</span></div></section>') for i, x in enumerate(s)]
    js = """
const S=[...document.querySelectorAll('.slide')];let i=Math.max(0,Math.min(S.length-1,(parseInt(location.hash.slice(1))||1)-1));
function fit(){const k=Math.min(innerWidth/1280,innerHeight/720);S.forEach(s=>s.style.transform='scale('+k+')')}
function show(n){i=Math.max(0,Math.min(S.length-1,n));S.forEach((s,j)=>s.classList.toggle('on',j===i));history.replaceState(null,'','#'+(i+1))}
addEventListener('keydown',ev=>{if(['ArrowRight','PageDown',' ','Enter'].includes(ev.key)){show(i+1);ev.preventDefault()}if(['ArrowLeft','PageUp','Backspace'].includes(ev.key)){show(i-1);ev.preventDefault()}if(ev.key==='Home')show(0);if(ev.key==='End')show(S.length-1)});
addEventListener('click',ev=>{if(ev.target.closest('a'))return;show(ev.clientX>innerWidth/2?i+1:i-1)});
let x0=null;addEventListener('touchstart',ev=>{x0=ev.touches[0].clientX},{passive:true});addEventListener('touchend',ev=>{if(x0===null)return;const dx=ev.changedTouches[0].clientX-x0;if(Math.abs(dx)>40)show(dx<0?i+1:i-1);x0=null});
addEventListener('hashchange',()=>{const n=(parseInt(location.hash.slice(1))||1)-1;if(n!==i)show(n)});
addEventListener('resize',fit);fit();show(i);
"""
    return ("<!doctype html><html lang=\"ja\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            "<title>WISS 登壇発表の統計（スライド）</title>"
            '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;600;700&display=swap" rel="stylesheet">'
            f"<style>{SLIDE_CSS}</style></head><body><div class=\"deck\">" + "\n".join(s)
            + '</div><div class="hint">← → で移動　｜　<a href="index.html">HTML 版</a></div>'
            + f"<script>{js}</script></body></html>")


open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(build_index())
open(os.path.join(HERE, "slides.html"), "w", encoding="utf-8").write(build_slides())
print("index.html と slides.html を書いた。版", VERSION, STATUS)
