import os, signal, random
from gio import * #OS is included here but ok
from subprocess import *

def handler(signal_num, stack_frame):
    print(": Process stop")
    print("-gum: Foreground process paused.")
    raise GumError

#constant ctrlZ listener
signal.signal(signal.SIGTSTP, handler)

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
                        print("-gum: FileNotFoundError: No such file or directory: \'%s\'"%list[1])
                elif list[0] == "bg":
                    if list[1] not in jobs:
                        print("-gum: job does not exist")
                    else:
                        try:
                            Popen(["kill", "-CONT", list[1]])
                            print("-gum: job "+list[1]+" continued in background")
                        except Exception:
                            print("-gum: unidentified error occurred")
                elif list[0] == "fg":
                    if list[1] not in jobs:
                        print("-gum: job does not exist")
                    else:
                        try:
                            out, err = None, None
                            process = Popen(["kill", "-CONT", list[1]], stdout=PIPE, stderr=PIPE)
                            try:
                                process.wait()
                                out, err = process.communicate()
                                process.stdout.close()
                                process.stderr.close()
                                if process.returncode == 0:
                                    if len(st(out))>0:
                                        print(st(out))#get rid of newline
                                else:
                                    print(st(err))
                                    #handle jobspecific error
                            except KeyboardInterrupt:#ctrl-c
                                print(': KeyboardInterrupt')
                                process.send_signal(signal.SIGINT)
                                print('-gum: Foreground process killed.')
                        except Exception as e:
                            pass
                elif list[0] == "8ball":
                        eight_ball()
                elif list[0] == "nyan":
                    run(["open", "http://www.nyan.cat/index.php?cat=technyancolor"])
                elif list[0] == "jobs":
                    if len(job_parse(jobs))>0:
                        print(check_output(["ps"]).split(b'\n')[0].decode('utf-8'))
                        for h in job_parse(jobs):
                            print(h)
                elif len(' '.join(list)) > 0:
                    if list[-1] == '&':
                        process = Popen(list[:-1])
                        #Popen attributes at https://docs.python.org/2.4/lib/node239.html
                        print("-gum: created job \'%s\' with pid %d"%(' '.join(list), process.pid))
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
                                        print(st(out))#get rid of newline
                                else:
                                    print(st(err))
                                    #handle jobspecific error
                            except KeyboardInterrupt:#ctrl-c
                                print(': KeyboardInterrupt')
                                process.send_signal(signal.SIGINT)
                                print('-gum: Foreground process killed.')
                        except FileNotFoundError:
                            print("-gum: %s: command not found"%list[0])
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
                        print("-gum: %s: command not found, stream terminated with command \'%s\'"%(list[i][0],list[i-1][0]))
                        ver = False
                        break
                    except Exception as c:
                        print("-gum: CPE with code=%s, related processes terminated"%(c.args[0]))
                        ver = False
                        break
                if ver:
                    for p in processes[:-1]:
                        p.stdout.close()
                        p.stderr.close()
                    e,f = processes[-1].communicate()
                    print(st(e))

shellLoop()
