import requests
import os
# import json

from utils import *
from requests.structures import CaseInsensitiveDict

url = 'https://api.github.com/search/repositories?q=stars:%3E100+language:javascript&per_page=100&sort=updated'

headers = CaseInsensitiveDict()
headers['Accept'] = 'application/vnd.github.mercy-preview+json'

resp = requests.get(url, headers=headers)

print('start processing...')


for p in resp.json()['items']:
    # In test environment: filter small projects to save time.
    if p['size'] > 50000:
        continue

    owner = p['owner']['login']
    reponame = p['name']

    with open('projects.txt', mode='a') as projectFilename:
        projectFilename.write(p['clone_url'])
        projectFilename.write('\n')

    os.system('git clone ' + p['clone_url'])
    deps = getLengthOfdeps(reponame)

    if deps == 0 or deps == None:
        os.system('rm -rf ' + reponame)
        continue
    else:
        # git log
        gitLogForRepo(reponame)

        # Count lines of code before 'npm install'
        getLocOfRepo(reponame)

        # After 'npm install', calculate the ratio.
        if not npmInstall(reponame):
            continue
        radioDict = countRatio(reponame)

        # Get median number for dependencies:
        medianNum = countMedianOfDeps(reponame)

        if not medianNum:
            continue

        # Get commits from log
        cmtDict = getCommitsOfRepo(reponame)

        os.system('rm -rf ' + reponame)

        # generating data for table1

        with open('table1.txt',  mode='a') as table_outfile:
            outStr = '\\texttt ' + p['name'] + '(\\href{https://github.com/' + owner + '/' + reponame + '/commit/' + cmtDict['fst_commit'] + '}{' + cmtDict['fst_commit'][7:15] + '})' + ' & ' + cmtDict['total_commits'] + ' & ' + p['pushed_at'][0:10] + ' & ' + str(
                radioDict['own_loc']) + ' & ' + str(deps) + ' & ' + str(p['watchers_count']) + ' \\\\ ' + '\n' + '\\hline \n'
            table_outfile.write(outStr)

        # generating data for table2
        with open('table2.txt',  mode='a') as table_outfile:
            outStr = '\\texttt ' + p['name'] + ' & ' + str(
                radioDict['own_loc']) + ' & ' + str(radioDict['dep_loc']) + ' & ' + str(medianNum) + ' & ' + str(radioDict['ratio']) + ' \\\\ ' + '\n' + '\\hline \n'
            table_outfile.write(outStr)
