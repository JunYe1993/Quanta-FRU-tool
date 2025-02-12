import re, json, copy
from toolconfig import parentheses_off
from toolconfig import get_fru_keysturct

fruConfig = {}
stageConfig = {}

default_stage_config_structure = {
    "Stages": ["M1", "M3", "M5"],
    "Chassis" : {
        "Type"          : None,
        "Part Number"   : None,
        "Serial Number" : None, # from harma
        "Custom Data"   : [],
    },
    "Board" : {
        "Language Code"          : None,
        "Manufacturer Date/Time" : None,
        "Manufacturer"           : None,
        "Product"                : None,
        "Serial Number"          : "[M1 defined]",
        "Part Number"            : None,
        "Fru ID"                 : None,
        "Custom Data"            : [None, "[M1 defined]", "[M1 defined]"],
    },
    "Product" : {
        "Language Code"     : None,
        "Manufacturer"      : None,
        "Name"              : None,
        "Part/Model Number" : "[M3 defined]",
        "Version"           : "[M3 defined]",
        "Serial Number"     : "[M3 defined]",
        "Asset Tag"         : "[M3 defined]",
        "Fru ID"            : "[M3 defined]",
        "Custom Data"       : ["[M3 defined]", "[M3 defined]", "[M3 defined]"],
    },
}

default_config_structure = {
    "Project": {
        "Name": "",
        "ChassisArea": True
    },
    "Stages": ["M1", "M3"],
    "Chassis" : {
        "Type"          : "",
        "Part Number"   : "",
        "Serial Number" : "",
        "Custom Data"   : [],
    },
    "Board" : {
        "Language Code"          : "",
        "Manufacturer Date/Time" : "",
        "Manufacturer"           : "",
        "Product"                : "",
        "Serial Number"          : "",
        "Part Number"            : "",
        "Fru ID"                 : "",
        "Custom Data"            : [],
    },
    "Product" : {
        "Language Code"     : "",
        "Manufacturer"      : "",
        "Name"              : "",
        "Part/Model Number" : "",
        "Version"           : "",
        "Serial Number"     : "",
        "Asset Tag"         : "",
        "Fru ID"            : "",
        "Custom Data"       : [],
    },
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

def get_tags(value):
    
    data = value.strip()
    data = data.replace('\n', ' ')
    data = data.replace('_', ' ')
    data = data.replace('-', ' ')
    data = data.replace('ODM PROGRAM', 'ODM DEFINE')
    for model in default_stage_config_structure["Stages"]:
        if data.find(f"{model} ODM DEFINE") != -1:
            return f"[{model} defined]"
    
    # old fashion way to fill in M3
    if data == "CPU serial":
        return "[M3 defined]"
    
    return None

def update_fru_stage(config, value):
    if value == "[M5 defined]" and "M5" not in config["Stages"]:
        config["Stages"].append("M5")

def get_value(FRU, area, fruKey, value, BPN_NUMBERS):

    if fruKey == "Language Code":
        # Remove "(english)"
        return parentheses_off(value)

    # base on new key (key_change_table's value)
    # there some exception need to change value
    elif area == "Chassis":
        if fruKey == "Type":
            value = parentheses_off(value).upper()
            return ipmi_chassis_type[value]

    elif area == "Board":
        if fruKey == "Part Number":
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
        elif fruKey == "FRU ID":
            # Remove "(english)"
            return parentheses_off(value)
        
    elif area == "Product":
        if fruKey == "Language Code":
            # Remove "(english)"
            return parentheses_off(value)

    # for customer data cases
    if type(value) == list:
        if len(BPN_NUMBERS) != len(value):
            print("BPN numbers and raw customer data is not matched")
            exit()
        ret = []
        customerDataIndex = len(fruConfig[FRU][area][fruKey])
        defaultag = stageConfig[FRU][area][fruKey][customerDataIndex] \
            if len(stageConfig[FRU][area][fruKey]) > customerDataIndex else None
        for index, subvalue in enumerate(value):
            subtag = get_tags(subvalue)
            subtag = subtag if subtag != None else defaultag
            subvalue = subtag if subtag != None else subvalue
            update_fru_stage(fruConfig[FRU], subvalue)
            for i in range(0, BPN_NUMBERS[index]):
                ret.append(subvalue)
        return ret
    else:
        defaultag = stageConfig[FRU][area][fruKey]
        subtag = get_tags(value)
        subtag = subtag if subtag != None else defaultag
        rvalue = subtag if subtag != None else value
        update_fru_stage(fruConfig[FRU], rvalue)
        return rvalue

def get_fru_config(excelConfig):
    global fruConfig, stageConfig
    for FRU, data in excelConfig.items():

        BPN_NUMBERS = []
        for excel_boards in data["Board Part Number"]:
            BPN_NUMBERS.append(len(excel_boards.splitlines()))

        fruConfig[FRU] = copy.deepcopy(default_config_structure)
        stageConfig[FRU] = copy.deepcopy(default_stage_config_structure)
        fruConfig[FRU]["Project"] = data["Project"].copy()
        for key, value in data.items():
            keySturct = get_fru_keysturct(key)
            if keySturct != None:
                area, fruKey = keySturct
                if type(fruConfig[FRU][area][fruKey]) == list:
                    fruConfig[FRU][area][fruKey].append(
                        get_value(FRU, area, fruKey, value, BPN_NUMBERS))
                else:
                    fruConfig[FRU][area].update(
                        {fruKey: get_value(FRU, area, fruKey, value, BPN_NUMBERS)})
        
    return fruConfig

def read_config(file="excel_raw_output.json"):
    with open (file, 'r', encoding='utf-8') as f:
        # create main config
        rawConfig = json.load(f)
        fruConfig = get_fru_config(rawConfig)
        
        return fruConfig

def dump(config, name="dump.json"):
    with open (name, 'w', encoding='utf-8') as json_file:
        json.dump(config, json_file, ensure_ascii=False, indent=4)

def read(file):
    with open (file, 'r', encoding='utf-8') as f:
        return json.load(f)

if __name__ == "__main__":
    config = read_config()
    dump(fruConfig, "fru_config.json")