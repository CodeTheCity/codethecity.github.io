#!/usr/bin/env python3

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mpl_dates
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import io
from flask import Flask, render_template, send_file, make_response, request
import datetime
from datetime import date, datetime, timedelta
import database_driver
import pandas as pd
import configparser, os
import numpy as np
from calendar import monthrange

app = Flask(__name__)
dbname = 'harbour.db'
db = database_driver.database(dbname)

def dir_last_updated(folder):
	return str(max(os.path.getmtime(os.path.join(root_path, f))
		for root_path, dirs, files in os.walk(folder)
		for f in files))

def getLastImport():
	rows = db.select('SELECT strftime("%H:%M %d-%m-%Y", timestamp) as formated_date, entries FROM imports ORDER BY timestamp DESC LIMIT 1')
	return rows[0][0], rows[0][1]

def getRecordCount():
	rows = db.select('SELECT COUNT(date) FROM arrivals')
	return rows[0][0]

def getCheckedRecordCount():
	rows = db.select('SELECT COUNT(date) FROM arrivals WHERE checker != ""')
	return rows[0][0]

def getDataForColumn(column):
	rows = db.select('SELECT DISTINCT {} FROM arrivals WHERE {} <> "" ORDER BY {}'.format(column, column, column))
	data = []
	for row in rows:
		data.append(row[0])

	return data

def getEntriesForColumnLike(column, value):
	rows = db.select('SELECT strftime("%d-%m-%Y", date) as formated_date, vessel, number, registered_port, master, registered_tonnage, from_port, cargo, activity, checker FROM arrivals WHERE {} LIKE :value ORDER BY date'.format(column), {"value":'%'+value+'%'})

	return rows


def getVesselsData():
	return getDataForColumn('vessel')

def getMastersData():
	return getDataForColumn('master')

def getCargoData():
	return getDataForColumn('cargo')

def getActivityData():
	return getDataForColumn('activity')

def getRegisteredPortsData():
	return getDataForColumn('registered_port')

def getFromPortsData():
	return getDataForColumn('from_port')

def getWeatherData():
	rows = db.select('SELECT strftime("%d-%m-%Y", date) as formated_date, weather FROM arrivals WHERE weather != "?" AND weather != "" ORDER BY date')

	return rows

def getNotesData():
	rows = db.select('SELECT strftime("%d-%m-%Y", date) as formated_date, notes FROM arrivals WHERE notes != "?" AND notes != "" ORDER BY date')

	return rows

def getTranscribersData():
	return getDataForColumn('transcriber')

def getCheckersData():
	return getDataForColumn('checker')

def getEntriesForVessel(vessel):
	return getEntriesForColumnLike('vessel', vessel)

def getEntriesForMaster(master):
	return getEntriesForColumnLike('master', master)

def getEntriesForCargo(cargo):
	return getEntriesForColumnLike('cargo', cargo)

def getEntriesForActivity(activity):
	return getEntriesForColumnLike('activity', activity)

def getEntriesForRegisteredPort(registered_port):
	return getEntriesForColumnLike('registered_port', registered_port)

def getEntriesForFromPort(from_port):
	return getEntriesForColumnLike('from_port', from_port)

def getWeatherDataForDate(date):
	rows = db.select('SELECT strftime("%d-%m-%Y", date) as formated_date, weather FROM arrivals WHERE weather != "?" AND weather != "" AND strftime("%d-%m-%Y", date) like :date ORDER BY date', { "date": '%{}%'.format(date)})

	return rows

def getNotesDataForDate(date):
	rows = db.select('SELECT strftime("%d-%m-%Y", date) as formated_date, notes FROM arrivals WHERE notes != "?" AND notes != "" AND strftime("%d-%m-%Y", date) like :date ORDER BY date', { "date": '%{}%'.format(date)})

	return rows

# Checks for partial match of date - e.g. search for 1914 gets all in 1914
# search for 5-4 gets all for 5th April any year
def getEntriesForDate(date):
	rows = db.select('SELECT strftime("%d-%m-%Y", date) as formated_date, vessel, number, registered_port, master, registered_tonnage, from_port, cargo, activity, checker FROM arrivals WHERE strftime("%d-%m-%Y", date) like :date ORDER BY date', { "date": '%{}%'.format(date)})

	return rows

def getEntriesForYear(year):
	rows = db.select('SELECT strftime("%d-%m-%Y", date) as formated_date, vessel, number, registered_port, master, registered_tonnage, from_port, cargo, activity, checker FROM arrivals WHERE strftime("%Y", date) = :year ORDER BY date', { "year":year})

	return rows

def getEntriesAfterYear(year):
	rows = db.select('SELECT strftime("%d-%m-%Y", date) as formated_date, vessel, number, registered_port, master, registered_tonnage, from_port, cargo, activity, checker FROM arrivals WHERE strftime("%Y", date) > :year ORDER BY date', { "year":year})

	return rows

def getEntriesWithTranscriberNotes():
	rows = db.select('SELECT strftime("%d-%m-%Y", date) as formated_date, vessel, number, registered_port, master, registered_tonnage, from_port, cargo, activity, checker, transcriber_notes FROM arrivals WHERE transcriber_notes <> "" ORDER BY date')

	return rows

@app.route('/')
# main route
def index():

	records_count = 0
	checked_records_count = 0
	cargo = []
	vessels = []
	registered_ports = []
	from_ports = []
	last_import, records_count = getLastImport()
	checked_records_count = getCheckedRecordCount()

	this_day = date.today().strftime("%d-%m")

	on_this_day = getEntriesForDate(this_day)

	on_this_day_weather = getWeatherDataForDate(this_day)


	weather = []

	try:
		cargo = getCargoData()
	except Exception as e:
		print(e)

	try:
		vessels = getVesselsData()
	except Exception as e:
		print(e)

	try:
		masters = getMastersData()
	except Exception as e:
		print(e)

	try:
		registered_ports = getRegisteredPortsData()
	except Exception as e:
		print(e)

	try:
		from_ports = getFromPortsData()
	except Exception as e:
		print(e)

	templateData = {
		'records_count' : records_count,
		'last_import' : datetime.strptime(last_import, '%H:%M %d-%m-%Y').strftime('%d %B %Y %H:%M'),
		'checked_records_count' : checked_records_count,
		'cargo' : cargo,
		'vessels' : vessels,
		'masters' : masters,
		'registered_ports' : registered_ports,
		'from_ports' : from_ports,
		'on_this_day' : on_this_day,
		'on_this_day_weather' : on_this_day_weather,
		'last_updated' : dir_last_updated('static')
	}
	return render_template('index.html', **templateData)

@app.route('/information')
def information():

	registered_port_mappings = []

	with open('mappings/registered_ports_mappings.txt', 'r') as file:
		line = file.readline()

		while line:
			line = line.rstrip('\n').replace(':', ' : ').replace(',', ', ')
			registered_port_mappings.append(line)

			line = file.readline()

	cargo_mappings = []

	with open('mappings/cargo_mappings.txt', 'r') as file:
		line = file.readline()

		while line:
			line = line.rstrip('\n').replace(':', ' : ').replace(',', ', ')
			cargo_mappings.append(line)

			line = file.readline()

	templateData = {
		'registered_port_mappings' : registered_port_mappings,
		'cargo_mappings' : cargo_mappings
	}
	return render_template('information.html', **templateData)

@app.route('/thanks')
def thanks():
	transcribers = []

	try:
		transcribers = getTranscribersData()
	except Exception as e:
		print(e)

	checkers = []

	try:
		checkers = getCheckersData()
	except Exception as e:
		print(e)


	templateData = {
		'transcribers' : transcribers,
		'checkers' : checkers
	}
	return render_template('thanks.html', **templateData)

@app.route('/vessels')
def vessels():
	vessels = []

	try:
		vessels = getVesselsData()
	except Exception as e:
		print(e)


	templateData = {
		'vessels' : vessels
	}
	return render_template('vessels.html', **templateData)

@app.route('/masters')
def masters():
	masters = []

	try:
		masters = getMastersData()
	except Exception as e:
		print(e)


	templateData = {
		'masters' : masters
	}
	return render_template('masters.html', **templateData)

@app.route('/cargos')
def cargos():
	cargos = []

	try:
		cargos = getCargoData()
	except Exception as e:
		print(e)


	templateData = {
		'cargos' : cargos
	}
	return render_template('cargos.html', **templateData)

@app.route('/activities')
def activities():
	activities = []

	try:
		activities = getActivityData()
	except Exception as e:
		print(e)


	templateData = {
		'activities' : activities
	}
	return render_template('activities.html', **templateData)

@app.route('/registered_ports')
def registered_ports():
	registered_ports = []

	try:
		registered_ports = getRegisteredPortsData()
	except Exception as e:
		print(e)


	templateData = {
		'registered_ports' : registered_ports
	}
	return render_template('registered_ports.html', **templateData)

@app.route('/from_ports')
def from_ports():
	from_ports = []

	try:
		from_ports = getFromPortsData()
	except Exception as e:
		print(e)


	templateData = {
		'from_ports' : from_ports
	}
	return render_template('from_ports.html', **templateData)

@app.route('/weather')
def weather():

	weather = []
	weather = getWeatherData()

	templateData = {
		'weather' : weather
	}
	return render_template('weather.html', **templateData)

@app.route('/notes')
def notes():

	notes = []
	notes = getNotesData()

	templateData = {
		'notes' : notes
	}
	return render_template('notes.html', **templateData)

@app.route('/transcriber_notes')
def transcriber_notes():

	entries = []
	entries = getEntriesWithTranscriberNotes()

	templateData = {
		'entries' : entries
	}
	return render_template('transcriber_notes.html', **templateData)

@app.route('/day/<year>/<month>/<day>')
def day(year, month, day):

	entries = []
	entries = getEntriesForYear(year)

	date_string = '{:0>2}-{:0>2}-{}'.format(day, month, year)
	date = datetime.strptime(date_string, '%d-%m-%Y').date()

	on_this_day = getEntriesForDate(date_string)
	on_this_day_weather = getWeatherDataForDate(date_string)
	on_this_day_note = getNotesDataForDate(date_string)

	templateData = {
		'entries' : on_this_day,
		'date' : date.strftime('%d %B %Y'),
		'tomorrow' : (date + timedelta(days=1)).strftime('%Y/%m/%d'),
		'yesterday' : (date + timedelta(days=-1)).strftime('%Y/%m/%d'),
		'current_day' : day,
		'current_month' : month,
		'current_year' : year,
		'days_in_month' : monthrange(int(year), int(month))[1],
		'on_this_day_weather' : on_this_day_weather,
		'on_this_day_note' : on_this_day_note,
		'on_this_day' : on_this_day,
		'last_updated' : dir_last_updated('static')
	}
	return render_template('day.html', **templateData)


@app.route('/arrivals/<year>')
def arrivals(year):

	entries = []
	entries = getEntriesForYear(year)

	sources = { '1914' : 'https://docs.google.com/spreadsheets/d/1gr-501asOIg-YLTWkkeX3iWwVR1ROnHfX4swNKinRUk/edit#gid=1432177458', '1915' : 'https://docs.google.com/spreadsheets/d/1gr-501asOIg-YLTWkkeX3iWwVR1ROnHfX4swNKinRUk/edit#gid=524481503', '1916' : 'https://docs.google.com/spreadsheets/d/1gr-501asOIg-YLTWkkeX3iWwVR1ROnHfX4swNKinRUk/edit#gid=247148901', '1917' : 'https://docs.google.com/spreadsheets/d/1gr-501asOIg-YLTWkkeX3iWwVR1ROnHfX4swNKinRUk/edit#gid=1725245449', '1918' : 'https://docs.google.com/spreadsheets/d/1gr-501asOIg-YLTWkkeX3iWwVR1ROnHfX4swNKinRUk/edit#gid=1155924912', '1919' : 'https://docs.google.com/spreadsheets/d/1gr-501asOIg-YLTWkkeX3iWwVR1ROnHfX4swNKinRUk/edit#gid=1705602406', '1920' : 'https://docs.google.com/spreadsheets/d/1gr-501asOIg-YLTWkkeX3iWwVR1ROnHfX4swNKinRUk/edit#gid=583956228' }

	source = None
	if year in sources:
		source = sources[year]

	templateData = {
		'entries' : entries,
		'year' : year,
		'source' : source
	}
	return render_template('entries.html', **templateData)

@app.route('/arrivals_after/<year>')
def arrivals_after(year):

	entries = []
	entries = getEntriesAfterYear(year)

	templateData = {
		'entries' : entries,
		'year' : 'after {}'.format(year)
	}
	return render_template('entries.html', **templateData)

@app.route('/vessel/<filter>')
def vessel(filter):

	entries = getEntriesForVessel(filter)

	templateData = {
		'entries' : entries,
		'vessel' : filter
	}
	return render_template('vessel.html', **templateData)
	
@app.route('/master/<filter>')
def master(filter):

	entries = getEntriesForMaster(filter)

	templateData = {
		'entries' : entries,
		'master' : filter
	}
	return render_template('master.html', **templateData)
	
@app.route('/cargo/<filter>')
def cargo(filter):

	entries = getEntriesForCargo(filter)

	templateData = {
		'entries' : entries,
		'cargo' : filter
	}
	return render_template('cargo.html', **templateData)
	
@app.route('/activity/<filter>')
def activity(filter):

	entries = getEntriesForActivity(filter)

	templateData = {
		'entries' : entries,
		'activity' : filter
	}
	return render_template('activity.html', **templateData)

@app.route('/registered_port/<filter>')
def registered_port(filter):

	entries = getEntriesForRegisteredPort(filter)

	templateData = {
		'entries' : entries,
		'registered_port' : filter
	}
	return render_template('registered_port.html', **templateData)

@app.route('/from_port/<filter>')
def from_port(filter):

	entries = getEntriesForFromPort(filter)

	templateData = {
		'entries' : entries,
		'from_port' : filter
	}
	return render_template('from_port.html', **templateData)
	
	

@app.route('/graphs_cargo')
def graphs_cargo():
	return render_template('graphs_cargo.html')

@app.route('/graphs_activity')
def graphs_activity():
	return render_template('graphs_activity.html')

@app.route('/graphs_top_vessels')
def graphs_top_vessels():
	return render_template('graphs_top_vessels.html')

@app.route('/graphs_registered_ports')
def graphs_registered_ports():
	return render_template('graphs_registered_ports.html')

@app.route('/graphs_from_ports')
def graphs_from_ports():
	return render_template('graphs_from_ports.html')

def buildCargoGraph(year):
	con = db.create_connection()
	df = pd.read_sql_query('SELECT date, cargo FROM arrivals WHERE strftime(\'%Y\', date) = "{}" AND cargo <> "" ORDER BY date'.format(year), con, parse_dates=['date'], index_col=['date'])
	con.close()

	fig = Figure(figsize=(12,12))
	axis = fig.subplots(1)

	if df.empty == False:
		df_cargos = df.groupby('date').cargo.value_counts().unstack().fillna(0)

		resampled = df_cargos.resample('W').sum()

		columns = resampled.columns
		labels = columns.values.tolist()

		colour_map = cm.get_cmap('tab20', len(columns) + 1)

		x = resampled.index
		bottom = np.zeros(resampled.shape[0])
		for i, column in enumerate(columns, start=0):
			axis.bar(x, resampled[column].values.tolist(), bottom=bottom, label=column, color=colour_map.colors[i])
			bottom += resampled[column].values.tolist()

	date_format = mpl_dates.DateFormatter('%d %b %Y')
	axis.xaxis_date()
	axis.xaxis.set_major_formatter(date_format)
	axis.set_title('Weekly cargo arrival at Aberdeen {}'.format(year))
	fig.legend(loc='center right', fancybox=True, shadow=True, fontsize=10, ncol=2)

	fig.autofmt_xdate()
	fig.tight_layout()
	fig.subplots_adjust(right=0.75)

	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response

def buildActivityGraph(year):
	con = db.create_connection()
	df = pd.read_sql_query('SELECT date, activity FROM arrivals WHERE strftime(\'%Y\', date) = "{}" AND activity <> "" ORDER BY date'.format(year), con, parse_dates=['date'], index_col=['date'])
	con.close()

	fig = Figure(figsize=(12,12))
	axis = fig.subplots(1)

	if df.empty == False:
		df_activity = df.groupby('date').activity.value_counts().unstack().fillna(0)

		resampled = df_activity.resample('W').sum()

		columns = resampled.columns
		labels = columns.values.tolist()

		colour_map = cm.get_cmap('tab20', len(columns) + 1)

		x = resampled.index
		bottom = np.zeros(resampled.shape[0])
		for i, column in enumerate(columns, start=0):
			axis.bar(x, resampled[column].values.tolist(), bottom=bottom, label=column, color=colour_map.colors[i])
			bottom += resampled[column].values.tolist()

	date_format = mpl_dates.DateFormatter('%d %b %Y')
	axis.xaxis_date()
	axis.xaxis.set_major_formatter(date_format)
	axis.set_title('Weekly arrival activity at Aberdeen {}'.format(year))
	fig.legend(loc='center right', fancybox=True, shadow=True, fontsize=10, ncol=2)

	fig.autofmt_xdate()
	fig.tight_layout()
	fig.subplots_adjust(right=0.75)

	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response


def buildTopVesselsGraph(year):
	con = db.create_connection()
	df = pd.read_sql_query('SELECT date, vessel FROM arrivals WHERE strftime(\'%Y\', date) = "{}" AND vessel <> "" ORDER BY date'.format(year), con, parse_dates=['date'], index_col=['date'])
	con.close()

	fig = Figure(figsize=(8,12))
	axis = fig.subplots(1)

	top = df['vessel'].value_counts()
	top = top[top > 4]

	colour_map = cm.get_cmap('tab20', len(top) + 1)

	axis.barh(top.index, top.values, color=colour_map.colors)
	axis.set_title('Vessels arriving more than 5 times at Aberdeen during {}'.format(year))

	fig.tight_layout()

	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response

def buildRegisteredPortsGraph(year):
	con = db.create_connection()
	df = pd.read_sql_query('SELECT DISTINCT vessel, registered_port FROM arrivals WHERE strftime(\'%Y\', date) = "{}" AND registered_port <> "" ORDER BY registered_port'.format(year), con)
	con.close()

	fig = Figure(figsize=(8,12))
	axis = fig.subplots(1)

	top = df['registered_port'].value_counts()
	#top = top[top > 4]

	colour_map = cm.get_cmap('tab20', len(top) + 1)

	axis.barh(top.index, top.values, color=colour_map.colors)

	for i, v in enumerate(top):
		axis.text(v, i, " "+str(v), va='center')

	axis.set_title('Registered Port of Vessels arriving at Aberdeen during {}'.format(year))
	axis.spines['right'].set_color('none')
	axis.spines['top'].set_color('none')
	fig.tight_layout()

	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response

def buildFromPortsGraph(year):
	con = db.create_connection()
	df = pd.read_sql_query('SELECT DISTINCT vessel, from_port FROM arrivals WHERE strftime(\'%Y\', date) = "{}" AND from_port <> "" ORDER BY from_port'.format(year), con)
	con.close()

	fig = Figure(figsize=(8,12))
	axis = fig.subplots(1)

	top = df['from_port'].value_counts()
	top = top[:75]

	colour_map = cm.get_cmap('tab20', len(top) + 1)

	axis.barh(top.index, top.values, color=colour_map.colors)

	for i, v in enumerate(top):
		axis.text(v, i, " "+str(v), va='center')

	axis.set_title('Top 75 Ports of Origin for Vessels arriving at Aberdeen during {}'.format(year))
	axis.spines['right'].set_color('none')
	axis.spines['top'].set_color('none')
	fig.tight_layout()

	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response

@app.route('/plot/cargo/<year>')
def plot_cargo(year):
	return buildCargoGraph(year)

@app.route('/plot/activity/<year>')
def plot_activity(year):
	return buildActivityGraph(year)

@app.route('/plot/top_vessels/<year>')
def plot_top_vessels(year):
	return buildTopVesselsGraph(year)

@app.route('/plot/registered_ports/<year>')
def plot_registered_ports(year):
	return buildRegisteredPortsGraph(year)

@app.route('/plot/from_ports/<year>')
def plot_from_ports(year):
	return buildFromPortsGraph(year)

@app.route('/api/v1.0/arrivals.csv')
def csv_get_arrivals():
	con = db.create_connection()
	df = pd.read_sql_query('SELECT * FROM arrivals ORDER BY date', con, parse_dates=['date'], index_col=['date'])
	con.close()

	response = make_response(df.to_csv())
	response.headers["Content-Disposition"] = "attachment; filename=arrivals.csv"
	response.headers["Content-Type"] = "text/csv"
	return response

@app.route('/api/v1.0/arrivals')
def api_get_arrivals():
	con = db.create_connection()
	df = pd.read_sql_query('SELECT * FROM arrivals ORDER BY date', con, parse_dates=['date'], index_col=['date'])
	con.close()

	response = make_response(df.to_json(orient='table', index=False))
	#response.headers["Content-Disposition"] = "attachment; filename=arrivals.json"
	response.headers["Content-Type"] = "application/json"
	return response

@app.route('/api/v1.0/cargo')
def api_get_cargo():
	con = db.create_connection()
	df = pd.read_sql_query('SELECT DISTINCT cargo FROM arrivals ORDER BY cargo', con)
	con.close()

	response = make_response(df.to_json(orient='table', index=False))
	#response.headers["Content-Disposition"] = "attachment; filename=cargo.json"
	response.headers["Content-Type"] = "application/json"
	return response

@app.route('/api/v1.0/vessels.csv')
def csv_get_vessels():
	con = db.create_connection()
	df = pd.read_sql_query('SELECT DISTINCT vessel FROM arrivals ORDER BY vessel', con)
	con.close()

	response = make_response(df.to_csv())
	response.headers["Content-Disposition"] = "attachment; filename=vessels.csv"
	response.headers["Content-Type"] = "text/csv"
	return response

@app.route('/api/v1.0/weather')
def api_get_weather():
	con = db.create_connection()
	df = pd.read_sql_query('SELECT date, weather FROM arrivals ORDER BY date', con)
	con.close()

	response = make_response(df.to_json(orient='table', index=False))
	#response.headers["Content-Disposition"] = "attachment; filename=cargo.json"
	response.headers["Content-Type"] = "application/json"
	return response

if __name__ == '__main__':
	config = configparser.ConfigParser()

	if not os.path.exists('config.ini'):
		config['server'] = {'port': '80'}
		config.write(open('config.ini', 'w'))

	config.read('config.ini')
	debug = False
	try:
		if config.getboolean('server', 'debug'):
			debug = True
	except Exception as e:
		print(e)

	app.run(debug=debug, port=config['server']['port'], host='0.0.0.0')