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
	try:
		rows = db.select('SELECT DISTINCT {} FROM arrivals WHERE {} <> "" ORDER BY {}'.format(column, column, column))
		data = []
		for row in rows:
			data.append(row[0])

		return data
	except Exception as e:
		raise e

def getEntriesForColumnLike(column, value):
	rows = db.select('SELECT strftime("%d-%m-%Y", date) as formated_date, vessel, vessel_prefix, number, registered_port, master, registered_tonnage, from_port, cargo, activity, checker, fishing_port_registration_number FROM arrivals WHERE {} LIKE :value ORDER BY date'.format(column), {"value":'%'+value+'%'})

	return rows


def getVesselsData():
	try:
		return getDataForColumn('vessel')
	except Exception as e:
		raise e

def getMastersData():
	try:
		return getDataForColumn('master')
	except Exception as e:
		raise e

def getCargoData():
	try:
		return getDataForColumn('cargo')
	except Exception as e:
		raise e

def getActivityData():
	try:
		return getDataForColumn('activity')
	except Exception as e:
		raise e

def getRegisteredPortsData():
	try:
		return getDataForColumn('registered_port')
	except Exception as e:
		raise e

def getFromPortsData():
	try:
		return getDataForColumn('from_port')
	except Exception as e:
		raise e

def getFishingPortRegistrationNumbersData():
	try:
		return getDataForColumn('fishing_port_registration_number')
	except Exception as e:
		raise e

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

def getEntriesForFishingPortRegistrationNumber(fishing_port_registration_number):
	return getEntriesForColumnLike('fishing_port_registration_number', fishing_port_registration_number)

def getWeatherDataForDate(date):
	rows = db.select('SELECT strftime("%d-%m-%Y", date) as formated_date, weather FROM arrivals WHERE weather != "?" AND weather != "" AND strftime("%d-%m-%Y", date) like :date ORDER BY date', { "date": '%{}%'.format(date)})

	return rows

def getNotesDataForDate(date):
	rows = db.select('SELECT strftime("%d-%m-%Y", date) as formated_date, notes FROM arrivals WHERE notes != "?" AND notes != "" AND strftime("%d-%m-%Y", date) like :date ORDER BY date', { "date": '%{}%'.format(date)})

	return rows

# Checks for partial match of date - e.g. search for 1914 gets all in 1914
# search for 5-4 gets all for 5th April any year
def getEntriesForDate(date):
	rows = db.select('SELECT strftime("%d-%m-%Y", date) as formated_date, vessel, vessel_prefix, number, registered_port, master, registered_tonnage, from_port, cargo, activity, checker, fishing_port_registration_number FROM arrivals WHERE strftime("%d-%m-%Y", date) like :date ORDER BY date', { "date": '%{}%'.format(date)})

	return rows

def getEntriesForYear(year):
	rows = db.select('SELECT strftime("%d-%m-%Y", date) as formated_date, vessel, vessel_prefix, number, registered_port, master, registered_tonnage, from_port, cargo, activity, checker, fishing_port_registration_number FROM arrivals WHERE strftime("%Y", date) = :year ORDER BY date', { "year":year})

	return rows

def getEntriesAfterYear(year):
	rows = db.select('SELECT strftime("%d-%m-%Y", date) as formated_date, vessel, vessel_prefix, number, registered_port, master, registered_tonnage, from_port, cargo, activity, checker, fishing_port_registration_number FROM arrivals WHERE strftime("%Y", date) > :year ORDER BY date', { "year":year})

	return rows

def getEntriesWithTranscriberNotes():
	rows = db.select('SELECT strftime("%d-%m-%Y", date) as formated_date, vessel, vessel_prefix, number, registered_port, master, registered_tonnage, from_port, cargo, activity, checker, fishing_port_registration_number, transcriber_notes FROM arrivals WHERE transcriber_notes <> "" ORDER BY date')

	return rows

@app.route('/')
# main route
def index():

	errors = []
	records_count = 0
	checked_records_count = 0
	cargo = []
	vessels = []
	registered_ports = []
	from_ports = []
	last_import, records_count = getLastImport()
	checked_records_count = getCheckedRecordCount()

	on_this_day = []
	on_this_day_weather = []

	this_day = date.today().strftime("%d-%m")


	try:
		on_this_day = getEntriesForDate(this_day)
	except Exception as e:
		print(e)
		errors.append(e)

	try:
		on_this_day_weather = getWeatherDataForDate(this_day)
	except Exception as e:
		print(e)
		errors.append(e)

	weather = []

	try:
		cargo = getCargoData()
	except Exception as e:
		print(e)
		errors.append(e)

	try:
		vessels = getVesselsData()
	except Exception as e:
		print(e)
		errors.append(e)

	try:
		masters = getMastersData()
	except Exception as e:
		print(e)
		errors.append(e)

	try:
		registered_ports = getRegisteredPortsData()
	except Exception as e:
		print(e)
		errors.append(e)

	try:
		from_ports = getFromPortsData()
	except Exception as e:
		print(e)
		errors.append(e)

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
		'this_day' : this_day,
		'last_updated' : dir_last_updated('static'),
		'errors' : errors
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

	registered_port_mappings.sort()

	from_port_mappings = []

	with open('mappings/from_ports_mappings.txt', 'r') as file:
		line = file.readline()

		while line:
			line = line.rstrip('\n').replace(':', ' : ').replace(',', ', ')
			from_port_mappings.append(line)

			line = file.readline()

	from_port_mappings.sort()

	cargo_mappings = []

	with open('mappings/cargo_mappings.txt', 'r') as file:
		line = file.readline()

		while line:
			line = line.rstrip('\n').replace(':', ' : ').replace(',', ', ')
			cargo_mappings.append(line)

			line = file.readline()
	
	cargo_mappings.sort()

	templateData = {
		'registered_port_mappings' : registered_port_mappings,
		'cargo_mappings' : cargo_mappings,
		'from_port_mappings' : from_port_mappings
	}
	return render_template('information.html', **templateData)

@app.route('/downloads')
def downloads():
	return render_template('downloads.html')

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
	errors = []
	cargos = []

	try:
		cargos = getCargoData()
	except Exception as e:
		print(e)
		errors.append(e)


	templateData = {
		'cargos' : cargos,
		'errors' : errors
	}
	return render_template('cargos.html', **templateData)

@app.route('/activities')
def activities():
	errors = []
	activities = []

	try:
		activities = getActivityData()
	except Exception as e:
		print(e)
		errors.append(e)


	templateData = {
		'activities' : activities,
		'errors' : errors
	}
	return render_template('activities.html', **templateData)

@app.route('/registered_ports')
def registered_ports():
	errors = []
	registered_ports = []

	try:
		registered_ports = getRegisteredPortsData()
	except Exception as e:
		print(e)
		errors.append(e)


	templateData = {
		'registered_ports' : registered_ports,
		'errors' : errors
	}
	return render_template('registered_ports.html', **templateData)

@app.route('/from_ports')
def from_ports():
	errors = []
	from_ports = []

	try:
		from_ports = getFromPortsData()
	except Exception as e:
		print(e)
		errors.append(e)


	templateData = {
		'from_ports' : from_ports,
		'errors' : errors
	}
	return render_template('from_ports.html', **templateData)

@app.route('/fishing_port_registration_numbers')
def fishing_port_registration_numbers():
	errors = []
	fishing_port_registration_numbers = []

	try:
		fishing_port_registration_numbers = getFishingPortRegistrationNumbersData()
	except Exception as e:
		print(e)
		errors.append(e)


	templateData = {
		'fishing_port_registration_numbers' : fishing_port_registration_numbers,
		'errors' : errors
	}
	return render_template('fishing_port_registration_numbers.html', **templateData)

@app.route('/weather')
def weather():

	errors = []
	weather = []
	try:
		weather = getWeatherData()
	except Exception as e:
		print(e)
		errors.append(e)

	templateData = {
		'weather' : weather,
		'errors' : errors
	}
	return render_template('weather.html', **templateData)

@app.route('/notes')
def notes():

	errors = []
	notes = []
	try:
		notes = getNotesData()
	except Exception as e:
		print(e)
		errors.append(e)

	templateData = {
		'notes' : notes,
		'errors' : errors
	}
	return render_template('notes.html', **templateData)

@app.route('/transcriber_notes')
def transcriber_notes():

	errors = []
	entries = []
	try:
		entries = getEntriesWithTranscriberNotes()
	except Exception as e:
		print(e)
		errors.append(e)

	templateData = {
		'entries' : entries,
		'errors' : errors
	}
	return render_template('transcriber_notes.html', **templateData)

@app.route('/day/<year>/<month>/<day>')
def day(year, month, day):

	errors = []
	entries = []
	on_this_day = []
	on_this_day_weather = []
	on_this_day_note = []

	try:
		entries = getEntriesForYear(year)
	except Exception as e:
		print(e)
		errors.append(e)

	date_string = '{:0>2}-{:0>2}-{}'.format(day, month, year)
	date = datetime.strptime(date_string, '%d-%m-%Y').date()

	try:
		on_this_day = getEntriesForDate(date_string)
	except Exception as e:
		print(e)
		errors.append(e)

	try:
		on_this_day_weather = getWeatherDataForDate(date_string)
	except Exception as e:
		print(e)
		errors.append(e)

	try:
		on_this_day_note = getNotesDataForDate(date_string)
	except Exception as e:
		print(e)
		errors.append(e)

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
		'last_updated' : dir_last_updated('static'),
		'errors' : errors
	}
	return render_template('day.html', **templateData)


@app.route('/arrivals/<year>')
def arrivals(year):

	errors = []
	entries = []
	try:
		entries = getEntriesForYear(year)
	except Exception as e:
		print(e)
		errors.append(e)

	sources = { '1914' : 'https://docs.google.com/spreadsheets/d/1gr-501asOIg-YLTWkkeX3iWwVR1ROnHfX4swNKinRUk/edit#gid=1432177458', '1915' : 'https://docs.google.com/spreadsheets/d/1gr-501asOIg-YLTWkkeX3iWwVR1ROnHfX4swNKinRUk/edit#gid=524481503', '1916' : 'https://docs.google.com/spreadsheets/d/1gr-501asOIg-YLTWkkeX3iWwVR1ROnHfX4swNKinRUk/edit#gid=247148901', '1917' : 'https://docs.google.com/spreadsheets/d/1gr-501asOIg-YLTWkkeX3iWwVR1ROnHfX4swNKinRUk/edit#gid=1725245449', '1918' : 'https://docs.google.com/spreadsheets/d/1gr-501asOIg-YLTWkkeX3iWwVR1ROnHfX4swNKinRUk/edit#gid=1155924912', '1919' : 'https://docs.google.com/spreadsheets/d/1gr-501asOIg-YLTWkkeX3iWwVR1ROnHfX4swNKinRUk/edit#gid=1705602406', '1920' : 'https://docs.google.com/spreadsheets/d/1gr-501asOIg-YLTWkkeX3iWwVR1ROnHfX4swNKinRUk/edit#gid=583956228' }

	source = None
	if year in sources:
		source = sources[year]

	templateData = {
		'entries' : entries,
		'year' : year,
		'source' : source,
		'errors' : errors
	}
	return render_template('entries.html', **templateData)

@app.route('/arrivals_after/<year>')
def arrivals_after(year):

	errors = []
	entries = []

	try:
		entries = getEntriesAfterYear(year)
	except Exception as e:
		print(e)
		errors.append(e)

	templateData = {
		'entries' : entries,
		'year' : 'after {}'.format(year),
		'errors' : errors
	}
	return render_template('entries.html', **templateData)

@app.route('/vessel/<filter>')
def vessel(filter):

	errors = []
	entries = []

	try:
		entries = getEntriesForVessel(filter)
	except Exception as e:
		print(e)
		errors.append(e)

	templateData = {
		'entries' : entries,
		'vessel' : filter,
		'errors' : errors
	}
	return render_template('vessel.html', **templateData)
	
@app.route('/master/<filter>')
def master(filter):

	errors = []
	entries = []

	try:
		entries = getEntriesForMaster(filter)
	except Exception as e:
		print(e)
		errors.append(e)

	templateData = {
		'entries' : entries,
		'master' : filter,
		'errors' : errors
	}
	return render_template('master.html', **templateData)
	
@app.route('/cargo/<filter>')
def cargo(filter):

	errors = []
	entries = []

	try:
		entries = getEntriesForCargo(filter)
	except Exception as e:
		print(e)
		errors.append(e)

	templateData = {
		'entries' : entries,
		'cargo' : filter,
		'errors' : errors
	}
	return render_template('cargo.html', **templateData)
	
@app.route('/activity/<filter>')
def activity(filter):

	errors = []
	entries = []

	try:
		entries = getEntriesForActivity(filter)
	except Exception as e:
		print(e)
		errors.append(e)

	templateData = {
		'entries' : entries,
		'activity' : filter,
		'errors' : errors
	}
	return render_template('activity.html', **templateData)

@app.route('/registered_port/<filter>')
def registered_port(filter):

	errors = []
	entries = []

	try:
		entries = getEntriesForRegisteredPort(filter)
	except Exception as e:
		print(e)
		errors.append(e)

	templateData = {
		'entries' : entries,
		'registered_port' : filter,
		'errors' : errors
	}
	return render_template('registered_port.html', **templateData)

@app.route('/from_port/<filter>')
def from_port(filter):

	errors = []
	entries = []

	try:
		entries = getEntriesForFromPort(filter)
	except Exception as e:
		print(e)
		errors.append(e)

	templateData = {
		'entries' : entries,
		'from_port' : filter,
		'errors' : errors
	}
	return render_template('from_port.html', **templateData)

@app.route('/fishing_port_registration_number/<filter>')
def fishing_port_registration_number(filter):

	errors = []
	entries = []

	try:
		entries = getEntriesForFishingPortRegistrationNumber(filter)
	except Exception as e:
		print(e)
		errors.append(e)

	templateData = {
		'entries' : entries,
		'fishing_port_registration_number' : filter,
		'errors' : errors
	}
	return render_template('fishing_port_registration_number.html', **templateData)
	
	

@app.route('/graphs_cargo')
def graphs_cargo():
	return render_template('graphs_cargo.html')

@app.route('/graphs_cargo_by_kind')
def graphs_cargo_by_kind():
	return render_template('graphs_cargo_by_kind.html')

@app.route('/graphs_activity')
def graphs_activity():
	return render_template('graphs_activity.html')

@app.route('/graphs_activity_by_kind')
def graphs_activity_by_kind():
	return render_template('graphs_activity_by_kind.html')

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
	df = pd.read_sql_query('SELECT date, cargo FROM arrivals WHERE strftime(\'%Y\', date) = "{}" AND cargo <> "" ORDER BY date'.format(year), con, parse_dates=['date'])
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

def buildCargoGraphByKind(year):
	con = db.create_connection()
	df = pd.read_sql_query('SELECT cargo FROM arrivals WHERE strftime(\'%Y\', date) = "{}" AND cargo <> "" ORDER BY cargo'.format(year), con)
	con.close()

	fig = Figure(figsize=(8,12))
	axis = fig.subplots(1)

	top = df['cargo'].value_counts().sort_index()
	#top = top[top > 4]

	colour_map = cm.get_cmap('tab20', len(top) + 1)

	axis.barh(top.index, top.values, color=colour_map.colors)

	for i, v in enumerate(top):
		axis.text(v, i, " "+str(v), va='center')

	axis.set_title('Number of arrivals of each cargo type Aberdeen during {}'.format(year))
	axis.spines['right'].set_color('none')
	axis.spines['top'].set_color('none')
	fig.tight_layout()

	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response


def buildActivityGraph(year):
	con = db.create_connection()
	df = pd.read_sql_query('SELECT date, activity FROM arrivals WHERE strftime(\'%Y\', date) = "{}" AND activity <> "" ORDER BY date'.format(year), con, parse_dates=['date'])
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

def buildActivityByKindGraph(year):
	con = db.create_connection()
	df = pd.read_sql_query('SELECT activity FROM arrivals WHERE strftime(\'%Y\', date) = "{}" AND activity <> "" ORDER BY activity'.format(year), con)
	con.close()

	fig = Figure(figsize=(8,12))
	axis = fig.subplots(1)

	top = df['activity'].value_counts().sort_index()
	#top = top[top > 4]

	colour_map = cm.get_cmap('tab20', len(top) + 1)

	axis.barh(top.index, top.values, color=colour_map.colors)

	for i, v in enumerate(top):
		axis.text(v, i, " "+str(v), va='center')

	axis.set_title('Number of arrivals of each activity type Aberdeen during {}'.format(year))
	axis.spines['right'].set_color('none')
	axis.spines['top'].set_color('none')
	fig.tight_layout()

	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response


def buildTopVesselsGraph(year):
	con = db.create_connection()
	df = pd.read_sql_query('SELECT date, vessel FROM arrivals WHERE strftime(\'%Y\', date) = "{}" AND vessel <> "" ORDER BY date'.format(year), con, parse_dates=['date'])
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

@app.route('/plot/cargo_by_kind/<year>')
def plot_cargo_by_kind(year):
	return buildCargoGraphByKind(year)

@app.route('/plot/activity/<year>')
def plot_activity(year):
	return buildActivityGraph(year)

@app.route('/plot/activity_by_kind/<year>')
def activity_by_kind(year):
	return buildActivityByKindGraph(year)

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
	df = pd.read_sql_query('SELECT * FROM arrivals ORDER BY date', con, parse_dates=['date'], index_col=['uuid'])
	con.close()

	response = make_response(df.to_csv())
	response.headers["Content-Disposition"] = "attachment; filename=arrivals.csv"
	response.headers["Content-Type"] = "text/csv"
	return response

@app.route('/api/v1.0/arrivals')
def api_get_arrivals():
	con = db.create_connection()
	df = pd.read_sql_query('SELECT * FROM arrivals ORDER BY date', con, parse_dates=['date'], index_col=['uuid'])
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