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

#### Count lines of code for each repo

We use [cloc](http://cloc.sourceforge.net/) to count lines of code (only containing JavaScript, JSON, and TypeScript) for each repo. To recognize the summary of the code, we output the result to `.csv` files. 

One example is like the following output:

 ```
 files,language,blank,comment,code,"github.com/AlDanial/cloc v 1.92  T=5.61 s (751.1 files/s, 123129.4 lines/s)"
 3766,JavaScript,67347,66935,490154
 322,JSON,62,0,52704
 128,TypeScript,1988,3375,8563
 4216,SUM,69397,70310,551421                   
 ```

For each `.csv` file, we extract the element in the last column of the last row, which represents the summary of lines of (JavaScript, JSON, TypeScript) code that we truly want. The python script is like the following code:

```python
def getSumInCSV(filename):
    total_lines = 0

    # Count the number of lines in csv
    with open(filename, "r", encoding="utf-8", errors="ignore") as scraped:
        reader = csv.reader(scraped)
        lines = list(reader)
        total_lines = len(lines)
        print(total_lines)
    # get the last number in the last line
    with open(filename, "r", encoding="utf-8", errors="ignore") as scraped:
        reader = csv.reader(scraped)
        for index, row in enumerate(reader):
            if index == total_lines - 1:
                return(row[-1])
```



#### Count median number for lines of code for dependencies

```python
# Use a dict to store lines of code for each dependency of a repo
depsDict = dict()
with open('finalhandler.csv', "r", encoding="utf-8", errors="ignore") as scraped:
    reader = csv.reader(scraped)
    for row in reader:
        # For each row in .csv file, we regonise each dependencies by name
        # and the corresponding lines of JS code, store them to a dict
        # From: JavaScript,finalhandler/node_modules/unpipe/index.js,15,22,32
        # Get: unpipe, 32
        # print(row[1].split('/'))

        # print('filename', row[1], 'lines: ', row[4])
        pathSplit = row[1].split('/')
        if len(pathSplit) > 2:
            dep = pathSplit[2]
            lines = int(row[4])
            if not dep in depsDict:
                depsDict[dep] = lines
            else:
                depsDict[dep] += lines
print(depsDict)
print(statistics.median(depsDict.values()))

```



#### Some projects that we do not count

+ Projects without dependencies.

+ Projects with only @ dependencies:

  For example, [ERC721A](https://github.com/chiru-labs/ERC721A#readme)

  ```
  "dependencies": {
      "@openzeppelin/contracts": "^4.4.2"
   },
  ```



#### Some issues we have encountered

+ Failed to run `npm install`

  Some bugs may exist in npm-cli when installing some specific package: same [here](https://github.com/npm/cli/issues/3257)

  We meet this problem when installing [bitshares-ui](https://github.com/bitshares/bitshares-ui)

+ Sometimes we meet Babel problems that is really time-consuming.

  ```
  [BABEL] Note: The code generator has deoptimised the styling of /Users/yuxinliu/Documents/Develop/JS-Dep/auspice/node_modules/react-icons/fa/index.esm.js as it exceeds the max of 500KB.
  ```

+ Sometimes we meet problems happen in *cloc*. There might be files that cloc can not manipulate.

  For example, in [audiobookshelf](https://github.com/advplyr/audiobookshelf), we meet such error:

  ```
  Line count, exceeded timeout:  audiobookshelf/node_modules/axios/dist/axios.min.js
  ```

  