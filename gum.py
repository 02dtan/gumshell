import os, glob, shlex, getpass, signal, curses
from termcolor import colored
from subprocess import *

class GumError(Exception):
    pass

#with termcolor for debug only
def printc(s):
    print(colored(s,'red'))

def jobs_update(jobs):
    active = check_output(["ps"])
    final = []
    for job in jobs:
        if job in [t.decode('utf-8').split(' ')[0] for t in active.split(b'\n')[1:]]:
            final.append(job)
    return final

#formatting next
def job_parse(jobs):
    active = check_output(["ps"])
    return [j.decode('utf-8') for j in active.split(b'\n')[1:] if j.decode('utf-8').split(' ')[0] in jobs]#might be redundant, don't have brain cells to figure out if so

#local cd
def cd(path = os.path.expanduser("~")):
    return os.chdir(path)

#strip formatting
def st(s):
    return s[:-1].decode('utf-8')

#all input, glob, regex, literal
#FIX: take pipe splits before quote splits to preserve spacing between commands where whitespace_split won't handle
#FIX: RECOGNIZE WHITESPACE in string literal especially on isolated \" or \' which would otherwise create a cmd='' and throw error
#FIX: make sure subcommand operator $() can take MULTI WORD commands -- ie create SAME buffer from quotes for string literal
def parseInput():
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

def shellLoop():
    auto_hist = [] #for up/down arrow in referencing
    jobs = []
    bypass = None
    while True:
        bypass = False
        jobs = jobs_update(jobs)
        try:
            list = parseInput()
        except GumError:
            break
        except KeyboardInterrupt:
            bypass = True
            print('')
        #implicit if len(list) == 0 there is no command passed thus do nothing and loop
        if not bypass:
            if len(list) == 1: #one-command input
                list = list[0]
                if list[0] == "cd":
                    try:
                        cd(list[1]) if len(list)>1 else cd()
                    except FileNotFoundError:
                        printc("-gum: FileNotFoundError: No such file or directory: \'%s\'"%list[1])
                elif list[0] == "8ball":
                    print("[GUM-BALL] SAYS:")
                    printc("\
        ____\n \
    ,dP9CGG88@b,\n \
  ,IP  _   Y888@@b,\n \
 dIi  (_)   G8888@b\n \
dCII  (_)   G8888@@b\n \
GCCIi     ,GG8888@@@\n \
GGCCCCCCCGGG88888@@@\n \
GGGGCCCGGGG88888@@@@...\n \
Y8GGGGGG8888888@@@@P.....\n \
 Y88888888888@@@@@P......\n \
 `Y8888888@@@@@@@P\'......\n \
    `@@@@@@@@@P'.......\n \
        \"\"\"\"........")
                elif list[0] == "jobs":
                    if len(job_parse(jobs))>0:
                        print(check_output(["ps"]).split(b'\n')[0].decode('utf-8'))
                        for h in job_parse(jobs):
                            print(h)
                elif len(' '.join(list)) > 0:
                    if list[-1] == '&':
                        process = Popen(list[:-1])
                        #Popen attributes at https://docs.python.org/2.4/lib/node239.html
                        printc("created job \'%s\' with pid %d"%(' '.join(list), process.pid))
                        jobs.append(str(process.pid))
                        jobs=jobs_update(jobs)
                    else: #fg
                        try:
                            out, err = None, None
                            process = Popen(list, stdout=PIPE, stderr=PIPE)
                            try:
                                process.wait()
                                out, err = process.communicate()
                                process.stdout.close()
                                process.stderr.close()
                                if process.returncode == 0:
                                    if len(st(out))>0:
                                        printc(st(out))#get rid of newline
                                else:
                                    printc(st(err))
                                    #handle jobspecific error
                            except KeyboardInterrupt:#ctrl-c
                                printc(': KeyboardInterrupt')
                                process.send_signal(signal.SIGINT)
                                printc('-gum: Foreground process killed.')
                        except FileNotFoundError:
                            printc("-gum: %s: command not found"%list[0])
                        except Exception as e:
                            pass

            #IMPLEMENT KEYBOARDINTERRUPT HANDLER FOR CTRL C IN PIPE
            elif len(list) > 1: #piping functionality
                processes = []
                processes.append(Popen(list[0], stdout=PIPE, stderr=PIPE))
                ver = True
                for i in range(1, len(list)):
                    try:
                        processes.append(Popen(list[i], stdin=processes[i-1].stdout, stdout=PIPE, stderr=PIPE))
                        if processes[i].returncode != None:
                            #zombie cleanup prior to connection close
                            for p in processes[::-1]:
                                p.wait()
                            raise Exception(processes[i].returncode, processes[i].pid)
                    except FileNotFoundError:
                        printc("-gum: %s: command not found, stream terminated with command \'%s\'"%(list[i][0],list[i-1][0]))
                        ver = False
                        break
                    except Exception as c:
                        printc("CPE with code=%s, related processes terminated"%(c.args[0]))
                        #os.system("kill -- %s"%c.args[1])
                        ver = False
                        break
                if ver:
                    for p in processes[:-1]:
                        p.stdout.close()
                        p.stderr.close()
                    e,f = processes[-1].communicate()
                    printc(st(e))

shellLoop()
