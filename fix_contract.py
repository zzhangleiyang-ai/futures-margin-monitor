import re
p = r'C:\Users\张雷洋\Documents\sxf\futures-margin-monitor\gen_auto.py'
c = open(p, 'r', encoding='utf-8').read()
# Replace the card header line to include contract code
old = "<span class=\"ck\">'+code+'</span></div>"
new = "<span class=\"ck\">'+code+'</span><span class=\"ck\" style=\"font-size:11px;color:#64748b\">['+sym+']</span></div>"
if old in c:
    c = c.replace(old, new)
    open(p, 'w', encoding='utf-8').write(c)
    print('OK - modified match')
else:
    # Try alternate format
    import re
    # Find the pattern
    m = re.search(r"<span class=\\\"ck\\\">'\+code\+'</span></div>", c)
    if m:
        print('Found with regex')
    else:
        print('Pattern not found, checking line...')
        for i, l in enumerate(c.split('\n')):
            if "ck" in l and "code" in l and "cn" in l:
                print(f'Line {i}: {l.strip()[:120]}')