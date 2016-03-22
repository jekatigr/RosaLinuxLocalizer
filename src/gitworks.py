import codecs
import json
import uuid
from os import path
from subprocess import call, PIPE
from difflib import unified_diff
from settings_keeper import load_settings


def prepare_patch(random_str, repo_path, package_name, patch_content, branch_name):
    """
    This is for saving patch file, adding it to git and pushing back to ABF.
    :param random_str:
    :param repo_path: git URL to clone from (ssh, https)
    :param package_name: package name to open spec file from
    :param patch_content: text to write to patch file
    :return: nothing
    """
    settings = json.loads(load_settings())
    login = settings["abf_login"]
    password = settings["abf_password"]
    new_repo_path = repo_path[:8] + login + ":" + password + "@" + repo_path[8:]
    print(random_str + " - " + package_name)
    call("cd " + path.expanduser('~') + "/ && git clone " + new_repo_path + " " + random_str +
         " && cd " + random_str + " && git checkout " + branch_name, shell=True, stdout=PIPE, stderr=PIPE)
    call("ls " + path.expanduser('~') + "/" + random_str, shell=True, stdout=PIPE)
    call("touch " + path.expanduser('~') + "/" + random_str + "/" + random_str + ".patch", shell=True, stdout=PIPE)

    with open("" + path.expanduser('~') + "/" + random_str + "/" + random_str + ".patch", "w") as concrete:
        for file in json.loads(patch_content):
            containment1 = [e + '\n' for e in file["containment"].split('\n') if e != ""]
            containment2 = containment1[:]
            for line in file["strings"]:
                containment2.append(line["variable_name"] + "[ru]=" + line["value"]["ru"] + "\n")
            for line in unified_diff(containment1, containment2, fromfile=file["path"], tofile=file["path"]):
                concrete.write(line)
    call("cd " + path.expanduser('~') + "/" + random_str + "/ && git add " + random_str + ".patch", shell=True,
         stdout=PIPE)
    call("sed -i \"1iPatch: " + random_str + ".patch\" " + path.expanduser(
        '~') + "/" + random_str + "/" + package_name + ".spec", shell=True, stdout=PIPE)


def push_patch(random_str):
    call("cd " + path.expanduser('~') + "/" + random_str + " && git commit -am \"Переведено\" && git push", shell=True,
         stdout=PIPE)
    # call("cd " + path.expanduser('~') + "/ && rm -rf " + random_str, shell=True, stdout=PIPE)
