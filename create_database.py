#!/usr/bin/env python3
import pandas as pd
import database_driver

dbname = 'harbour.db'
db = database_driver.database(dbname)
 
if __name__ == '__main__':
		google_sheet_url = 'https://docs.google.com/spreadsheets/d/120KGS0oRFby5so-4_QVtaJWgAzuFEsnq86C1EgZW0-A/export#gid=0?format=csv'

		dfname = pd.ExcelFile(google_sheet_url)
		print(dfname.sheet_names)

		df=pd.read_excel(google_sheet_url, dtype={6:'string', 7:'string',12:'string', 13:'string'}, parse_dates=[0])

		for year in range(1915, 1921):
			dfnew=pd.read_excel(google_sheet_url, sheet_name=str(year), dtype={6:'string', 7:'string',12:'string', 13:'string'}, parse_dates=[0])
			df = pd.concat([df, dfnew])

		df = df.rename(columns = {'Date of Arrival (dd-mmm-yyyy)':'date', 'Number':'number', 'Ship\'s Name':'vessel', 'Of What Port':'registered_port', 'Master':'master', 'Registered Tonnage':'registered_tonnage','Port From Whence':'from_port','Cargo':'cargo', 'Wind and Weather':'weather','Other Notes':'notes', 'Transcriber Notes':'transcriber_notes', 'Transcribed by':'transcriber', 'Checked by':'checker', 'Queries':'transcriber_queries'})

		# Fix missing data issues
		df['cargo'] = df['cargo'].fillna("?")
		df['registered_port'] = df['registered_port'].fillna('?')
		df['from_port'] = df['from_port'].fillna('?')
		df["vessel"] = df["vessel"].fillna('?')
		df["weather"] = df["weather"].fillna('?')
		df["notes"] = df["notes"].fillna('?')
		df["transcriber_notes"] = df["transcriber_notes"].fillna('?')
		df["transcriber"] = df["transcriber"].fillna('?')
		df["checker"] = df["checker"].fillna('?')
		df["transcriber_queries"] = df["transcriber_queries"].fillna('?')

		# Write to database
		con = db.create_connection()
		df.to_sql('arrivals', con, if_exists='replace', index = False)
		con.close()