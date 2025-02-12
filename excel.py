#!/bin/python3
import sys, re
import xlrd
import json
from toolconfig import read_config_json
from toolconfig import parentheses_off
config = read_config_json()

row_json_table = [
    "Organization",
    "Chassis Info Area",
    "Chassis Type",
    "Chassis Part Number",
    "Chassis Serial Number",
    # "Chassis Custom Data X",
    "Board Info Area",
    "Board Language Code",
    "Board Mfg Date",
    "Board Mfg",
    "Board Product",
    "Board Serial",
    "Board Part Number",
    "Board FRU ID",
    # "Board Custom Data X",
    "Product Info Area",
    "Product Language Code",
    "Product Manufacturer",
    "Product Name",
    "Product Part Number",
    "Product Version",
    "Product Serial",
    "Product Asset Tag",
    "Product FRU ID",
    # "Product Custom Data X",
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
folder_name_table = config['Project']['BoardNames']
excel_offset = config['Excel']['FRURow']
data_follow_bpn_list = ['Board Part Number']

def check_argv():

    if len(sys.argv) > 1:
        if sys.argv[1][-5:] != ".xlsx":
            print("please input the .xlsx file")
            exit()
    else:
        print("please input the .xlsx file")
        print("usage: python3 %s filename.xlsx" % sys.argv[0])
        exit()

def get_worksheet(workbook):
    
    sheetnames = workbook.sheet_names()
    if len(sheetnames) == 0:
        print("There is no sheet in the excel file.")
        exit()
    elif len(sheetnames) == 1:
        print("There is only one sheet in the excel file.")
        print("Target sheet name is %s" % sheetnames[0])
        return workbook.sheet_by_index(0)
    else:
        for sheetname in sheetnames:
            if sheetname.find("FRU") != -1:
                print("Target sheet name is %s" % sheetname)
                return workbook.sheet_by_name(sheetname)
            
    print("There is no sheet named FRU in the excel file.")
    exit()

def check_row_name(worksheet):

    global updated_json_table
    area = ""
    for i in range(excel_offset, worksheet.nrows):
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
        elif data.find("Custom Data") != -1:
            updated_json_table.append(data)
            data_follow_bpn_list.append(data)
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

    pattern = r'N/A'
    if re.search(pattern, value):
        return ""

    return value

def output_json(worksheet):

    global updated_json_table
    output = {}
    target_folder = {}
    for i in range(1, worksheet.ncols):

        # remove full-width space
        folder = worksheet.cell_value(config['Excel']['FolderRow'], i).strip().replace(u'\xa0', u' ')
        # remove typesetting space, tab, and newline characters
        folder = re.sub(r'\s+', ' ', folder)

        if folder not in folder_name_table:
            print("%s is not in the config.json" % folder)
            print("Please update the folder name in the config.json")
            print("Or check Excel section in config.json")
            exit()

        # folder_name_index      = 0
        # folder_proj_name_index = 1
        if len(folder_name_table[folder]) == 1:
            folder_name_table[folder].append(config['Project']['Name'])

        folder_name = folder_name_table[folder][folder_name_index]
        #target_folder[folder_name] = {}
        #target_folder[folder_name]["Chassis Info"] = True
        #target_folder[folder_name]["Project Name"] = folder_name_table[folder][folder_proj_name_index]

        folder_data = {}
        folder_data["Project"] = {}
        folder_data["Project"]["Name"] = folder_name_table[folder][folder_proj_name_index]
        folder_data["Project"]["ChassisArea"] = True
        for j in range(config['Excel']['FRURow'], worksheet.nrows):
            value = worksheet.cell_value(j, i).strip().replace(u'\xa0', u' ')
            value = value_check(value)

            # decide what prototype should be used.
            if value == "no chassis information":
                folder_data["Project"]["ChassisArea"] = False
                value = ""
            # there is one dickhead just dont like to fill "no chassis information"
            # judge by no input in Chassis Type
            elif worksheet.cell_value(j, 0).strip().replace(u'\xa0', u' ') == "Chassis Type" \
                and value == "":
                folder_data["Project"]["ChassisArea"] = False

            # there may some conments are under the chart, should be ignored
            if (j-excel_offset != len(updated_json_table)):
                # some column set to be ignored
                if updated_json_table[j-excel_offset] not in ignore_columns:
                    folder_data[updated_json_table[j-excel_offset]] = value
            else:
                break

        # there might be more than one row which has the same board name.
        # it meant to be merge, so the data should be the same except BPN and Customer Data
        if folder_name in output:
            for key in data_follow_bpn_list:
                output[folder_name][key].append(folder_data[key])
        else:
            output[folder_name] = folder_data
            # merge list for same folder name (ex. MB)
            for key in data_follow_bpn_list:
                output[folder_name][key] = [output[folder_name][key]]

    with open ("excel_raw_output.json", 'w', encoding='utf-8') as json_file:
        json.dump(output, json_file, ensure_ascii=False, indent=4)
    #with open ("excel_raw_folder.json", 'w', encoding='utf-8') as json_file:
    #    json.dump(target_folder, json_file, ensure_ascii=False, indent=4)

if __name__ == "__main__":

    # Check file
    check_argv()

    # Open the excel
    workbook = xlrd.open_workbook(sys.argv[1])
    worksheet = get_worksheet(workbook)

    # Check data
    check_row_name(worksheet)

    # Output json
    output_json(worksheet)