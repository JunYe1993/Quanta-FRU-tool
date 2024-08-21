- Intro

    FRU generator

- Reqirement

    1. python3
    2. python3 module: xlrd

- Usage (example is linux based)

    FRU:
    1. python3 excel.py \[target.xlsx\]
    2. python3 tool.py
       
    result zip file will be "projectname_stage_currentdate.zip"

    ICT:
    1. python3 toolconfig.py | xargs python3 ict_tool.py
       
    result zip file will be "ICT/projectname_stage_ICT_currentdate.zip"
