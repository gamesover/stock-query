from flask import Flask, render_template, request, redirect
import requests
from bokeh.plotting import figure
from bokeh.embed import components
from pandas import DataFrame
import pandas as pd
from bokeh.palettes import Spectral4

app = Flask(__name__)

app.vars = {}


@app.route('/')
def main():
    return redirect('/index')


@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        # request was a POST
        app.vars['ticker'] = request.form['ticker']
        app.vars['features'] = request.form.getlist('features')

        return redirect('/graph')


@app.route('/graph', methods=['GET'])
def graph():
    api_url = 'https://www.quandl.com/api/v1/datasets/WIKI/%s.json' % app.vars['ticker']
    session = requests.Session()
    session.mount('http://', requests.adapters.HTTPAdapter(max_retries=3))
    raw_data = session.get(api_url)

    if raw_data.status_code != 200:
        return redirect('/error-quandle')

    json = raw_data.json()

    df = DataFrame(data=json['data'], columns=json['column_names'])

    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values('Date')

    TOOLS = "pan,box_zoom,wheel_zoom,reset,save"
    plot = figure(tools=TOOLS,
                  title='Data from Quandle WIKI set',
                  x_axis_label='date',
                  x_axis_type='datetime')

    ticker = app.vars['ticker'].upper()

    for idx, item in enumerate(app.vars['features']):
        plot.line(df['Date'], df[item], line_color=Spectral4[idx], legend=ticker + ': ' + item)

    script, div = components(plot)

    return render_template('graph.html', script=script, div=div, ticker=ticker)


@app.route('/error-quandle')
def error():
    return render_template('error.html')


if __name__ == "__main__":
    app.run(port=33507)
