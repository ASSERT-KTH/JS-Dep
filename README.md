# JS-Dep

## Fetch stars for a repo

There are two ways to fetch data through [REST API](https://docs.github.com/en/rest): Shell and JavaScript, we choose Shell.

In order to use a shell script to get the data and manipulate .json files, we need to take the following step to install useful tools.

### 1. Homebrew install on Mac

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. ql install on Mac

```
brew install jq
```

### 3. Fetch the amount of stars for a repo

Suppose we want to get this repo:

Username: jasonrudolph

Reponame: keyboard

```
curl --silent 'https://api.github.com/repos/jasonrudolph/keyboard' -H 'Accept: application/vnd.github.preview' | jq '.watchers_count'
```



