# 2020-2025年の予稿集とプログラムから、年ごとのTSVを作る
import re, sys, os, json, unicodedata
sys.path.insert(0, os.path.dirname(__file__))
from parse_proc import parse
BASE='WORK'
SEP=set('，,、;；')
def split_authors(raw):
    # 括弧（入れ子を含む）を区切りとして取り除き、区切り記号で分ける
    out=[]; buf=''; depth=0
    for ch in raw:
        if ch in '(（':
            depth+=1
            if depth==1: out.append(buf); buf=''
            continue
        if ch in ')）':
            if depth>0: depth-=1
            continue
        if depth>0: continue
        if ch in SEP:
            out.append(buf); buf=''; continue
        buf+=ch
    out.append(buf)
    names=[]
    for n in out:
        n=re.sub(r'\s+',' ',n).strip(' ・')
        if n: names.append(n)
    return names
def prog_tags(y):
    p=f'{BASE}/web2/prog_{y}.txt'
    tags={}
    for l in open(p,encoding='utf-8'):
        m=re.match(r'^\[(\w+)\]\s*(.*?)\s*(ロング発表|ショート発表|議論枠発表|国際発表)\s*$',l.strip())
        if m: tags[m.group(1).lstrip('0')]=(m.group(3),m.group(2))
    return tags
SECKIND={'登壇発表':None,'査読なし発表':'デモ','ロングティザー発表':'その他','デモポスター発表':'デモ',
 'デモ発表':'デモ','国際学会招待発表':'国際学会招待発表','国際会議招待発表':'国際学会招待発表','WISS Challenge':'その他'}
TAGKIND={'ロング発表':'登壇ロング','ショート発表':'登壇ショート','議論枠発表':'登壇ショート','国際発表':'国際学会招待発表'}
KEYNOTE={2024:('WISS30周年企画 特別講演',['増井 俊之','暦本 純一','小池 英樹']),
         2025:('WISS 2025 特別講演 WISSから広がる道',['小松 弘幸','小室真紀','門村 亜珠沙','神原 啓介'])}
def norm(s): return re.sub(r'\s+','',unicodedata.normalize('NFKC',s))
for y in range(2020,2026):
    ents=parse(f'{BASE}/web/p{y}.html')
    tags=prog_tags(y)
    rows=[]; log=[]
    for e in ents:
        if not e['authors_raw']:
            log.append(f"skip(no authors): [{e['num']}] {e['title']}"); continue
        kind=SECKIND[e['section']]
        if kind is None:
            t=tags.get(e['num'].lstrip('0'))
            if t:
                kind=TAGKIND[t[0]]
                if norm(t[1])!=norm(e['title']): log.append(f"TITLE MISMATCH [{e['num']}] proc={e['title']} | prog={t[1]}")
            else: kind='登壇（区別なし）'
        au=split_authors(e['authors_raw'])
        rows.append((str(y),kind,e['title'],';'.join(au),au[0],e['section'],e['num']))
    if y in KEYNOTE:
        t,sp=KEYNOTE[y]
        for s in sp: rows.append((str(y),'招待講演',t,s,s,'特別講演',''))
    with open(f'{BASE}/out/{y}.tsv','w',encoding='utf-8') as f:
        f.write('year\tkind\ttitle\tauthors\tfirst_author\n')
        for r in rows: f.write('\t'.join(r[:5])+'\n')
    with open(f'{BASE}/debug2020s/{y}.debug.tsv','w',encoding='utf-8') as f:
        for r in rows: f.write('\t'.join(r)+'\n')
    from collections import Counter
    print(y, dict(Counter(r[1] for r in rows)), 'tags', len(tags))
    for l in log: print('  ',l)
