# JS-Dep

## Fetch projects from GitHub

We fetch data through [REST API](https://docs.github.com/en/rest)  by Python.

In order to use a python script to get the data and manipulate .json files, we need to install the `requests` library for our python script.

#### Request REST API

The following code is an example for fetching projects with **more than 100** stars, the programming language is **JavaScript,** and the first **100** items. The original dataset is ordered by the most recent update projects on GitHub. From the responded projects, we can see some detailed information of the repo. Among them, there is a `watchers_count` representing the number of stars of the repo.

```python
import requests

from requests.structures import CaseInsensitiveDict

url = 'https://api.github.com/search/repositories?q=stars:%3E100+language:javascript&per_page=100&sort=updated'

headers = CaseInsensitiveDict()
headers['Accept'] = 'application/vnd.github.mercy-preview+json'

resp = requests.get(url, headers=headers)
```

#### Filter projects

Not all projects that respond meet our criteria. We want projects with:

1. at least one dependency
2. less than 50MB

```python
if p['size'] > 50000:
    continue

if deps == 0 or deps == None:
	  os.system('rm -rf ' + repo_name)
	  continue
```

#### Get the direct dependencies of a repo

We process `package.json`, count the number of items in the key `dependencies`.

```python
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
```

#### Count total commits and the lastest commit

To count total commits for a repo, we do the following steps:

1. git clone the repo

2. git log and output to a file

3. recognize commits 

   ```python
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



#### Compute median number for lines of code for dependencies

We record

```python
def countMedianOfDeps(csvname):
    print('enter: calculate median number......')
    if not os.path.exists(csvname + '_deps.csv'):
        print('no repo_deps.csv file')
        return False

    # Use a dict to store lines of code for each dependency of a repo
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

```

#### Compute the ratio

After we get LOCs for the project before and after `npm install`, we calculate the ratio by `LOC_p / (LOC_p + LOC_DEP)`. Then we show the results in decreasing order.

#### Some projects that we do not count

+ Projects without dependencies.

+ Projects with only @ dependencies:

  For example, [ERC721A](https://github.com/chiru-labs/ERC721A#readme)

  ```
  "dependencies": {
      "@openzeppelin/contracts": "^4.4.2"
   },
  ```



#### Some issues that we have encountered

+ Failed to run `npm install`

  Some bugs may exist in npm-cli when installing some specific package: same [here](https://github.com/npm/cli/issues/3257)

  We meet this problem when installing [bitshares-ui](https://github.com/bitshares/bitshares-ui)

+ Sometimes we meet Babel problems that is really time-consuming.

  ```
  [BABEL] Note: The code generator has deoptimised the styling of /Users/yuxinliu/Documents/Develop/JS-Dep/auspice/node_modules/react-icons/fa/index.esm.js as it exceeds the max of 500KB.
  ```

+ Sometimes we meet problems happen in *cloc*. There might be files that *cloc* can not manipulate.

  For example, in [audiobookshelf](https://github.com/advplyr/audiobookshelf), we meet such error:

  ```
  Line count, exceeded timeout:  audiobookshelf/node_modules/axios/dist/axios.min.js
  ```

+ We can not only count direct sub-directories, there are folders with "namespace", like babel:
  ```
  nextjs-woocommerce/node_modules/@babel/helper-annotate-as-pure/package.json
  nextjs-woocommerce/node_modules/@babel/helper-function-name/package.json
  nextjs-woocommerce/node_modules/@babel/helper-get-function-arity/package.json
  nextjs-woocommerce/node_modules/@babel/types/package.json
  nextjs-woocommerce/node_modules/@babel/types/scripts/package.json
  nextjs-woocommerce/node_modules/@babel/helper-hoist-variables/package.json
  nextjs-woocommerce/node_modules/@babel/highlight/package.json
  nextjs-woocommerce/node_modules/@babel/highlight/node_modules/escape-string-regexp/package.json
  nextjs-woocommerce/node_modules/@babel/highlight/node_modules/color-name/package.json
  nextjs-woocommerce/node_modules/@babel/highlight/node_modules/chalk/package.json
  nextjs-woocommerce/node_modules/@babel/highlight/node_modules/has-flag/package.json
  nextjs-woocommerce/node_modules/@babel/highlight/node_modules/supports-color/package.json
  nextjs-woocommerce/node_modules/@babel/highlight/node_modules/color-convert/package.json
  nextjs-woocommerce/node_modules/@babel/highlight/node_modules/ansi-styles/package.json
  nextjs-woocommerce/node_modules/@babel/helper-split-export-declaration/package.json
  nextjs-woocommerce/node_modules/@babel/runtime/package.json
  nextjs-woocommerce/node_modules/@babel/runtime/helpers/esm/package.json
  nextjs-woocommerce/node_modules/@babel/template/package.json
  nextjs-woocommerce/node_modules/@babel/parser/package.json
  nextjs-woocommerce/node_modules/@babel/generator/package.json
  nextjs-woocommerce/node_modules/@babel/helper-validator-identifier/package.json
  nextjs-woocommerce/node_modules/@babel/helper-environment-visitor/package.json
  nextjs-woocommerce/node_modules/@babel/code-frame/package.json
  nextjs-woocommerce/node_modules/@babel/traverse/package.json
  nextjs-woocommerce/node_modules/@babel/traverse/node_modules/globals/package.json
  nextjs-woocommerce/node_modules/@babel/traverse/scripts/package.json
  nextjs-woocommerce/node_modules/@babel/helper-module-imports/package.json
  ```

  So at first, we list all "package.json" files and filter them with an effective repo_url. However, dealing with a list of package.json is a detour. There are many noisy items in this list. So we go back to list all directories (first-level directories, as well as second-level directories in a folder with a name like "@types"). Then we collect all effective package.json files into a list `depList` and consider this `depList` as a list of all dependencies of a repo.

  

  Another reason why we could use 'package.json' is sometimes the requesting is duplicated.

  ```
  nextjs-woocommerce,0132abef,9534,89,jsesc,1276
  nextjs-woocommerce,0132abef,9534,89,zen-observable-ts,6442
  nextjs-woocommerce,0132abef,9534,89,zen-observable,6108
  nextjs-woocommerce,0132abef,9534,89,algoliasearch-client-javascript,13746
  nextjs-woocommerce,0132abef,9534,89,DefinitelyTyped,2818910
  nextjs-woocommerce,0132abef,9534,89,DefinitelyTyped,2818910
  nextjs-woocommerce,0132abef,9534,89,DefinitelyTyped,2818910
  nextjs-woocommerce,0132abef,9534,89,react-instantsearch,67768
  nextjs-woocommerce,0132abef,9534,89,react,365425
  nextjs-woocommerce,0132abef,9534,89,react,365425
  nextjs-woocommerce,0132abef,9534,89,babel,502973
  nextjs-woocommerce,0132abef,9534,89,react,365425
  nextjs-woocommerce,0132abef,9534,89,loose-envify,12513
  nextjs-woocommerce,0132abef,9534,89,optimism,4398
  nextjs-woocommerce,0132abef,9534,89,styled-components,12949
  nextjs-woocommerce,0132abef,9534,89,camelize,139
  nextjs-woocommerce,0132abef,9534,89,css-to-react-native,1907
  nextjs-woocommerce,0132abef,9534,89,algoliasearch-helper-js,23823
  nextjs-woocommerce,0132abef,9534,89,tslib,826
  nextjs-woocommerce,0132abef,9534,89,picomatch,7998
  nextjs-woocommerce,0132abef,9534,89,react-hook-form,42605
  nextjs-woocommerce,0132abef,9534,89,classnames,9227
  nextjs-woocommerce,0132abef,9534,89,react,365425
  nextjs-woocommerce,0132abef,9534,89,apollo-client,96671
  nextjs-woocommerce,0132abef,9534,89,nprogress,517
  nextjs-woocommerce,0132abef,9534,89,Fraction.js,2930
  nextjs-woocommerce,0132abef,9534,89,react,365425
  nextjs-woocommerce,0132abef,9534,89,postcss-value-parser,2856
  nextjs-woocommerce,0132abef,9534,89,graphql-js,140773
  nextjs-woocommerce,0132abef,9534,89,babel,502973
  nextjs-woocommerce,0132abef,9534,89,babel,502973
  nextjs-woocommerce,0132abef,9534,89,babel,502973
  nextjs-woocommerce,0132abef,9534,89,babel,502973
  nextjs-woocommerce,0132abef,9534,89,babel,502973
  nextjs-woocommerce,0132abef,9534,89,babel,502973
  nextjs-woocommerce,0132abef,9534,89,babel,502973
  nextjs-woocommerce,0132abef,9534,89,babel,502973
  nextjs-woocommerce,0132abef,9534,89,babel,502973
  nextjs-woocommerce,0132abef,9534,89,babel,502973
  nextjs-woocommerce,0132abef,9534,89,babel,502973
  nextjs-woocommerce,0132abef,9534,89,babel,502973
  nextjs-woocommerce,0132abef,9534,89,babel,502973
  nextjs-woocommerce,0132abef,9534,89,babel,502973
  nextjs-woocommerce,0132abef,9534,89,babel,502973
  nextjs-woocommerce,0132abef,9534,89,babel,502973
  nextjs-woocommerce,0132abef,9534,89,algoliasearch-client-js,13746
  nextjs-woocommerce,0132abef,9534,89,algoliasearch-client-javascript,13746
  nextjs-woocommerce,0132abef,9534,89,algoliasearch-client-javascript,13746
  nextjs-woocommerce,0132abef,9534,89,algoliasearch-client-javascript,13746
  nextjs-woocommerce,0132abef,9534,89,algoliasearch-client-javascript,13746
  nextjs-woocommerce,0132abef,9534,89,algoliasearch-client-js,13746
  nextjs-woocommerce,0132abef,9534,89,algoliasearch-client-javascript,13746
  nextjs-woocommerce,0132abef,9534,89,algoliasearch-client-javascript,13746
  nextjs-woocommerce,0132abef,9534,89,algoliasearch-client-javascript,13746
  nextjs-woocommerce,0132abef,9534,89,algoliasearch-client-javascript,13746
  nextjs-woocommerce,0132abef,9534,89,algoliasearch-client-javascript,13746
  nextjs-woocommerce,0132abef,9534,89,algoliasearch-client-javascript,13746
  nextjs-woocommerce,0132abef,9534,89,algoliasearch-client-javascript,13746
  nextjs-woocommerce,0132abef,9534,89,algoliasearch-client-js,13746
  nextjs-woocommerce,0132abef,9534,89,events,951
  nextjs-woocommerce,0132abef,9534,89,react-instantsearch,67768
  nextjs-woocommerce,0132abef,9534,89,react,365425
  nextjs-woocommerce,0132abef,9534,89,source-map,7680
  nextjs-woocommerce,0132abef,9534,89,next.js,337206
  nextjs-woocommerce,0132abef,9534,89,hoist-non-react-statics,432
  
  ```

  

  

+ Even with an effective URL, we can get all LOC for each of them:

  1. can not be git cloned

  2. `[BABEL] Note: The code generator has deoptimised the styling of /Users/yuxinliu/Documents/Develop/JS-Dep/auspice/node_modules/react-icons/fa/index.esm.js as it exceeds the max of 500KB.`

  3. No JS, JSON, or TS in that dependency, in this case, we get a "None", for example:
     ```
     Cloning into 'regenerator-runtime'...
     remote: Please upgrade your git client.
     remote: GitHub.com no longer supports git over dumb-http: https://github.com/blog/809-git-dumb-http-transport-to-be-turned-off-in-90-days
     fatal: unable to access 'https://github.com/facebook/regenerator/tree/master/packages/regenerator-runtime.git/': The requested URL returned error: 403
     ```

#### Refine the function to get the clone URL from a package.json

**I am still struggling with the refine of the method:**

```python
def getGitUrlFromPkg(pkgPath):
    if not os.path.exists(pkgPath):
        return False
    with open(pkgPath) as depPkg:
        depPkgJson = json.load(depPkg)
        if 'repository' in depPkgJson:
            if isinstance(depPkgJson['repository'], str):
                origStr = depPkgJson['repository']
                if origStr.find('https://') and origStr.find('.git'):
                    gitCloneUrl = origStr
                elif depPkgJson['repository'].find('git://'):
                    gitCloneUrl = origStr.replace('git://', 'https://')
                    if not '.git' in gitCloneUrl:
                        gitCloneUrl += '.git'
                elif origStr.find('github:'):
                    gitCloneUrl = origStr.replace(
                        'github:', 'https://github.com/') + '.git'
                else:
                    gitCloneUrl = 'https://github.com/' + \
                        depPkgJson['repository'] + '.git'
            elif isinstance(depPkgJson['repository'], dict):
                depUrl = depPkgJson['repository']['url']
                gitCloneUrl = 'https:' + depUrl[depUrl.find('//'):]
                if not '.git' in gitCloneUrl:
                    gitCloneUrl += '.git'

        elif 'homepage' in depPkgJson:
            gitCloneUrl = depPkgJson['homepage'] + '.git'

        else:
            return False
        return gitCloneUrl

```



1. clone URL in 'repository' dict in a very standard way, with an URL that does not need to be modified:

   ```
   "repository": {
       "type": "git",
       "url": "https://github.com/d3/d3-selection.git"
    },
   ```

   

2. clone URL in 'repository' dict in a not that standard way, with an URL needs to be refined:

   ```
   "repository": {
   	"type": "git",
   	"url": "git://github.com/fb55/htmlparser2.git"
   }
   ```

   ```
   "repository": {
       "type": "git",
       "url": "git@github.com:runtimejs/runtime.git"
   }
   ```

   

3. clone URL in 'repository' string:

   1. `"repository": "https://github.com/Borewit/readable-web-to-node-stream.git"`

   2. `"repository": "git://github.com/isaacs/inherits"`

      fatal: remote error:  The unauthenticated git protocol on port 9418 is no longer supported.

   3. `"repository": "isaacs/inherits"`

   4. `"repository": "github:dash-ui/unitless"`

   5. `"repository": "https://github.com/thysultan/stylis.js"` Shall we fix such a sample manually?

4. clone URL in 'homepage' string:

```
{'babel': '502973', 'graphql-tag': '8855', 'algoliasearch-helper-js': '23823', '': 'None', 'camelize': '139', 'css-to-react-native': '1907', 'react-hook-form': '42605', 'tslib': '826', 'Fraction.js': '2930', 'graphql-js': '140773', 'runtime': 'None', 'styled-components': '12949', 'events': '951', 'jsesc': '1276', 'zen-observable': '6108', 'react-spring': '16026', 'optimism': '4398', 'algoliasearch-client-javascript': '13746', 'picomatch': '7998', 'https:t': 'None', 'wryware': '16713', 'invariant-packages': '17952', 'DefinitelyTyped': '2818910', 'react-fast-compare': '726', 'classnames': '9227', 'postcss-value-parser': '2856', 'loose-envify': '12513', 'apollo-client': '96671', 'uuid': '31375', 'next.js': '337206', 'source-map': '7680', 'source-map-js': '5658', 'nextjs.org': 'None', 'hoist-non-react-statics': '432', 'tooling#babel-plugin': 'None', 'https:s': 'None', 'zen-observable-ts': '6442', 'algoliasearch-client-js': '13746', 'nprogress': '517', 'debug': '707', 'react': '365425', 'regenerator-runtime': 'None', 'react-instantsearch': '68442'}
```

