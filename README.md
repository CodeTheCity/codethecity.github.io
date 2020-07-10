# Aberdeen Harbour Historical Arrivals Data API and Dashboard
This is a self contained web server that provides an API and dashboard for historical arrivals at Aberdeen harbour during the period 1914 - 1920. The data has been transcribed from the log books record at the time. The transcription was done as part of [CodeTheCity 19](https://codethecity.org/what-we-do/hack-weekends/code-the-city-19-history-data-innovation).

A demonstration of the site can be seen at [http://161.35.162.175](http://161.35.162.175).

# Features

The dashboard currently contains an indication of number of records transcribed and the last time the data was imported from the transcription spreadsheet.

There are separate pages for the following:

* List of entries for each year
* List of unique vessel entries
* List of unique register port entries
* List of unique master entries
* List of unique ports of origin entries
* List of unique cargo entries
* List of weather events ordered by date
* Graphs showing the number of each cargo type per day. There is a graph for each year.

There is also an API for downloading all the data as CSV or JSON. Also for downloading JSON of the following:

* List of unique cargo entries
* All weather entries
* All note entries

# Installation

The dashboard is written in Python3 and uses Flask as a webserver.

The prototype version of this is running on a Raspberry Pi running Buster and the installation instructions are for that platform.

## Raspberry Pi

The following are required to be installed for the various components of the system.

First run

```
sudo apt-get update
```

| Component | Purpose | Installation commands |
| --- | --- | --- |
| Git | git client to download code | `sudo apt install git` |
| PIP | python installer | `sudo apt install python3-pip` |
| SQLite | database| `sudo apt-get install sqlite3`|
| Flask | webserver| `sudo apt-get install python3-flask`|
| Pandas | data wrangling|`sudo pip3 install pandas`|
| Matplot | graphing|`sudo pip3 install matplotlib`|
| Seaborn | graph styling| `sudo apt-get install libatlas3-base`<br>`sudo pip3 install seaborn`|
| xlrd | Excel support | `sudo pip3 install xlrd` |

# Use

## Database

The records are imported from a Google Spreadsheet, cleaned and then stored in a SQLite database. The following rebuilds and populates the database:

```
./create_database.py
```

If you want to have the database automatically rebuild with the latest data from the source spreadsheets then setup a Cron job.

```
crontab -e
```

Add

```
*/<interval> * * * * cd <path> && ./create_database.py > /home/pi/logs/cronlog 2>&1
```

where <path> is the path to the directory that you have the code installed and <interval> is the minute frequency that you want the rebuild to occur at.

The output is sent to a log file in a directory named `logs` that you will need to create first.

A sample completed entry that runs every 5 minutes for the code in `/home/pi/Projects/historical_harbour_arrivals_api` would be:

```
*/5 * * * * cd /home/pi/Projects/historical_harbour_arrivals_api && ./create_database.py > /home/pi/logs/cronlog 2>&1
```



## Webserver

To start the webserver running use the following:

```
sudo ./webserver.py
```

By default it uses port 80, however the port used can be set by editing the `config.ini` file.

To keep the webserver running whilst logged out from the Raspberry Pi do the following:

```
sudo nohup ./webserver.py &
```

To stop it running in the background:

```
ps ax | grep aqsensor.py
kill PID
```

### Automatically start on reboot

To automatically start the webserver on reboot:

```
crontab -e
```

Add the following to the end of the file:

```
@reboot cd /home/pi/Projects/historical_harbour_arrivals_api && sudo /home/pi/Projects/historical_harbour_arrivals_api/webserver.py & > /home/pi/logs/cronlog 2>&1
```

## Setting up a development machine

If you want to get things up and running on your local machine, please follow these instructions to get set up.

### [Optional] Setting up a virtual environment

If you'd like to keep the libs installed for this project separate from your main install, you can set up [virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment).

### Python dependencies

You'll need to install the following dependencies:

```
# for running ./create_database.py

pip install numpy pandas xlrd
```

```
# for running the webserver

pip install flask matplotlib
```

### Build the database

```
./create_database.py
```

### Run the webserver

```
./webserver.py
```

### Contributing

If you'd like to contribute to the project, that's great. There's a guide to contributing to, both code and general help, over in [CONTRIBUTING](https://github.com/CodeTheCity/historical_harbour_arrivals_api/blob/master/CONTRIBUTING.md)

# Discussing the Project

## Slack

Feel free to come and join discussions on our Slack channels. [Join CTC on Slack](https://join.slack.com/t/codethecity/shared_invite/zt-d4a8eohu-pbc_J4rn~caNlPGGuq28Zw)
## Twitter

Feel free to contact the CodeTheCity core team via Twitter [@CodeTheCity](https://twitter.com/codethecity)

