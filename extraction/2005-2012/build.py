import re,sys
sys.path.insert(0,'WORK/wiss_script')
from parse import items
OUT='WORK/out/'
# ロング（30分枠）の題名の先頭部分。根拠は各年のプログラムのページ
LONG={
 2005:['Information Fishing','Openism','Enzin'],          # 30分枠（時刻表から）
 2006:['Goromi-TV','PodCastle'],                           # 「検索［各30分発表］」
 2007:['あみぐるみのための3次元モデリング','Album Weaver'], # (L)
 2008:['電脳化粧鏡','PhotoelasticTouch: LCD'],             # (Long)
 2009:['Cat@Log'],                                         # (Long)
}
OPEN='(（'; CLOSE=')）'; SEPS=',，、､'
def split_authors(s):
    s=s.strip().strip('"').rstrip('<').strip()
    parts=[];buf='';d=0
    for ch in s:
        if ch in OPEN: d+=1
        elif ch in CLOSE: d=max(0,d-1)
        if ch in SEPS and d==0:
            parts.append(buf);buf=''
        else: buf+=ch
    parts.append(buf)
    out=[]
    for p in parts:
        q='';d=0
        for ch in p:
            if ch in OPEN: d+=1;continue
            if ch in CLOSE: d=max(0,d-1);continue
            if d==0: q+=ch
        q=q.strip().strip('"').strip()
        if q: out.append(q)
    return out
def clean_title(t):
    t=re.sub(r'\s*\((Long|L)\)\s*$','',t)
    if t.startswith('"') and t.endswith('"'):
        t=t[1:-1].replace('""','"')
    return t.strip()
def first_clean(a):
    return re.sub(r'[\s*＊†‡]+$','',a).strip()
def kind_of(y,it):
    h2=it['h2'];h3=it['h3']
    if h2=='登壇発表':
        if h3=='招待講演': return '招待講演'
        if y in LONG:
            return '登壇ロング' if any(it['title'].startswith(p) for p in LONG[y]) else '登壇ショート'
        return '登壇（区別なし）'
    if 'デモ' in h2 or 'ポスター' in h2: return 'デモ'
    return None
def esc(s): return re.sub(r'[\t\r\n]+',' ',s)
for y in range(2005,2013):
    rows=[]
    for it in items(y):
        k=kind_of(y,it)
        if k is None: continue  # まえがき
        auth=it['authors']
        if y==2010 and auth.startswith('ロボットを用いた天井上のオブジェクト移動システム: '):
            auth=auth.split(': ',1)[1]
        al=split_authors(auth)
        rows.append((y,k,clean_title(it['title']),';'.join(al),first_clean(al[0]) if al else ''))
    if y==2012:
        rows.append((2012,'招待講演','岩手県災害対策本部の闘い（仮題）','秋冨慎司','秋冨慎司'))
    with open(f'{OUT}{y}.tsv','w') as f:
        f.write('year\tkind\ttitle\tauthors\tfirst_author\n')
        for r in rows: f.write('\t'.join(esc(str(x)) for x in r)+'\n')
    from collections import Counter
    print(y,dict(Counter(r[1] for r in rows)))
