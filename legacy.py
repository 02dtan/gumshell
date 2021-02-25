import sys, os

def cd(path = os.path.expanduser("~")):
    return os.chdir(path)

def jobs():
    return os.system("ps S")

processes = {"pwd": os.getcwd,
             "cd": cd,
             "jobs": jobs}

def shellLoop():
    cmd = None
    status = True #False=kill
    while status:
        terms = input("$ ").split(" ") #implement substitution with current directory, implement better regex later, can put into one line with cmd declaration
        cmd = terms[0]
        if cmd == "exit":
            status = False
        elif cmd in processes.keys():
            if len(terms)>1 and terms[1] != '':
                if terms[1] != '&':
                    print(processes[cmd](terms[1]))
                else:
                    #return process sigcont in background.
                    return
            else:
                print(processes[cmd]())
        else:
            print("shmeat")

shellLoop()
