#!/bin/python3
import json

PROJECT_PROCEDURES = {
    "Meta-OpenBmc" : "fruid-util xxx --write fru.bin",
    "LF-OpenBmc"   : "dd if=/tmp/fru.bin of=/sys/class/i2c-dev/i2c-xx/device/xx-00xx/eeprom"
}

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

if __name__ == "__main__":
    folder_string = ""
    with open ("excel_raw_folder.json", 'r', encoding='utf-8') as f:
        folders = json.load(f)
        for name in folders:
            folder_string += "\""+name+"\" "

    print(folder_string)