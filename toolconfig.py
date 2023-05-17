#!/bin/python3
import json

# config
PROJECT_NAME = "GT"
DEVELOP_STAGE = "MP"

# define
FRU_SUB_FOLDER_KEY = "Sub Folder Name"
FRU_VERSION_KEY = "M/B Fru File ID"
FRU_PART_NUMBER_KEY = "M/B Part Number"
CHASSIS_QPN_MARK = "#Marker"

if __name__ == "__main__":
    folder_string = ""
    with open ("excel_raw_folder.json", 'r', encoding='utf-8') as f:
        folders = json.load(f)
        for name in folders:
            folder_string += "\""+name+"\" "

    print(folder_string)