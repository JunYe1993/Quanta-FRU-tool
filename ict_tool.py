import os, sys, glob, subprocess
import re
from toolconfig import PROJECT_NAME
from toolconfig import DEVELOP_STAGE
from datetime import date

rootpath = "ICT/"
tool = rootpath + "a.out"

def get_target():
    targets = []
    if len(sys.argv) == 1:
        print("Please enter the folder name")
    else:
        for name in sys.argv:
            if name == "ict_tool.py":
                continue
            else:
                targets.append("%s_%s_FRU" % (PROJECT_NAME, name))
    return targets

def get_folder():
    folders = []
    pattern = r'.*_.*_FRU_v[0-9]{3}'
    for raw in glob.glob("*"):
        if re.search(pattern, raw):
            folders.append(raw)
    return folders

def check_tool():
    if not os.path.isfile(tool):
        print("Tool (%s) does't exist." % tool)
        exit()

def clean_last():
    # remove folder ICT/*
    for raw in glob.glob(rootpath + "*"):
        if os.path.isdir(raw):
            command = "rm -r %s" % raw
            process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()

def get_bin(folder):
    binfiles = {}
    path = folder + "/linux/FRU_Writer/M1/"
    os.chdir(path)
    for script in glob.glob("*.sh"):
        head, tail = os.path.split(script)
        root, ext  = os.path.splitext(tail)
        proc = subprocess.Popen(["./" + script, root + ".bin"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        proc.stdin.write('123456789012345\n'.encode())
        proc.stdin.write('1234567\n'.encode())
        proc.stdin.write('12345\n'.encode())
        proc.stdin.close()
        proc.wait()
        binfiles
        binfiles[root+".bin"] = path+root+".bin"

    os.chdir('../../../../')
    return binfiles

def move_to_ICT(binfiles, target):
    newpath = rootpath+target
    os.mkdir(newpath)
    for binfile in binfiles.keys():
        os.rename(binfiles[binfile], newpath+"/"+binfile)

def exec_a_out():
    for raw in glob.glob(rootpath+"**/*.bin"):
        head, tail = os.path.split(raw)
        root, ext  = os.path.splitext(tail)
        command = "./%s %s" % (tool, raw)
        with open(head + "/" + root + ".csv", "w") as file:
            process = subprocess.Popen(command.split(), stdout=file)
            output, error = process.communicate()

def get_zip():
    # get file name
    filedate = date.today().strftime("%Y%m%d")
    filename = "%s%s_%s_ICT_%s.zip" % (rootpath, PROJECT_NAME, DEVELOP_STAGE, filedate[2:])

    zipcommand = "zip -r %s %s -x %s -x *.zip" % (filename, rootpath, tool)
    process = subprocess.Popen(zipcommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

if __name__ == "__main__":

    check_tool()
    clean_last()

    targets = get_target()
    folders = get_folder()
    for folder in folders:
        for target in targets:
            if folder.find(target) != -1:
                binfiles = get_bin(folder)
                move_to_ICT(binfiles, target)

    exec_a_out()
    get_zip()
