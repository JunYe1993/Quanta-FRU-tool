#!/bin/python3
import sys, re
import xlrd
import json

row_check_table = [
    "Organization",
    "Chassis Info Area",
    "Chassis Type",
    "Chassis Part Number",
    "Chassis Serial Number",
    "Chassis Custom Data 1",
    "Chassis Custom Data 2",
    "Board Info Area",
    "Language Code",
    "Board Mfg Date",
    "Board Mfg",
    "Board Product",
    "Board Serial",
    "Board Part Number",
    "Board FRU ID",
    "Board  Custom Data 1",
    "Board  Custom Data 2",
    "Board  Custom Data 3",
    "Product Info Area",
    "Language Code",
    "Product Manufacturer",
    "Product Name",
    "Product Part Number",
    "Product Version",
    "Product Serial",
    "Product Asset Tag",
    "Product FRU ID",
    "Product  Custom Data 1",
    "Product  Custom Data 2",
    "Product  Custom Data 3",
]

row_json_table = [
    "",
    "Chassis Info Area",
    "Chassis Type",
    "Chassis Part Number",
    "Chassis Serial Number",
    "Chassis Custom Data 1",
    "Chassis Custom Data 2",
    "",
    "Board Language Code",
    "Board Mfg Date",
    "Board Mfg",
    "Board Product",
    "Board Serial",
    "Board Part Number",
    "Board FRU ID",
    "Board Custom Data 1",
    "Board Custom Data 2",
    "Board Custom Data 3",
    "",
    "Product Language Code",
    "Product Manufacturer",
    "Product Name",
    "Product Part Number",
    "Product Version",
    "Product Serial",
    "Product Asset Tag",
    "Product FRU ID",
    "Product Custom Data 1",
    "Product Custom Data 2",
    "Product Custom Data 3",
]

folder_name_table = {
    "BMC Storage Module"                     : "BSM",
    "Grand Teton MB"                         : "MB",
    "Grand Teton MB (HSC on board)"          : "MB(on_board)",
    "Grand Teton MB (HSC module)"            : "MB(module)",
    "Grand Teton_MB_HSC Module"              : "MB_HSC",
    "Grand Teton SCM"                        : "SCM",
    "Grand Teton Expander BD"                : "SWB",
    "Grand Teton Expander BD (HSC on board)" : "SWB(on_board)",
    "Grand Teton Expander BD (HSC module)"   : "SWB(module)",
    "Grand Teton_Expander BD_HSC Module"     : "SWB_HSC",
    "Grand Teton Front IO Board"             : "FIO",
    "Grand Teton Vertical PDB"               : "VPDB",
    "Grand Teton HGX PDB"                    : "HPDB",
    "Grand Teton FAN Board"                  : "FAN_BP",
    "Grand Teton Vertical PDB_Brick"         : "VPDB_Brick",
    "Grand Teton Vertical PDB_Discrete"      : "VPDB_Discrete",
}

def parentheses_off(string):

    pattern = r'(.*)\(.*\)(.*)'
    x = re.search(pattern, string)
    if x != None:
        string = x.group(1) + x.group(2)

    pattern = r'(.*)\[.*\](.*)'
    x = re.search(pattern, string)
    if x != None:
        string = x.group(1) + x.group(2)

    return string

def check_argv():

    if len(sys.argv) > 1:
        if sys.argv[1][-5:] != ".xlsx":
            print("please input the .xlsx file")
            exit()
    else:
        print("please input the .xlsx file")
        print("usage: python3 %s filename.xlsx" % sys.argv[0])
        exit()

def check_row_name(worksheet):

    for i in range(1, worksheet.nrows):
        data = parentheses_off(worksheet.cell_value(i, 0))
        data = data.strip().replace(u'\xa0', u' ')
        if i-2 == len(row_check_table):
            if data != "":
                print("row table need to be updated.")
                exit()
            else:
                break

def value_check(value):

    pattern = r'\[.*not defined.*\]'
    if re.search(pattern, value):
        return "[not defined]"

    pattern = r'\[.*empty.*\]'
    if re.search(pattern, value):
        return "[not defined]"

    pattern = r'\(.*no chassis information.*\)'
    if re.search(pattern, value):
        return "no chassis information"

    pattern = r'^\(.*\)$'
    if re.search(pattern, value):
        return ""

    pattern = r'^\[.*\]$'
    if re.search(pattern, value):
        return ""

    pattern = r'ODM_DEFINE'
    if re.search(pattern, value):
        return ""

    pattern = r'N/A'
    if re.search(pattern, value):
        return ""

    return value

def output_json(worksheet):

    output = {}
    target_folder = {}
    for i in range(1, worksheet.ncols):
        # folder = parentheses_off(worksheet.cell_value(0, i))
        folder = worksheet.cell_value(0, i).strip().replace(u'\xa0', u' ')
        folder_name = folder_name_table[folder]
        target_folder[folder_name] = {}
        target_folder[folder_name]["Chassis Info"] = True

        folder_data = {}
        for j in range(2, worksheet.nrows):
            value = worksheet.cell_value(j, i).strip().replace(u'\xa0', u' ')
            value = value_check(value)

            if value == "no chassis information":
                target_folder[folder_name]["Chassis Info"] = False
                value = ""

            if (j-2 != len(row_json_table)):
                if row_json_table[j-2] != "":
                    folder_data[row_json_table[j-2]] = value
            else:
                break

        output[folder_name] = folder_data

    with open ("excel_raw_output.json", 'w', encoding='utf-8') as json_file:
        json.dump(output, json_file, ensure_ascii=False, indent=4)
    with open ("excel_raw_folder.json", 'w', encoding='utf-8') as json_file:
        json.dump(target_folder, json_file, ensure_ascii=False, indent=4)

if __name__ == "__main__":

    # Check file
    check_argv()

    # Open the excel
    workbook = xlrd.open_workbook(sys.argv[1])
    worksheet = workbook.sheet_by_index(2)

    # Check data
    check_row_name(worksheet)

    # Output json
    output_json(worksheet)