# inner = sys.stdin.read()
import json

import settings_keeper
from gitworks import prepare_patch, push_patch
from handsome import full_project_info
from list_utils import filter_input
from translation import translate
import uuid

import argparse

from yaml_importer import from_file_with_list

parser = argparse.ArgumentParser(description='Translate some packages')
parser.add_argument('--git-branch', dest="git_branch", default="master")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--prepare', dest='target', action='store_const', const='prepare')
group.add_argument('--translate', dest='target', action='store_const', const='translate')
group.add_argument('--commit', dest='target', action='store_const', const='commit')
parser.add_argument('file', metavar='filename.yml', type=str,
                    help='an integer for the accumulator')
args = parser.parse_args()
settings = json.loads(settings_keeper.load_settings())
project_group = settings["abf_projects_group"]
yandex_api_key = settings["yandex_api_key"]

assert translate(yandex_api_key, "en-ru",
                 "Lazy cat jumps over talking dog") == "Ленивый кот перепрыгивает через говорящая собака"

project_info = [full_project_info(project_group, f, ["Name", "Comment"]) for f in from_file_with_list(args.file)]

for one in project_info:
    random_str = uuid.uuid4().hex.capitalize()
    for f in one["desktop_files"]:
        for i in f["strings"]:
            if args.target in ['translate', 'commit']:
                i["value"]["ru"] = translate(yandex_api_key, "en-ru", i["value"]["en"])
            else:
                i["value"]["ru"] = "    "
    prepare_patch(random_str, one["git"], one["package_name"], json.dumps(one["desktop_files"]),
                  args.git_branch)
    if (args.target == 'commit'):
        push_patch(random_str)
