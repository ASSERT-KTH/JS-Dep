import os
import json
from utils import getSumInCSV

globalRepoList = dict()
calcSumWithAt = dict()


def countSharedDeps():
    depfile = open('repo_deps.txt', 'r')
    deps = depfile.read().split(',')
    sharedCount = 0
    depsDict = dict()
    for dep in deps:
        if not dep in depsDict:
            depsDict[dep] = 1
        else:
            depsDict[dep] += 1
    # print(depsDict)

    sortedDict = sorted(depsDict.items(), key=lambda x: x[1], reverse=True)

    with open('shared_deps.txt', mode='a') as depsFilename:
        for dep in sortedDict:
            if dep[1] > 1:
                sharedCount += 1
                outStr = dep[0] + ': ' + str(dep[1])
                depsFilename.write(outStr)
                depsFilename.write('\n')

    print('There are ' + str(sharedCount) +
          ' dependencies shared by more than 2 repos.')
    depfile.close()


def getAllDeps():
    depfile = open('repo_deps.txt', 'r')
    oldList = depfile.read().split(',')
    newList = list(set(oldList))
    print(len(newList))

    with open('all_deps.txt', mode='a') as depsFilename:
        for dep in newList:
            depsFilename.write(dep)
            depsFilename.write('\n')
    depfile.close()


def getNameFromGitUrl(url):
    return url[url.rfind('/')+1:url.rfind('.git')]


"""
Parameters:
dep: the git clone url of the dependency

Returns:
A string with two infos:
1. name of the repo
2. LOC of the repo
e.g audiobookshelf,18225
"""


def recordForSingleDep(depName, depUrl):
    os.system('git clone ' + depUrl)
    os.system('cloc ' + depName +
              ' --by-file --include-lang=JavaScript,JSON,TypeScript --csv --out=' + depName + '_deps.csv')
    os.system('rm -rf ' + depName)
    if os.path.exists(depName + '_deps.csv'):
        sumOfDep = getSumInCSV(depName + '_deps.csv')
        os.system('rm -rf ' + depName + '_deps.csv')
        return sumOfDep
    else:
        return False


def recordWithoutUrl(reponame, depName):
    try:
        print('enter................try, ', depName)
        exceptFolder = os.path.join(reponame + '/node_modules/' + depName)
        if os.path.exists(exceptFolder):
            clocFolder = exceptFolder
        else:
            clocFolder = os.path.join(
                reponame + '/node_modules/' + calcSumWithAt[depName] + '/' + depName)
        print('...............', clocFolder)
        os.system('cloc ' + clocFolder +
                  ' --by-file --include-lang=JavaScript,JSON,TypeScript --csv --out=' + depName + '_deps.csv')
        if os.path.exists(depName + '_deps.csv'):
            sumOfDep = getSumInCSV(depName + '_deps.csv')
            os.system('rm -rf ' + depName + '_deps.csv')
            print('...............sumOfDep,', sumOfDep)
            return sumOfDep
    except:
        print('enter................except, failed to calculate: ', depName)
        return 'None'


def getGitUrlFromPkg(pkgPath):
    if not os.path.exists(pkgPath):
        return False
    with open(pkgPath) as depPkg:
        depPkgJson = json.load(depPkg)
        if 'repository' in depPkgJson:
            try:
                if isinstance(depPkgJson['repository'], str):
                    origStr = depPkgJson['repository']
                    if 'thysultan/stylis' in origStr:
                        gitCloneUrl = 'https://github.com/thysultan/stylis.git'
                    elif 'https://' in origStr and '.git' in origStr:
                        gitCloneUrl = origStr
                    elif 'https://' in origStr and origStr[-1] == '/':
                        gitCloneUrl = origStr.strip('/') + '.git'
                    elif 'git@' in origStr:
                        gitCloneUrl = origStr.replace('git@', 'https://')
                    elif 'git://' in origStr:
                        gitCloneUrl = origStr.replace('git://', 'https://')
                        if not '.git' in gitCloneUrl:
                            gitCloneUrl += '.git'
                    elif 'github:' in origStr:
                        gitCloneUrl = origStr.replace(
                            'github:', 'https://github.com/') + '.git'
                    elif 'https://github.com' in origStr and not '.git' in origStr:
                        gitCloneUrl = origStr + '.git'
                    else:
                        gitCloneUrl = 'https://github.com/' + origStr + '.git'
                if isinstance(depPkgJson['repository'], dict):
                    # exit()
                    depUrl = depPkgJson['repository']['url']
                    if 'git@github.com:' in depUrl:
                        tmpUrl = depUrl
                        gitCloneUrl = tmpUrl.replace(
                            'git@github.com:', 'https://github.com/')
                    else:
                        gitCloneUrl = 'https:' + depUrl[depUrl.find('//'):]
                        if not '.git' in gitCloneUrl:
                            gitCloneUrl += '.git'
            except:
                if 'homepage' in depPkgJson:
                    gitCloneUrl = depPkgJson['homepage'] + '.git'

        else:
            return False
        return gitCloneUrl


def getDepListByRepo(reponame):
    # git clone, modify package.json, npm install, get all subfolders in node_modules

    with open(reponame + "/package.json") as f:
        pkgJson = json.load(f)
    # For repos that have devDependencies, empty them in package.json and install the repo.
    # That is because we do NOT need to count lines of code from devDependencies, which is
    # only used in develop environment. We only need to count lines of code in productive environment.
    if 'devDependencies' in pkgJson:
        # Crutial step: empty the depDependencies
        pkgJson["devDependencies"] = {}
        with open(reponame + "/package.json", 'w') as repoPkg:
            json.dump(pkgJson, repoPkg)

    os.system('cd ' + reponame + ' && npm install')

    depsFolder = os.path.join(reponame + '/node_modules')
    if not os.path.exists(depsFolder):
        print('Failed to perform npm install.....')
        return False

    # sometimes a package.json does not has repo url, in this situation, we do not consider it a effective dependency
    depList = list()
    depCount = 0

    for folder in os.listdir(depsFolder):
        if folder[0] == '.':
            continue

        depCount += 1
        print(folder, '\n')
        if folder[0] == '@':
            subDepsFolder = os.path.join(reponame + '/node_modules/' + folder)
            for subfolder in os.listdir(subDepsFolder):
                calcSumWithAt[subfolder] = folder
                subPckPath = os.path.join(
                    depsFolder + '/' + folder + '/' + subfolder + '/package.json')
                gitCloneUrl = getGitUrlFromPkg(subPckPath)
                if gitCloneUrl:
                    depList.append(gitCloneUrl)

        else:
            pckPath = os.path.join(depsFolder + '/' + folder + '/package.json')
            gitCloneUrl = getGitUrlFromPkg(pckPath)
            if gitCloneUrl:
                depList.append(gitCloneUrl)
        # Here we need to de-duplicate depList
        noDupDeplist = list(set(depList))
    return {'list': noDupDeplist, 'count': depCount}


def recordLocForAllDeps():
    repoFile = open('project_demo.txt', 'r')
    repoList = repoFile.read().split('\n')
    repoFile.close()

    with open('deps_loc.txt', mode='a') as depsFilename:
        for repo in repoList:
            repoUrl = repo.split(',')[0]
            cmt = repo.split(',')[1][0:8]
            reponame = getNameFromGitUrl(repoUrl)

            os.system('git clone ' + repoUrl)

            if not os.path.exists(reponame + "/package.json"):
                print('no package.json file')
                return False

            os.system('cd ' + reponame + ' && git checkout ' + cmt)
            os.system('cloc ' + reponame +
                      ' --by-file --include-lang=JavaScript,JSON,TypeScript --csv --out=' + reponame + '_deps.csv')
            sumOfRepo = getSumInCSV(reponame + '_deps.csv')

            depDict = getDepListByRepo(reponame)
            depList = depDict['list']
            depLength = str(len(depList))
            depCount = str(depDict['count'])

            for dep in depList:
                print(dep, '\n')
                depName = getNameFromGitUrl(dep)
                if depName in globalRepoList:
                    sumOfDep = globalRepoList[depName]

                else:
                    sumOfDep = recordForSingleDep(depName, dep)
                    if not sumOfDep:
                        print('................fail to get sumOfDep: ', depName)
                        sumOfDep = recordWithoutUrl(reponame, depName)
                        if not isinstance(sumOfDep, str):
                            sumOfDep = 'None'

                    globalRepoList[depName] = sumOfDep

                outString = reponame + ',' + cmt + ',' + \
                    sumOfRepo + ',' + depCount + ',' + depLength + \
                    ',' + depName + ',' + sumOfDep + '\n'
                depsFilename.write(outString)

            os.system('rm -rf ' + reponame + ' ' + reponame + '_deps.csv')


recordLocForAllDeps()
