import pandas as pd
import plotly.express as px
import plotly
import plotly.graph_objs as go
from flask import Flask, render_template, url_for, flash, redirect
import json
#from coincap.forms import RegistrationForm, LoginForm
from dotenv import load_dotenv
import os
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = 'egg'

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username=os.getenv('mysqldb_username'),
    password=os.getenv('mysqldb_password'),
    hostname=os.getenv('mysql_host'),
    databasename=os.getenv('mysqldb_name'),
)

app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
conn = db.engine.connect().connection
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

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
            xaxis = dict(
                tickformat = '%Y-%m-%d'
                ),
            xaxis_title="Date",
            yaxis_title=y_axis,
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
from coincap import routes