#!/usr/bin/env python3

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mpl_dates
import io
from flask import Flask, render_template, send_file, make_response, request
import datetime
import database_driver
import pandas as pd
import configparser, os

app = Flask(__name__)
dbname = 'harbour.db'
db = database_driver.database(dbname)

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

@app.route('/')
# main route
def index():

	cargo = []
	vessels = []
	registered_ports = []
	from_ports = []
	try:
		cargo = getCargoData()
	except Exception as e:
		print(e)

	try:
		vessels = getVesselsData()
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
		'cargo' : cargo,
		'vessels' : vessels,
		'registered_ports' : registered_ports,
		'from_ports' : from_ports
	}
	return render_template('index.html', **templateData)

if __name__ == '__main__':
	app.run(debug=True, port=81, host='0.0.0.0')