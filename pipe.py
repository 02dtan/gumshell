import re, os
from subprocess import *

stre = 'ls|grep "\.*\(jpg\|txt\)"'
stri = 'cat ok.txt| grep "last" |uniq'
strin = 'echo ok'

def escaped_split(s, delim):
    ret = []
    current = []
    itr = iter(s)
    for ch in itr:
        if ch == '\\':
            try:
                current.append('\\')
                current.append(next(itr))
            except StopIteration:
                pass
        elif ch == delim:
            ret.append(''.join(current))
            current=[]
        else:
            current.append(ch)
    ret.append(''.join(current))
    return ret

for i in escaped_split(strin, '|'):
    print(i.strip())
