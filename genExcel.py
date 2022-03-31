import xlwt
import statistics
import math

globalDict = dict()

excelFile = open('excel_demo.txt', 'r')
rowList = excelFile.read().split('\n')

for row in rowList:
    colums = row.split(',')
    if not colums[0] in globalDict:
        depListName = list()
        depListLoc = list()
        globalDict[colums[0]] = {
            'name': colums[0],
            'commit': colums[1],
            'loc': colums[2],
            'depFolderCount': colums[3],
            'count': 1,
            'depListName': depListLoc.append(colums[5]),
            'depListLoc': depListLoc.append(colums[6]),
            'locInDep': colums[6]
        }
    else:
        globalDict[colums[0]]['count'] += 1
        globalDict[colums[0]]['depListName'].append(colums[5])
        globalDict[colums[0]]['depListLoc'].append(colums[6])
        globalDict[colums[0]]['locInDep'] += colums[6]


for dep in globalDict:
    dep['medianDep'] = math.floor(statistics.median(dep['depListLoc']))

print(globalDict)

excelFile.close()
