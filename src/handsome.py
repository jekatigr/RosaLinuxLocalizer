#!/usr/bin/python3
import os
import shutil
import uuid
from os import walk
from subprocess import call, Popen, PIPE

from abf_interface import get_project_id
from os import path


def read_desktop(dir_name, file, dyn_names):
    """
    this creates list of dictionary structure with variable name and provider en and ru translations
    :param dyn_names: list of names to read from .desktop file
    :param dir_name: directory to read file from
    :param file: RPM-root relative file name
    :return: list of dict
    """
    va = []
    with open(dir_name + file) as d:
        va.extend(d.read().split("\n"))
    t = [[a + "=", a + "[ru]="] for a in dyn_names]
    k = [a for g in t for a in g]
    mixed = [one for one in va for b in k if b in one and one[0] != '#']
    en = [one.split("=") for one in mixed if "[ru]" not in one]
    ru = [one.split("=") for one in mixed if "[ru]" in one]
    enchanted_en = dict([(one[0], {"variable_name": one[0], "value": {"en": one[1]}}) for one in en])
    for (name, value) in ru:
        entry = enchanted_en[name[:-4]]
        entry["value"]["ru"] = value
        enchanted_en[name[:-4]] = entry
    return [enchanted_en[a] for a in enchanted_en]


def read_file(way):
    with open(way) as d:
        return d.read()


def read_rpm_file(filename, dyn_names):
    """
    reads desktop file from supplied filename and yields list of desktop files here,
    for each desktop file yields list of strings to be localized
    :param dyn_names: list of strings to extract from file
    :param filename: file to read desktop files from
    :return: [desktop_file_name, [pair, pair]]
    """
    random_str = uuid.uuid4().hex.capitalize()
    basename = os.path.basename(filename)
    dir_name = path.expanduser('~') + "/" + random_str + "/"
    new_name = dir_name + basename
    os.mkdir(path.expanduser('~') + "/" + random_str)
    shutil.copy(filename, new_name)

    call_string = "cd " + dir_name + " && rpm2cpio " + basename + " | cpio -idmv"
    call(call_string, shell=True, stderr=PIPE)
    os.remove(new_name)

    f = []
    for (dir_path, dir_names, file_names) in walk(dir_name):
        f.extend([(dir_path + "/" + x)[len(dir_name):] for x in file_names if ".desktop" in x])

    desktop_file_entries = [
        {"path": line, "strings": read_desktop(dir_name, line, dyn_names), "containment": read_file(dir_name + line)}
        for line in f]

    shutil.rmtree(dir_name)

    return desktop_file_entries


def get_rpm_project_name(filename):
    """
    executes rpm command against specified file to obtain ABF project name
    :param filename:  file to execute command against
    :return: ABF project name string
    """
    process = Popen("rpm -qp --qf=\"%{SOURCERPM}\" " + filename + "| rev | cut -f3- -d- | rev", shell=True, stderr=PIPE,
                    stdout=PIPE)
    out, err = process.communicate()
    return out.decode("UTF-8")[:-1]


def full_project_info(group, filename, dyn_names):
    """
    This returns all information gathered from RPM file and quick ABF lookup.
    :param group: ABF group to look project in
    :param filename: path to provided RPM file
    :return: complex dict structure
    """
    project_name = get_rpm_project_name(filename)

    if "(none)" == project_name:
        return None, filename

    t = get_project_id(group, project_name)
    if t is None:
        return None, filename
    b, a = t
    file = read_rpm_file(filename, dyn_names)
    if len(file) == 0:
        status = 3
    elif any([len(var["value"]) < 2 for b in file for var in b["strings"]]):
        status = 2
    else:
        status = 4

    return {"status": status, "rpm": filename, "package_name": project_name, "git": a, "project_id": b,
            "desktop_files": file}
