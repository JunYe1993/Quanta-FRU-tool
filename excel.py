#!/bin/python3
import sys, re
import xlrd
import json
from toolconfig import FRU_SUB_FOLDER_KEY

row_json_table = [
    "Organization",
    "Chassis Info Area",
    "Chassis Type",
    "Chassis Part Number",
    "Chassis Serial Number",
    "Chassis Custom Data 1",
    "Chassis Custom Data 2",
    "Board Info Area",
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
    "Board Custom Data 4",
    "Product Info Area",
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
    "",
]

updated_json_table = []

ignore_columns = [
    "Organization",
    "Board Info Area",
    "Product Info Area"
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
    "Grand Teton Expander BD (PVT1)"         : "SWB(PVT1)",
    "Grand Teton Expander BD (PVT2)"         : "SWB(PVT2)",
    "Grand Teton Vertical PDB (PVT1)"        : "VPDB(PVT1)",
    "Grand Teton Vertical PDB (PVT2)"        : "VPDB(PVT2)",
    "Grand Teton Vertical PDB (PVT3)"        : "VPDB(PVT3)",
    "Grand Teton Vertical PDB (PVT4)"        : "VPDB(PVT4)",
    "Grand Teton HGX PDB (PVT1)"             : "HPDB(PVT1)",
    "Grand Teton HGX PDB (PVT2)"             : "HPDB(PVT2)",
    "Grand Teton HGX PDB (PVT3)"             : "HPDB(PVT3)",
    "Grand Teton HGX PDB (PVT4)"             : "HPDB(PVT4)",
}

def parentheses_off(string):

    string = string.replace('\n', '')

    pattern = r'(.*)\(.*\)(.*)'
    x = re.search(pattern, string)
    if x != None:
        string = x.group(1) + x.group(2)

    pattern = r'(.*)\[.*\](.*)'
    x = re.search(pattern, string)
    if x != None:
        string = x.group(1) + x.group(2)

    return string.strip()

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

    area = ""
    for i in range(2, worksheet.nrows):
        data = parentheses_off(worksheet.cell_value(i, 0))
        data = data.strip().replace(u'\xa0', u' ')
        data = data.replace("  ", " ")

        area = "Board " if data == "Board Info Area" else area
        area = "Product " if data == "Product Info Area" else area
        if data == "Language Code":
            data = area + data
        if data == "":
            break

        if data in row_json_table:
            updated_json_table.append(data)
        else:
            print("Needs to update JSON table")
            exit()


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

        # remove full-width space
        folder = worksheet.cell_value(0, i).strip().replace(u'\xa0', u' ')
        # remove typesetting space, tab, and newline characters
        folder = re.sub(r'\s+', ' ', folder)

        folder_name = folder_name_table[folder]
        target_folder[folder_name] = {}
        target_folder[folder_name]["Chassis Info"] = True

        folder_data = {}
        folder_data[FRU_SUB_FOLDER_KEY] = worksheet.cell_value(1, i).strip().replace(u'\xa0', u' ')
        for j in range(2, worksheet.nrows):
            value = worksheet.cell_value(j, i).strip().replace(u'\xa0', u' ')
            value = value_check(value)

            # decide what prototype should be used.
            if value == "no chassis information":
                target_folder[folder_name]["Chassis Info"] = False
                value = ""

            # there may some conments are under the chart, should be ignored
            if (j-2 != len(updated_json_table)):
                # some column set to be ignored
                if updated_json_table[j-2] not in ignore_columns:
                    folder_data[updated_json_table[j-2]] = value
            else:
                break

        # there might be more than one row which has the same board name.
        # it meant to be merge, so the data should be the same except "Board Part Number"
        if folder_name in output:
            output[folder_name][FRU_SUB_FOLDER_KEY] += "\n" + folder_data[FRU_SUB_FOLDER_KEY]
            output[folder_name]["Board Part Number"] += "\n" + folder_data["Board Part Number"]
        else:
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
    worksheet = workbook.sheet_by_index(1)

    # Check data
    check_row_name(worksheet)

    # Output json
    output_json(worksheet)