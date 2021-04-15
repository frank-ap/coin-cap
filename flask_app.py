
# A very simple Flask Hello World app for you to get started with...
import os
from dotenv import load_dotenv
import json
import pandas as pd
import plotly
import plotly.graph_objs as go
import mysql.connector
from flask import Flask, render_template, url_for

load_dotenv()

app = Flask(__name__)

def create_plot(df, group, y_axis):
    fig = go.Figure()
    for group_name, df in group:
        data = fig.add_trace(
            go.Line(
                x=df['date']
                , y=df[y_axis]
                , name=group_name
                ))
        fig.update_layout(
            autosize=False,
            width=1400,
            height=700,
            title=y_axis,
            xaxis_title="Date",
            yaxis_title="Percentage (%)",
            legend_title="Cryptocurrencies",
            font=dict(
                family="Courier New, monospace",
                size=18,
                color="RebeccaPurple"
                )
                )
        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1d", step="day", stepmode="backward"),
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                    ])
                    )
                    )


    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

@app.route('/')
def home_page():

    return render_template('home.html')

@app.route('/data')
def line():
    mydb = mysql.connector.connect(
        host=os.getenv('mysql_host'),
        user=os.getenv('mysqldb_username'),
        password=os.getenv('mysqldb_password'),
        database=os.getenv('mysqldb_name')

    )
    df = pd.read_sql("SELECT * FROM listings", mydb)
    group = df.groupby('name')
    y_axis = 'percent_change_90d'
    bar = create_plot(df, group, y_axis)
    return render_template('index.html', plot=bar, title='Data')

if __name__ == "__main__":
    app.run(debug=True)
