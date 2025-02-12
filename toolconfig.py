#!/bin/python3
import json, re

# define
def get_fru_keysturct(key):
    key_change_table = {
        "Chassis Type"          : ("Chassis", "Type"),
        "Chassis Part Number"   : ("Chassis", "Part Number"),
        "Chassis Serial Number" : ("Chassis", "Serial Number"),
        "Chassis Custom Data"   : ("Chassis", "Custom Data"),

        "Board Language Code"   : ("Board", "Language Code"),
        "Board Mfg Date"        : ("Board", "Manufacturer Date/Time"),
        "Board Mfg"             : ("Board", "Manufacturer"),
        "Board Product"         : ("Board", "Product"),
        "Board Serial"          : ("Board", "Serial Number"),
        "Board Part Number"     : ("Board", "Part Number"),
        "Board FRU ID"          : ("Board", "Fru ID"),
        "Board Custom Data"     : ("Board", "Custom Data"),

        "Product Language Code" : ("Product", "Language Code"),
        "Product Manufacturer"  : ("Product", "Manufacturer"),
        "Product Name"          : ("Product", "Name"),
        "Product Part Number"   : ("Product", "Part/Model Number"),
        "Product Version"       : ("Product", "Version"),
        "Product Serial"        : ("Product", "Serial Number"),
        "Product Asset Tag"     : ("Product", "Asset Tag"),
        "Product FRU ID"        : ("Product", "Fru ID"),
        "Product Custom Data"   : ("Product", "Custom Data"),
    }

    if key_change_table.get(key):
        return key_change_table[key]
    elif key.find("Custom Data") != -1:
        for prefix in ["Board", "Product", "Chassis"]:
            if key.startswith(prefix):
                return key_change_table[f"{prefix} Custom Data"]
    else:
        return None
    
def get_fru_util_option(label):
    # 提取字首規則
    words = label.split()
    if not words:
        return "Unknown Label"
    
    # 處理數字結尾，將它與字首分開
    left_label = ""
    for word in words:
        if word.isdigit():  # 如果是數字，直接保留
            left_label += word
        else:  # 否則取首字母
            left_label += word[0].upper()
    
    return left_label

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
    with open ("excel_raw_output.json", 'r', encoding='utf-8') as f:
        folders = json.load(f)
        for name in folders:
            folder_string += '\"%s\" ' % (name)

    print(folder_string)