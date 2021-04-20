"""
see: https://stackoverflow.com/questions/51522463/use-dash-plot-ly-in-pyqt5-gui
	https://stackoverflow.com/questions/57063046/embedding-a-plotly-dash-plot-in-a-pyqt5-gui-handshake-failed-ssl-error
"""

import sys

import threading

from PyQt5 import QtWidgets, QtCore, QtGui, QtWebEngineWidgets

import dash
import dash_core_components as dcc
import dash_html_components as html

def run_dash(data, layout):
	app = dash.Dash()

	app.layout = html.Div(children=[
		html.H1(children='Hello Dash'),

		html.Div(children='''
			Dash: A web application framework for Python.
		'''),

		dcc.Graph(
			id='example-graph',
			figure={
				'data': data,
				'layout': layout
			})
		])
	app.run_server(debug=False)


class MainWindow(QtWidgets.QMainWindow):
	def __init__(self, *args, **kwargs):
		super(MainWindow, self).__init__(*args, **kwargs)
#		a = 1

		self.setWindowTitle("Window Title")

		label = QtWidgets.QLabel("Label")
		label.setAlignment(QtCore.Qt.AlignCenter)
#
		layout = QtWidgets.QVBoxLayout()
#		layout.addWidget(Color('red'))
#		layout.addWidget(Color('green'))
		layout.addWidget(Color('blue'))

		TW = QtWidgets.QTabWidget()


		web1 = QtWebEngineWidgets.QWebEngineView()
		web1.load(QtCore.QUrl("http://127.0.0.1:8050"))

		web2 = QtWebEngineWidgets.QWebEngineView()
		web2.load(QtCore.QUrl("https://sanpy.herokuapp.com"))
		#web1.load(QUrl("http://127.0.0.1:8050"))

		TW.addTab(web1, 'web1')
		TW.addTab(web2, 'web2')
		layout.addWidget(TW)

		widget = QtWidgets.QWidget()
		widget.setLayout(layout)
		self.setCentralWidget(widget)

class Color(QtWidgets.QWidget):

	def __init__(self, color, *args, **kwargs):
		super(Color, self).__init__(*args, **kwargs)
		self.setAutoFillBackground(True)

		palette = self.palette()
		palette.setColor(QtGui.QPalette.Window, QtGui.QColor(color))
		self.setPalette(palette)

if __name__ == '__main__':
	data = [
		{'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
		{'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
	]

	layout = {
		'title': 'Dash Data Visualization'
	}

	# run dash web server
	#threading.Thread(target=run_dash, args=(data, layout), daemon=True).start()

	# run qt app
	app = QtWidgets.QApplication(sys.argv)
	mainWin = MainWindow()
	mainWin.show()
	sys.exit(app.exec_())
