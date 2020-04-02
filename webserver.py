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
import database_driver
import pandas as pd
import configparser, os
import numpy as np

app = Flask(__name__)
dbname = 'harbour.db'
db = database_driver.database(dbname)

def getLastImport():
	rows = db.select('SELECT strftime("%H:%M %d-%m-%Y", timestamp) as formated_date, entries FROM imports ORDER BY timestamp DESC LIMIT 1')
	return rows[0][0], rows[0][1]

def getRecordCount():
	rows = db.select('SELECT COUNT(date) FROM arrivals')
	return rows[0][0]


def getCargoData():
	rows = db.select('SELECT DISTINCT cargo FROM arrivals ORDER BY cargo')
	data = []
	for row in rows:
		data.append(row[0])

	return data

def getVesselsData():
	rows = db.select('SELECT DISTINCT vessel FROM arrivals ORDER BY vessel')
	data = []
	for row in rows:
		data.append(row[0])

	return data

def getMastersData():
	rows = db.select('SELECT DISTINCT master FROM arrivals WHERE master is not null ORDER BY master')
	data = []
	for row in rows:
		data.append(row[0])

	return data

def getRegisteredPortsData():
	rows = db.select('SELECT DISTINCT registered_port FROM arrivals ORDER BY registered_port')
	data = []
	for row in rows:
		data.append(row[0])

	return data

def getFromPortsData():
	rows = db.select('SELECT DISTINCT from_port FROM arrivals ORDER BY from_port')
	data = []
	for row in rows:
		data.append(row[0])

	return data

def getWeatherData():
	rows = db.select('SELECT strftime("%d-%m-%Y", date) as formated_date, weather FROM arrivals WHERE weather != "?" AND weather != "" ORDER BY date')

	return rows

def getNotesData():
	rows = db.select('SELECT strftime("%d-%m-%Y", date) as formated_date, notes FROM arrivals WHERE notes != "?" AND notes != "" ORDER BY date')

	return rows

def getTranscribersData():
	rows = db.select('SELECT DISTINCT transcriber FROM arrivals ORDER BY transcriber')
	data = []
	for row in rows:
		data.append(row[0])

	return data

def getCheckersData():
	rows = db.select('SELECT DISTINCT checker FROM arrivals ORDER BY checker')
	data = []
	for row in rows:
		data.append(row[0])

	return data

def getEntriesForVessel(vessel):
	rows = db.select('SELECT strftime("%d-%m-%Y", date) as formated_date, vessel, registered_port, master, registered_tonnage, from_port, cargo, checker FROM arrivals WHERE vessel LIKE :vessel ORDER BY date', {"vessel":'%'+vessel+'%'})

	return rows

def getEntriesForMaster(master):
	rows = db.select('SELECT strftime("%d-%m-%Y", date) as formated_date, vessel, registered_port, master, registered_tonnage, from_port, cargo, checker FROM arrivals WHERE master LIKE :master ORDER BY date', {"master":'%'+master+'%'})

	return rows

def getEntriesForCargo(cargo):
	rows = db.select('SELECT strftime("%d-%m-%Y", date) as formated_date, vessel, registered_port, master, registered_tonnage, from_port, cargo, checker FROM arrivals WHERE cargo LIKE :cargo ORDER BY date', {"cargo":'%'+cargo+'%'})

	return rows

def getEntriesForRegisteredPort(registered_port):
	rows = db.select('SELECT strftime("%d-%m-%Y", date) as formated_date, vessel, registered_port, master, registered_tonnage, from_port, cargo, checker FROM arrivals WHERE registered_port LIKE :registered_port ORDER BY date', {"registered_port":'%'+registered_port+'%'})

	return rows

def getEntriesForFromPort(from_port):
	rows = db.select('SELECT strftime("%d-%m-%Y", date) as formated_date, vessel, registered_port, master, registered_tonnage, from_port, cargo, checker FROM arrivals WHERE from_port LIKE :from_port ORDER BY date', {"from_port":'%'+from_port+'%'})

	return rows

def getEntriesForYear(year):
	rows = db.select('SELECT strftime("%d-%m-%Y", date) as formated_date, vessel, registered_port, master, registered_tonnage, from_port, cargo, checker FROM arrivals WHERE strftime("%Y", date) = :year ORDER BY date', { "year":year})

	return rows

def getEntriesAfterYear(year):
	rows = db.select('SELECT strftime("%d-%m-%Y", date) as formated_date, vessel, registered_port, master, registered_tonnage, from_port, cargo, checker FROM arrivals WHERE strftime("%Y", date) > :year ORDER BY date', { "year":year})

	return rows

@app.route('/')
# main route
def index():

	records_count = 0
	cargo = []
	vessels = []
	registered_ports = []
	from_ports = []
	last_import, records_count = getLastImport()

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
		'last_import' : last_import,
		'cargo' : cargo,
		'vessels' : vessels,
		'masters' : masters,
		'registered_ports' : registered_ports,
		'from_ports' : from_ports
	}
	return render_template('index.html', **templateData)


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

@app.route('/arrivals/<year>')
def arrivals(year):

	entries = []
	entries = getEntriesForYear(year)

	templateData = {
		'entries' : entries,
		'year' : year
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

def buildCargoGraph(year):
	con = db.create_connection()
	df = pd.read_sql_query('SELECT date, cargo FROM arrivals WHERE strftime(\'%Y\', date) = "{}" ORDER BY date'.format(year), con, parse_dates=['date'], index_col=['date'])
	con.close()

	fig = Figure(figsize=(12,8))
	axis = fig.subplots(1)

	if df.empty == False:
		df_cargos = df.groupby('date').cargo.value_counts().unstack().fillna(0)

		columns = df_cargos.columns
		labels = columns.values.tolist()

		colour_map = cm.get_cmap('tab20', len(columns) + 1)

		x = df_cargos.index
		bottom = np.zeros(df_cargos.shape[0])
		for i, column in enumerate(columns, start=0):
			axis.bar(x, df_cargos[column].values.tolist(), bottom=bottom, label=column, color=colour_map.colors[i])
			bottom += df_cargos[column].values.tolist()

	date_format = mpl_dates.DateFormatter('%d %b %Y')
	axis.xaxis_date()
	axis.xaxis.set_major_formatter(date_format)
	axis.set_title('Cargo arrival at Aberdeen {}'.format(year))
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

@app.route('/plot/cargo/<year>')
def plot_cargo(year):
	return buildCargoGraph(year)
	

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
	app.run(debug=True, port=config['server']['port'], host='0.0.0.0')