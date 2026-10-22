import re, sys, html, json
WEB='WORK/web/'
def clean(s):
    s=re.sub(r'<[^>]+>','',s)
    s=html.unescape(s)
    s=re.sub(r'[\t\r\n]+',' ',s)
    s=re.sub(r'\s+',' ',s).strip()
    return s
def parse(y):
    h=open(WEB+f'p{y}.html',encoding='utf-8',errors='replace').read()
    h=re.sub(r'<!--.*?-->','',h,flags=re.S)
    cat=sess=None
    out=[]
    tok=re.compile(r'<h2[^>]*>(.*?)</h2>|<h3[^>]*>(.*?)</h3>|<span class="title">(.*?)</span>(.*?)<span class="authors">(.*?)</span>',re.S)
    for m in tok.finditer(h):
        if m.group(1) is not None: cat=clean(m.group(1)); sess=None
        elif m.group(2) is not None: sess=clean(m.group(2))
        else:
            links=re.findall(r'href="([^"]*)"',m.group(4))
            out.append(dict(cat=cat,sess=sess,title=clean(m.group(3)),authors_raw=clean(m.group(5)),links=links))
    return out
if __name__=='__main__':
    y=sys.argv[1]
    for e in parse(y):
        print(e['cat'],'|',e['sess'],'|',e['title'],'|',e['authors_raw'],'|',' '.join(e['links'][:1]))
