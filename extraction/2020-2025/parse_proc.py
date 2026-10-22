# 予稿集のHTMLから節と論文の一覧を取り出す
import re, html, sys, json
def clean(s):
    s=re.sub(r'<[^>]+>','',s)
    s=html.unescape(s)
    s=s.replace('\t',' ').replace('\r',' ').replace('\n',' ')
    return re.sub(r'\s+',' ',s).strip()
def parse(path):
    s=open(path,encoding='utf-8').read()
    # h2 見出しと entry ブロックを順に拾う。title の閉じタグ抜けに備え、authors の手前で切る
    toks=re.finditer(r'<h2[^>]*>(.*?)</h2>|<div class="entry">(.*?)(?=<div class="entry">|<h2|</body>)',s,re.S)
    sec=None; out=[]
    for m in toks:
        if m.group(1) is not None:
            sec=clean(m.group(1)); continue
        b=m.group(2)
        mt=re.search(r'<p class="title">(.*?)(?:</p>|<p class="authors">)',b,re.S)
        ma=re.search(r'<p class="authors">(.*?)</p>',b,re.S)
        t=re.sub(r'<a [^>]*>.*?</a>','',mt.group(1),flags=re.S)
        t=clean(t)
        mm=re.match(r'\[([^\]]+)\]\s*(.*)$',t)
        num,title=(mm.group(1),mm.group(2)) if mm else ('',t)
        out.append(dict(section=sec,num=num,title=title,authors_raw=clean(ma.group(1)) if ma else ''))
    return out
if __name__=='__main__':
    for e in parse(sys.argv[1]): print(json.dumps(e,ensure_ascii=False))
