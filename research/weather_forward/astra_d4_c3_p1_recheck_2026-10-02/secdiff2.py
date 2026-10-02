"""Spec section byte comparison 4423c5c3 -> 61f4904f (sections split at '## n' / '### n.m[a-z]' headings)."""
import re, hashlib
def secs(path):
    out = {}; cur = 'HEADER'; buf = []
    for line in open(path, encoding='utf-8'):
        m = re.match(r'^(#{2,3}) (\d+(\.\d+[a-z]?)?)\b', line)
        if m:
            out[cur] = ''.join(buf); cur = m.group(2); buf = []
        buf.append(line)
    out[cur] = ''.join(buf)
    return out
o, n = secs('spec_old.md'), secs('spec_new.md')
keys = list(dict.fromkeys(list(o) + list(n)))
same, diff = [], []
for k in keys:
    (same if o.get(k) == n.get(k) else diff).append(k)
print('IDENTICAL:', ' '.join(same))
print('CHANGED/NEW:', ' '.join(diff))
print('OWNER-FROZEN / R3 SURFACES:')
for k in ('3', '4', '4.1', '5', '5.1', '5.2', '5.3', '11.1', '11.2', '11.3', '12', '12.1', '12.2', '12.3', '12.4', '13', '14', '14.1', '14.2', '14.3', '15', '15.1', '15.2', '15.3', '16', '17.1', '17.2', '17.4', '17.5', '17.6', '17.7', '8.5b', '8.5c', '10.2', '22', '23', '25'):
    print(' ', k, 'identical' if o.get(k) == n.get(k) else 'CHANGED', hashlib.sha256(n.get(k, '').encode()).hexdigest()[:12])
