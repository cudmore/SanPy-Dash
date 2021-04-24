import os

import pandas as pd

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
#from plotly.subplots import make_subplots
# trying to get row layout simple
import dash_bootstrap_components as dbc

from statList import statList # dictionary mapping human readable to columns
 							# column = statList[human]['yStat']

'''
for k,v in statList.items():
	print(k, '\t', v['yStat'])
'''

# see: https://community.plotly.com/t/deploying-multi-page-app-to-heroku-not-deploying-as-set-up/7877/2
from app import app
from app import server # needed for heroku
# import all pages in the app
#from apps import global_situation, singapore, home
from pages import mynavbar, uploadpage
#from mynavbar import myNavBar
#from uploadPage import uploadPageLayout

def loadCsv():
	path = 'data/Superior vs Inferior database_13_Feb_master.csv'
	df = pd.read_csv(path, header=0)
	return df

def getMean(dfMaster, groupByList, theStat):
	"""
	for one column (like spikeFreq_hz) get stats like count, mean, std, ...
	"""
	aggList = ['count', 'mean', 'std', 'sem', 'median']

	dfMean = dfMaster.groupby(groupByList, as_index=False)[theStat].agg(aggList)
	dfMean = dfMean.reset_index()
	dfMean.insert(1, 'stat', theStat) # column 1, in place
	return dfMean

def makeDropdown(id, itemList, defaultItem):
	"""
	defaultItem: Needs to be in itemList
	"""
	ret = dcc.Dropdown(
		id=id,
		options=[{'label': i, 'value': i} for i in itemList],
		value=defaultItem,
		)
	#
	return ret

def makeCheckList(id, itemList, defaultItem):
	options = [{'label': x, 'value': x} for x in itemList]
	ret = dcc.Checklist(
		id=id,
		options=options,
		value=[itemList[0]],
		#labelStyle={'display': 'inline-block'}
		labelStyle={"margin-right": "15px"}, # adds space between options list
		inputStyle={"margin-right": "5px"}, # adds space between check and its label
	), # Checklist
	return ret

def makeRadio(id, itemList, defaultItem):
	options = [{'label': x, 'value': x} for x in itemList]
	ret = dcc.RadioItems(
		id=id,
		options=options,
		value=itemList[0],
		labelStyle={"margin-right": "15px"}, # adds space between options list
		inputStyle={"margin-right": "5px"}, # adds space between check and its label
	)
	return ret

def makeTable(id, df, height=200, row_selectable='single', defaultRow=0):
	"""
	defaultRow: row index selected on __init__
	"""
	ret = dash_table.DataTable(
		id=id,
		columns=[{"name": i, "id": i} for i in df.columns],
		data=df.to_dict('records'),
		row_selectable=row_selectable,
		fixed_rows={'headers': True}, # on scroll, keep headers at top
		selected_rows = [defaultRow], # default selected row
		style_header={
			'backgroundColor': 'rgb(200, 200, 255)',
			'fontWeight': 'bold',
		},
		style_cell={
			'textAlign': 'left',
			'fontSize':11, 'font-family':'sans-serif',
			#'backgroundColor': 'rgb(30, 30, 30)',# dark theme
			#'color': 'white' # dark theme
			},
		style_data_conditional=[
			{
			'if': {'row_index': 'odd'},
			#'backgroundColor': 'rgb(50, 50, 50)' # dark theme
			'backgroundColor': 'rgb(200, 200, 200)' # light theme
			}
		],
		style_table={
			'height': height, # hard coding height
			#'overflowY': 'scroll',
			'overflowX': 'auto',
			'overflowY': 'auto',
			#'width': width
		}
	)
	return ret

def plotStripPlot(df, groupBy, yStatCol, doMeanSem=True):
	dfMaster = df
	fig = px.strip(dfMaster,
					x=groupBy, color=groupBy,
					y=yStatCol,
					stripmode='overlay',
					hover_data=dfMaster.columns)
	#
	return fig

def plotHistogram(df, groupBy, yStatCol, doCumulative=False, doBoxPlotInset=False):
	"""
	global:
		dfMaster
	"""
	dfMaster = df
	if doCumulative:
		#show_hist = False
		histnorm = 'probability density' #probability'
	else:
		#show_hist = True
		histnorm = None

	if doBoxPlotInset:
		marginal = 'box' # ['box', 'violin', 'rug']
	else:
		marginal = None
	fig = px.histogram(
		dfMaster, x=yStatCol, color=groupBy,
		#histfunc=histfunc,
		cumulative=doCumulative,
		histnorm=histnorm,
		#show_hist=show_hist,
		marginal=marginal,
		hover_data=dfMaster.columns)
	return fig

def plotScatter(df, xStatCol, yStatCol, groupBy, colorBy, plotRaw=True, plotMean=False):
	"""
	groupBy: for example 'Region'
	"""
	colors = px.colors.qualitative.Dark24
	dfMaster = df
	ret = []

	if plotRaw:
		# todo: if groupBy is None then no grouping, use very row in dfMaster
		groups = dfMaster[groupBy].unique()
		print('	plotScatter() groupBy:', groupBy, 'num:', len(groups))
		for idx, group in enumerate(groups):
			#print('	plotScatter() group:', group)
			color = colors[idx] # global
			dfGroup = dfMaster[ dfMaster[groupBy]==group ]
			xRaw = dfGroup[xStatCol].tolist()
			yRaw = dfGroup[yStatCol].tolist()
			rawScatter = go.Scatter(x=xRaw, y=yRaw,
							# for legend, str() needed because 'File Number' column is numpy.int64
							name=str(group),
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
			ret.append(rawScatter)

	if plotMean:
		#xMeanDf = getMean(dfMaster, groupByList, xStatCol)
		#yMeanDf = getMean(dfMaster, groupByList, yStatCol)
		xMeanDf = getMean(dfMaster, groupBy, xStatCol)
		yMeanDf = getMean(dfMaster, groupBy, yStatCol)
		xMean = xMeanDf['mean'].tolist()
		yMean = yMeanDf['mean'].tolist()
		xSem = xMeanDf['sem'].tolist()
		ySem = yMeanDf['sem'].tolist()
		# plot mean as different colors, this does not work ???
		# color of mean, tricky
		meanColor = xMeanDf[groupBy].tolist()
		meanColorList = [colors[idx] for idx, x in enumerate(meanColor)]

		meanScatter = go.Scatter(x=xMean, y=yMean,
						mode='markers',
						error_x=dict(
							type='data', # value of error bar given in data coordinates
							array=xSem,
							visible=True),
						error_y=dict(
							type='data', # value of error bar given in data coordinates
							array=ySem,
							visible=True),
						marker=dict(
							#color='Black',
							color=meanColorList,
							size=10,
							line=dict(
								color='Gray',
								width=1
							)
						),
						showlegend=False
						)
		#
		#fig.add_trace(meanScatter)
		ret.append(meanScatter)
	#
	return ret

##
## start main
##
def dashMain():

	# todo: allow to load any csv
	dfMaster = loadCsv()

	# get columns to make a stat table (list of columns)
	statsDf = pd.DataFrame(columns=['idx', 'stat'])
	statsDf['idx'] = [i for i in range(len(statList.keys()))]
	statsDf['stat'] = [x for x in statList.keys()]

	plotTypeList = ['Scatter', 'Histogram', 'Histogram + Box Plot', 'Cumulative Histogram', 'Strip Plot']

	# todo: add this as param to __init__
	# todo: implement 'None', in particular in getMean()
	groupByList = ['File Number', 'analysisname', 'Region', 'Sex', 'Condition']
	colorByList = ['None', 'analysisname', 'Region', 'Sex', 'Condition']

	# todo: add as a parameter to __init__
	defaultDict = {
		'plotType': 'Scatter',
		'groupBy': 'Region',
		'colorBy': 'Region',
		'xDefaultRow': 2, # todo: need to grab this index from preferred stat in statList
		'yDefaultRow': 0,
	}

	# initial tables
	xStat = 'thresholdVal'
	yStat = 'spikeFreq_hz'
	xMeanDf = getMean(dfMaster, groupByList, xStat)
	yMeanDf = getMean(dfMaster, groupByList, yStat)

	# todo: add same colors to all plots
	#colors = px.colors.qualitative.Dark24
	#print('  colors:', colors)

	#
	# moved to app.py
	'''
	myStyles = 'assets/myStyle.css'
	# this is crap, no layout
	#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
	# can't use dark themes
	external_stylesheets = [dbc.themes.BOOTSTRAP, myStyles]
	app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
	server = app.server
	'''

	# a control panel div with dropdowns, checkbox, and radio
	tmpControlDiv = html.Div(
		[
			dbc.Row(
				[
					dbc.Col(
						html.Label('Plot Type')
						, width="auto"
					),
					dbc.Col(
						makeDropdown('plot-type-dropdown', plotTypeList, defaultDict['plotType'])
						#, width=3
					),
				],
				#],no_gutters=True,
			), # row
			dbc.Row(
				[
					dbc.Col(
						html.Label('Group By')
						, width="auto"
					),
					dbc.Col(
						makeDropdown('group-by-dropdown', groupByList, defaultDict['groupBy'])
						#, width=3
					),
				],
				#],no_gutters=True,
			), # row
			dbc.Row(
				[
					dbc.Col(
						html.Label('Color By')
						, width="auto"
					),
					dbc.Col(
						makeDropdown('color-by-dropdown', colorByList, defaultDict['colorBy'])
						#, width=3
					),
				],
				#],no_gutters=True,
			), # row
			dbc.Label(''),
			dbc.Row(
				[
					dbc.Col(
						html.Label('Plot Data')
						, width="auto"
					),
					dbc.Col(
						makeCheckList('plot-options-check-list', ['Raw', 'Mean'], 'Raw')
						#, width=3
					),
				],
				#],no_gutters=True,
			), # row
			dbc.Label(''),
			dbc.Row(
				[
					dbc.Col(
						html.Label('Update Plot')
						, width="auto"
					),
					dbc.Col(
						makeRadio('update-plot-radio', ['Left', 'Right'], 'Left')
						#, width=3
					),
				],
				#],no_gutters=True,
			), # row

		], className = 'container', style={'font-size': '12px'})
		#, style={'fontColor': 'blue'})
		#]) # outerdiv

	##
	##
	boxBorder = "0px black solid"
	tmpOneRow2 = html.Div( # outer div
		[
			dbc.Row(
				[
					dbc.Col(
						html.Div([
							html.Label('Parameters'),
							tmpControlDiv
						]
						#,style={'font-size': '11px'}
						) # div
						,width=4,style={"border":boxBorder}
					),
					dbc.Col(
						html.Div([
							html.Label('X-Stat'),
							makeTable('x-stat-table', statsDf, height=180, defaultRow=defaultDict['xDefaultRow'])
						]) # div
						,width=4,style={"border":boxBorder}
					), # col
					dbc.Col(
						html.Div([
							html.Label('Y-Stat'),
							makeTable('y-stat-table', statsDf, height=180, defaultRow=defaultDict['yDefaultRow'])
						]) # div
						,width=4,style={"border":boxBorder}
					), # col
					#dbc.Col(
					#	html.Div([
					#		#html.Label('Color By'),
					#		dcc.Graph(id="scatter-plot")
					#	])
					#	,width=6,style={"border":boxBorder}), # col
				],
				#],no_gutters=True,
			), # row
			dbc.Row(
				[
					dbc.Col(
						html.Div([
							#html.Label('Color By'),
							dcc.Graph(id="scatter-plot-left")
						])
						,width=6,style={"border":boxBorder}), # col
					dbc.Col(
						html.Div([
							#html.Label('Color By'),
							dcc.Graph(id="scatter-plot-right")
						])
						,width=6,style={"border":boxBorder}), # col
				],
			), # row
		], className = 'container') # outerdiv

	tmpOneRow3 = html.Div( # outer div
		[
			dbc.Row(
				[
					dbc.Col(
						html.Div([
							html.Label('X Group By'),
							#makeTable('x-mean-table', xMeanDf, height=300, row_selectable=None),
							makeTable('x-mean-table', xMeanDf, height=300, row_selectable='multi'),
						])
						,width=6,style={"border":boxBorder}), # col
					dbc.Col(
						html.Div([
							html.Label('Y Group By'),
							makeTable('y-mean-table', yMeanDf, height=300, row_selectable=None),
						]) # div
						,width=6,style={"border":boxBorder}), # col
				],
			), # row
		], className = 'container') # outerdiv

	indexLayout = html.Div([
		tmpOneRow2, # controls and x/y stat tables
		tmpOneRow3, # plots
	])

	app.layout = html.Div([
		# i don't understand this. This is hidden but allows
		# callback to go to a different page?
		#dcc.Location(id='url', refresh=False),
		dcc.Location(id='url'),

		mynavbar.myNavBar,
		#tmpOneRow, # controls
		#tmpControlDiv, # single div for all controls v2

		# was this
		#tmpOneRow2, # controls and x/y stat tables
		#tmpOneRow3, # plots

		html.Div(id='page-content'), # working on two page app

	]) #, style={'columnCount': 3})

	#
	# callbacks
	#

	@app.callback(dash.dependencies.Output("page-content", "children"),
				  [dash.dependencies.Input('url', 'pathname')])
	def displayPageCallback(pathname):
		print('displayPageCallback() pathname:', pathname)
		if pathname == "/":
			return indexLayout
		elif pathname == '/uploadPage':
			return uploadpage.uploadPageLayout
		else:
			# If the user tries to reach a different page, return a 404 message
			return dbc.Jumbotron(
				[
					html.H1("404: Not found", className="text-danger"),
					html.Hr(),
					html.P(f"The pathname {pathname} was not recognised..."),
				]
			)

	@app.callback(
		[
			Output("scatter-plot-left", "figure"),
			Output("scatter-plot-right", "figure"),
			Output("x-mean-table", "data"),
			Output("y-mean-table", "data"),
		],
		[
			Input('plot-type-dropdown', 'value'),
			Input('x-stat-table', 'selected_rows'),
			Input('y-stat-table', 'selected_rows'),
			Input('group-by-dropdown', 'value'),
			Input('color-by-dropdown', 'value'),
			Input('plot-options-check-list', 'value'), # (raw, mean)
			State('update-plot-radio', 'value'), # (left, right)
		]
		)
	def f(plotType, xRow, yRow, groupBy, colorBy, plotOptions, plotLeftRight):
		"""
		Parameters:
			plotType:
			xRow,yRow: [list]
			groupBy:
			plotOptions: List of options that are checked, like
					['plot raw', 'plot mean']
			plotLeftRight: plot to either the left or right plot
		"""
		print('=== f()')

		print('  plotType:', plotType)
		print('  xRow:', xRow)
		print('  yRow:', yRow)
		print('  groupBy:', groupBy)
		print('  colorBy:', colorBy)
		print('  plotOptions:', plotOptions)
		print('  plotLeftRight:', plotLeftRight)

		print('  1) defaultDict:', defaultDict)
		defaultDict['xDefaultRow'] = xRow[0]
		defaultDict['yDefaultRow'] = yRow[0]
		print('  2) defaultDict:', defaultDict)

		# use context ctx to determine who triggered callback
		ctx = dash.callback_context
		if not ctx.triggered:
			idTriggered = 'No clicks yet'
		else:
			idTriggered = ctx.triggered[0]['prop_id'].split('.')[0]
		print('  idTriggered:', idTriggered)

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

		# convertt human to actual column
		xStatCol = statList[xStat]['yStat']
		yStatCol = statList[yStat]['yStat']

		# todo: append xMeanDf/yMeanDf to tables
		'''
		xMeanDf = getMean(dfMaster, groupByList, xStatCol)
		yMeanDf = getMean(dfMaster, groupByList, yStatCol)
		xMean = xMeanDf['mean'].tolist()
		yMean = yMeanDf['mean'].tolist()
		xSem = xMeanDf['sem'].tolist()
		ySem = yMeanDf['sem'].tolist()

		# plot mean as different colors, this does not work ???
		# color of mean, tricky
		meanColor = xMeanDf[groupBy].tolist()
		meanColorList = [colors[idx] for idx, x in enumerate(meanColor)]
		'''

		fig = go.Figure()

		#plotRaw = plotOptions is not None and 'plot raw' in plotOptions
		#plotMean = plotOptions is not None and 'plot mean' in plotOptions
		plotRaw = plotOptions is not None and 'Raw' in plotOptions
		plotMean = plotOptions is not None and 'Mean' in plotOptions

		#plotType = 'Histogram + Boxplot'
		xAxisTitle = ''
		yAxisTitle = ''
		if plotType == 'Scatter':
			rawScatterList = plotScatter(dfMaster, xStatCol, yStatCol, groupBy, colorBy, plotRaw=plotRaw, plotMean=plotMean)
			# rawScatterList is a list of [scatter, mean)
			for rawScatter in rawScatterList:
				fig.add_trace(rawScatter)
			xAxisTitle = xStat
			yAxisTitle = yStat
		elif plotType in ['Histogram', 'Histogram + Box Plot', 'Cumulative Histogram']:
			doBoxPlotInset = plotType == 'Histogram + Box Plot'
			doCumulative = plotType == 'Cumulative Histogram'
			fig = plotHistogram(dfMaster, groupBy, yStatCol, doCumulative=doCumulative, doBoxPlotInset=doBoxPlotInset)
			#fig.add_trace(rawScatter)
			xAxisTitle = yStat
			yAxisTitle = 'Count'
		elif plotType == 'Strip Plot':
			doMeanSem = True
			fig = plotStripPlot(dfMaster, groupBy, yStatCol, doMeanSem=doMeanSem)
			# gives error
			#fig.update_layout(traceorder='normal')
			xAxisTitle = groupBy
			yAxisTitle = yStat

		fig.update_layout(
			#title="Plot Title",
			xaxis_title=xAxisTitle,
			yaxis_title=yAxisTitle,
			legend_title=groupBy,
			font=dict(
				family="Arial",
				size=12,
				color="Black"
			),
			margin=dict(l=20, r=20, t=20, b=20),
		)

		#
		# use dash.no_update to update left/right and keep other the same
		# this works, but started using State for update-plot-radio
		#if idTriggered == 'update-plot-radio':
		#	# don't update plot when use just click on plot radio left/right
		#	print('  user selected left/right -->> no update')
		#	return dash.no_update, dash.no_update, dash.no_update, dash.no_update
		if plotLeftRight == 'Left':
			#
			return fig, dash.no_update, xMeanDf.to_dict('records'), yMeanDf.to_dict('records')
		elif plotLeftRight == 'Right':
			#
			return dash.no_update, fig, xMeanDf.to_dict('records'), yMeanDf.to_dict('records')
	#
	#
	#return app, server

'''
# grab hover from one plot and show in other plot
@app.callback([Output('local and imported', 'figure'),
			   Output('dorms', 'figure')],
			  [Input('graph_by_period', 'hoverData')])

def update_breakdown(hoverData):
	day = hoverData['points'][0]['x']
	dff = df[df['Date'] == day]
'''

# "server" needs to be global for heroku
#app, server = dashMain()
dashMain()

if __name__ == '__main__':
	# causing heroku to crash
	#app = dashMain()
	# procfile for Heroku is: web: gunicorn app:server
	# expects app.py to have global variable "server"
	#app, server = dashMain()
	#dashMain()
	app.run_server(debug=True)
