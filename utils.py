import os
import json
import csv
import statistics
import math


def npmInstall(reponame):
    print('enter npmInstall....')

    # For repos that do not have a package.json, return false.
    if not os.path.exists(reponame + "/package.json"):
        print('no package.json file')
        return False

    with open(reponame + "/package.json") as f:
        pkg_json = json.load(f)

    # For repos that have devDependencies, empty them in package.json and install the repo.
    # That is because we do NOT need to count lines of code from devDependencies, which is
    # only used in develop environment. We only need to count lines of code in productive environment.
    if 'devDependencies' in pkg_json:
        os.system("rm -r " + reponame + "/node_modules")
        # Next step is to back up the initial package.json, it is not nessacery
        # in this experiment, just in case.
        os.system("mv " + reponame + "/package.json " +
                  reponame + "/TEMP_package.json_TEMP")

        # Crutial step: empty the depDependencies, and recover the original package.json.
        pkg_json["devDependencies"] = {}
        with open(reponame + "/package.json", 'w') as f:
            json.dump(pkg_json, f)

    # No matter the repo has devDependecies or not, we need to install the project,
    # and count lines of code after installation.
    # Then we can get the entire code in the whole repo with dependencies.
    os.system('cd ' + reponame + ' && npm install')

    # Count lines of code
    getLocOfEntire(reponame)

    # Collect info of dependencies
    if recordDeps(reponame):
        return True
    else:
        return False


def getLocOfRepo(reponame):
    os.system('cloc ' + reponame +
              ' --include-lang=JavaScript,JSON,TypeScript --csv --out=' + reponame + '.csv')


def getLocOfEntire(reponame):
    print('enter: getLocOfEntire...................')
    os.system('cloc ' + reponame +
              ' --include-lang=JavaScript,JSON,TypeScript --csv --out=' + reponame + '_entire.csv')


def getLengthOfdeps(reponame):
    if not os.path.exists(reponame + "/package.json"):
        print('no package.json file')
        return

    with open(reponame + "/package.json") as f:
        pkg_json = json.load(f)

    if 'dependencies' in pkg_json:
        depLength = len(pkg_json['dependencies'])
    else:
        depLength = 0

    return depLength


def getSumInCSV(filename):
    total_lines = 0

    # Count the number of lines in csv
    with open(filename, "r", encoding="utf-8", errors="ignore") as scraped:
        reader = csv.reader(scraped)
        lines = list(reader)
        total_lines = len(lines)
    # get the last number in the last line
    with open(filename, "r", encoding="utf-8", errors="ignore") as scraped:
        reader = csv.reader(scraped)
        for index, row in enumerate(reader):
            if index == total_lines - 1:
                return(row[-1])


def countRatio(reponame):
    print('enter: count ratio......')
    own_sum = getSumInCSV(reponame + '.csv')

    if not os.path.exists(reponame + "/package.json"):
        return 0

    app_sum = getSumInCSV(reponame + '_entire.csv')

    d = dict()
    own_loc = int(own_sum)
    app_loc = int(app_sum)
    dep_loc = app_loc - own_loc
    d['own_loc'] = own_loc
    d['app_loc'] = app_loc
    d['dep_loc'] = dep_loc
    d['ratio'] = round(own_loc / app_loc, 2)
    return d


def recordDeps(reponame):
    depsFolder = reponame + '/node_modules'
    if not os.path.exists(depsFolder):
        print('Failed to perform npm install.....')
        return False

    count = 0
    for files in os.listdir(depsFolder):
        # Filter files with a name starts with a '.'
        if files[0] != '.':
            count += 1
    try:
        os.system('cloc ' + depsFolder +
                  ' --by-file --include-lang=JavaScript --csv --out=' + reponame + '_deps.csv')
        return True
    except:
        print('Errors happened in cloc counting....')
        return False


def countMedianOfDeps(csvname):
    print('enter: calculate median number......')
    if not os.path.exists(csvname + '_deps.csv'):
        print('no repo_deps.csv file')
        return False

    depsDict = dict()

    with open(csvname + '_deps.csv', "r", encoding="utf-8", errors="ignore") as scraped:
        reader = csv.reader(scraped)
        for row in reader:
            # For each row in .csv file, we regonise each dependencies by name
            # and the corresponding lines of JS code, store them to a dict
            # From: JavaScript,finalhandler/node_modules/unpipe/index.js,15,22,32
            # Get: dict: { 'unpipe', 32 }
            pathSplit = row[1].split('/')
            if len(pathSplit) > 2:
                dep = pathSplit[2]
                lines = int(row[4])
                if not dep in depsDict:
                    depsDict[dep] = lines
                else:
                    depsDict[dep] += lines

    if len(depsDict):
        depsList = list(depsDict.keys())

        # Meanwhile log all dependencies into repoDeps.txt,
        # for counting dependencies shared by more than 2 repos.
        with open('repo_deps.txt', mode='a') as depsFilename:
            for dep in depsList:
                depsFilename.write(dep)
                depsFilename.write(',')

        return math.floor(statistics.median(depsDict.values()))


def gitLogForRepo(reponame):
    os.system('cd ' + reponame + ' && git --no-pager log > ' +
              '../' + reponame + '_log.txt')


def getCommitsOfRepo(reponame):
    cmtDict = dict()
    logfile = open(reponame + '_log.txt', 'r')
    # Get the first commit
    firstCommit = logfile.readline()
    count = 1

    # THEN, read line by line.
    Lines = logfile.readlines()
    # Strips the newline character
    for line in Lines:
        if line.startswith('commit'):
            count += 1
            # print("Line{}: {}".format(count, line.strip()))

    # Get the first 8 characters of the first commits
    cmtDict['fst_commit'] = firstCommit[7:]
    cmtDict['total_commits'] = str(count)
    logfile.close()
    return cmtDict
