import re, sys
sys.path.insert(0, 'WORK/scripts_1319')
from parse import parse
OUT='WORK/out/'
L,S,N='登壇ロング','登壇ショート','登壇（区別なし）'
# 議論枠採録の論文は N（ロングでもショートでもない）とする
ORAL={
 '2013':[N]*19,
 '2014':[L,L,L,L, L,S,S,S, L,L,L, L,L,S, L,S,S, L,L,S],
 '2015':[N]*19,
 '2016':[L,L,S,S,S, L,S,S,L, L,L,L,L,S, S,S,S,N, L,L,L,S,S, L,S,S],
 '2017':[L,S,S,S, L,S,S,S, L,S,S,S, L,L,N, L,S,S, S,S,S],
 '2018':[L,S,S, S,S,S,S, L,L,S, L,L,S, L,S,S],
 '2019':[S,S,S,L, S,S,S,S,N, L,L,N, S,S,L,L],
}
EXTRA={
 '2013':[('招待講演','智猶水也：研究構想の経験から','石田亨(京都大学)')],
 '2014':[('招待講演','楽器インタフェイスの歴史と、新しい楽器への挑戦','櫻田 信弥（ヤマハ株式会社 楽器・音響開発本部 NVPプロジェクト 企画担当技師）'),
         ('招待講演','2045年問題・・・コンピュータが人類を超える日','松田卓也（NPO法人あいんしゅたいん副理事長）')],
 '2015':[('招待講演','音声分析による感情推定とその応用','光吉 俊二（東京大学大学院医学系研究科社会連携講座特任講師）')],
 '2016':[('招待講演','アナログメカの魅力 ～先人たちの知恵と工夫のモノづくり～','木村雅人（トヨタ産業技術記念館）')],
 '2019':[('国際会議招待発表','BBeep: A Sonic Collision Avoidance System for Blind Travellers and Nearby Pedestrians (CHI \'19)','Seita Kayukawa, Keita Higuchi, João Guerreiro, Shigeo Morishima, Yoichi Sato, Kris Kitani, and Chieko Asakawa'),
         ('国際会議招待発表','REsCUE: A framework for REal-time feedback on behavioral CUEs using multimodal anomaly detection (CHI \'19)','Riku Arakawa and Hiromu Yakura'),
         ('国際会議招待発表','Magneto-Haptics: Embedding Magnetic Force Feedback for Physical Interactions (UIST \'18)','Masa Ogata')],
}
def split_authors(raw):
    s=raw
    # 括弧（所属）を内側から取り除き、区切りに置き換える
    prev=None
    while prev!=s:
        prev=s
        s=re.sub(r'[（(][^（）()]*[）)]',';',s)
    s=re.sub(r',?\s+and\s+',';',s)
    parts=[p.strip(' 　') for p in re.split(r'[,，、;；]',s)]
    return [p for p in parts if p]
def clean_first(n):
    n=re.sub(r'[†‡§¶∗*＊]','',n)
    n=re.sub(r'(?<=[぀-ヿ一-鿿])[a-z]+$','',n)
    return n.strip(' 　')
def tsvsafe(s): return re.sub(r'[\t\r\n]+',' ',s).strip()
def build(y):
    ents=parse(y)
    rows=[]; oi=0
    for e in ents:
        c=e['cat']
        if c=='登壇発表':
            kind=ORAL[y][oi]; oi+=1
        elif c=='ロングティザー発表': kind='その他'
        elif c.startswith('デモ'): kind='デモ'
        elif c=='巻頭': continue
        else: raise Exception(c)
        au=split_authors(e['authors_raw'])
        rows.append((y,kind,e['title'],au))
    assert oi==len(ORAL[y]), (y,oi,len(ORAL[y]))
    for k,t,a in EXTRA.get(y,[]):
        rows.append((y,k,t,split_authors(a)))
    with open(OUT+f'{y}.tsv','w',encoding='utf-8') as f:
        f.write('year\tkind\ttitle\tauthors\tfirst_author\n')
        for y_,k,t,au in rows:
            f.write('\t'.join([y_,k,tsvsafe(t),tsvsafe(';'.join(au)),tsvsafe(clean_first(au[0]) if au else '')])+'\n')
    return rows
if __name__=='__main__':
    for y in sys.argv[1:]: build(y)
