import re,csv
B='WORK/'
def norm(s): return re.sub(r'[\s　:：･・\-－―〜～"“”]','',s)
for y in range(2005,2013):
    rows=list(csv.DictReader(open(f'{B}out/{y}.tsv'),delimiter='\t'))
    # (A) 予稿集の文字版との突き合わせ: 題名の行の後、次の題名の前に第一著者がいるか
    lines=[l.strip() for l in open(f'{B}web/p{y}.txt',encoding='utf-8',errors='replace')]
    nl=[norm(l) for l in lines]
    bad=0
    for r in rows:
        if r['kind']=='招待講演' and y==2012: continue
        t=norm(r['title'])[:25]
        idx=[i for i,l in enumerate(nl) if l.startswith(t) or t in l]
        if not idx: print(y,'TXT題名なし',r['title']);bad+=1;continue
        fa=norm(r['first_author'])
        ok=any(fa in ''.join(nl[i+1:i+5]) for i in idx)
        if not ok: print(y,'TXT著者ずれ?',r['title'],r['first_author']);bad+=1
    # (B) プログラムとの突き合わせ（登壇のみ）
    pf=f'{B}prog/prog{y}.txt' if y>2005 else f'{B}web/y2005.txt'
    ptxt=norm(open(pf,encoding='utf-8',errors='replace').read())
    orals=[r for r in rows if r['kind'].startswith('登壇')]
    pb=0
    for r in orals:
        t=norm(r['title'])
        # 題名の一部（先頭12字か末尾12字）がプログラムにあり、その直後200字以内に第一著者
        found=False
        for key in [t[:12],t[-12:],t[2:14]]:
            for m in re.finditer(re.escape(key),ptxt):
                if norm(r['first_author'].replace(' ','')) in ptxt[m.end():m.end()+250] or norm(r['first_author']) in ptxt[m.end():m.end()+250]:
                    found=True;break
            if found:break
        if not found: print(y,'PROG照合できず',r['title'],r['first_author']);pb+=1
    # 生HTMLの題名の数
    print(y,'行数',len(rows),'登壇',len(orals),'TXT不一致',bad,'PROG不一致',pb)
