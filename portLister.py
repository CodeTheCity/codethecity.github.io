#!/usr/bin/env python3

import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mpl_dates
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

import numpy as np

pd.set_option('display.max_rows', None)

google_sheet_url = 'https://docs.google.com/spreadsheets/d/120KGS0oRFby5so-4_QVtaJWgAzuFEsnq86C1EgZW0-A/export#gid=0?format=csv'

dfname = pd.ExcelFile(google_sheet_url)
print(dfname.sheet_names)

df=pd.read_excel(google_sheet_url, dtype={6:'string', 7:'string',12:'string', 13:'string'}, parse_dates=[0])

sheet_names = ['1914', '1915', '1916', '1917', '1918', '1919', '1920']
for items in sheet_names[1:]:
	dfnew=pd.read_excel(google_sheet_url, sheet_name=items, dtype={6:'string', 7:'string',12:'string', 13:'string'}, parse_dates=[0])
	df = pd.concat([df, dfnew])

df = df.rename(columns = {'Date of Arrival (dd-mmm-yyyy)':'Date', 'Ship\'s Name':'Vessel'})

df['Cargo'] = df['Cargo'].fillna("?")

df['Registered Tonnage'] = df[['Registered Tonnage']].apply(pd.to_numeric, errors='coerce')
print(df.info())
ports_from = df['Port From Whence'].fillna('?').unique()
print("Ports from:")
print(', '.join(ports_from))
registered_ports = df['Of What Port'].fillna('?').unique()
print("Registered ports:")
print(', '.join(registered_ports))
vessels = df["Vessel"].fillna('?').unique()
print("Vessels:")
print(', '.join(vessels))
cargo = df["Cargo"].fillna('?').unique()
print("Cargo:")
print(', '.join(cargo))

df_cargos = df[['Date', 'Cargo']].groupby('Date').Cargo.value_counts().unstack().fillna(0)

fig, (ax1) = plt.subplots(1, figsize=(15,7))

columns = df_cargos.columns
labels = columns.values.tolist()

colour_map = cm.get_cmap('tab20', len(columns) + 1)

x = df_cargos.index
bottom = np.zeros(df_cargos.shape[0])
for i, column in enumerate(columns, start=0):
	ax1.bar(x, df_cargos[column].values.tolist(), bottom=bottom, label=column, color=colour_map.colors[i])
	bottom += df_cargos[column].values.tolist()

date_format = mpl_dates.DateFormatter('%d %b %Y')
ax1.xaxis_date()
ax1.xaxis.set_major_formatter(date_format)
ax1.set_title('Cargo arrival at Aberdeen')
ax1.legend(fontsize=10, ncol=4)

fig.tight_layout()
fig.savefig('cargo.png')