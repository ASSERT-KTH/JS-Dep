import os
import json
from statistics import median


def reinstall(repo_name):
    print('enter reinstall')

    if not os.path.exists(repo_name + "/package.json"):
        print('no package.json file')
        return False
    with open(repo_name + "/package.json") as f:
        pkg_json = json.load(f)
    if 'devDependencies' in pkg_json:
        os.system("rm -r " + repo_name + "/node_modules")
        os.system("mv " + repo_name + "/package.json " +
                  repo_name + "/TEMP_package.json_TEMP")

        pkg_json["devDependencies"] = {}

        with open(repo_name + "/package.json", 'w') as f:
            json.dump(pkg_json, f)

    os.system('cd ' + repo_name + ' && npm install')
    os.system('cloc ' + repo_name + ' --out=' + repo_name + '_entire.txt')
    # TODO: median LOCDEP
    return True


def getLengthOfdeps(repo_name):
    if not os.path.exists(repo_name + "/package.json"):
        print('no package.json file')
        return
    with open(repo_name + "/package.json") as f:
        pkg_json = json.load(f)

    if 'dependencies' in pkg_json:
        depLength = len(pkg_json['dependencies'])
    else:
        depLength = 0

    return depLength


def countRatio(reponame):
    print('enter count ratio......')
    with open(reponame + ".txt", "r") as file:
        last_line = file.readlines()[-2]
        own_sum = last_line.split(' ')
        print(own_sum[-1])

    if not os.path.exists(reponame + "/package.json"):
        return 0

    with open(reponame + "_entire.txt", "r") as file:
        sum_last_line = file.readlines()[-2]
        app_sum = sum_last_line.split(' ')
        print(app_sum[-1])

    d = dict()
    own_loc = int(own_sum[-1])
    app_loc = int(app_sum[-1])
    dep_loc = app_loc - own_loc
    d['own_loc'] = own_loc
    d['app_loc'] = app_loc
    d['dep_loc'] = dep_loc
    d['ratio'] = round((app_loc - own_loc) / app_loc, 2)
    return d
