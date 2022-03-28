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

    with open('shared_deps.txt', mode='a') as depsFilename:
        for dep in depsDict:
            if depsDict[dep] > 1:
                sharedCount += 1
                outStr = dep + ': ' + str(depsDict[dep])
                depsFilename.write(outStr)
                depsFilename.write('\n')

    print('There are ' + str(sharedCount) +
          ' dependencies shared by more than 2 repos.')
    depfile.close()


countSharedDeps()
