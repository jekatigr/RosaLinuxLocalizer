import os

import yaml

from repo_handler import mirror_repo_to_tmp


def from_file_with_list(path):
    with open(path, 'r') as stream:
        try:
            loaded = yaml.load(stream)["places"]
            files = [f["path"] for f in loaded if f["type"] == "file"]
            directories = [f["path"] for f in loaded if f["type"] == "dir"]
            files_in_directories = [directory+file for directory in directories for file in os.listdir(directory) if
                                    ".rpm" in file]
            files_from_repos = [mirror_repo_to_tmp(repo["values"][0]) for repo in loaded if repo["type"] == "repo"]
            return files + files_in_directories + files_from_repos
        except yaml.YAMLError as exc:
            return {"errors": exc}