import json
import urllib.request


def get_project_id(group, name):
    """
    requests search of specified project group and name and returns found project id
    :param group: ABF group to use
    :param name: string like "import/project_name" to search in ABF
    :return: Project ID in ABF (number)
    """
    response = urllib.request.urlopen("https://abf.io/api/v1/search.json?type=projects&query=" + name)
    decode = response.read().decode("UTF-8")
    projects = json.loads(decode)['results']['projects']
    projects = [x for x in projects if "fullname" in x and x['fullname'] == group + "/" + name]
    if len(projects) > 0:
        project = projects[0]
        return project['id'], project['git_url']
    else:
        return None
