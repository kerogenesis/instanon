<p align="center">
  <img src="https://res.cloudinary.com/wark/image/upload/v1576917345/instanon.png" width="638px">
  <h2 align="center" style="margin-top: -4px !important;">Download Instagram stories or highlights anonymously</h2>
  <p align="center">
    <a href="https://github.com/dt-wark/instanon/blob/master/LICENSE">
      <img src="https://img.shields.io/badge/license-MIT-green.svg">
    </a>
    <a href="https://www.python.org/">
    	<img src="https://img.shields.io/badge/python-v3.8-blue.svg">
    </a>
    <a href="#">
      <img src="https://img.shields.io/badge/status-stable-brightgreen.svg">
    </a>
    <a href="https://github.com/SeleniumHQ/selenium">
      <img src="https://img.shields.io/badge/built%20with-Selenium-yellow.svg">
    </a>
  <a href="https://github.com/dt-wark/instanon/pulls?utf8=%E2%9C%93&amp;q=is%3Apr%20author%3Aapp%2Fdependabot"><img src="https://camo.githubusercontent.com/6266857d1c53194119edf1d9aafae7a4b301fa16/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f646570656e64656e636965732d7570253230746f253230646174652d627269676874677265656e2e737667" alt="Dependencies Status" data-canonical-src="https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg" style="max-width:100%;"></a>
    <a href="https://res.cloudinary.com/wark/image/upload/v1576597812/bit.png">
      <img src="https://img.shields.io/badge/btc-1AnYqP7mt7QxqYc6fmQk5m6YHN8Rqan4ze-informational.svg">
    </a>
  </p>
</p>


## Setup

1. Install Python 3.8
2. Clone this repo
```
git clone https://github.com/dt-wark/instanon.git
```

3. Create and activate virtual environment
```
python3.8 -m venv venv
source venv/bin/activate
```

4. Install dependencies
```
pip3 install -r requirements.txt
```

## Usage

```
Options:
  -u, --users        Instagram username(s)
  -s, --stories      Download stories
  -h, --highlights   Download highlights
  -o, --output       Directory for data storage
  -c, --chaos        Save stories in one directory
```

### Example:

#### Download stories and save them to /mnt/e/instagram directory
```
python3.8 instanon.py -u katie_westwood -u sharishanya --stories --chaos --output "/mnt/e/instagram"
```

#### Download highlights and save them to /mnt/e/instagram directory
```
python3.8 instanon.py -u katie_westwood --highlights --output "/mnt/e/instagram"
```

#### Download stories and save them to instanon script directory with script_run_days directories 
```
python3.8 instanon.py -u katie_westwood --stories
```


## Tasks Automation

### Linux/osx 

#### cron

```
# run the script every day at 1 p.m.
0 13 * * * root source /path/to/virtualenv/bin/activate && python3.8 /path/to/instanon/instanon.py -u USER --stories
```

### Windows

#### Windows Task Scheduler

- Press Win+R → type taskschd.msc

- In the Task Scheduler window, go to the Task Scheduler Library row, go to the Actions column on the right. There, click "Create Task" link, to open the wizard bearing the same name.

- Enter a name and a description for your new task. Example:
<img src="https://res.cloudinary.com/wark/image/upload/v1576572206/task-name.png" style="margin-top: 12px !important;">

- Also select "Run whether user is logged on or not", choose HIDDEN option and сhoose the configuration for Windows 10.

- In the Triggers tab, click New... and set the script runtime.

- In the Actions tab, enter your Python path, script options and script folder path. Example:
<img src="https://res.cloudinary.com/wark/image/upload/v1577606322/actions.png" style="margin-top: 12px !important;">
