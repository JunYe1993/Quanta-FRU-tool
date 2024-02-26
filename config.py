import re, json
from excel import parentheses_off
from toolconfig import FRU_SUB_FOLDER_KEY
from toolconfig import FRU_PART_NUMBER_KEY
from toolconfig import FRU_VERSION_KEY
from toolconfig import FRU_FBPN_KEY

key_change_table = {
    FRU_SUB_FOLDER_KEY      : FRU_SUB_FOLDER_KEY,
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
    "Board Part Number"     : FRU_PART_NUMBER_KEY, # "M/B Fru File ID"
    "Board FRU ID"          : FRU_VERSION_KEY,     # "M/B Part Number"
    "Board Custom Data 1"   : FRU_FBPN_KEY,        # "M/B Custom Field 1"
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

ini_key_m1_table = {
    "mode":"M1",
    "Read EEPROM fru data(Y/N)"         : "N",
    "Write FRU Bin file to EEPROM(Y/N)" : "N",
    "Write FRU Txt file to EEPROM(Y/N)" : "Y",
    "FRU 2 Use(Y/N)"                    : "N",
    "FRU 3 Use(Y/N)"                    : "N",
    "Internal Use Data(Y/N)"            : "N",
    "Chassis Part Number(Y/N)"          : "N",
    "Chassis Serial Number(Y/N)"        : "N",
    "Chassis Custom Field 1(Y/N)"       : "N",
    "Chassis Custom Field 2(Y/N)"       : "N",
    "M/B Manufacturer Name(Y/N)"        : "N",
    "M/B Product Name(Y/N)"             : "N",
    "M/B Serial Number(Y/N)"            : "Y",
    FRU_PART_NUMBER_KEY+"(Y/N)"         : "N",
    FRU_VERSION_KEY+"(Y/N)"             : "N",
    FRU_FBPN_KEY+"(Y/N)"                : "N",
    "M/B Custom Field 2(Y/N)"           : "Y",
    "M/B Custom Field 3(Y/N)"           : "Y",
    "M/B Custom Field 4(Y/N)"           : "N",
    "PD Manufacturer Name(Y/N)"         : "N",
    "PD Product Name(Y/N)"              : "N",
    "PD Part/Model Number(Y/N)"         : "N",
    "PD Version(Y/N)"                   : "N",
    "PD Serial Number(Y/N)"             : "N",
    "PD Asset Tag(Y/N)"                 : "N",
    "PD Fru File ID(Y/N)"               : "N",
    "PD Custom Field 1(Y/N)"            : "N",
    "PD Custom Field 2(Y/N)"            : "N",
    "PD Custom Field 3(Y/N)"            : "N",
}

ini_key_m3_table = {
    "mode":"M3",
    "Read EEPROM fru data(Y/N)"         : "N",
    "Write FRU Bin file to EEPROM(Y/N)" : "Y",
    "Write FRU Txt file to EEPROM(Y/N)" : "Y",
    "FRU 2 Use(Y/N)"                    : "N",
    "FRU 3 Use(Y/N)"                    : "N",
    "Internal Use Data(Y/N)"            : "N",
    "Chassis Part Number(Y/N)"          : "N",
    "Chassis Serial Number(Y/N)"        : "Y",
    "Chassis Custom Field 1(Y/N)"       : "N",
    "Chassis Custom Field 2(Y/N)"       : "N",
    "M/B Manufacturer Name(Y/N)"        : "N",
    "M/B Product Name(Y/N)"             : "N",
    "M/B Serial Number(Y/N)"            : "N",
    FRU_PART_NUMBER_KEY+"(Y/N)"         : "N",
    FRU_VERSION_KEY+"(Y/N)"             : "N",
    FRU_FBPN_KEY+"(Y/N)"                : "N",
    "M/B Custom Field 2(Y/N)"           : "N",
    "M/B Custom Field 3(Y/N)"           : "N",
    "M/B Custom Field 4(Y/N)"           : "N",
    "PD Manufacturer Name(Y/N)"         : "N",
    "PD Product Name(Y/N)"              : "N",
    "PD Part/Model Number(Y/N)"         : "Y",
    "PD Version(Y/N)"                   : "Y",
    "PD Serial Number(Y/N)"             : "Y",
    "PD Asset Tag(Y/N)"                 : "Y",
    "PD Fru File ID(Y/N)"               : "Y",
    "PD Custom Field 1(Y/N)"            : "Y",
    "PD Custom Field 2(Y/N)"            : "Y",
    "PD Custom Field 3(Y/N)"            : "Y",
}

tags = {
    "[M3 defined]",
    "[not defined]",
}

FBPN_NUMBER_LIST = {}

def get_value(key, value, FRU):
    # base on new key (key_change_table's value)
    # there some exception need to change value
    if key == "Chassis Type":
        # Rack Mount Chassis = 17h
        return "17h"

    elif key.find("Chassis Custom Field") != -1:
        # normally this value equal to "CPU serial"
        # when need to be filled on M3 status
        return "[M3 defined]" if value != "" else ""

    elif key == "M/B Language Code":
        # Remove "(english)"
        return parentheses_off(value)

    elif key == "PD Language Code":
        # Remove "(english)"
        return parentheses_off(value)

    elif key == FRU_PART_NUMBER_KEY:
        # Board Part Number: is a string list && split by \n
        FBPN_NUMBER_LIST[FRU] = []
        ret = []
        for item in value:
            arr = item.splitlines()
            for i in range(0, len(arr)):
                pattern = r'([0-9A-Z]{11})'
                x = re.search(pattern, arr[i])
                if x != None:
                    ret.append(x.group(1))
                elif parentheses_off(arr[i]) == "TBD":
                    ret.append("TBD")

            # for board merge consequence
            # others should base on FRU PART NUMBER
            FBPN_NUMBER_LIST[FRU].append(len(arr))

        return ret

    elif key == FRU_VERSION_KEY:
        # Remove "(english)"
        return parentheses_off(value)

    elif key == FRU_FBPN_KEY:
        # for board merge
        if len(FBPN_NUMBER_LIST[FRU]) != len(value):
            print("excel proccess went wrong, FBPN_NUMBER_LIST length not matching")
            exit()

        ret = []
        for i in range(0, len(FBPN_NUMBER_LIST[FRU])):
            for j in range(0, FBPN_NUMBER_LIST[FRU][i]):
                ret.append(value[i])
        return ret

    else:
        ini_key = key + "(Y/N)"
        if ini_key_m1_table.get(ini_key) != None:
            if ini_key_m1_table[ini_key] == "Y" or \
                ini_key_m3_table[ini_key] == "Y":
                if value not in tags:
                    value = ""
        return value

def key_change(config):
    newConfig = {}
    for FRU in config:
        newConfig[FRU] = {}
        # TODO: someday needs to fix that PART NUMBER (FRU_PART_NUMBER_KEY)
        #       should be the first key for board merging
        for key in config[FRU].keys():
            if key_change_table.get(key) and key != "":
                newKey = key_change_table[key]
                newConfig[FRU][newKey] = get_value(newKey, config[FRU][key], FRU)
        # for some PM or early stage that may not have FRU_SUB_FOLDER_KEY filled
        if len(newConfig[FRU][FRU_SUB_FOLDER_KEY]) == 0:
            newConfig[FRU][FRU_SUB_FOLDER_KEY] = newConfig[FRU][FRU_PART_NUMBER_KEY]

    return newConfig

def ini_value_check(config, key, table):
    table_key = key + "(Y/N)"
    if table.get(table_key) != None:
        if config[key] == "[not defined]":
            table[table_key] = "N"
        elif config[key] == "[M3 defined]" and table["mode"] == "M3":
            table[table_key] = "Y"

    return table

def get_ini_config(ini_table, config):
    ret_config = {}
    for FRU in config:
        ret_table = ini_table.copy()
        for key in config[FRU]:
            ret_table = ini_value_check(config[FRU], key, ret_table)
        # del ret_table["mode"]
        ret_config[FRU] = ret_table
    return ret_config

def read_config(filename):
    with open ("excel_raw_output.json", 'r', encoding='utf-8') as f:
        # create main config
        txt_config = json.load(f)
        txt_config = key_change(txt_config)

        # create ini config
        ini_m1_config = get_ini_config(ini_key_m1_table, txt_config)
        ini_m3_config = get_ini_config(ini_key_m3_table, txt_config)

        # merge config
        config = {}
        config["txt"] = txt_config
        config["m1_ini"] = ini_m1_config
        config["m3_ini"] = ini_m3_config
        return config

def dump(config, name="dump.json"):
    with open (name, 'w', encoding='utf-8') as json_file:
        json.dump(config, json_file, ensure_ascii=False, indent=4)

def read(file):
    with open (file, 'r', encoding='utf-8') as f:
        return json.load(f)

if __name__ == "__main__":
    config = read_config("excel_raw_output.json")
    dump(config["txt"], "txt_dump.json")
    dump(config["m1_ini"], "ini_m1_dump.json")
    dump(config["m3_ini"], "ini_m3_dump.json")