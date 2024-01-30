#!/bin/python3
import json

# config
PROJECT_BASE = "LF-OpenBmc"
PROJECT_NAME = "Minerva"
DEVELOP_STAGE = "EVT"

# define
FRU_SUB_FOLDER_KEY = "Sub Folder Name"
FRU_VERSION_KEY = "M/B Fru File ID"
FRU_PART_NUMBER_KEY = "M/B Part Number"
QPN_MARK = "#QPN_Marker"
FRU_MARK = "#FRU_Marker"
PRC_MARK = "#PRC_Marker"
INI_PUT_MARK = "#PUT_Marker"
INI_LEN_MARK = "#LEN_Marker"

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

if __name__ == "__main__":
    folder_string = ""
    with open ("excel_raw_folder.json", 'r', encoding='utf-8') as f:
        folders = json.load(f)
        for name in folders:
            folder_string += "\""+name+"\" "

    print(folder_string)