## Following:

https://dash.plotly.com/deployment


# SanPy as a Plotly Dash app on Heroku

* You can view the finished app on [Heroku](https://sanpy.herokuapp.com/).
* Plotly Dash apps can only be viewed in a modern browser (like Chrome or Mozilla). They won't render in antediluvian browsers such as Microsoft.

## Install

```
python -m venv sanpy_dash_env
source sanpy_dash_env/bin/activate
pip install -r requirements
```

## Run

```
source sanpy_dash_env/bin/activate
python app.py
```
## Development notes

When run locally with 'python app.py', browse at http://127.0.0.1:8050/

My Heroku dashboard is at https://dashboard.heroku.com/apps/sanpy/deploy/github

Need to manually deploy heroku app after each git push to sanpy-dash

There is also dash bio for bioinformatics plotting: https://dash.plotly.com/dash-bio

## PyQt to show dash web interface

### Install

```
python -m venv sanpy-dash-qt-env
source sanpy-dash-qt-env/bin/activate
pip install -r requirements.txt
pip install -r requirements-pyqt.txt
```

### Run

```
source sanpy-dash-qt-env/bin/activate
python qtDash.py
```
