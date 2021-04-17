import os

import pandas as pd

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from statList import statList # dictionary mapping human readable to columns
 							# column = statList[human]['yStat']

def loadCsv():
	path = 'data/Superior vs Inferior database_13_Feb_master.csv'
	df = pd.read_csv(path, header=0)
	return df
dfMaster = loadCsv()

# get columns to make a stat table (list of columns)
statsDf = pd.DataFrame(columns=['idx', 'stat'])
statsDf['idx'] = [i for i in range(len(statList.keys()))]
statsDf['stat'] = [x for x in statList.keys()]

groupByList = ['analysisname', 'Region', 'Sex', 'Condition']

def getMean(dfMaster, groupByList, theStat):
	"""
	for one column (like spikeFreq_hz) get stats like count, mean, std, ...
	"""
	aggList = ['count', 'mean', 'std', 'sem', 'median']

	dfMean = dfMaster.groupby(groupByList, as_index=False)[theStat].agg(aggList)
	dfMean = dfMean.reset_index()
	dfMean.insert(1, 'stat', theStat) # column 1, in place
	return dfMean

xStat = 'spikeFreq_hz'
dfMean = getMean(dfMaster, groupByList, xStat)
#print(dfMean.head())

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

def makeTable(id, df):
	ret = dash_table.DataTable(
		id=id,
		columns=[{"name": i, "id": i} for i in df.columns],
		data=df.to_dict('records'),
		row_selectable='single',
		style_cell={'textAlign': 'left'},
		style_data_conditional=[
			{
			'if': {'row_index': 'odd'},
			'backgroundColor': 'rgb(220, 220, 220)'
			}
		],
		style_table={
			'height': 500,
			'overflowY': 'scroll',
			'width': 280
		}
	)
	return ret

app.layout = html.Div([
	#dcc.Dropdown(
	#	id='dropdown',
	#	options=[{'label': i, 'value': i} for i in ['LA', 'NYC', 'MTL']],
	#	value='LA'
	#),

	html.Div([
		html.Div([
           html.Label('Group By'),
		   dcc.Dropdown(
				id='group-by-dropdown',
				options=[{'label': i, 'value': i} for i in groupByList],
				value=groupByList[0],
			),
			dcc.Checklist(
				id='plot-options-check-list',
				options=[
					{'label': 'Plot Raw', 'value': 'plot raw'},
					{'label': 'Plot Mean', 'value': 'plot mean'},
				],
				labelStyle={'display': 'inline-block'}
			),
		]),
	], className="row"),

	html.Div([
		html.Div([
			html.P('X-Stat'),
			makeTable('x-stat-table', statsDf)],
			className="three columns"
		),

		html.Div([
			html.P('Y-Stat'),
			makeTable('y-stat-table', statsDf)],
			className="three columns"
		),

		html.Div([
			html.H3(''),
			dcc.Graph(id="scatter-plot")],
			className="six columns"
		),
	], className="row")

	#dash_table.DataTable(
	#	id='my-stat-table',
	#	columns=[{"name": i, "id": i} for i in dfMean.columns],
	#	data=dfMean.to_dict('records'),
	#),

]) #, style={'columnCount': 3})

@app.callback(
	Output("scatter-plot", "figure"),
	Input('x-stat-table', 'selected_rows'),
	Input('y-stat-table', 'selected_rows'),
	Input('group-by-dropdown', 'value'),
	Input('plot-options-check-list', 'value'),
	)
def f(xRow, yRow, groupBy, plotOptions):
	"""
	plotOptions: List of options that are checked, like
				['plot raw', 'plot mean']
	"""
	print('=== f()')

	# x
	if xRow is None:
		xRow = 0
	else:
		xRow = xRow[0]
	xStat = statsDf.iloc[xRow]['stat']
	print('  x-stat-table Input:', xStat)
	# y
	if yRow is None:
		yRow = 0
	else:
		yRow = yRow[0]
	yStat = statsDf.iloc[yRow]['stat']
	print('  y-stat-table Input:', yStat)

	xStatCol = statList[xStat]['yStat']
	yStatCol = statList[yStat]['yStat']

	xMeanDf = getMean(dfMaster, groupByList, xStatCol)
	yMeanDf = getMean(dfMaster, groupByList, yStatCol)
	xMean = xMeanDf['mean'].tolist()
	yMean = yMeanDf['mean'].tolist()
	#print('xMean:', xMean)
	#print('yMean:', yMean)

	fig = go.Figure()

	colors = px.colors.qualitative.Dark24
	#print('  colors:', colors)

	print('  plotOptions:', plotOptions)
	if plotOptions is not None and 'plot raw' in plotOptions:
		print('  plotting raw with groupBy:', groupBy)
		regions = dfMaster[groupBy].unique()
		#print(' using groupBy:', groupBy, regions)
		for idx, region in enumerate(regions):
			print('    region:', region)
			color = colors[idx]
			dfRegion = dfMaster[ dfMaster[groupBy]==region ]
			xRaw = dfRegion[xStatCol].tolist()
			yRaw = dfRegion[yStatCol].tolist()
			rawScatter = go.Scatter(x=xRaw, y=yRaw,
							name=region,
							mode='markers',
							marker=dict(
								color=color,
								size=5,
								line=dict(
									color='Gray',
									width=0
								)
							),
							showlegend=True
							)
			#
			fig.add_trace(rawScatter)

	if plotOptions is not None and 'plot mean' in plotOptions:
		print('  plotting mean')
		meanScatter = go.Scatter(x=xMean, y=yMean,
						mode='markers',
						marker=dict(
							color='Black',
							size=10,
							line=dict(
								color='Gray',
								width=1
							)
						),
						showlegend=False
						)
		#
		fig.add_trace(meanScatter)

	fig.update_layout(
		#title="Plot Title",
		xaxis_title=xStat,
		yaxis_title=yStat,
		legend_title=groupBy,
		font=dict(
			family="Arial",
			size=12,
			color="Black"
		)
	)


	#
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

'''
@app.callback(dash.dependencies.Output('display-value', 'children'),
			  [dash.dependencies.Input('dropdown', 'value')])
def display_value(value):
	return 'You have selected "{}"'.format(value)
'''

if __name__ == '__main__':
	#df = loadCsv()
	app.run_server(debug=True)
