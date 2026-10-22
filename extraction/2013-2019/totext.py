import sys,re,html
b=open(sys.argv[1],'rb').read()
for enc in ('utf-8','cp932','euc-jp'):
    try: s=b.decode(enc); break
    except: pass
s=re.sub(r'<(script|style)[^>]*>.*?</\1>','',s,flags=re.S|re.I)
s=re.sub(r'<br\s*/?>|</p>|</li>|</h\d>|</tr>|</div>','\n',s,flags=re.I)
s=re.sub(r'<td[^>]*>',' | ',s,flags=re.I)
s=re.sub(r'<[^>]+>','',s)
s=html.unescape(s)
s=re.sub(r'[ \t　]+',' ',s)
s=re.sub(r'\n\s*\n+','\n',s)
print(s)
