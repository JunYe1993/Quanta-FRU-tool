#!/bin/python3
import os
import glob, re, subprocess

def remove_folder(dir):
    command = "rm -r %s" % dir
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

def clear_folder():
    # remove folder _***_FRU_v***
    for raw in glob.glob("*"):
        pattern = r'_(.*)_FRU_v[0-9]+'
        x = re.search(pattern, raw)
        if os.path.isdir(raw) and x != None:
            remove_folder(raw)

def clear_ict_folder():
    # remove folder _***_ICT_v***
    for raw in glob.glob("ICT/*"):
        pattern = r'_FRU'
        x = re.search(pattern, raw)
        if os.path.isdir(raw) and x != None:
            remove_folder(raw)

def clear_json():
    # remove json file
    for raw in glob.glob("*.json"):
        os.remove(raw)

if __name__ == "__main__":
    clear_folder()
    clear_ict_folder()
    clear_json()