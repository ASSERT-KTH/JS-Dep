import xlwt
import statistics
import math

globalDict = dict()
noneDict = dict()
shareDepDict = dict()
medianList = list()
excelFile = open('deps_loc.txt', 'r')
rowList = excelFile.read().split('\n')

for row in rowList:

    colums = row.split(',')
    isNone = colums[6] == 'None'

    if colums[5] not in shareDepDict:
        shareDepDict[colums[5]] = 1
    else:
        shareDepDict[colums[5]] += 1

    if isNone and colums[5] not in noneDict:
        noneDict[colums[5]] = 'None'

    if not colums[0] in globalDict:
        medianList.clear()

        initCount = 0 if isNone else 1
        initLoc = int(colums[6])
        globalDict[colums[0]] = {
            'name': colums[0],
            'commit': colums[1],
            'loc': colums[2],
            'depFolderCount': colums[3],
            'count': initCount,
            'sumInDep': initLoc,
            'maxDep': initLoc,
            'minDep': initLoc,
            'medianNum': 0
        }
        if not isNone:
            medianList.append(initLoc)
    else:
        addCount = 0 if isNone else 1
        if isNone:
            sumCount = 0
        else:
            sumCount = int(colums[6])
            medianList.append(sumCount)

        globalDict[colums[0]]['count'] += addCount
        globalDict[colums[0]]['sumInDep'] += sumCount
        globalDict[colums[0]]['maxDep'] = globalDict[colums[0]]['maxDep'] if (
            globalDict[colums[0]]['maxDep'] > sumCount or isNone) else sumCount
        globalDict[colums[0]]['minDep'] = globalDict[colums[0]]['minDep'] if (
            globalDict[colums[0]]['minDep'] < sumCount or isNone) else sumCount

        globalDict[colums[0]]['medianNum'] = medianNum = math.floor(
            statistics.median(medianList))

for name in globalDict:
    ratio = round(int(
        globalDict[name]['loc']) * 100 / (int(globalDict[name]['sumInDep']) + int(globalDict[name]['loc'])), 2)
    globalDict[name]['ratio'] = str(ratio)


def saveStat():
    with open('stat.txt', mode='a') as statFile:
        for name in globalDict:
            statFile.write(str(globalDict[name]))
            statFile.write('\n')


def saveNoneDep():
    with open('none_stat.txt', mode='a') as noneFile:
        for name in noneDict:
            outStr = name + ', None' + '\n'
            noneFile.write(outStr)


def saveSharedDep():
    sortedDict = sorted(shareDepDict.items(), key=lambda x: x[1], reverse=True)
    with open('shared_deps.txt', mode='a') as sharedFile:
        for shared in sortedDict:
            outStr = shared[0] + ': ' + str(shared[1])
            sharedFile.write(outStr)
            sharedFile.write('\n')


def saveToExcel():
    header = ['project', 'commit', 'loc of app', 'num of dep',
              'loc of dep', 'maxDep', 'minDep', 'median of Dep', 'ratio']

    book = xlwt.Workbook(encoding='utf-8', style_compression=0)

    sheet = book.add_sheet('test', cell_overwrite_ok=True)

    # set header
    i = 0
    for k in header:
        sheet.write(0, i, k)
        i = i + 1

    # write to excel
    row = 1
    for dep in globalDict:
        print(dep)
        sheet.write(row, 0, globalDict[dep]['name'])
        sheet.write(row, 1, globalDict[dep]['commit'])
        sheet.write(row, 2, globalDict[dep]['loc'])
        sheet.write(row, 3, globalDict[dep]['count'])
        sheet.write(row, 4, globalDict[dep]['sumInDep'])
        sheet.write(row, 5, globalDict[dep]['maxDep'])
        sheet.write(row, 6, globalDict[dep]['minDep'])
        sheet.write(row, 7, globalDict[dep]['medianNum'])
        sheet.write(row, 8, globalDict[dep]['ratio'])
        row = row + 1

    book.save('order.xls')


saveToExcel()
# saveSharedDep()
# saveStat()
# saveNoneDep()
excelFile.close()
