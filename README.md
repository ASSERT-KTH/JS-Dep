# JS-Dep

## Fetch projects from GitHub

We fetch data through [REST API](https://docs.github.com/en/rest)  by Python.

In order to use a python script to get the data and manipulate .json files, we need to install the `requests` library for our python script.

#### Request REST API

The following code is an example for fetching projects with **more than 100** stars, programming language is **JavaScript**, and the top **10** items. The original dataset is ordered by the most resent projects in GitHub.



```python
import requests

from requests.structures import CaseInsensitiveDict

url = 'https://api.github.com/search/repositories?q=stars:%3E100+language:javascript&per_page=10&sort=updated'

headers = CaseInsensitiveDict()
headers['Accept'] = 'application/vnd.github.mercy-preview+json'

resp = requests.get(url, headers=headers)
```

#### Filter projects

Not all projects responsed meet our cretiria. We want projects with at least one dependency.

```python
if deps == 0 or deps == None:
	  os.system('rm -rf ' + repo_name)
	  continue
```



## Issues right now:

### In Projects:

1. list: not by dependencies, but by updated time.

the largest number of dependencies → most recently published.

1. random data, difficult to reproduce
2. about the criteria of a number of stars, how to find references?
3. Projects with “Dep 0 or Dep None” are more than I expected. That leads to a collection with more time.
4. There are projects with no package.json

### In dataset

commits:

Due to the [rate limit for GitHub API](https://docs.github.com/en/developers/apps/building-github-apps/rate-limits-for-github-apps): How to deal with such a situation? Request manually one time for each project?

LOCDEP:

How to deal with the massive text files?