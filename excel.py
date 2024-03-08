#!/bin/python3
import sys, re
import xlrd
import json
from toolconfig import PROJECT_NAME
from toolconfig import NO_SUB_FOLDER_ROW
from toolconfig import MERGE_KEY_LIST
from toolconfig import SUB_FOLDER_KEY

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
    "PCBA QPN", # Just for dickhead.
]

updated_json_table = []

ignore_columns = [
    "Organization",
    "Board Info Area",
    "Product Info Area"
]

folder_name_index = 0
folder_proj_name_index = 1
folder_name_table = {
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

        folder_row = 1
        # remove full-width space
        folder = worksheet.cell_value(folder_row, i).strip().replace(u'\xa0', u' ')
        # remove typesetting space, tab, and newline characters
        folder = re.sub(r'\s+', ' ', folder)

        # folder_name_index      = 1
        # folder_proj_name_index = 2
        folder_name = folder_name_table[folder][folder_name_index]
        target_folder[folder_name] = {}
        target_folder[folder_name]["Chassis Info"] = True
        target_folder[folder_name]["Project Name"] = folder_name_table[folder][folder_proj_name_index]

        folder_data = {}
        folder_data[SUB_FOLDER_KEY] = worksheet.cell_value(folder_row+1, i).strip().replace(u'\xa0', u' ')
        if NO_SUB_FOLDER_ROW:
            folder_data[SUB_FOLDER_KEY] = ""

        for j in range(folder_row+2, worksheet.nrows):
            value = worksheet.cell_value(j, i).strip().replace(u'\xa0', u' ')
            value = value_check(value)

            # decide what prototype should be used.
            if value == "no chassis information":
                target_folder[folder_name]["Chassis Info"] = False
                value = ""
            # there is one dickhead just dont like to fill "no chassis information"
            # judge by no input in Chassis Type
            elif worksheet.cell_value(j, 0).strip().replace(u'\xa0', u' ') == "Chassis Type" \
                and value == "":
                target_folder[folder_name]["Chassis Info"] = False

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
            for key in MERGE_KEY_LIST:
                output[folder_name][key].append(folder_data[key])
        else:
            output[folder_name] = folder_data
            # merge list for same folder name (ex. MB)
            for key in MERGE_KEY_LIST:
                output[folder_name][key] = [output[folder_name][key]]

    with open ("excel_raw_output.json", 'w', encoding='utf-8') as json_file:
        json.dump(output, json_file, ensure_ascii=False, indent=4)
    with open ("excel_raw_folder.json", 'w', encoding='utf-8') as json_file:
        json.dump(target_folder, json_file, ensure_ascii=False, indent=4)

if __name__ == "__main__":

    # Check file
    check_argv()

    # Open the excel
    workbook = xlrd.open_workbook(sys.argv[1])
    worksheet = workbook.sheet_by_index(0)

    # Check data
    check_row_name(worksheet)

    # Output json
    output_json(worksheet)