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
		
		dfAdjustments = pd.read_excel(google_sheet_url, header=0, parse_dates=[1],
			na_values=['[Blank]', '(blank)', '(Blank)','Blank','blank', '-',''])

		con = self.db.create_connection()
		dfOriginal = pd.read_sql_query(
			'SELECT * FROM arrivals_temp ORDER BY date',
			con,
			parse_dates=['date']
			)
		queryString = 'SELECT * FROM arrivals_temp WHERE uuid IS NULL AND vessel <> "" ORDER BY date'
		dfOriginalMissingUUID = pd.read_sql_query(
			queryString,
			con,
			parse_dates=['date']
			)
		con.close()

		dfAdjusted = dfOriginal.merge(dfAdjustments[
			['uuid', 'fishing_port_registration_numbers']
			], on='uuid')

		dfAdjusted = pd.concat([dfAdjusted, dfOriginalMissingUUID])

		dfAdjusted = dfAdjusted.rename(
			columns={'fishing_port_registration_numbers':'fishing_port_registration_number'}
			)

		dfAdjusted['fishing_port_registration_number'] = dfAdjusted['fishing_port_registration_number'].fillna('')

		columns = ['vessel','registered_port','master','registered_tonnage',
			'from_port','cargo_transcribed','weather','notes','cargo', 'activity']

		for column in columns:
			grouped = dfAdjustments.groupby('{}_update'.format(column))
			for name, group in grouped:
				dfAdjusted.loc[
					(dfAdjusted[column].isin([value for value in group[column]])),
					column] = name		

		# Extract HMx prefix from Vessel name
		dfAdjusted['vessel_prefix'] = dfAdjusted['vessel'].apply(
			lambda row:getVesselPrefix(row)
			)

		dfAdjusted['vessel'] = dfAdjusted['vessel'].apply(
			lambda row: splitVesselName(row)
			)

		# Write to database
		con = self.db.create_connection()
		dfAdjusted.to_sql('arrivals', con, if_exists='replace', index = False)
		con.close()

def getVesselPrefix(x):
	result = ''

	if x is not None:
		parts = x.split(' ')
		if parts[0] in ['HMSL', 'HMTB', 'HMM', 'HMOC', 'HMPO', 'HMQS', 'HML',
			'HMTS', 'HMRS', 'HMSS', 'HMR', 'HMFB', 'HMFS', 'HMMB', 'HMBO',
			'HMBS', 'HMME', 'HMMD', 'HMC', 'HMMO', 'HMT', 'HMD', 'HMMP', 'HMPS',
			'HMML', 'HMW', 'HMY', 'HMB', 'HHMS', 'HMBD', 'HMO', 'HMMR', 'HMS',
			'HMMS', 'HMP', 'HM']:
			result = parts[0]

	return result

def splitVesselName(x):
	result = x

	if x is not None:
		parts = x.split(' ')
		if parts[0] in ['HMSL', 'HMTB', 'HMM', 'HMOC', 'HMPO', 'HMQS', 'HML',
			'HMTS', 'HMRS', 'HMSS', 'HMR', 'HMFB', 'HMFS', 'HMMB', 'HMBO',
			'HMBS', 'HMME', 'HMMD', 'HMC', 'HMMO', 'HMT', 'HMD', 'HMMP', 'HMPS',
			'HMML', 'HMW', 'HMY', 'HMB', 'HHMS', 'HMBD', 'HMO', 'HMMR', 'HMS',
			'HMMS', 'HMP', 'HM']:
			result = ' '.join(parts[1:])

	return result


def main():
	processor = ProcessAdjustments()
	processor.process()

if __name__ == '__main__':
	main()
