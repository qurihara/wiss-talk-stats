# -*- coding: utf-8 -*-
"""README.md を figs/stats.json と data/ から作る。

使い方: python3 make_figures.py のあとに python3 build_readme.py
文章の中の数値、名前、表は集計から埋め込むので、年を足して作り直せば README もそろう。
README を手で直したいときは、この中の文章を直す。
"""
import csv, glob, json, os, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(HERE, "figs", "stats.json"), encoding="utf-8"))
VERSION = open(os.path.join(HERE, "VERSION"), encoding="utf-8").read().strip()
AS_OF = open(os.path.join(HERE, "AS_OF"), encoding="utf-8").read().strip()  # 資料の日付（1か所で管理する）
AS_OF_JA = f"{int(AS_OF[:4])}年{int(AS_OF[5:7])}月{int(AS_OF[8:10])}日"
Y0, Y1 = S["years"]
N = Y1 - Y0 + 1
PROVISIONAL = Y1 < 2026
STATUS = "暫定版" if PROVISIONAL else "確定版"
aa, wd = S["authors_all"], S["window"]
top = S["top"]
max_n = top[0][1]
leaders = [a for a, c, *_ in top if c == max_n]
pyc = list(S["per_year"].values())
DY = max(int(y) for y in S["demos"]); DN = S["demos"][str(DY)]
fs20 = [v for y, v in S["first_share"].items() if int(y) >= 2020]
ma = {int(k): v for k, v in aa["mean_authors"].items()}
ma90 = statistics.mean(v for y, v in ma.items() if y < 2000)
ma20 = statistics.mean(v for y, v in ma.items() if y >= 2020)
any1, any2 = aa["top_any"][0], aa["top_any"][1]
other_kinds = 0
for f in glob.glob(os.path.join(HERE, "data", "*.tsv")):
    for r in csv.DictReader(open(f, encoding="utf-8"), delimiter="\t"):
        if r["kind"] in ("招待講演", "国際学会招待発表", "国際会議招待発表"):
            other_kinds += 1


def presence_note(S):
    pr = S["presence"]; k, g = pr["rank"]["栗原一貴"], pr["rank"]["五十嵐健夫"]
    if k > g:
        return (f"この指標は、調査者の栗原一貴が、なんとか自分の順位が師匠である五十嵐健夫さんを上回る指標はないものかと模索した結果、思いついたものである。"
                f"しかし、栗原は{k}位（{pr['value']['栗原一貴']:.1f}）で、五十嵐さんの{g}位（{pr['value']['五十嵐健夫']:.1f}）には、まだ届かなかった。")
    return (f"この指標は、調査者の栗原一貴が、なんとか自分の順位が師匠である五十嵐健夫さんを上回る指標はないものかと模索した結果、思いついたものである。"
            f"栗原は{k}位（{pr['value']['栗原一貴']:.1f}）で、五十嵐さんの{g}位（{pr['value']['五十嵐健夫']:.1f}）を、ついに上回った。")


def join_names(ns):
    return "さんと".join(ns) + "さん" if len(ns) <= 2 else "さん、".join(ns[:-1]) + "さん、" + ns[-1] + "さん"


def pic(name, alt, w):
    return (f'<picture>\n  <source media="(prefers-color-scheme: dark)" srcset="figs/{name}_dark.png">\n'
            f'  <img alt="{alt}" src="figs/{name}_light.png" width="{w}">\n</picture>\n')


def ranked(rows, key):
    out, prev, rk = [], None, 0
    for i, r in enumerate(rows, 1):
        if key(r) != prev:
            rk, prev = i, key(r)
        out.append((rk, r))
    return out


md = []
md.append(f"# WISS 登壇発表の第一著者（すなわちおそらく発表者）の統計（{Y0}–{Y1}）\n")
md.append(f"日本ソフトウェア科学会の「インタラクティブシステムとソフトウェアに関するワークショップ」（WISS）について、"
          f"第1回（{Y0}年）から第{N}回（{Y1}年）までの登壇発表を全件集め、第一著者ごとの登壇回数を集計した調査である。\n")
if PROVISIONAL:
    md.append("> **暫定版である。** WISS2026（第34回）のプログラムが公開されたあとに2026年分を加え、確定版として公開する予定である。\n")
md.append(f"調査と集計：栗原一貴（津田塾大学）　｜　{AS_OF_JA}時点　｜　版 {VERSION}（{STATUS}）　｜　[変更履歴](CHANGELOG.md)\n")
md.append("- **HTML 版**：https://unryu.org/wiss-talk-stats/\n- **スライド版**：https://unryu.org/wiss-talk-stats/slides.html （← → キーで移動）\n")

md.append("## 調査の結果の概要\n")
md.append(f"- {Y0}年から{Y1}年までの{N}回で、登壇発表は **{S['talks']}件** あった。そのうち{S['talks_known']}件の第一著者が分かっており、第一著者は **{S['authors']}人** である。\n"
          f"- 第一著者の **{S['once_share']:.0%}（{S['once']}人）は、登壇発表が1回だけ** である。2回以上登壇した{S['authors'] - S['once']}人の発表が、全体の{S['talks_by_repeaters_share']:.0%}を占める。\n"
          f"- 最も多く登壇したのは、**{join_names(leaders)}の{max_n}回** である。次いで" + "、".join(f"{a}さんの{c}回" for a, c, *_ in top[len(leaders):len(leaders) + 4]) + "が続く。\n"
          f"- 各年の登壇発表のうち、第一著者が WISS で初めて登壇する発表の割合は、平均で{S['first_share_mean']:.0%}である。2020年以降は{min(fs20):.0%}から{max(fs20):.0%}である。\n"
          f"- 登壇発表は毎年{min(pyc)}件から{max(pyc)}件である。一方、デモ・ポスター発表は2020年以降に大きく増え、{DY}年には{DN}件になった。\n"
          f"- 登壇回数と登壇発表の実績がある期間の幾何平均で表した「長期的な登壇の貢献」では、{S['presence']['top'][0][1]}さん、{S['presence']['top'][1][1]}さん、{S['presence']['top'][2][1]}さんの順になる（[長期的な登壇の貢献](#長期的な登壇の貢献)）。\n"
          f"- 第一著者として続けて登壇した年数の最長記録は、{S['streak']['top'][0][1]}さんの{S['streak']['top'][0][2]}年連続である（[連続登壇の最長記録](#連続登壇の最長記録)）。\n"
          f"- 著者全員で数えると、登壇発表に関わった人は{aa['people']}人である。最も多くの登壇発表に関わったのは{any1[0]}さんの{any1[1]}件である（[著者全員で見た分析](#著者全員で見た分析)）。\n")

md.append("## 図\n")
md.append(pic("ranking", "登壇回数の多い第一著者の横棒グラフ", 640))
md.append(pic("distribution", "登壇回数ごとの第一著者の人数の棒グラフ（縦軸は対数）", 640))
md.append(f"この図の縦軸は対数目盛である。1回の人数（{S['once']}人）と、それ以外の人数の差が大きいためである。\n")
md.append(pic("timeline", "登壇回数が6回以上の第一著者が登壇した年を示す点の図", 680))
md.append(pic("per_year", "年ごとの登壇発表とデモ・ポスター発表の件数の折れ線グラフ", 680))
md.append(f"デモ・ポスター発表は、予稿集かプログラムに一覧が残っている分だけを数えた。1993年から1996年は一覧が無い。{DY + 1}年以降のデモ・ポスター発表はまだ入れていない。\n")
md.append(pic("first_timers", "各年の登壇発表のうち、第一著者が初めて登壇する発表の割合の折れ線グラフ", 680))

md.append("## 登壇回数が4回以上の第一著者\n")
md.append("| 順位 | 第一著者 | 登壇回数 | 最初の年 | 最後の年 |\n|---:|---|---:|---:|---:|\n"
          + "".join(f"| {rk} | {a} | {c} | {y0} | {y1} |\n" for rk, (a, c, y0, y1) in ranked(top, lambda r: r[1])))
md.append("\n同じ回数の人は、最後に登壇した年が新しい順に並べた（いまも登壇している人を先にするため。それも同じなら、最初に登壇した年の順）。全員分の表は [ranking_all.tsv](ranking_all.tsv) にある。\n")

st = S["streak"]
md.append("## 連続登壇の最長記録\n")
md.append(f"第一著者として登壇した年が何年続いたかの最長記録である。WISS は{Y0}年から毎年開かれている（2020年はオンライン）。最も長いのは{st['top'][0][1]}さんの{st['top'][0][2]}年連続（{st['top'][0][3]}年から{st['top'][0][4]}年）である。同じ年数の人は、記録が新しい順に並べた。\n")
md.append(pic("streak", "連続登壇の最長記録が4年以上の人の横棒グラフ", 640))
md.append("| 順位 | 第一著者 | 連続登壇の最長記録 | 期間 | 登壇回数 |\n|---:|---|---:|---|---:|\n"
          + "".join(f"| {r[0]} | {r[1]} | {r[2]}年 | {r[3]}–{r[4]} | {r[5]} |\n" for r in st["top"]))
md.append("\n3年以上続けて登壇した人を挙げた。全員分の表は [ranking_streak.tsv](ranking_streak.tsv) にある。\n")
md.append("## 著者全員で見た分析\n")
md.append(f"第一著者だけでなく、登壇発表の著者として名前を連ねた人を全員数えた。{Y0 + 1}年以降は著者全員を数え、{Y0}年は共著者が分からないので、分かっている第一著者だけを数えた。\n")
md.append(f"- 登壇発表に著者として関わった人は **{aa['people']}人** である。\n"
          f"- 最も多くの登壇発表に関わったのは **{any1[0]}さんの{any1[1]}件** で、2位の{any2[0]}さん（{any2[1]}件）を大きく上回る。{any1[0]}さんの{any1[1]}件のうち{any1[3]}件は最終著者である。\n"
          "- 第一著者としての回数と、著者として関わった数は、別の人を浮かび上がらせる。第一著者の回数が少なくても、共著者として数十件に関わった人がいる。研究室や研究グループを率いて、学生や若手の研究者の発表を支えてきた人たちと考えられる。\n"
          f"- 登壇発表1件あたりの著者の数は、1990年代の平均の約{ma90:.1f}人から、2020年代の平均の約{ma20:.1f}人に増えた。\n")
md.append(pic("authors_any", "著者として関わった登壇発表の多い上位20人の横棒グラフ。第一著者としての回数と共著者としての回数に分けて積み上げてある", 660))
md.append(pic("mean_authors", "登壇発表1件あたりの著者の数の年ごとの平均の折れ線グラフ", 680))
md.append("### 最終著者としての回数（上位15人）\n\n著者が2人以上の登壇発表で、最後に名前がある回数である。研究室を主宰する人が最後に名前を連ねることが多いので、その目安になる。\n")
md.append("| 順位 | 最終著者 | 最終著者の回数 | 著者として関わった数 |\n|---:|---|---:|---:|\n"
          + "".join(f"| {rk} | {a} | {c} | {n} |\n" for rk, (a, c, n) in ranked(aa["top_last"], lambda r: r[1])))
md.append("\n### 共著の多い組（上位15組）\n\n同じ登壇発表に著者として並んだ回数である。\n")
md.append("| 組 | 回数 |\n|---|---:|\n" + "".join(f"| {a}・{b} | {c} |\n" for a, b, c in aa["top_pairs"]))
md.append("\n全員分の表は [ranking_authors.tsv](ranking_authors.tsv) にある。著者として関わった数、第一著者の回数、最終著者の回数、最初と最後の年の列がある。\n")

pr = S["presence"]
md.append("## 長期的な登壇の貢献\n")
md.append("登壇回数の多さと、長い年月にわたって登壇し続けたことを、合わせて1つの数で表す指標である。登壇回数と登壇発表の実績がある期間の幾何平均を求めた。登壇発表の実績がある期間は、最後に登壇した年から最初に登壇した年を引いて1を足した年数である。何度も、しかも長い年月にわたって登壇し続けた人ほど大きくなる。1回だけ登壇した人は1になる。登壇発表の実績がある期間をデビューから集計の最後の年までにすると、登壇をやめたあとの年月も数えてしまうので、最後に登壇した年までにした。\n")
md.append("```\n長期的な登壇の貢献 ＝ √（登壇回数 × 登壇発表の実績がある期間の年数）\n```\n")
md.append(presence_note(S) + "\n")
md.append(pic("presence", "長期的な登壇の貢献の上位20人の横棒グラフ", 660))
md.append("| 順位 | 第一著者 | 長期的な登壇の貢献 | 登壇回数 | 登壇発表の実績がある期間 |\n|---:|---|---:|---:|---|\n"
          + "".join(f"| {r[0]} | {r[1]} | {r[2]:.1f} | {r[3]} | {r[4]}–{r[5]}（{r[6]}年） |\n" for r in pr["top"]))
md.append("\n全員分の表は [ranking_presence.tsv](ranking_presence.tsv) にある。\n")
md.append("## デビューから10年間の登壇回数\n")
md.append(f"期間を同じ長さにそろえて比べる指標である。第一著者として初めて登壇した年（デビュー年）を1年目として、{wd['window']}年間に第一著者として何回登壇したかを数えた。{wd['window']}年間がそろう、{wd['last_debut']}年までにデビューした{wd['people']}人が対象である。\n")
md.append(pic("window", "デビューから10年間の登壇回数が4回以上の人の横棒グラフ", 640))
md.append(f"| 順位 | 第一著者 | デビューから{wd['window']}年間の登壇回数 | デビュー年 | 登壇回数の合計 |\n|---:|---|---:|---:|---:|\n"
          + "".join(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} |\n" for r in wd["top"]))
md.append("\n全員分の表は [ranking_window.tsv](ranking_window.tsv) にある。\n")

md.append("## 経緯\n")
md.append("1. **2011年に、1994年から2011年までの一覧を作った。** 栗原一貴が、WISS のウェブサイトのプログラムと紙の予稿集から、登壇発表410件の題名と著者（第4著者まで）を Microsoft Access のデータベースにまとめた（[legacy/](legacy/)）。1997年のウェブのプログラムは著者の大半が姓だけで書かれているので、この年の姓名は紙の予稿集で補ったと考えられる。1997年に5人目の著者がいる2件は、5人目をウェブの姓から同じ年の姓名に引き当てて足した。\n"
          "2. **2026年10月に、1993年から2025年までの33回を調べ直した。** 栗原一貴の WISS2026 の登壇発表が何回目にあたるかを確かめる目的で始め、全員の順位表を作る調査に広げた。wiss.org に残る各年のプログラムと予稿集の目次を取得し、生成AI（Anthropic の Claude Code）に年代ごとに分けて一覧の表を作らせた。表は、取得したページの本文と全件を機械で照合して確かめた。\n"
          "3. **2011年のデータベースと突き合わせた。** 1994年から2011年までの410件を、題名で対応づけて第一著者を照合した。食い違いは、旧姓による表記の違いが1件と、データベースで名前が途中で切れていたものが2件だけであった。データベースに漏れていた登壇発表が3件見つかった（2002年、2003年、2004年に1件ずつ）。\n"
          f"4. **1993年（第1回）を再構成した。** 1993年だけは発表の一覧のページが作られておらず、出版社（近代科学社）の書籍のページに題名38件だけが残っている。CiNii の引用の書誌、学会誌「コンピュータソフトウェア」11巻6号（1994年）の特集「インタラクティブシステムとソフトウェア」への再録、本人の researchmap、同じ著者の後の論文から、24件の第一著者を補った。残る{S['talks_unknown']}件は分かっていない。\n")
if Y1 >= 2026:
    md.append(f"5. **2026年11月に、WISS2026（第34回）を加えた。** 2026年11月5日に、栗原一貴が参加者として受け取った仮プログラムの PDF から、登壇発表と国際学会招待発表の題名と著者を取り出した（[pipeline/parse_wiss2026_pdf.py](pipeline/parse_wiss2026_pdf.py)）。2026年11月12日に公式のプログラムが [wiss.org](https://www.wiss.org/WISS2026/program.html) で公開されたので、表をこちらから作り直した（[pipeline/parse_wiss2026_html.py](pipeline/parse_wiss2026_html.py)）。仮プログラムとの照合では、登壇発表{S['per_year']['2026']}件の番号、順序、第一著者はすべて一致し、違いは題名の中の空白3件と、仮プログラムの表で取りこぼしていた国際学会招待発表1件の共著者だけであった。\n")

md.append("\n## 方法\n\n### 情報源\n\n| 年 | 情報源 |\n|---|---|\n"
          "| 1993 | 近代科学社の書籍『インタラクティブシステムとソフトウェアI』のページ（Internet Archive の保存版）の目次。著者は上記の方法で補った |\n"
          "| 1994–2004 | wiss.org の各年のプログラムのページ。1997年の姓名は2011年のデータベースで補った |\n"
          "| 2005–2025 | wiss.org の各年の予稿集の目次と、ロング・ショートの区別のためのプログラムのページ |\n"
          + ("| 2026 | wiss.org の公式のプログラムのページ（2026年11月12日に公開） |\n" if Y1 >= 2026 else ""))
md.append("\n### 数え方\n\n"
          "- **数えたもの**：論文を伴う口頭発表（登壇発表）の第一著者。ロング発表、ショート発表、議論枠の発表を含む。\n"
          f"- **数えていないもの**：デモ・ポスター発表、招待講演、国際学会招待発表、ロングティザー発表（登壇発表として採択されなかった論文の短い紹介）、WISS Challenge、WISS Design。招待講演と国際学会招待発表は合わせて{other_kinds}件あり、表には区分を付けて残してある。\n"
          "- **名前の表記の揺れ**：空白と異体字をそろえ、旧姓と字体の違いは対応表で同一人物として扱った（[rank.py](rank.py)）。上位の人については、別の表記で数え漏れていないことを目で確かめた。英字の名前は、上位に関わらないので照合していない。\n")
md.append("\n### 1993年の第一著者の根拠\n\n[data/1993.tsv](data/1993.tsv) の「根拠」の列に、次の3段階で根拠を書いた。\n\n"
          "- **確定（16件）**：引用の書誌が複数ある、学会誌の特集に再録されている、または本人の researchmap に登録されている。\n"
          "- **有力（6件）**：同じ人の、ほぼ同じ題名の後の論文がある。\n- **推定（2件）**：同じ時期に同じ主題の論文を書いている。\n")
md.append("\n## この調査の限界\n\n"
          f"- 1993年の{S['talks_unknown']}件は第一著者が分からない。紙の予稿集で確かめれば埋められる。上位の人の回数が変わる見込みは小さいが、1993年から登壇している人（暦本純一さん、綾塚祐二さん、増井俊之さん、原田康徳さんなど）の回数は増える可能性がある。\n"
          "- 1993年の暦本純一さんの1回を除くと、五十嵐健夫さんが単独で最多になる。1993年の暦本さんの発表（InformationCube）は、学会誌への再録で確かめられている。\n"
          "- ロング発表とショート発表の区別は、年によっては発表時間の長さから判断した。この区別は回数の集計には影響しない。\n"
          "- 同じ人が姓を変えた場合、対応表に載せた人だけを同一人物として扱っている。\n"
          + (f"- 2026年は、会期の前に公開された公式のプログラム（{AS_OF_JA}時点）に基づく。そのあとの発表の取り下げや題名の変更は反映されていない。012 の題名は、プログラムでも「開催1週間前に公開予定」となっている。2026年のデモ・ポスター発表は入れていない。\n" if Y1 >= 2026 else ""))

md.append("\n## ファイル\n\n| 場所 | 内容 |\n|---|---|\n"
          "| [data/](data/) | 年ごとの発表の一覧。列は year, kind（区分）, title, authors, first_author |\n"
          "| [ranking_all.tsv](ranking_all.tsv) | 第一著者の登壇回数の、全員分の順位表 |\n"
          "| [ranking_window.tsv](ranking_window.tsv) | デビューから10年間の登壇回数の表 |\n"
          "| [ranking_streak.tsv](ranking_streak.tsv) | 連続登壇の最長記録の表 |\n"
          "| [ranking_presence.tsv](ranking_presence.tsv) | 長期的な登壇の貢献（登壇回数と登壇発表の実績がある期間の幾何平均）の表 |\n"
          "| [ranking_authors.tsv](ranking_authors.tsv) | 著者全員で数えた表（著者として関わった数、第一著者の回数、最終著者の回数） |\n"
          "| [figs/](figs/) | README の図と、図に使った数値（stats.json） |\n"
          "| [rank.py](rank.py) | 順位表を作る。名前の表記をそろえる対応表もここにある |\n"
          "| [make_figures.py](make_figures.py) | 図と数値を作る |\n"
          "| [build_site.py](build_site.py) | HTML 版（index.html）とスライド版（slides.html）を作る |\n"
          "| [build_readme.py](build_readme.py) | この README を作る |\n"
          "| [crosscheck_legacy.py](crosscheck_legacy.py) | 2011年のデータベースと照合する |\n"
          "| [fix1997_from_legacy.py](fix1997_from_legacy.py) | 1997年の著者を2011年のデータベースの姓名で補う |\n"
          "| [fill1993.py](fill1993.py) | 1993年の第一著者を根拠つきで書き込む |\n"
          "| [legacy/](legacy/) | 2011年に作った Access のデータベースと、その Excel と CSV の写し |\n"
          "| [extraction/](extraction/) | 取得したページから年ごとの表を作るスクリプト。年代ごとに分かれている。中の `WORK` は作業の場所を表し、`pipeline/extract.py` がこの名前のフォルダを組み立てて動かす |\n"
          "| [pipeline/](pipeline/) | 元のページの取得、中間のファイルの作成、抜き出しと照合の手順（[再現と発展のための手順](#再現と発展のための手順)）。2026年のプログラムの PDF から表を作るスクリプトもここにある |\n"
          "| [LICENSE](LICENSE) | ライセンス。スクリプトは MIT、表と図と文章は CC BY 4.0 |\n"
          "| [VERSION](VERSION) | 版の番号。README、HTML 版、スライド版に表示する |\n| [AS_OF](AS_OF) | 資料の日付。README、HTML 版、スライド版に「何年何月何日時点」として表示する |\n"
          "| [CHANGELOG.md](CHANGELOG.md) | 変更履歴 |\n")

md.append("\n## 再現と発展のための手順\n\n"
          "集計に使った表、スクリプト、2011年のデータベースは、すべてこのリポジトリに入っている。取得した元のページ（wiss.org のプログラムと予稿集の目次、2026年のプログラムの PDF）だけは、論文の概要の全文を含むので入れていない。その代わりに、元のページを取得し直して、年ごとの表を1から作り直す手順を用意した。Python 3 と matplotlib があれば動く。\n\n"
          "1. `python3 pipeline/fetch_raw.py` … 1993年から2026年の元のページ53件を wiss.org と Internet Archive から `raw/` に取得する。URL と、取得したとき（1993年から2025年は2026年10月22日、2026年は2026年11月12日）の SHA-256 は [pipeline/sources.json](pipeline/sources.json) にある。当時から中身が変わったページがあれば表示する。\n"
          "2. `python3 pipeline/prepare.py` … 文字コードを UTF-8 にそろえた写しと、文字だけの写しを作る。古いページは文字コードがまちまちなので、ファイルごとに指定してある。\n"
          "3. `python3 pipeline/extract.py` … 年代ごとの抜き出しのスクリプト（[extraction/](extraction/)）を動かして年ごとの表を `build/WORK/out/` に作り、公開している `data/` と1件ずつ照合する。\n"
          "4. `python3 rank.py`、`python3 make_figures.py`、`python3 build_site.py`、`python3 build_readme.py` … 順位表、図と数値、HTML 版とスライド版、この README を作る。\n\n"
          "2026年の表（`data/2026.tsv`）は、手順3の中で `pipeline/parse_wiss2026_html.py` が公式のプログラムのページから作る。仮プログラムの PDF から表を作ったスクリプト（`pipeline/parse_wiss2026_pdf.py`）は、記録として残してある。\n\n"
          "2026年10月22日に、元のページを持たない空のフォルダで手順1から4を通して動かし、1993年から2025年の33年分の表、順位表、図の数値、2つのページが、公開しているものと一致することを確かめた。2026年11月12日には、手順3で2026年を含む34年分の表が `data/` と一致することを確かめた。\n\n"
          "この調査を発展させるときの入口は、次のとおりである。\n\n"
          "- **別の数え方を試す**：`data/<年>.tsv` の `kind` 列に、デモ、招待講演、国際学会招待発表なども区分を付けて残してある。`rank.py` の `COUNTED` を変えれば、数える範囲を変えられる。\n"
          "- **名前の表記の揺れを直す**：`rank.py` の `ALIASES` に、同一人物の別の表記を足す。\n"
          "- **1993年を埋める**：`fill1993.py` の対応表に、第一著者と根拠を足す。\n"
          "- **新しい年を足す**：`data/<年>.tsv` を同じ列で作り、手順4を動かす。\n")
md.append("\n## 作り直す手順\n\n"
          "1. 新しい年の `data/<年>.tsv` を同じ列で作る。\n"
          "2. `python3 rank.py`、`python3 make_figures.py`、`python3 build_site.py`、`python3 build_readme.py` を順に動かす。\n"
          "3. `VERSION` の番号を上げ、`CHANGELOG.md` に変更を書く。\n")
open(os.path.join(HERE, "README.md"), "w", encoding="utf-8").write("\n".join(md))
print("README.md を書いた。版", VERSION, STATUS)
