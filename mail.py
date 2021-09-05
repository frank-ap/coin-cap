import os
from dotenv import load_dotenv
import pandas as pd
from requests import Request, Session
import json
import mysql.connector
import numpy as np
from flask_mail import Mail, Message
from coincap import app, db, create_plot
from flask import render_template, url_for
import plotly.express as px


load_dotenv()

app.config.update(dict(
    DEBUG = True,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USERNAME = os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD'),
))


conn = db.engine.connect().connection
df = pd.read_sql("""select name, percent_change_24h, price, date, email from listings l
inner join alerts a on a.crypto1 = l.name or a.crypto2 = l.name or a.crypto3 = l.name
inner join user u on a.user_id = u.id
where l.date = (select MAX(l2.date) from listings l2
                where l2.name = l.name)
                and email = 'farreggerpowell@gmail.com'
                ;""", conn)
conn.close()

for  email, df in df.groupby('email'):
    email_dict = {"email": "", "message":[]}
    email_dict["email"] = email
    dict = df.to_dict('index')
    print(df)
    for i in dict:
        email_dict['message'].append(f"Your crypto {dict[i]['name']} has changed in value by {dict[i]['percent_change_24h']}%")
    email_dict['message'] = str(email_dict['message'])
    #fig = px.bar(df, x='date', y='price')
    #fig.write_html("/home/franksalot/mysite/coincap/templates/email.html")
    mail = Mail(app)
    msg = Message('Your crypto update', sender='farreggerpowell@gmail.com', recipients=[email_dict['email']])
    with app.app_context():
        msg.html = render_template("email.html", values=email_dict)
        mail.send(msg)

