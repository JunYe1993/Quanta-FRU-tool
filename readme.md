- Intro

    FRU generator

- Reqirement

    1. python3
    2. python3 module: xlrd

- Config

    Basically, what needs to be done is to fork from the master branch and then add the config commit from target project.

    example commit : grandteton 1.5
    ```
    diff --git a/excel.py b/excel.py
    index 7e0e182..1176f91 100644
    --- a/excel.py
    +++ b/excel.py
    @@ -54,6 +54,14 @@ ignore_columns = [
     folder_name_index = 0
     folder_proj_name_index = 1
     folder_name_table = {
    +    "BMC Storage Module"                               : ["BSM",    PROJECT_NAME],
    +    "Grand Teton MB (HSC on board or module)"          : ["MB",     PROJECT_NAME],
    +    "Grand Teton Expander BD (HSC on board or module)" : ["SWB",    PROJECT_NAME],
    +    "Grand Teton SCM"                                  : ["SCM",    PROJECT_NAME],
    +    "Grand Teton Front IO Board"                       : ["FIO",    PROJECT_NAME],
    +    "Grand Teton Vertical PDB"                         : ["VPDB",   PROJECT_NAME],
    +    "Grand Teton HGX PDB"                              : ["HPDB",   PROJECT_NAME],
    +    "Grand Teton FAN Board"                            : ["FAN_BP", PROJECT_NAME],
     }

     excel_offset = 3
    @@ -160,7 +168,7 @@ def output_json(worksheet):
         target_folder = {}
         for i in range(1, worksheet.ncols):

    -        folder_row = 1
    +        folder_row = 0
             # remove full-width space
             folder = worksheet.cell_value(folder_row, i).strip().replace(u'\xa0', u' ')
             # remove typesetting space, tab, and newline characters
    @@ -178,7 +186,7 @@ def output_json(worksheet):
             if NO_SUB_FOLDER_ROW:
                 folder_data[SUB_FOLDER_KEY] = ""

    -        for j in range(folder_row+2, worksheet.nrows):
    +        for j in range(folder_row+1, worksheet.nrows):
                 value = worksheet.cell_value(j, i).strip().replace(u'\xa0', u' ')
                 value = value_check(value)

    diff --git a/toolconfig.py b/toolconfig.py
    index c7d0977..bce808e 100644
    --- a/toolconfig.py
    +++ b/toolconfig.py
    @@ -2,7 +2,7 @@
     import json, re

     # excel spec
    -NO_SUB_FOLDER_ROW = False
    +NO_SUB_FOLDER_ROW = True
     SUB_FOLDER_KEY  = "Sub Folder Name" # TODO : need to rework if some project put in
     MERGE_KEY_LIST = [
         SUB_FOLDER_KEY,
    @@ -11,9 +11,9 @@ MERGE_KEY_LIST = [
     ]

     # config
    -PROJECT_BASE = "" # "Meta-OpenBmc", "LF-OpenBmc"
    -PROJECT_NAME = ""
    -DEVELOP_STAGE = ""
    +PROJECT_BASE = "Meta-OpenBmc" # "Meta-OpenBmc", "LF-OpenBmc"
    +PROJECT_NAME = "GT1.5"
    +DEVELOP_STAGE = "EVT"

     # define
     def get_fru_key(key):
    ```

- Usage (example is linux based)

    FRU:
    1. python3 excel.py \[target.xlsx\]
    2. python3 tool.py

    result zip file will be "projectname_stage_currentdate.zip"

    ICT:
    1. python3 toolconfig.py | xargs python3 ict_tool.py

    result zip file will be "ICT/projectname_stage_ICT_currentdate.zip"
