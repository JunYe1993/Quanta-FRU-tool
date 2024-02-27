#!/bin/python3
import json, re

# excel spec
NO_SUB_FOLDER_ROW = False
SUB_FOLDER_KEY  = "Sub Folder Name" # TODO : need to rework if some project put in
MERGE_KEY_LIST = [
    SUB_FOLDER_KEY,
    "Board Part Number",   # FRU_PART_NUMBER_KEY
    "Board Custom Data 1", # FRU_FBPN_KEY
]

# config
PROJECT_BASE = "" # "Meta-OpenBmc", "LF-OpenBmc"
PROJECT_NAME = ""
DEVELOP_STAGE = ""

# define
FRU_PART_NUMBER_KEY = "M/B Part Number"
FRU_VERSION_KEY     = "M/B Fru File ID"
FRU_FBPN_KEY        = "M/B Custom Field 1"
MERGE_FRU_KEY_LIST = [
    FRU_PART_NUMBER_KEY,
    FRU_FBPN_KEY,
]

def parentheses_off(string):
    # remove \n
    string = string.replace('\n', '')

    # foo1(feee)foo2 > foo1foo2
    pattern = r'(.*)\(.*\)(.*)'
    x = re.search(pattern, string)
    if x != None:
        string = x.group(1) + x.group(2)

    # foo1[feee]foo2 > foo1foo2
    pattern = r'(.*)\[.*\](.*)'
    x = re.search(pattern, string)
    if x != None:
        string = x.group(1) + x.group(2)

    # remove space
    return string.strip()

if __name__ == "__main__":
    folder_string = ""
    with open ("excel_raw_folder.json", 'r', encoding='utf-8') as f:
        folders = json.load(f)
        for name in folders:
            folder_string += '\"%s\" ' % (name)

    print(folder_string)