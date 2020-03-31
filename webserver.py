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
	rows = db.select('SELECT DISTINCT master FROM arrivals ORDER BY master')
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
	rows = db.select('SELECT strftime("%d-%m-%Y", date) as formated_date, weather FROM arrivals WHERE weather != "?" ORDER BY date')

	return rows

@app.route('/')
# main route
def index():

	records_count = 0
	cargo = []
	vessels = []
	registered_ports = []
	from_ports = []
	records_count = getRecordCount()
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

	weather = getWeatherData()

	templateData = {
		'records_count' : records_count,
		'cargo' : cargo,
		'vessels' : vessels,
		'masters' : masters,
		'registered_ports' : registered_ports,
		'from_ports' : from_ports,
		'weather' : weather
	}
	return render_template('index.html', **templateData)

@app.route('/weather')
def weather():

	weather = []
	weather = getWeatherData()

	templateData = {
		'weather' : weather
	}
	return render_template('weather.html', **templateData)

def buildCargoGraph(year):
	con = db.create_connection()
	df = pd.read_sql_query('SELECT date, cargo FROM arrivals WHERE strftime(\'%Y\', date) = "{}" ORDER BY date'.format(year), con, parse_dates=['date'], index_col=['date'])
	con.close()

	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)

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
	axis.legend(fontsize=10, ncol=4)

	fig.autofmt_xdate()
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

if __name__ == '__main__':
	config = configparser.ConfigParser()

	if not os.path.exists('config.ini'):
		config['server'] = {'port': '80'}
		config.write(open('config.ini', 'w'))

	config.read('config.ini')
	app.run(debug=True, port=config['server']['port'], host='0.0.0.0')