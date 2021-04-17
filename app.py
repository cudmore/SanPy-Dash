import os

import pandas as pd

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

def loadCsv():
	path = 'data/Superior vs Inferior database_13_Feb_master.csv'
	df = pd.read_csv(path, header=0)
	return df
dfMaster = loadCsv()

# get columns to make a stat table (list of columns)
yStatsDf = pd.DataFrame(columns=['idx', 'stat'])
yStatsDf['idx'] = [i for i in range(len(dfMaster.columns))]
yStatsDf['stat'] = [x for x in dfMaster.columns]

def getMean(dfMaster, theStat):
	"""
	for one column (like spikeFreq_hz) get stats like count, mean, std, ...
	"""
	aggList = ['count', 'mean', 'std', 'sem', 'median']
	groupByList = ['analysisname', 'Region', 'Sex', 'Condition']
	dfMean = dfMaster.groupby(groupByList, as_index=False)[theStat].agg(aggList)
	dfMean = dfMean.reset_index()
	dfMean.insert(1, 'stat', theStat) # column 1, in place
	return dfMean

xStat = 'spikeFreq_hz'
dfMean = getMean(dfMaster, xStat)
print(dfMean.head())

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

def makeTable(id, df):
	ret = dash_table.DataTable(
		id=id,
		columns=[{"name": i, "id": i} for i in df.columns],
		data=df.to_dict('records'),
		row_selectable='single'
	)
	return ret

app.layout = html.Div([
	html.H2('Hello World'),
	dcc.Dropdown(
		id='dropdown',
		options=[{'label': i, 'value': i} for i in ['LA', 'NYC', 'MTL']],
		value='LA'
	),

	html.Div(id='display-value'),

	dcc.Graph(id="scatter-plot"),

	#dash_table.DataTable(
	#	id='my-stat-table',
	#	columns=[{"name": i, "id": i} for i in dfMean.columns],
	#	data=dfMean.to_dict('records'),
	#),

	makeTable('y-stat-table', yStatsDf),
])

@app.callback(
	Output("scatter-plot", "figure"),
	[Input('y-stat-table', 'selected_rows')])
def f(selected_rows):
	if selected_rows is None:
		selected_rows = 0
	else:
		selected_rows = selected_rows[0]
	stat = yStatsDf.iloc[selected_rows]['stat']
	print('stat:', stat)
	fig = px.scatter(
		dfMaster, x="isi_ms", y=stat,
		color="Region",
		#size='petal_length',
		hover_data=['Region'])
	return fig

'''
def update_bar_chart(slider_range):
	low, high = slider_range
	mask = (df['petal_width'] > low) & (df['petal_width'] < high)
	fig = px.scatter(
		df[mask], x="sepal_width", y="sepal_length",
		color="species", size='petal_length',
		hover_data=['petal_width'])
	return fig
'''

@app.callback(dash.dependencies.Output('display-value', 'children'),
			  [dash.dependencies.Input('dropdown', 'value')])
def display_value(value):
	return 'You have selected "{}"'.format(value)

if __name__ == '__main__':
	#df = loadCsv()
	app.run_server(debug=True)
