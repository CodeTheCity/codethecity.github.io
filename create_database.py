#!/usr/bin/env python3
import numpy as np
import pandas as pd
import database_driver
import datetime
from pathlib import Path  # <= Added Line

dbname = 'harbour.db'
db = database_driver.database(dbname)
 
if __name__ == '__main__':

		sql_create_imports_table = "CREATE TABLE IF NOT EXISTS imports (timestamp DATETIME, entries NUMERIC);"
		
		try:
				db.create_table(sql_create_imports_table)
		except Error as e:
				print(e)


		# new function to save errors - NEEDS a new directory called "errors" to save them to		
		def write_out(name, dframe):
				file_path = "errors/"+ name + ".csv"
				dframe.to_csv(file_path)


		# Import transcribed records
		google_sheet_url = 'https://docs.google.com/spreadsheets/d/120KGS0oRFby5so-4_QVtaJWgAzuFEsnq86C1EgZW0-A/export#gid=0?format=csv'

		df = pd.DataFrame()

		# set to None to import all
		import_nrows = None

		for year in range(1914, 1921):
			dfnew=pd.read_excel(google_sheet_url, sheet_name=str(year), nrows=import_nrows, header=1, dtype={1:'str', 5:'str', 6:'string', 7:'string',12:'string', 13:'string'}, parse_dates=[0], na_values=['(blank)', '(Blank)','Blank','blank', '-'])
			df = pd.concat([df, dfnew])
			print(dfnew)

		#df = df.rename(columns = {'Date of Arrival (dd-mmm-yyyy)':'date', 'Number':'number', 'Ship\'s Name':'vessel', 'Of What Port':'registered_port', 'Master':'master', 'Registered Tonnage':'registered_tonnage','Port From Whence':'from_port','Cargo':'cargo_transcribed', 'Wind and Weather':'weather','Other Notes':'notes', 'Transcriber Notes':'transcriber_notes', 'Transcribed by':'transcriber', 'Checked by':'checker', 'Queries':'transcriber_queries'})

		df.columns = ['date','number','vessel','registered_port','master','registered_tonnage','from_port','cargo_transcribed','weather','notes', 'transcriber_notes', 'transcriber', 'checker', 'transcriber_queries']

		#########################
		#Main new code starts here
		start_date = '01-01-1914' # You can test this working by making start_date 1915 or end date 1919 
		end_date = '31-12-1920'

		te_mask = (df['date'] < start_date)
		too_early_df = df.loc[te_mask]

		tl_mask = (df['date'] > end_date)
		too_late_df = df.loc[tl_mask]

		mask = (df['date'] >= start_date) & (df['date'] <= end_date)
		df = df.loc[mask]

		if len(too_late_df.count(axis='columns')) > 0:
				write_out("too_late", too_late_df)
		if len(too_early_df.count(axis='columns')) > 0:
				write_out("too_early", too_early_df)

		# Ends
		##################

		# Fix missing data issues and clean out whitespace
		columns = ['number', 'cargo_transcribed', 'master', 'registered_port', 'registered_tonnage', 'from_port', 'vessel', 'weather', 'notes', 'transcriber_notes', 'transcriber', 'checker', 'transcriber_queries']

		for column in columns:
			df[column] = df[column].fillna('').str.strip()
			#df.loc[(df[column] == '(blank)'), column] = ''

		df.loc[(df['transcriber_notes'] == '?'), 'transcriber_notes'] = ''
		df['cargo'] = df['cargo_transcribed']

		# Remap cargo into unified list
		mappings = {}

		with open('mappings/cargo_mappings.txt') as file:
			line = file.readline()

			while line:
				line = line.rstrip('\n')
				key = line.split(':')[0]
				values = line.split(':')[1]

				mappings[key] = values.split(',')

				line = file.readline()

		for key, values in mappings.items():
			df.loc[(df['cargo'].str.lower().isin([value.lower() for value in values])), 'cargo'] = key

		# Reallocate cargo to activities where required
		activities = []
		with open('mappings/activities_mappings.txt') as file:
			line = file.readline()

			while line:
				line = line.rstrip('\n')
				activities.append(line)
				line = file.readline()
		
		df['activity'] = np.where(df['cargo'].str.lower().isin([value.lower() for value in activities]), df['cargo'], '')
		df['cargo'] = np.where(df['cargo'].str.lower().isin([value.lower() for value in activities]), '', df['cargo'])


		# Remap Registered Ports into unified list
		mappings = {}

		with open('mappings/registered_ports_mappings.txt') as file:
			line = file.readline()

			while line:
				line = line.rstrip('\n')
				key = line.split(':')[0]
				values = line.split(':')[1]

				mappings[key] = values.split(',')

				line = file.readline()

		for key, values in mappings.items():
			df.loc[(df['registered_port'].str.lower().isin([value.lower() for value in values])), 'registered_port'] = key

		# Remap From Ports into unified list
		mappings = {}

		with open('mappings/from_ports_mappings.txt') as file:
			line = file.readline()

			while line:
				line = line.rstrip('\n')
				key = line.split(':')[0]
				values = line.split(':')[1]

				mappings[key] = values.split(',')

				line = file.readline()

		for key, values in mappings.items():
			df.loc[(df['from_port'].str.lower().isin([value.lower() for value in values])), 'from_port'] = key

		# Write to database
		con = db.create_connection()
		df.to_sql('arrivals', con, if_exists='replace', index = False)
		con.close()

		rows = db.select('SELECT COUNT(date) FROM arrivals')

		print('{} imported'.format(rows[0][0]))
		db.execute_query("INSERT INTO imports values((?), (?))", (datetime.datetime.now(), rows[0][0]))