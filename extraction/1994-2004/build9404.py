import re, html, os, sys

BASE = 'WORK/'
U8 = BASE + 'u8/'
W = BASE + 'w9404/'
OUT = BASE + 'out/'


def rd(p):
    return open(p).read().replace('\r', '')


def txt(s):
    s = re.sub(r'(?is)<!--.*?-->', '', s)
    s = re.sub(r'(?i)<br\s*/?>|</br>', ' ', s)
    s = re.sub(r'<[^>]*>', '', s)
    s = html.unescape(s)
    CJ = '　-ヿ一-鿿！-｠'
    s = re.sub('(?<=[' + CJ + '])[ \t]*\n\\s*(?=[' + CJ + '])', '', s)
    s = s.replace('　', ' ')
    s = re.sub(r'\s+', ' ', s).strip()
    return s


KANJI = r'[一-鿿]'


def strip_aff(s):
    # keep single-kanji disambiguators like 田中(一)
    s = re.sub(r'(' + KANJI + r')[（(](' + KANJI + r')[)）]', r'\1〔\2〕', s)
    prev = None
    while prev != s:
        prev = s
        s = re.sub(r'\s*[（(][^()（）]*[)）]', '', s)
    # unbalanced leftover "( ..." at end
    s = re.sub(r'\s*[（(][^)）]*$', '', s)
    s = s.replace('〔', '(').replace('〕', ')')
    return s


def split_authors(s, seps='、,，'):
    s = txt(s)
    s = strip_aff(s)
    parts = re.split('[' + seps + ']', s)
    out = []
    for p in parts:
        p = p.strip()
        p = re.sub(r'^[★○＊*☆\s]+', '', p)
        p = re.sub(r'[\s\d*＊]+$', '', p)  # trailing markers like 悟1, 吉伸*
        p = p.strip()
        if p:
            out.append(p)
    return out


def row(year, kind, title, authors):
    title = re.sub(r'\s+', ' ', title).strip()
    authors = [re.sub(r'\s+', ' ', a).strip() for a in authors]
    return (str(year), kind, title, ';'.join(authors), authors[0] if authors else '')


def events_li(h):
    """Yield ('H', text) for headings and ('LI', raw) for list items, in order."""
    h = re.sub(r'(?is)<!--.*?-->', '', h)
    toks = re.split(r'(?is)(<h\d[^>]*>.*?</h\d>|<li[^>]*>|</ul>|</ol>)', h)
    cur = None
    for t in toks:
        if re.match(r'(?i)<h\d', t):
            if cur is not None:
                yield ('LI', cur); cur = None
            yield ('H', txt(t))
        elif re.match(r'(?i)<li', t):
            if cur is not None:
                yield ('LI', cur)
            cur = ''
        elif re.match(r'(?i)</(ul|ol)', t):
            if cur is not None:
                yield ('LI', cur); cur = None
        else:
            if cur is not None:
                cur += t
    if cur is not None:
        yield ('LI', cur)


def li_title_auth(raw):
    raw = re.sub(r'(?is)<font color=green.*?</font>', '', raw)
    short = bool(re.search(r'(?is)<font color=blue>\s*\*\s*</font>', raw))
    raw = re.sub(r'(?is)<font color=blue>\s*\*\s*</font>', '', raw)
    parts = re.split(r'(?i)<br\s*/?>|</br>', raw)
    parts = [p for p in parts]
    title = txt(parts[0])
    auth = txt(parts[1]) if len(parts) > 1 else ''
    return title, auth, short


def y1994_95(y):
    h = rd(U8 + f'y{y}.html')
    rows = []
    for ev, v in events_li(h):
        if ev == 'LI':
            t, a, _ = li_title_auth(v)
            rows.append(row(y, '登壇（区別なし）', t, split_authors(a, '・、,')))
    return rows


def y1996():
    h = rd(U8 + 'y1996.html')
    h = h[h.index('Preliminary Program'):]
    rows = []
    for ev, v in events_li(h):
        if ev == 'LI':
            t, a, _ = li_title_auth(v)
            rows.append(row(1996, '登壇（区別なし）', t, split_authors(a)))
    rows.append(row(1996, '招待講演', 'インターネット空間でのコンピュータグラフィクス', ['山本 強']))
    return rows


def y1997_99(y):
    h = rd(U8 + f'y{y}.html')
    rows = []
    sess = ''
    for ev, v in events_li(h):
        if ev == 'H':
            sess = v; continue
        t, a, short = li_title_auth(v)
        if not a and '賞(' in t:
            continue  # award descriptions at top of 1999 page
        if y == 1999 and t.startswith('協調型情報探索を支援する仮想評者とその視覚化'):
            t, a = '協調型情報探索を支援する仮想評者とその視覚化', '舘村純一(東大)'
        if 'ポスター' in sess:
            kind = 'ポスター'
        else:
            kind = '登壇ショート' if short else '登壇ロング'
        rows.append(row(y, kind, t, split_authors(a)))
    if y == 1999:
        d = rd(W + 'WISS99_demo.html.u8')
        for m in re.finditer(r'(?is)<dt>\s*<font size=\+1 color=blue>(.*?)</font>\s*<br>\s*<font color=green>(.*?)</font>', d):
            rows.append(row(1999, 'デモ', txt(m.group(1)), split_authors(m.group(2))))
    return rows


def y2000():
    h = rd(U8 + 'y2000.html')
    rows = []
    sess = ''
    for ev, v in events_li(h):
        if ev == 'H':
            sess = v; continue
        parts = re.split(r'(?i)<br\s*/?>', v)
        if 'オンライン・チャット' in sess:
            rows.append(row(2000, 'その他', 'オンライン・チャットシステム参加チーム', split_authors(txt(v))))
            continue
        title = txt(parts[0]); auth = txt(parts[1]) if len(parts) > 1 else ''
        if title.startswith('SpaceTagを利用したチャットシステム'):
            title = 'SpaceTagを利用したチャットシステム PetAvatar'; auth = txt(parts[2])
        if 'ポスターセッションタイトル' in sess:
            kind = 'ポスター'
        elif 'デモセッションタイトル' in sess:
            kind = 'デモ'
        else:
            kind = '登壇ロング' if '★' in title else '登壇ショート'
        title = title.replace('★', '').strip()
        a = auth
        # space-separated author lists without commas
        if not re.search('[、,，]', strip_aff(a)):
            names = strip_aff(a).split()
            if len(names) > 1 and all(len(n) >= 3 for n in names):
                a = '、'.join(names)
            elif strip_aff(a).strip() == '豊原 純平 佐賀 聡人':
                a = '豊原 純平、佐賀 聡人'
        if '山本吉伸*' in a:
            a = a.replace('*', '')
        rows.append(row(2000, kind, title, split_authors(a)))
    return rows


def demo_pages(path, year):
    d = rd(path)
    rows = []
    for m in re.finditer(r'(?is)\[([0-9A-Za-z\-]+\*?)\]\s*<font color="[^"]*">([^\[]*?)</font>\s*<br>([^\[]*?)(?:<br>|</pre>|<ul>)', d):
        t = txt(m.group(2)); a = split_authors(m.group(3))
        if not a or set(t) <= set('*＊ '):
            continue  # empty placeholder slots
        rows.append(row(year, 'デモ', t, a))
    return rows


def y2001():
    h = rd(U8 + 'y2001.html')
    rows = []
    for m in re.finditer(r'(?is)<font color="green">(.*?)</font>(.*?)<br>(.*?)<br>', h):
        title = txt(m.group(1)); mid = m.group(2)
        long_ = '★' in mid
        rows.append(row(2001, '登壇ロング' if long_ else '登壇ショート', title, split_authors(m.group(3))))
    rows += demo_pages(W + 'WISS2001_wiss2001demo.html.u8', 2001)
    return rows


def divs(h, year):
    rows = []
    sess = ''
    toks = re.split(r'(?is)(<h\d[^>]*>.*?</h\d>|<div class="?presentation"?>)', h)
    for t in toks:
        if re.match(r'(?i)<h\d', t):
            sess = txt(t); continue
        if re.match(r'(?i)<div class="?presentation', t):
            continue
        mt = re.search(r'(?is)<div class="?title"?>(.*?)</div>', t)
        ma = re.search(r'(?is)<div class="?author"?>(.*?)</div>', t)
        if not mt:
            continue
        title_raw = mt.group(1)
        long_ = '★' in title_raw
        star2 = '☆' in title_raw
        title = txt(title_raw).replace('★', '').replace('☆', '').strip()
        auth = txt(ma.group(1)) if ma else ''
        if 'デモ' in sess:
            kind = 'デモ'
        else:
            kind = '登壇ロング' if long_ else '登壇ショート'
        rows.append((sess, kind, title, auth))
    return rows


def y2002():
    h = rd(U8 + 'y2002.html')
    rows = [row(2002, k, t, split_authors(a)) for s, k, t, a in divs(h, 2002)]
    rows += demo_pages(W + 'WISS2002_Wiss2002demo.html.u8', 2002)
    return rows


def y2003():
    L, S = '登壇ロング', '登壇ショート'
    data = [
        (S, '自分自身との対戦：生体信号を利用したゲーム', '櫻沢 繁, 吉田 直史, 棟方 渚, 塚原 保夫, 松原 仁'),
        (S, 'タッチレス入力装置とジェスチャ・コマンド', '石川 忠明, 星野 剛史, 堀井 洋一'),
        (L, '音声スポッタ: 人間同士の会話中に音声認識が利用できる新たな音声インタフェース', '北山 広治, 後藤 真孝, 伊藤 克亘, 小林 哲則'),
        (S, 'ism：即興演奏の不自然な旋律を補正する演奏支援システム', '石田 克久, 北原 鉄朗, 武田 正之'),
        (S, 'ウェアラブル環境のためのルールベースBGMプレーヤについて', '寺田 努, 塚本 昌彦, 宮前 雅一, 西尾 章治郎'),
        (L, '意味内容に基づく映像の自動編集', '出口 嘉紀, 吉高 淳夫'),
        (S, 'EnhancedMovie: 机型インタフェースを用いた動画編集システム', '石井 陽子, 中西 泰人, 小池 英樹, 岡 兼司, 佐藤 洋一'),
        (L, 'Viscuit : 柔軟な動作をするビジュアル言語', '原田 康徳, 加藤 美由紀, Richard Potter'),
        (L, '高次元の利用による対話的グラフ配置法', '細部 博史'),
        (S, 'SmartGray：彩色文書の情報を保持した無彩配色法', '脇田 建'),
        (S, '社会的関係を用いたネットオークションの評価コメントの自動要約', '大野 華子, 楠村 幸貴, 土方 嘉徳, 西田 正吾'),
        (L, '近傍関係にもとづく情報検索システム', '増井 俊之, 塚田 浩二, 高林 哲'),
        (S, '共鳴に基づく人と環境とのインタラクションのためのフレームワーク', '栗原 聡, 青柳 滋己, 広津 登志夫, 高田 敏弘, 菅原 俊治'),
        (L, 'tranStick: 空間を越えて仮想的に繋がったメディア', '綾塚 祐二, 暦本 純一'),
        (S, 'Proximal Networking: 近接センシングによるワイヤレス環境制御のための直接操作技法', '暦本 純一, 味八木 崇, 河野 通宗'),
        (S, 'Lumisight Table: 天地問題を解消した対面協調支援システム', '筧 康明, 飯田 誠, 苗村 健, 白井 良成, 松下 光範, 大黒 毅'),
        (L, '秘映プロジェクタ: 不可視情報による実環境の拡張', '白井 良成, 松下 光範, 大黒 毅'),
        (S, '設備点検支援のための機器音可視化および検索手法', '堤 富士雄'),
        (S, 'RICA: 動的にサービス構成の変更が可能な分散ディスプレイシステム', '斉藤 功冶, 河口 信夫, 稲垣 康善'),
    ]
    rows = [row(2003, k, t, split_authors(a)) for k, t, a in data]
    rows += demo_pages(W + 'WISS2003_demoprogram.html.u8', 2003)
    return rows


def y2004():
    h = rd(U8 + 'y2004.html')
    rows = []
    for s, k, t, a in divs(h, 2004):
        if s.startswith('10:40-11:20') and t.startswith('ActivateSheet'):
            # page error: authors belong to Transpost (see vote.html / awards.html)
            t = 'Transpost: 360度どこからでも見ることができる立体映像ディスプレイ'
        rows.append(row(2004, k, t, split_authors(a)))
    ch = rd(W + 'WISS2004_wiss-challenge.html.u8')
    i = ch.index('採用されたシステム')
    seg = ch[i:]
    # entries: title line then author line
    lines = [l for l in (txt(x) for x in re.split(r'(?i)<br\s*/?>|<li[^>]*>|</li>|<p>|</p>|\n', seg)) if l]
    j = lines.index('以下の4件の応募があり、4件とも運用して頂くことになりました。')
    for k in range(4):
        rows.append(row(2004, 'その他', 'WISS Challenge: ' + lines[j+1+2*k], split_authors(lines[j+2+2*k])))
    return rows, lines


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    res = {}
    res[1994] = y1994_95(1994)
    res[1995] = y1994_95(1995)
    res[1996] = y1996()
    for y in (1997, 1998, 1999):
        res[y] = y1997_99(y)
    res[2000] = y2000()
    res[2001] = y2001()
    res[2002] = y2002()
    res[2003] = y2003()
    r4, chlines = y2004()
    res[2004] = r4
    print('CHALLENGE', chlines[:20])
    extra = getattr(sys.modules[__name__], 'EXTRA', {})
    for y, rows in res.items():
        rows = rows + extra.get(y, [])
        with open(OUT + f'{y}.tsv', 'w') as f:
            f.write('year\tkind\ttitle\tauthors\tfirst_author\n')
            for r in rows:
                f.write('\t'.join(c.replace('\t', ' ').replace('\n', ' ') for c in r) + '\n')
        from collections import Counter
        print(y, dict(Counter(r[1] for r in rows)))
