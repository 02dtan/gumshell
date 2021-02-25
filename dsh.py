import sys, os

def shellLoop():
    cmd = None
    status = True
    while status:
        cmd = input("$ ")
        list = cmd.split(" ")
        if list[0] == "exit":
            status = False
        elif len(list) > 1 and list[1] != '':
            os.system(cmd)
        else:
            os.system(list[0])

shellLoop()
