import re,sys,html
s=open(sys.argv[1]).read()
s=re.sub(r'<!--.*?-->','',s,flags=re.S)
s=re.sub(r'(?is)<font color=green.*?</font>','',s)
s=re.sub(r'(?is)<font[^>]*>(\s*\*\s*)</font>','<STAR>',s)
s=re.sub(r'(?is)</?(a|font|b|i|strong|em|span|p|table|tr|td|th|tbody|div|center|small|big|u)\b[^>]*>','',s)
s=re.sub(r'(?i)</br>|<br\s*/?>','<BR>',s)
toks=re.split(r'(?i)(<h\d[^>]*>.*?</h\d>|<li[^>]*>|<dt[^>]*>|<dd[^>]*>|</ul>|</ol>|<hr[^>]*>)',s,flags=re.S)
for t in toks:
    if not t.strip(): continue
    t2=re.sub(r'<(?!BR|STAR)[^>]*>','',t)
    t2=html.unescape(t2); t2=re.sub(r'\s+',' ',t2).strip()
    if re.match(r'(?i)<h\d',t): print('##',t2)
    elif re.match(r'(?i)<(li|dt|dd)',t): print('--')
    elif t2: print('   ',t2)
