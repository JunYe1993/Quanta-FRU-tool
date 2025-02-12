import re, os, glob, subprocess
from datetime import date
from shutil import copyfile

import config as config_reader
from config import default_stage_config_structure as stage_config

from toolconfig import read_config_json
from toolconfig import parentheses_off
from toolconfig import get_fru_util_option

PROJECT_NAME = read_config_json()["Project"]["Name"]
DEVELOP_STAGE = read_config_json()["Project"]["Stage"]

### Marker
# script
SCR_DEFALUT_MARK = "#Default_Markers"
SCR_STAGE_MARK = "#Stage_Markers"
SCR_MODIFY_MARK = "#Modify_Markers"
# release note
NOTE_FRU_VER_MARK = "#FRU_Ver_Marker"
NOTE_FRU_MARK = "#FRU_Marker"
NOTE_QPN_MARK = "#QPN_Marker"
NOTE_PRC_MARK = "#PRC_Marker"
NOTE_DATE_MARK = "#Date_Marker"

showMsgEnable = False
configs = {}
folders = {}
opts = []

def showMsg(msg, enable=showMsgEnable):
    if enable:
        print(msg)

def remove_folder(dir):
    command = "rm -r %s" % dir
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

def create_folder(config):

    # remove folder _***_FRU_v***
    for raw in glob.glob("*"):
        pattern = r'_(.*)_FRU_v[0-9]+'
        x = re.search(pattern, raw)
        if os.path.isdir(raw) and x != None:
            remove_folder(raw)

    # copy folder from prototype
    for FRU in config:

        folder = "prototype"
        targetname = "%s_%s_FRU_v001" % (config[FRU]["Project"]["Name"], FRU)
        # copy
        command = "cp -r %s %s" % (folder, targetname)
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()

        # copy tool
        command = "cp fruid-util/%s %s/" % ("fruid-util.py", targetname)
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()

        command = "cp fruid-util/%s %s/" % ("README.md", targetname)
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()

        # set tool
        command = "chmod 755 %s" % (targetname+"/fruid-util.py")
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()

        missStages = [stage for stage in config[FRU]["Stages"] if stage not in stage_config["Stages"]]
        for missstage in missStages:
            command = "rm -r %s/%s" % (targetname, missstage)
            process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()

def get_folder():
    folders = {}
    projectNames = {configs[FRU]["Project"]["Name"] for FRU in configs}
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

def match_bpn_numbers(FRU):
    folder = folders[FRU]
    config = configs[FRU]
    bpnNumbers = len(config["Board"]["Part Number"])
    for stage in config["Stages"]:
        copyFile = f"{folder}/{stage}/0.sh"
        for i in range(1, bpnNumbers):
            filename = f"{folder}/{stage}/{i}.sh"
            copyfile(copyFile, filename)
            os.chmod(filename, 0o755)
    
def update_script_area(config, area, bpnIndex, stage=None):

    line = ""
    for key, value in config[area].items():

        keys = [key]
        vals = [value]
        if area == "Board" and key == "Part Number":
            vals = [value[bpnIndex]]
        if key == "Custom Data":
            keys = [f"Custom Data {i+1}" for i in range(len(value))]
            vals = [subvalue[bpnIndex] for subvalue in value]
        if key == "Language Code":
            continue
        if key == "Type":
            continue

        for index, key in enumerate(keys):
            val = parentheses_off(vals[index])
            
            if stage == None:
                if val != "":
                    opt = get_fru_util_option(f"{area} {key}")
                    line += f"{opt}=\"{val}\"\n"
                    opts.append(opt)

            else: 
                if vals[index] in [ f"[{s} defined]" for s in stage_config["Stages"]]:
                    if f"[{stage} defined]" == vals[index]:
                        opt = get_fru_util_option(f"{area} {key}")
                        line += f"read -p \"{area} {key}: \" {opt}\n"
                        opts.append(opt)
        
    return line

def update_script_data(line, config, bpnIndex, stage):

    if line.find(SCR_DEFALUT_MARK) != -1:
        retLine = ""
        if config["Project"]["ChassisArea"]:
            retLine += update_script_area(config, "Chassis", bpnIndex)
        retLine += update_script_area(config, "Board", bpnIndex)
        retLine += update_script_area(config, "Product", bpnIndex)
        return retLine
    
    if line.find(SCR_STAGE_MARK) != -1:
        retLine = ""
        if config["Project"]["ChassisArea"]:
            retLine += update_script_area(config, "Chassis", bpnIndex, stage)
        retLine += update_script_area(config, "Board", bpnIndex, stage)
        retLine += update_script_area(config, "Product", bpnIndex, stage)
        return retLine
    
    if line.find(SCR_MODIFY_MARK) != -1:
        retLine = "python3 $UTIL $BIN -m \\\n"
        for opt in opts:
            retLine += f" --{opt} \"${opt}\" \\\n"
        retLine += f" --BMD \"$(date '+%F %H:%M:%S')\"\n"
        return retLine
    
    return line

def update_script(FRU):
    global opts
    folder = folders[FRU]
    config = configs[FRU]
    bpnNumbers = len(config["Board"]["Part Number"])
    
    for stage in config["Stages"]:
        for bpnIndex in range(bpnNumbers):
            opts = []
            scriptName = f"{folder}/{stage}/{bpnIndex}.sh"
            scriptContent = ""
            for line in open(scriptName, "r"):
                scriptContent += update_script_data(line, config, bpnIndex, stage)

            fd = open(scriptName, "w")
            fd.write(scriptContent)

            newName = f"{folder}/{stage}/{config['Board']['Part Number'][bpnIndex]}.sh"
            os.rename(scriptName, newName)

            showMsg(newName + " > name updated.", True)
            showMsg(newName + " > data updated.", True)

def get_procedure(fru):
    # TODO: provide an exact string not just xx in config.json
    config = read_config_json()
    CopyMethod = config["ReleaseNote"]["CopyMethod"]
    return config["ReleaseNote"]["CopyMethod-"+CopyMethod]

def get_fru_version(config):
    raw = config["Board"]["Fru ID"]
    pattern = r'\d.*\d.*\d'
    x = re.search(pattern, raw)
    return x.group(0).replace(".", "")

def update_note(line, config, FRU):
    if line.find(NOTE_QPN_MARK) != -1:
        line = line.replace(NOTE_QPN_MARK, config["Board"]["Part Number"][0])
    if line.find(NOTE_FRU_MARK) != -1:
        line = line.replace(NOTE_FRU_MARK, FRU)
    if line.find(NOTE_PRC_MARK) != -1:
        line = line.replace(NOTE_PRC_MARK, get_procedure(FRU))
    if line.find(NOTE_DATE_MARK) != -1:
        line = line.replace(NOTE_DATE_MARK, date.today().strftime("%Y/%m/%d"))
    if line.find(NOTE_FRU_VER_MARK) != -1:
        line = line.replace(NOTE_FRU_VER_MARK, get_fru_version(config))
    
    return line

def update_release_note(FRU):
    folder = folders[FRU]
    config = configs[FRU]

    releaseNoteName = f"{folder}/FRU_Release_Note_.txt"
    releaseNoteContent = ""
    for line in open(releaseNoteName, "r"):
        releaseNoteContent += update_note(line, config, FRU)
    fd = open(releaseNoteName, "w")
    fd.write(releaseNoteContent)

    newName = f"{folder}/FRU_Release_Note_{get_fru_version(config)}.txt"
    os.rename(releaseNoteName, newName)

    showMsg(newName + " > name updated.", True)
    showMsg(newName + " > data updated.", True)

def update_folder_name(FRU):
    folder = folders[FRU]
    config = configs[FRU]

    folderName = f"{folder}"
    newName = f"{folder[:-3]}{get_fru_version(config)}"

    os.rename(folderName, newName)
    showMsg(newName + " > name updated.", True)

def update(_config):
    global configs, folders
    configs = _config
    folders = get_folder()

    for FRU in config:
        if folders.get(FRU):
            match_bpn_numbers(FRU)
            update_script(FRU)
            update_release_note(FRU)
            update_folder_name(FRU)
        else:
            showMsg("Can't find %s folder" % FRU, True)

def get_zip():
    # get file name
    filedate = date.today().strftime("%Y%m%d")
    filename = "%s_%s_%s.zip" % (PROJECT_NAME, DEVELOP_STAGE, filedate[2:])

    zipcommand = "zip -r %s . \
                -x excel.py \
                -x config.py \
                -x tool.py \
                -x toolconfig.py \
                -x ict_tool.py \
                -x clear.py \
                -x *.json \
                -x *.zip \
                -x __pycache__* \
                -x prototype* \
                -x .git* \
                -x ICT* \
                -x history* \
                -x readme* \
                -x fruid-util/* \
                " %  filename
    process = subprocess.Popen(zipcommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

if __name__ == "__main__":
    config = config_reader.read_config("excel_raw_output.json")
    create_folder(config)
    update(config)
    get_zip()
