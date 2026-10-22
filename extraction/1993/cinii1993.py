import json,re,sys,urllib.request,urllib.parse,time,collections
txt=open(sys.argv[1]).read()
titles=[l.strip().lstrip('*').strip() for l in txt.split('\n') if l.strip().startswith('*') or l.strip()=='並列論理型言語GHCのビジュアル化の試み']
titles=[t for t in titles if t and '主要目次' not in t]
out=[]
for t in titles:
    q=re.split(r'[:：ー\-]',t)[0] if len(t)>25 else t
    q=t[:30]
    url='https://cir.nii.ac.jp/opensearch/all?format=json&count=20&q='+urllib.parse.quote(q)
    try: d=json.load(urllib.request.urlopen(url,timeout=40))
    except Exception as e: d={}
    cands=collections.Counter(); allauth=None
    for i in d.get('items',[]):
        pub=str(i.get('prism:publicationName',''))
        cr=i.get('dc:creator') or []
        if isinstance(cr,str): cr=[cr]
        if not cr: continue
        if 'WISS' in pub or 'インタラクティブシステムとソフトウェア' in pub or True:
            cands[re.sub(r'\s','',cr[0])]+=1
            if ('WISS' in pub or 'インタラクティブ' in pub) and (allauth is None or len(cr)>len(allauth)): allauth=cr
    out.append((t,cands.most_common(3),allauth))
    print(t,'|',cands.most_common(3),'|',allauth,flush=True)
    time.sleep(0.5)
