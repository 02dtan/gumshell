import os, glob, getpass, random
from subprocess import *

class GumError(Exception):
    pass

#all indices of char in string for nested token parsing
def sfind(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]

#strip formatting
def st(s):
    return s[:-1].decode('utf-8')

#split input by command. can be used for more than | pipe but only using it for that
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

#parse nested subcommands
def parseNestedParens(s):
    stack=[]
    for i,c in enumerate(s):
        if c=='$' and s[i+1]=='(':
            stack.append(i)
        elif c==')' and stack:
            start=stack.pop()
            yield (len(stack), s[start+2:i], start)

#process nested subcommands (in conjunction with parseNestedParents each iteration)
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

#JANK helper function for processNestedParents because the actual function won't return
### (DON'T ASK ME WHY I DON'T KNOW)
def pHelp(s):
    try:
        processNestedParens(s)
    except Exception as e:
        return e.args[0]

#now for processing of string literals - at this stage, CMDS is a list of strings.
def strings(cmdlist):
    buffer, single, check = [], [], ['\'', '\"']
    readable, c = [], -1
    cmds = [i.split(" ") for i in cmdlist]
    for cmd in cmds:
        c += 1
        readable.append([])
        for token in cmd:
            if len(token)>0:
                if (token[0] in check or token[-1] in check) or len(single)>0:
                    if (token[0] == token[-1]) and token[0] in check:
                        if token[0] == '\'' and len(token.strip('\''))>0:
                            readable[c].append(token.strip('\''))
                        elif token[0] == '\"' and len(token.strip('\"'))>0:
                            readable[c].append(token.strip('\"'))
                    elif token[0] in check:#implicit beginning of whitespaced literal
                        if token[0] == '\'':
                            single.append(True)
                        else:
                            single.append(False)
                        buffer.append(token[1:])
                    elif token[-1] in check:
                        current_buffer=single.pop()
                        if (current_buffer and token[-1] == '\'') or (not current_buffer and token[-1] == '\"'):
                            buffer.append(token[:-1])
                        if len(single)==0:
                            readable[c].append(' '.join(buffer))
                            buffer.clear()
                    else:
                        buffer.append(token)
                else:
                    full = glob.glob(token)
                    if len(full)>0:
                        for g in glob.glob(token):
                            readable[c].append(g)
                    else:
                        readable[c].append(token.replace('\\', ''))
    return readable

#EVERY actual input iteration returns list of commands via this.
def parseInput():
    i = input('%s %s$ ' % ((os.getcwd().split('/')[-1] if os.getcwd().split('/')[-1]
        != getpass.getuser() else '~'), getpass.getuser()))
    if i.split(' ')[0] == "exit":
        raise GumError
    cmds = []
    cmds.extend([stri.strip() for stri in escaped_split(i, '|')])
    for i in range(len(cmds)):
        cmds[i] = pHelp(cmds[i])
    return strings(cmds)

def eight_ball():
    random.seed()
    result = random.randint(0, 7)
    print("[GUM-BALL] SAYS:")
    if result == 0:
        print("\
                ____\n \
            ,dP9CGG88@b,\n \
          ,IP      Y888@@b,\n \
         dIi  YES   G8888@b\n \
        dCII        G8888@@b\n \
        GCCIi     ,GG8888@@@\n \
        GGCCCCCCCGGG88888@@@\n \
        GGGGCCCGGGG88888@@@@...\n \
        Y8GGGGGG8888888@@@@P.....\n \
         Y88888888888@@@@@P......\n \
         `Y8888888@@@@@@@P\'......\n \
            `@@@@@@@@@P'.......\n \
                \"\"\"\"........")
    elif result == 1:
        print("\
                ____\n \
            ,dP9CGG88@b,\n \
          ,IP      Y888@@b,\n \
         dIi  FUCK  G8888@b\n \
        dCII  THAT  G8888@@b\n \
        GCCIi     ,GG8888@@@\n \
        GGCCCCCCCGGG88888@@@\n \
        GGGGCCCGGGG88888@@@@...\n \
        Y8GGGGGG8888888@@@@P.....\n \
         Y88888888888@@@@@P......\n \
         `Y8888888@@@@@@@P\'......\n \
            `@@@@@@@@@P'.......\n \
                \"\"\"\"........")
    elif result == 2:
        print("\
                ____\n \
            ,dP9CGG88@b,\n \
          ,IP      Y888@@b,\n \
         dIi  ASK   G8888@b\n \
        dCII AGAIN  G8888@@b\n \
        GCCIi     ,GG8888@@@\n \
        GGCCCCCCCGGG88888@@@\n \
        GGGGCCCGGGG88888@@@@...\n \
        Y8GGGGGG8888888@@@@P.....\n \
         Y88888888888@@@@@P......\n \
         `Y8888888@@@@@@@P\'......\n \
            `@@@@@@@@@P'.......\n \
                \"\"\"\"........")
    elif result == 3:
        print("\
                ____\n \
            ,dP9CGG88@b,\n \
          ,IP      Y888@@b,\n \
         dIi   NO   G8888@b\n \
        dCII DOUBT! G8888@@b\n \
        GCCIi     ,GG8888@@@\n \
        GGCCCCCCCGGG88888@@@\n \
        GGGGCCCGGGG88888@@@@...\n \
        Y8GGGGGG8888888@@@@P.....\n \
         Y88888888888@@@@@P......\n \
         `Y8888888@@@@@@@P\'......\n \
            `@@@@@@@@@P'.......\n \
                \"\"\"\"........")
    elif result == 4:
        print("\
                ____\n \
            ,dP9CGG88@b,\n \
          ,IP      Y888@@b,\n \
         dIi   DO   G8888@b\n \
        dCII  COKE  G8888@@b\n \
        GCCIi     ,GG8888@@@\n \
        GGCCCCCCCGGG88888@@@\n \
        GGGGCCCGGGG88888@@@@...\n \
        Y8GGGGGG8888888@@@@P.....\n \
         Y88888888888@@@@@P......\n \
         `Y8888888@@@@@@@P\'......\n \
            `@@@@@@@@@P'.......\n \
                \"\"\"\"........")
    elif result == 5:
        print("\
                ____\n \
            ,dP9CGG88@b,\n \
          ,IP      Y888@@b,\n \
         dIi   NO   G8888@b\n \
        dCII  WAY   G8888@@b\n \
        GCCIi     ,GG8888@@@\n \
        GGCCCCCCCGGG88888@@@\n \
        GGGGCCCGGGG88888@@@@...\n \
        Y8GGGGGG8888888@@@@P.....\n \
         Y88888888888@@@@@P......\n \
         `Y8888888@@@@@@@P\'......\n \
            `@@@@@@@@@P'.......\n \
                \"\"\"\"........")
    elif result == 6:
        print("\
                ____\n \
            ,dP9CGG88@b,\n \
          ,IP      Y888@@b,\n \
         dIi  DOUBT G8888@b\n \
        dCII   FUL  G8888@@b\n \
        GCCIi     ,GG8888@@@\n \
        GGCCCCCCCGGG88888@@@\n \
        GGGGCCCGGGG88888@@@@...\n \
        Y8GGGGGG8888888@@@@P.....\n \
         Y88888888888@@@@@P......\n \
         `Y8888888@@@@@@@P\'......\n \
            `@@@@@@@@@P'.......\n \
                \"\"\"\"........")
    elif result == 7:
        print("\
                ____\n \
            ,dP9CGG88@b,\n \
          ,IP      Y888@@b,\n \
         dIi  REPLY G8888@b\n \
        dCII  HAZY  G8888@@b\n \
        GCCIi     ,GG8888@@@\n \
        GGCCCCCCCGGG88888@@@\n \
        GGGGCCCGGGG88888@@@@...\n \
        Y8GGGGGG8888888@@@@P.....\n \
         Y88888888888@@@@@P......\n \
         `Y8888888@@@@@@@P\'......\n \
            `@@@@@@@@@P'.......\n \
                \"\"\"\"........")
