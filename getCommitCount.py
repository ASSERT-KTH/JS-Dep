import requests

base_url = 'https://api.github.com'


def get_all_commits_count(owner, repo, sha):
    first_commit = get_first_commit(owner, repo)
    compare_url = '{}/repos/{}/{}/compare/{}...{}'.format(
        base_url, owner, repo, first_commit, sha)

    commit_req = requests.get(compare_url)
    if 'total_commits' in commit_req.json():
        commit_count = commit_req.json()['total_commits'] + 1
        return commit_count
    else:
        return 0


def get_first_commit(owner, repo):
    url = '{}/repos/{}/{}/commits'.format(base_url, owner, repo)
    req = requests.get(url)
    json_data = req.json()

    if req.headers.get('Link'):
        page_url = req.headers.get('Link').split(',')[1].split(';')[
            0].split('<')[1].split('>')[0]
        req_last_commit = requests.get(page_url)
        first_commit = req_last_commit.json()
        first_commit_hash = first_commit[-1]['sha']
    else:
        first_commit_hash = json_data[-1]['sha']
    return first_commit_hash


def get_last_commit_sha(owner, repo):
    # e.g. https://api.github.com/repos/duty-machine/news/commits?per_page=1
    url = '{}/repos/{}/{}/commits?per_page=1'.format(base_url, owner, repo)
    req = requests.get(url)
    json_data = req.json()
    return json_data[0]['sha']


def main():
    owner = 'getredash'
    repo = 'redash'
    # Took the last commit, Can do it automatically also but keeping it open
    sha = '5ba15ef35074a88daa5032ec4bec34d3a22a607e'
    get_all_commits_count(owner, repo, sha)


if __name__ == '__main__':
    main()
