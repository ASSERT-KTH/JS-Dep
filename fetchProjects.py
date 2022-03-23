import requests
import os
# import json

import getCommitCount
import countRatioUtils

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
    repo_name = p['name']

    with open('projects.txt', mode='a') as project_filename:
        project_filename.write(p['clone_url'])
        project_filename.write('\n')

    # getCommitCount.get_last_commit_sha(owner, repo_name)
    # last_sha = getCommitCount.get_last_commit_sha(owner, repo_name)
    # print(last_sha)
    # commit_count = getCommitCount.get_all_commits_count(
    #     owner, repo_name, last_sha)
    # print(commit_count)

    os.system('git clone ' + p['clone_url'])
    deps = countRatioUtils.getLengthOfdeps(repo_name)
    print("deps: ")
    print(deps)

    if deps == 0 or deps == None:
        os.system('rm -rf ' + repo_name)
        continue
    else:
        os.system('cloc ' + repo_name + ' --out=' + repo_name + '.txt')
        if not countRatioUtils.reinstall(repo_name):
            continue
        radio_dict = countRatioUtils.countRatio(repo_name)

        os.system('rm -rf ' + repo_name)

        # outStr = p['name'] + '&' + str(commit_count) + '&' + p['pushed_at'][0:10] + \
        #     '&' + str(deps) + '&' + str(p['watchers_count']) + '\r'

        with open('table1.txt',  mode='a') as table_outfile:
            outStr = '\\texttt ' + p['name'] + ' & ' + 'commits' + ' & ' + p['pushed_at'][0:10] + ' & ' + str(
                radio_dict['own_loc']) + ' & ' + str(deps) + ' & ' + str(p['watchers_count']) + ' \\\\ ' + '\n'
            table_outfile.write(outStr)

        with open('table2.txt',  mode='a') as table_outfile:
            outStr = '\\texttt ' + p['name'] + ' & ' + str(
                radio_dict['own_loc']) + ' & ' + str(radio_dict['dep_loc']) + ' & ' + str(round(radio_dict['dep_loc'] / deps, 1)) + ' & ' + str(radio_dict['ratio']) + ' \\\\ ' + '\n'
            table_outfile.write(outStr)
