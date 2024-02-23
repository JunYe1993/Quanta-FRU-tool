#!/bin/python3
import json

# excel spec
NO_SUB_FOLDER_ROW = True
MERGE_KEY_LIST = [
    "Board Part Number",   # FRU_PART_NUMBER_KEY
    "Board Custom Data 1", # FRU_FBPN_KEY
]

# config
PROJECT_BASE = ""
PROJECT_NAME = ""
DEVELOP_STAGE = ""

# define
FRU_SUB_FOLDER_KEY  = "Sub Folder Name" # TODO : need to rework if some project put in
FRU_PART_NUMBER_KEY = "M/B Part Number"
FRU_VERSION_KEY     = "M/B Fru File ID"
FRU_FBPN_KEY        = "M/B Custom Field 1"
MERGE_FRU_KEY_LIST = [
    FRU_PART_NUMBER_KEY,
    FRU_FBPN_KEY,
]

# Marker
QPN_MARK = "#QPN_Marker"
FRU_MARK = "#FRU_Marker"
PRC_MARK = "#PRC_Marker"
INI_PUT_MARK = "#PUT_Marker"
INI_LEN_MARK = "#LEN_Marker"

if __name__ == "__main__":
    folder_string = ""
    with open ("excel_raw_folder.json", 'r', encoding='utf-8') as f:
        folders = json.load(f)
        for name in folders:
            folder_string += "\""+name+"\" "

    print(folder_string)