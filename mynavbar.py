"""

"""

import dash_bootstrap_components as dbc

sanpyDocsHttps = 'https://cudmore.github.io/SanPy-Docs'
sanpyDashGithubHttps = 'https://github.com/cudmore/SanPy-Dash'

myNavBar = dbc.NavbarSimple(
	children=[
		dbc.NavItem(dbc.NavLink("Docs", external_link=True, href=sanpyDocsHttps)),
		dbc.NavItem(dbc.NavLink("GitHub", external_link=True, href=sanpyDashGithubHttps)),

		#dbc.DropdownMenu(
		#	children=[
		#		dbc.DropdownMenuItem("More pages", header=True),
		#		dbc.DropdownMenuItem("Page 2", href="#"),
		#		dbc.DropdownMenuItem("Page 3", href="#"),
		#	],
		#	nav=True,
		#	in_navbar=True,
		#	label="More",
		#),
	],
	brand="SanPy-Dash",
	brand_href="#",
	color="primary",
	dark=True,
)
