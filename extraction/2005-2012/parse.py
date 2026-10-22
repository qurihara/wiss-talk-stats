import sys,re,html,json
WEB='WORK/web/'
def load(y):
    b=open(f'{WEB}p{y}.html','rb').read()
    m=re.search(rb'charset=["]?([\w_-]+)',b)
    enc=m.group(1).decode().lower() if m else 'utf-8'
    enc={'shift_jis':'cp932','x-sjis':'cp932','euc-jp':'euc_jis_2004'}.get(enc,enc)
    s=b.decode(enc,errors='replace')
    return s
def clean(t):
    t=re.sub(r'<br\s*/?>',' ',t,flags=re.I)
    t=re.sub(r'<[^>]+>','',t)
    t=html.unescape(t).replace('　',' ')
    t=re.sub(r'\s+',' ',t).strip()
    return t
def items(y):
    s=load(y)
    s=re.sub(r'<!--.*?-->','',s,flags=re.S)
    pat=re.compile(r'<(h2|h3)[^>]*>(.*?)</\1>|<span class"?=?"?(title|authors)"?>(.*?)</span>(?=\s*(?:&nbsp;?|<|$))',re.S|re.I)
    out=[];h2=h3=''
    # more robust: find span title/authors by balanced approach: title span may contain <a>; authors plain
    toks=[]
    for m in re.finditer(r'<(h2|h3)[^>]*>(.*?)</\1>',s,re.S|re.I):
        toks.append((m.start(),m.group(1).lower(),clean(m.group(2))))
    for m in re.finditer(r'<span class"?=?"?(title|authors)"?>',s,re.I):
        # find matching </span> accounting nested spans
        i=m.end();depth=1
        while depth:
            n=re.search(r'<span\b|</span>',s[i:],re.I)
            if not n: break
            if n.group(0).lower().startswith('<span'): depth+=1
            else: depth-=1
            i+=n.end()
        toks.append((m.start(),m.group(1),clean(s[m.end():i-7])))
    toks.sort()
    cur=None
    for pos,k,t in toks:
        if k=='h2': h2=t;h3=''
        elif k=='h3': h3=t
        elif k=='title':
            if cur: out.append(cur)
            cur=dict(h2=h2,h3=h3,title=t,authors=None)
        elif k=='authors':
            if cur is None or cur['authors'] is not None:
                out.append(dict(h2=h2,h3=h3,title=None,authors=t)); continue
            cur['authors']=t
    if cur: out.append(cur)
    return out
if __name__=='__main__':
    for it in items(sys.argv[1]):
        print(it['h2'],'|',it['h3'],'|',it['title'],'|',it['authors'])
