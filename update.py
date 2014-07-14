#!/usr/bin/python
import os
import shutil
from chocolatey import process_chocolatey, postprocess_chocolatey
from url import process_url, postprocess_url
from zipfile import ZipFile

def loadconfig(filename):
    f = open(os.path.join("config",filename))
    cfg = {}
    for line in f:
        line = line.strip().split(" ",1)
        cfg[line[0]] = line[1]
    if "path" in cfg:
        cfg["dest_dir"] = os.path.join("root",os.path.join(*cfg["path"].split("/")))
        cfg["path"] = os.path.join(cfg["dest_dir"],cfg["filename"])
    return cfg


def move_file(config):
    if not "filename" in config:
        return
    # Make the destination dir if it doesn't already exist
    if not os.path.exists(config["dest_dir"]):
        os.makedirs(config["dest_dir"])
    # If the file already exists, delete it
    if os.path.exists(config["path"]):
        os.unlink(config["path"])
    # move the newly downloaded file into place
    print("Moving %s into place for %s"%(config["filename"],config["friendly_name"]))
    shutil.move(os.path.join("temp",config["filename"]),config["path"])

def process(config):
    if config["type"] == "chocolatey":
        return process_chocolatey(config)
    if config["type"] == "url":
        return process_url(config)

def postprocess(config):
    move_file(config)

    if config["type"] == "chocolatey":
        postprocess_chocolatey(config)
    if config["type"] == "url":
        postprocess_url(config)

    if "zipfile" in config and config["zipfile"] == "yes":
        zf = ZipFile(os.path.join(config["path"]))
        if not os.path.exists(os.path.join("root",config["zipfile_extract_path"])):
            os.makedirs(os.path.join("root",config["zipfile_extract_path"]))
        zf.extractall(os.path.join("root",config["zipfile_extract_path"]))
        os.unlink(os.path.join(config["path"]))


def main():
    if not os.path.exists("temp"):
        os.makedirs("temp")
    for filename in os.listdir("config"):
        if not filename[-3:] == "cfg" or filename[:1] == ".": # Skip over other files in that dir that don't end in cfg, or dotfiles
            continue
        config = loadconfig(filename)
        if not process(config) == "NOPOST":
            postprocess(config)


main()
