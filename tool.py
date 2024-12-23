import re, os, glob, subprocess
from datetime import date
from shutil import copyfile
from distutils.dir_util import copy_tree

import config as config_reader

from toolconfig import read_config_json
from toolconfig import parentheses_off

from toolconfig import SUB_FOLDER_KEY
from toolconfig import FRU_PART_NUMBER_KEY
from toolconfig import FRU_VERSION_KEY
from toolconfig import MERGE_FRU_KEY_LIST

PROJECT_NAME = read_config_json()["Project"]["Name"]
DEVELOP_STAGE = read_config_json()["Project"]["Stage"]

### Marker
# non txt and ini files. (ex release_note and bash script ...)
QPN_MARK = "#QPN_Marker" #
FRU_MARK = "#FRU_Marker" #
PRC_MARK = "#PRC_Marker" # command for BMC FRU update (dd or fru-util ...)
# ini
INI_PUT_MARK = "#PUT_Marker"
INI_LEN_MARK = "#LEN_Marker"
# txt
TXT_VAL_MARK = "#VAL_Marker"

showMsgEnable = False
MODES = ["M1/", "M3/", "M5/"]
configs = {}
folders = {}

def showMsg(msg, enable=showMsgEnable):
    if enable:
        print(msg)

def remove_folder(dir):
    command = "rm -r %s" % dir
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

def folder(config):

    # remove folder _***_FRU_v***
    for raw in glob.glob("*"):
        pattern = r'_(.*)_FRU_v[0-9]+'
        x = re.search(pattern, raw)
        if os.path.isdir(raw) and x != None:
            remove_folder(raw)

    # copy folder from prototype
    for name in config:
        folder = "prototype/chassis" if config[name]["Chassis Info"] else "prototype/no_chassis"
        targetname = "%s_%s_FRU_v001" % (config[name]["Project Name"], name)
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
    folderConfig = config_reader.read("excel_raw_folder.json")
    projectNames = {folderConfig[name]["Project Name"] for name in folderConfig}
    for raw in glob.glob("*"):
        if not os.path.isdir(raw):
            continue
        pattern = r'_(.+)_FRU_v[0-9]+$'
        tempraw = raw
        for projectName in projectNames:
            tempraw = tempraw.replace(projectName, "")
        match = re.search(pattern, tempraw)
        if match != None:
            board = match.group(1)
            folders[board] = raw

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

def match_file_number(FRU):
    folder = folders[FRU]
    fru_config = configs["mainData"][FRU]

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

def update_txt_data(file, line, update_list={}):
    key = get_line_key(line)

    if key != None:
        # match keys in config list
        value = ""
        if update_list.get(key) != None:
            value = parentheses_off(update_list[key])

        return line.replace(TXT_VAL_MARK, value)
    else:
        return line

def update_txt_files(FRU):
    folder = folders[FRU]
    fru_config = configs["mainData"][FRU]

    for mode in MODES:

        part_number_index = 0
        files = get_txt_files(folder, mode)

        for file in files:
            if len(fru_config[FRU_PART_NUMBER_KEY]) == 0:
                continue
            # update content
            # for board merge
            temp_FruConfig = fru_config.copy()
            for key in MERGE_FRU_KEY_LIST:
                temp_FruConfig[key] = fru_config[key][part_number_index]

            context = ""
            for line in open(file, "r"):
                line = update_txt_data(file, line, temp_FruConfig)
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

def update_ini_files(FRU, ini_key):
    folder = folders[FRU]
    ini_config = configs[ini_key][FRU]

    if ini_config["enable"] == False:
        remove_folder('%s/FRU/%s' % (folder, ini_config["mode"]))
        remove_folder('%s/linux/FRU_Writer/%s' % (folder, ini_config["mode"]))
        return

    files = get_ini_files(folder, ini_config["mode"])
    for file in files:
        context = ""
        for line in open(file, "r"):
            line = update_ini_data(file, line, ini_config)
            context += line
        fd = open(file, "w")
        fd.write(context)

        # show message
        showMsg(file + " > data updated.", True)

def get_ReleaseNote(folder):
    return glob.glob(os.path.join(folder, "*FRU_Release_Note*"), recursive=True)

def get_procedure(fru):
    # TODO: provide an exact string not just xx in config.json
    config = read_config_json()
    CopyMethod = config["ReleaseNote"]["CopyMethod"]
    return config["ReleaseNote"]["CopyMethod-"+CopyMethod]

def update_note(line, FRU, update_list={}):
    # TODO : these two can be replace by Marker
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

def update_release_note(FRU):
    folder = folders[FRU]
    fru_config = configs["mainData"][FRU]

    # expected only one file
    for note in get_ReleaseNote(folder):
        context = ""
        for line in open(note, "r"):
            line = update_note(line, FRU, fru_config)
            context += line

        fd = open(note, "w")
        fd.write(context)
        showMsg(note + " > data updated")

        new_name = "%s/%s" % (os.path.dirname(note), os.path.basename(note))
        os.rename(note, new_name)

def update_script(FRU):
    folder = folders[FRU]
    fru_config = configs["mainData"][FRU]

    # update file name folder/linux/**/*.sh
    for mode in MODES:
        pn_index = 0
        for script in get_linux_scripts(folder, mode):
            new_content = ""
            for line in open(script, "r"):
                new_content += line.replace(QPN_MARK, fru_config[SUB_FOLDER_KEY][pn_index])
            with open(script, "w") as s:
                s.write(new_content)

            new_name = os.path.dirname(script)+"/"+fru_config[FRU_PART_NUMBER_KEY][pn_index]+".sh"
            os.rename(script, new_name)
            pn_index += 1

def update_folder_name(FRU):
    folder = folders[FRU]
    fru_config = configs["mainData"][FRU]

    # update folder name folder/FRU/**/*
    folder_names = get_txt_files(folder)
    for name in folder_names:
        index, file = os.path.split(name)
        file,  base = os.path.splitext(file)
        index = fru_config[FRU_PART_NUMBER_KEY].index(file)
        old = os.path.dirname(name)
        new = os.path.dirname(old)+"/"+fru_config[SUB_FOLDER_KEY][index]
        os.rename(old, new)

def get_fru_version(config={}):
    if config.get(FRU_VERSION_KEY):
        raw = config[FRU_VERSION_KEY]
        pattern = r'\d.*\d.*\d'
        x = re.search(pattern, raw)
        return x.group(0).replace(".", "")
    return None

def update_folder_fru_version(FRU):
    folder = folders[FRU]
    version = get_fru_version(configs["mainData"][FRU])

    if version == "xxx": return

    # update file name /folder/Release Note.txt
    for note in get_ReleaseNote(folder):
        dir_ = os.path.dirname(note)
        base = os.path.basename(note)
        new_note = "%s/%sv%s.txt" % (dir_, base, version)
        os.rename(note, new_note)
        showMsg(new_note + " > name updated.", True)

    # update folder name /folder
    new_name = folder[:-3]+version
    os.rename(folder, new_name)
    showMsg(new_name + " > name updated.", True)

def update(config):
    global configs, folders
    configs = config
    folders = get_folder()

    for FRU in config["mainData"]:
        if folders.get(FRU):
            match_file_number(FRU)
            update_txt_files(FRU)
            update_ini_files(FRU, "m1_ini")
            update_ini_files(FRU, "m3_ini")
            update_ini_files(FRU, "m5_ini")
            update_release_note(FRU)
            update_script(FRU)
            update_folder_name(FRU)
            update_folder_fru_version(FRU)
        else:
            showMsg("Can't find %s folder" % FRU, True)

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
                -x history* \
                -x readme* \
                " %  filename
    process = subprocess.Popen(zipcommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

if __name__ == "__main__":
    folder(config_reader.read("excel_raw_folder.json"))
    update(config_reader.read_config("excel_raw_output.json"))
    get_zip()
