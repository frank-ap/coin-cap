import os
from dotenv import load_dotenv
import pandas as pd
from requests import Request, Session
import json
import mysql.connector
import numpy as np
from flask_mail import Mail, Message
from coincap import app, db

load_dotenv()

url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"

headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': os.getenv('X_CMC_PRO_API_KEY'),
}

session = Session()
session.headers.update(headers)

request = session.get(url)
results = request.json()

jsonDict = json.dumps(results, sort_keys=True, indent=4)
data = json.loads(jsonDict)
#print(data)
df = pd.DataFrame()

dict = {"name":[],
        "percent_change_24h":[],
        "percent_change_7d":[],
        "percent_change_30d":[],
        "percent_change_90d":[],
        "price":[],
        "date":[]}

for i in range(100):
    name = data["data"][i]["name"]
    percent_24h = data["data"][i]["quote"]["USD"]["percent_change_24h"]
    percent_7d = data["data"][i]["quote"]["USD"]["percent_change_7d"]
    percent_30d = data["data"][i]["quote"]["USD"]["percent_change_30d"]
    percent_90d = data["data"][i]["quote"]["USD"]["percent_change_90d"]
    price = data["data"][i]["quote"]["USD"]["price"]
    last_updated = data["data"][i]["last_updated"]

    dict["name"].append(name)
    dict["percent_change_24h"].append(percent_24h)
    dict["percent_change_7d"].append(percent_7d)
    dict["percent_change_30d"].append(percent_30d)
    dict["percent_change_90d"].append(percent_90d)
    dict["price"].append(price)
    dict["date"].append(last_updated)

df = pd.DataFrame.from_dict(dict)
df['date'] = pd.to_datetime(df['date']).dt.date

print(df.head())

mydb = mysql.connector.connect(
  host=os.getenv('mysql_host'),
  user=os.getenv('mysqldb_username'),
  password=os.getenv('mysqldb_password'),
  database=os.getenv('mysqldb_name')

)
mycursor = mydb.cursor()

sql = "INSERT INTO listings (name, percent_change_24h, percent_change_7d, percent_change_30d, percent_change_90d, price, date) VALUES (%s, %s, %s, %s, %s, %s, %s);"
tuples = [tuple(x) for x in df.to_numpy()]

mycursor.executemany(sql, tuples)

mydb.commit()

print(mycursor.rowcount, "was inserted.")

mycursor.close()
mydb.close()

app.config.update(
    DEBUG = True,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USERNAME = os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD'),
)

conn = db.engine.connect().connection
df = pd.read_sql("""select name, percent_change_24h, date, email from listings l
inner join alerts a on a.crypto1 = l.name or a.crypto2 = l.name or a.crypto3 = l.name
inner join user u on a.user_id = u.id
where l.date = (select MAX(l2.date) from listings l2
                where l2.name = l.name);
                ;""", conn)
conn.close()


for  email, df in df.groupby('email'):
    email_dict = {"email": "", "message":[]}
    email_dict["email"] = email
    dict = df.to_dict('index')
    for i in dict:
        email_dict['message'].append(f"Your crypto {dict[i]['name']} has changed in value by {dict[i]['percent_change_24h']}%")
    email_dict['message'] = str(email_dict['message'])
    mail = Mail(app)
    msg = Message('Your crypto update', sender='farreggerpowell@gmail.com', recipients=[email_dict['email']])
    msg.body = email_dict['message']
    with app.app_context():
        mail.send(msg)
