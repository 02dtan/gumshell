#MISSING SOME IMPORTS
#SAVED AS VERSION CONTROL. USE GIO PY SUITE NOW
def parseInputLegacy():
    i = input(colored('%s %s$ ' % ((os.getcwd().split('/')[-1] if os.getcwd().split('/')[-1]
        != getpass.getuser() else '~'), getpass.getuser()), 'red'))
    if i.split(' ')[0] == "exit":
        raise GumError#DANGEROUS for errortype later
    cmds, c = [[]], 0
    s = shlex.shlex(i, posix=True)
    s.quotes=''
    s.escape=''
    s.whitespace_split = True
    buffer, single, check = [], [], ['\'', '\"']
    for token in s:
        if len(token)>0:
            #manual quotation handling for regex, escape, literal
            if (token[0] in check or token[-1] in check) or len(single)>0:
                if (token[0] == token[-1]) and (token[0] == '\'' or token[0] == '\"'):
                    if token[0] == '\'' and len(token.strip('\'')) > 0:
                        if token.strip('\'')[0] == '$': #$(xyz)
                            if '(' in token and ')' in token:
                                temp = token.split('(')[1].split(')')[0]
                                cmds[c].append(st(check_output(temp)))
                        else:
                            cmds[c].append(token.strip('\''))
                    elif token[0] == '\"' and len(token.strip('\"')) > 0:
                        if token.strip('\"')[0] == '$': #$(xyz)
                            if '(' in token and ')' in token:
                                temp = token.split('(')[1].split(')')[0]
                                cmds[c].append(st(check_output(temp)))
                        else:
                            cmds[c].append(token.strip('\"'))
                elif token[0] in check:#implicit beginning of whitespaced literal
                    if token[0] == '\'':
                        single.append(True)
                    else:
                        single.append(False)
                    if token[0] == '$': #$(xyz)
                        if '(' in token and ')' in token:
                            temp = token.split('(')[1].split(')')[0]
                            buffer.append(st(check_output(temp)))
                    else:
                        buffer.append(token[1:])
                elif token[-1] in check:
                    current_buffer=single.pop()
                    if token[0] == '$': #$(xyz)
                        if '(' in token and ')' in token:
                            temp = token.split('(')[1].split(')')[0]
                            buffer.append(st(check_output(temp)))
                    elif (current_buffer and token[-1] == '\'') or (not current_buffer and token[-1] == '\"'):
                         buffer.append(token[:-1])
                    if len(single)==0:
                        cmds[c].append(' '.join(buffer))
                        buffer.clear()
                else:
                    if token[0] == '$': #$(xyz)
                        if '(' in token and ')' in token:
                            temp = token.split('(')[1].split(')')[0]
                            buffer.append(st(check_output(temp)))
                    else:
                        buffer.append(token)
            else:
                #clear to parse
                if token == '|':
                    c += 1
                    cmds.append([])
                elif '|' in token and '\\|' not in token:
                    l = token.split('|')
                    for term in l[:-1]:
                        if term != '':
                            cmds[c].append(term)
                        c+=1
                        cmds.append([])
                    if l[-1] != '':
                        cmds[c].append(l[-1])
                else:
                    #take care of nonescaped wildcards
                    if token[0] == '$': #$(xyz)
                        if '(' in token and ')' in token:
                            temp = token.split('(')[1].split(')')[0]
                            cmds[c].append(st(check_output(temp)))
                    else:
                        full = glob.glob(token)
                        if len(full)>0:
                            for g in glob.glob(token):
                                cmds[c].append(g)
                        else:
                            #take care of normal shlex escape processing bc I told shlex not to for literals
                            cmds[c].append(token.replace('\\', ''))
    return cmds
