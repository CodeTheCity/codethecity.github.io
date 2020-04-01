# Aberdeen Harbour Historical Arrivals Data API and Dashboard
This is a self contained web server that provides an API and dashboard for historical arrivals at Aberdeen harbour during the period 1914 - 1920. The data has been transcribed from the log books record at the time. The transcription was done as part of [CodeTheCity 19](https://codethecity.org/what-we-do/hack-weekends/code-the-city-19-history-data-innovation).

# Features

The dashboard currently contains a list of unqiue values for the following fields:

* Cargo
* Vessel
* Master
* Registered Port
* From Port

There are separate pages for the following:

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
| Seaborn | graph styling|`sudo apt-get install libatlas3-base`<br>`sudo pip3 install seaborn`|

# Use

## Database

The records are imported from a Google Spreadsheet, cleaned and then stored in a SQLite database. The following rebuilds and populates the database:

```
./create_database.py
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
