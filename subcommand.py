import re, os
from subprocess import *

stre = 'echo $(echo $(echo $(echo ok) ok) $(echo ok) ok)'
stri = "echo $(ec$(echo ho) ok) ok"
strin = "echo ok"
# print(full)
# subc = re.compile('\$\(.+\){1}')
# print(re.search(subc, str))

#strip formatting
def st(s):
    return s[:-1].decode('utf-8')

def parseNestedParens(s):
    stack=[]
    for i,c in enumerate(s):
        if c=='$' and s[i+1]=='(':
            stack.append(i)
        elif c==')' and stack:
            start=stack.pop()
            yield (len(stack), s[start+2:i], start)

def processNestedParens(s):
    l = list(parseNestedParens(s))
    if len(l)>0:
        sorted(l, key=lambda x: x[0])
        toplevel = l[0][0]
        processing = [i for i in l if i[0] == toplevel]
        for item in processing:
            res = st(check_output(item[1].split(' ')))
            s=s.replace('$('+item[1]+')', res)
        if toplevel > 0:
            processNestedParens(s)
        else:
            raise Exception(s)
    else:
        raise Exception(s)

def pHelp(s):
    try:
        processNestedParens(s)
    except Exception as e:
        return e.args[0]

print(pHelp(strin))
