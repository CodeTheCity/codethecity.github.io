#!/usr/bin/env python3
import numpy as np
import pandas as pd
import database_driver
import datetime
from pathlib import Path  # <= Added Line

dbname = 'harbour.db'

class ProcessAdjustments:
	def __init__(self):
		self.db = database_driver.database(dbname)

	def process(self):

		# Import transcribed records
		google_sheet_url = 'https://docs.google.com/spreadsheets/d/1S4Kfl0gskYiWXtinLfh2pNMiFbS7-8qgRWTGY11XD6E/export#gid=0?format=csv'

		df = pd.DataFrame()
		
		dfAdjustments = pd.read_excel(google_sheet_url, header=0, parse_dates=[1], na_values=['(blank)', '(Blank)','Blank','blank', '-',''])

		# Just to see what has been imported
		#print(dfAdjustments)

		con = self.db.create_connection()
		dfOriginal = pd.read_sql_query('SELECT * FROM arrivals_temp ORDER BY date', con, parse_dates=['date'])
		con.close()

		#print(dfOriginal)

		#print(dfOriginal.dtypes)
		#print(dfAdjustments.dtypes)

		dfAdjusted = dfOriginal.merge(dfAdjustments[['uuid', 'fishing_port_registration_numbers']], on='uuid')

		dfAdjusted = dfAdjusted.rename(columns={'fishing_port_registration_numbers':'fishing_port_registration_number'})

		dfAdjusted['fishing_port_registration_number'] = dfAdjusted['fishing_port_registration_number'].fillna('')

		print(dfAdjusted)
		print(dfAdjusted.dtypes)

		# Write to database
		con = self.db.create_connection()
		dfAdjusted.to_sql('arrivals', con, if_exists='replace', index = False)
		con.close()

def main():
	processor = ProcessAdjustments()
	processor.process()

if __name__ == '__main__':
	main()
