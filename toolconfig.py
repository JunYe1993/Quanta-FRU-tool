#!/bin/python3
import json, re

# excel spec
SUB_FOLDER_KEY  = "Sub Folder Name" # TODO : need to rework if some project put in
MERGE_KEY_LIST = [
    SUB_FOLDER_KEY,
    "Board Part Number",   # FRU_PART_NUMBER_KEY
    "Board Custom Data 1", # FRU_FBPN_KEY
]

# define
def get_fru_key(key):
    key_change_table = {
        SUB_FOLDER_KEY          : SUB_FOLDER_KEY,
        "Chassis Type"          : "Chassis Type",
        "Chassis Part Number"   : "Chassis Part Number",
        "Chassis Serial Number" : "Chassis Serial Number",
        "Chassis Custom Data 1" : "Chassis Custom Field 1",
        "Chassis Custom Data 2" : "Chassis Custom Field 2",

        "Board Language Code"   : "M/B Language Code",
        "Board Mfg Date"        : "M/B Manufacturer Date/Time",
        "Board Mfg"             : "M/B Manufacturer Name",
        "Board Product"         : "M/B Product Name",
        "Board Serial"          : "M/B Serial Number",
        "Board Part Number"     : "M/B Part Number", 
        "Board FRU ID"          : "M/B Fru File ID",     
        "Board Custom Data 1"   : "M/B Custom Field 1",        
        "Board Custom Data 2"   : "M/B Custom Field 2",
        "Board Custom Data 3"   : "M/B Custom Field 3",
        "Board Custom Data 4"   : "M/B Custom Field 4",

        "Product Language Code" : "PD Language Code",
        "Product Manufacturer"  : "PD Manufacturer Name",
        "Product Name"          : "PD Product Name",
        "Product Part Number"   : "PD Part/Model Number",
        "Product Version"       : "PD Version",
        "Product Serial"        : "PD Serial Number",
        "Product Asset Tag"     : "PD Asset Tag",
        "Product FRU ID"        : "PD Fru File ID",
        "Product Custom Data 1" : "PD Custom Field 1",
        "Product Custom Data 2" : "PD Custom Field 2",
        "Product Custom Data 3" : "PD Custom Field 3",
    }
    return key_change_table[key] if key_change_table.get(key) else None

FRU_PART_NUMBER_KEY = get_fru_key("Board Part Number")
FRU_VERSION_KEY     = get_fru_key("Board FRU ID")
FRU_FBPN_KEY        = get_fru_key("Board Custom Data 1")


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

def read_config_json():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

if __name__ == "__main__":
    folder_string = ""
    with open ("excel_raw_folder.json", 'r', encoding='utf-8') as f:
        folders = json.load(f)
        for name in folders:
            folder_string += '\"%s\" ' % (name)

    print(folder_string)