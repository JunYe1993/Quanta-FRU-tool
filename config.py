import re, json
from toolconfig import parentheses_off
from toolconfig import get_fru_key
from toolconfig import SUB_FOLDER_KEY
from toolconfig import FRU_PART_NUMBER_KEY
from toolconfig import FRU_VERSION_KEY
from toolconfig import FRU_FBPN_KEY
from toolconfig import MERGE_FRU_KEY_LIST

ini_key_m1_table = {
    "mode":"M1",
    "enable":True,
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
    "enable":True,
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

ini_key_m5_table = {
    "mode":"M5",
    "enable":False,
    "Read EEPROM fru data(Y/N)"         : "N",
    "Write FRU Bin file to EEPROM(Y/N)" : "Y",
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
    "M/B Serial Number(Y/N)"            : "N",
    FRU_PART_NUMBER_KEY+"(Y/N)"         : "N",
    FRU_VERSION_KEY+"(Y/N)"             : "N",
    FRU_FBPN_KEY+"(Y/N)"                : "N",
    "M/B Custom Field 2(Y/N)"           : "N",
    "M/B Custom Field 3(Y/N)"           : "N",
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

ipmi_chassis_type = {
    ""                      : "00h", # self made
    "OTHER"                 : "01h",
    "UNKNOWN"               : "02h",
    "DESKTOP"               : "03h",
    "LOW PROFILE DESKTOP"   : "04h",
    "PIZZA BOX"             : "05h",
    "MINI TOWER"            : "06h",
    "TOWER"                 : "07h",
    "PORTABLE"              : "08h",
    "LAPTOP"                : "09h",
    "NOTEBOOK"              : "0Ah",
    "HAND HELD"             : "0Bh",
    "DOCKING STATION"       : "0Ch",
    "ALL IN ONE"            : "0Dh",
    "SUB NOTEBOOK"          : "0Eh",
    "SPACE SAVING"          : "0Fh",
    "LUNCH BOX"             : "10h",
    "MAIN SERVER CHASSIS"   : "11h",
    "EXPANSION CHASSIS"     : "12h",
    "SUBCHASSIS"            : "13h",
    "BUS EXPANSION CHASSIS" : "14h",
    "PERIPHERAL CHASSIS"    : "15h",
    "RAID CHASSIS"          : "16h",
    "RACK MOUNT CHASSIS"    : "17h",
}

tags = {
    "[M1 defined]",
    "[M3 defined]",
    "[M5 defined]",
    "[not defined]",
}

FBPN_NUMBER_LIST = {}

def get_value(key, value, FRU):
    # base on new key (key_change_table's value)
    # there some exception need to change value
    if key == "Chassis Type":
        value = parentheses_off(value).upper()
        return ipmi_chassis_type[value]

    # old fashion way to fill in M3
    elif key.find("Chassis Custom Field") != -1 and \
            value.find("CPU serial") != -1:
        # normally this value equal to "CPU serial"
        # when need to be filled on M3 status
        return "[M3 defined]" if value != "" else ""

    elif key == "M/B Language Code":
        # Remove "(english)"
        return parentheses_off(value)

    elif key == "PD Language Code":
        # Remove "(english)"
        return parentheses_off(value)

    elif key == SUB_FOLDER_KEY:
        # Board Part Number: is a string list && split by \n
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

        return ret

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

    elif key in MERGE_FRU_KEY_LIST:
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
        # check if value need to be filled in specific mode
        ODMstr = value.strip()
        ODMstr = ODMstr.replace('_', ' ')
        ODMstr = ODMstr.replace('-', ' ')

        if ODMstr.find("M1 ODM PROGRAM") != -1 or \
            ODMstr.find("M1 ODM DEFINE") != -1:
            return "[M1 defined]"
        elif ODMstr.find("M3 ODM PROGRAM") != -1 or \
            ODMstr.find("M3 ODM DEFINE") != -1:
            return "[M3 defined]"
        elif ODMstr.find("M5 ODM PROGRAM") != -1 or \
            ODMstr.find("M5 ODM DEFINE") != -1:
            return "[M5 defined]"

        # check if key originally in specific mode
        ini_key = key + "(Y/N)"
        if ini_key_m1_table.get(ini_key) != None:
            if ini_key_m1_table[ini_key] == "Y" or \
                ini_key_m3_table[ini_key] == "Y" or \
                ini_key_m5_table[ini_key] == "Y":
                if value not in tags:
                    value = ""
        return value

def key_change(config):
    newConfig = {}
    for FRU in config:
        newConfig[FRU] = {}
        keys = [FRU_PART_NUMBER_KEY] + [key for key in config[FRU].keys() if key != FRU_PART_NUMBER_KEY]
        for key in keys:
            if get_fru_key(key) and key != "":
                newKey = get_fru_key(key)
                newConfig[FRU][newKey] = get_value(newKey, config[FRU][key], FRU)
        # for some PM or early stage that may not have SUB_FOLDER_KEY filled
        if len(newConfig[FRU][SUB_FOLDER_KEY]) == 0:
            newConfig[FRU][SUB_FOLDER_KEY] = newConfig[FRU][FRU_PART_NUMBER_KEY]

    return newConfig

def get_ini_config(config):

    m1_config = {}
    m3_config = {}
    m5_config = {}

    for FRU in config:
        m1_table = ini_key_m1_table.copy()
        m3_table = ini_key_m3_table.copy()
        m5_table = ini_key_m5_table.copy()

        for key in config[FRU]:
            tablekey = key + "(Y/N)"
            # if ini don't have this key, skip
            if m1_table.get(tablekey) == None:
                continue

            if config[FRU][key] == "[not defined]":
                m1_table[tablekey] = "N"
                m3_table[tablekey] = "N"
                m5_table[tablekey] = "N"
            if config[FRU][key] == "[M1 defined]":
                m1_table[tablekey] = "Y"
                m3_table[tablekey] = "N"
                m5_table[tablekey] = "N"
            elif config[FRU][key] == "[M3 defined]":
                m1_table[tablekey] = "N"
                m3_table[tablekey] = "Y"
                m5_table[tablekey] = "N"
            elif config[FRU][key] == "[M5 defined]":
                m1_table[tablekey] = "N"
                m3_table[tablekey] = "N"
                m5_table[tablekey] = "Y"
                # if format is M5 defined, then enable M5
                m5_table["enable"] = True

        m1_config[FRU] = m1_table
        m3_config[FRU] = m3_table
        m5_config[FRU] = m5_table

    return m1_config, m3_config, m5_config

def read_config(filename):
    with open ("excel_raw_output.json", 'r', encoding='utf-8') as f:
        # create main config
        data_config = json.load(f)
        data_config = key_change(data_config)

        # create ini config
        ini_m1_config, ini_m3_config, ini_m5_config = get_ini_config(data_config)

        # merge config
        config = {}
        config["mainData"] = data_config
        config["m1_ini"] = ini_m1_config
        config["m3_ini"] = ini_m3_config
        config["m5_ini"] = ini_m5_config
        return config

def dump(config, name="dump.json"):
    with open (name, 'w', encoding='utf-8') as json_file:
        json.dump(config, json_file, ensure_ascii=False, indent=4)

def read(file):
    with open (file, 'r', encoding='utf-8') as f:
        return json.load(f)

if __name__ == "__main__":
    config = read_config("excel_raw_output.json")
    dump(config["mainData"], "data_dump.json")
    dump(config["m1_ini"], "ini_m1_dump.json")
    dump(config["m3_ini"], "ini_m3_dump.json")
    dump(config["m5_ini"], "ini_m5_dump.json")