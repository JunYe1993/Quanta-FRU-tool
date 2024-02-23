import re, os, glob, subprocess
from datetime import date
from shutil import copyfile
from distutils.dir_util import copy_tree

import config as config_reader
from excel import parentheses_off

from toolconfig import PROJECT_BASE
from toolconfig import PROJECT_NAME
from toolconfig import DEVELOP_STAGE

from toolconfig import FRU_SUB_FOLDER_KEY
from toolconfig import FRU_PART_NUMBER_KEY
from toolconfig import FRU_VERSION_KEY
from toolconfig import MERGE_FRU_KEY_LIST

from toolconfig import QPN_MARK
from toolconfig import FRU_MARK
from toolconfig import PRC_MARK
from toolconfig import INI_PUT_MARK
from toolconfig import INI_LEN_MARK

showMsgEnable = False
MODES = ["M1/", "M3/"]

def showMsg(msg, enable=showMsgEnable):
    if enable:
        print(msg)

def folder(config):

    # remove folder _***_FRU_v***
    for raw in glob.glob("*"):
        pattern = r'_(.*)_FRU_v[0-9]+'
        x = re.search(pattern, raw)
        if os.path.isdir(raw) and x != None:
            command = "rm -r %s" % raw
            process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()

    # copy folder from prototype
    for name in config:
        folder = "prototype/chassis" if config[name]["Chassis Info"] else "prototype/no_chassis"
        targetname = "%s_%s_FRU_v001" % (PROJECT_NAME, name)
        # copy
        command = "cp -r %s %s" % (folder, targetname)
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        # set bmcfwtool
        command = "chmod 755 %s" % (targetname+"/linux/bmcfwtool")
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()

def get_folder():
    folders = {}
    for raw in glob.glob("*"):
        pattern = PROJECT_NAME + r'_(.+)_FRU_v[0-9]+'
        x = re.search(pattern, raw)
        if (os.path.isdir(raw) and x):
            folders[x.group(1)] = raw
    # print(folders)
    return folders

def get_txt_files(folder, mode=None):
    path = folder + "/FRU/**/" if mode == None else folder + "/FRU/"+ mode +"/*/"
    return glob.glob(os.path.join(path, "*txt"), recursive=True)

def get_linux_scripts(folder, mode=None):
    path = folder + "/linux/**/" if mode == None else folder + "/linux/*/"+ mode +"/"
    return glob.glob(os.path.join(path, "*sh"), recursive=True)

def get_part_numbers(fru_config={}):
    if fru_config.get(FRU_PART_NUMBER_KEY):
        return fru_config[FRU_PART_NUMBER_KEY]
    else:
        showMsg("Can't find %s in fru_config" % FRU_PART_NUMBER_KEY, True)
        exit()

def match_file_number(folder, fru_config):
    # copy file to match number of part_numbers
    part_numbers_n = len(get_part_numbers(fru_config))

    for mode in MODES:
        # copy FRU/mode/*/
        copyfrom = ""
        for file in get_txt_files(folder):
            if file.find(mode) > 0:
                copyfrom = file
                break
        if copyfrom == "":
            showMsg("Can't find *.txt in FRU/%s" % mode, True)
            exit()
        copyfrom = os.path.dirname(copyfrom)
        for i in range(1, part_numbers_n):
            copy_tree(copyfrom, os.path.dirname(copyfrom)+"/"+str(i))

        # copy linux/mode/*.sh
        copyfrom = ""
        for file in get_linux_scripts(folder, mode):
            if file.find(mode) > 0:
                copyfrom = file
                break
        if copyfrom == "":
            showMsg("Can't find *.sh in linux/%s\n" % mode, True)
            exit()
        for i in range(1, part_numbers_n):
            filename = os.path.dirname(copyfrom)+"/"+str(i)+".sh"
            copyfile(copyfrom, filename)
            os.chmod(filename, 0o755)


def get_line_key(line):
    pattern = r'[\s]{2,}(.*)='
    x = re.search(pattern, line)
    return x.group(1).rstrip() if x != None else None

def get_updated_line(line, value):
    pattern = r'".*"'
    sindex, eindex = re.search(pattern, line).span()
    return line[:sindex+1] + value + line[eindex-1:]

def update_txt_data(file, line, update_list={}):
    key = get_line_key(line)
    if update_list.get(key) != None:
        return get_updated_line(line, parentheses_off(update_list[key]))
    return line

def update_txt_files(folder, fru_config):

    for mode in MODES:

        part_number_index = 0
        files = get_txt_files(folder, mode)
        files.sort()

        for file in files:
            if len(fru_config[FRU_PART_NUMBER_KEY]) == 0:
                continue
            # update content
            # for board merge
            temp_FruConfig = fru_config.copy()
            for key in MERGE_FRU_KEY_LIST:
                temp_FruConfig[key] = fru_config[key][part_number_index]

            context = ""
            isupdated = False
            for line in open(file, "r"):
                newline = update_txt_data(file, line, temp_FruConfig)
                if line != newline:
                    line = newline
                    isupdated = True
                context += line
            fd = open(file, "w")
            fd.write(context)
            part_number_index += 1

            # update file name
            newFileName = os.path.dirname(file)+"/"+temp_FruConfig[FRU_PART_NUMBER_KEY]+".txt"
            os.rename(file, newFileName)

            # show message
            file = newFileName
            showMsg(file + " > name updated.", True)
            showMsg(file + " > data updated.", True)

def get_ini_files(folder, mode=None):
    path = folder + "/FRU/**/" if mode == None else folder + "/FRU/"+ mode +"/*/"
    return glob.glob(os.path.join(path, "*ini"), recursive=True)

def get_ini_line_key(line):
    pattern = r'[\s]{2,}(.*)\('
    x = re.search(pattern, line)
    return x.group(1).strip() if x != None else ""

def update_ini_data(file, line, update_list={}):
    key = get_ini_line_key(line) + "(Y/N)"
    if update_list.get(key) != None:
        if update_list[key] == "Y":
            line = line.replace(INI_PUT_MARK, "Y")
            line = line.replace(INI_LEN_MARK, "2:63")
        elif update_list[key] == "N":
            line = line.replace(INI_PUT_MARK, "N")
            line = line.replace(INI_LEN_MARK, "0:63")
    return line

def update_ini_files(folder, fru_config):

    files = get_ini_files(folder, fru_config["mode"])
    for file in files:
        context = ""
        isupdated = False
        for line in open(file, "r"):
            newline = update_ini_data(file, line, fru_config)
            if line != newline:
                line = newline
                isupdated = True
            context += line
        fd = open(file, "w")
        fd.write(context)

        # show message
        showMsg(file + " > data updated.", True)

def get_ReleaseNote(folder):
    return glob.glob(os.path.join(folder, "*txt"), recursive=True)

def get_procedure(fru):
    if PROJECT_BASE == "Meta-OpenBmc":
        return "fruid-util xxx --write fru.bin"
    elif PROJECT_BASE == "LF-OpenBmc":
        target = {
            "MB"     : [15, 56],
            "PTTV"   : [15, 50],
            "PDB"    : [ 4, 52],
            "MB_SCM" : [29, 54],
            "MB_BSM" : [ 9, 52]
        }
        if fru in target.keys():
            return "dd if=/tmp/fru.bin of=/sys/class/i2c-dev/i2c-%d/device/%d-00%d/eeprom" \
                        % (target[fru][0], target[fru][0], target[fru][1])
        else:
            return "dd if=/tmp/fru.bin of=/sys/class/i2c-dev/i2c-xx/device/xx-00xx/eeprom"

def update_note(line, FRU, update_list={}):
    pattern_version = r'v[0-9].[0-9]{2}'
    pattern_date = r'[0-9]{4}/[0-9]{2}/[0-9]{2}'

    # update version
    new_version = get_fru_version(update_list)
    if new_version != None:
        new_version = "v" + new_version[0] + "." + new_version[1:]
        x = re.search(pattern_version, line)
        if x != None:
            line = line.replace(line[x.start():x.end()], new_version)

    # update part number
    new_pnumber = get_part_numbers(update_list)[0]
    line = line.replace(QPN_MARK, new_pnumber)

    # update fru
    line = line.replace(FRU_MARK, FRU)

    # update date
    new_date = date.today().strftime("%Y/%m/%d")
    x = re.search(pattern_date, line)
    if x != None:
        line = line.replace(line[x.start():x.end()], new_date)

    # update flash procedure
    line = line.replace(PRC_MARK, get_procedure(FRU))

    return line

def update_release_note(folder, fru_config, FRU):
    # expected only one file
    for note in get_ReleaseNote(folder):
        context = ""
        isupdated = False
        for line in open(note, "r"):
            newline = update_note(line, FRU, fru_config)
            if line != newline:
                line = newline
                isupdated = True
            context += line
        fd = open(note, "w")
        fd.write(context)
        msg = " updated." if isupdated else " already updated."
        showMsg(note + " > data" + msg, isupdated)

        new_name = "%s/%s%s" % (os.path.dirname(note), PROJECT_NAME, os.path.basename(note))
        os.rename(note, new_name)

def update_script(folder, fru_config):
    # update file name folder/linux/**/*.sh
    for mode in MODES:
        pn_index = 0
        for script in get_linux_scripts(folder, mode):
            new_content = ""
            for line in open(script, "r"):
                new_content += line.replace(QPN_MARK, fru_config[FRU_SUB_FOLDER_KEY][pn_index])
            with open(script, "w") as s:
                s.write(new_content)

            new_name = os.path.dirname(script)+"/"+fru_config[FRU_PART_NUMBER_KEY][pn_index]+".sh"
            os.rename(script, new_name)
            pn_index += 1

def update_folder_name(folder, fru_config):
    # update folder name folder/FRU/**/*
    folder_names = get_txt_files(folder)
    for name in folder_names:
        index, file = os.path.split(name)
        null, index = os.path.split(index)
        index = int(index) % len(fru_config[FRU_SUB_FOLDER_KEY])
        old = os.path.dirname(name)
        new = os.path.dirname(old)+"/"+fru_config[FRU_SUB_FOLDER_KEY][index]
        os.rename(old, new)

def get_fru_version(config={}):
    if config.get(FRU_VERSION_KEY):
        raw = config[FRU_VERSION_KEY]
        pattern = r'\d.*\d.*\d'
        x = re.search(pattern, raw)
        return x.group(0).replace(".", "")
    return None

def update_folder_fru_version(folder, version):
    if version == "xxx": return

    pattern = r'v[0-9]{3}'
    new_version = "v" + version

    # update file name /folder/Release Note.txt
    for note in get_ReleaseNote(folder):
        _dir = os.path.dirname(note)
        note = os.path.basename(note)
        x = re.search(pattern, note)
        if x != None and note[x.start():x.end()] != new_version:
            new_note = note.replace(note[x.start():x.end()], new_version)
            os.rename(_dir+"/"+note, _dir+"/"+new_note)
            showMsg(_dir+"/"+new_note + " > name updated.", True)
        else:
            showMsg(_dir+"/"+note + " already updated.")

    # update folder name /folder
    if folder[-3:] == version:
        showMsg(folder + " already updated.")
    else:
        new_name = folder[:-3]+version
        os.rename(folder, new_name)
        showMsg(new_name + " > name updated.", True)

def update(config):
    folders = get_folder()
    for FRU in config["txt"]:
        # FRU = "HPDB"
        if folders.get(FRU):
            match_file_number(folders[FRU], config["txt"][FRU])
            update_txt_files(folders[FRU], config["txt"][FRU])
            update_ini_files(folders[FRU], config["m1_ini"][FRU])
            update_ini_files(folders[FRU], config["m3_ini"][FRU])
            update_release_note(folders[FRU], config["txt"][FRU], FRU)
            update_script(folders[FRU], config["txt"][FRU])
            update_folder_name(folders[FRU], config["txt"][FRU])
            update_folder_fru_version(folders[FRU], get_fru_version(config["txt"][FRU]))
        # break


def get_zip():
    # get file name
    filedate = date.today().strftime("%Y%m%d")
    filename = "%s_%s_%s.zip" % (PROJECT_NAME, DEVELOP_STAGE, filedate[2:])

    zipcommand = "zip -r %s . \
                -x *.py \
                -x *.json \
                -x *.zip \
                -x __pycache__* \
                -x prototype* \
                -x .git* \
                -x ICT* \
                " %  filename
    process = subprocess.Popen(zipcommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

if __name__ == "__main__":
    folder(config_reader.read("excel_raw_folder.json"))
    update(config_reader.read_config("excel_raw_output.json"))
    get_zip()
