import os
from dotenv import load_dotenv
import pandas as pd
import datetime
from requests import Request, Session
import json
import plotly.express as px
import psycopg2
import numpy as np
import psycopg2.extras as extras
from io import StringIO
import mysql.connector

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

mydb = mysql.connector.connect(
  host=os.getenv('mysql_host'),
  user=os.getenv('mysqldb_username'),
  password=os.getenv('mysqldb_password'),
  database=os.getenv('mysqldb_name')

)
mycursor = mydb.cursor()

sql = "INSERT INTO customers (name, address) VALUES (%s, %s)"
val = [
  ('Peter', 'Lowstreet 4'),
  ('Amy', 'Apple st 652'),
  ('Hannah', 'Mountain 21'),
  ('Michael', 'Valley 345')
]

mycursor.executemany(sql, val)

mydb.commit()

print(mycursor.rowcount, "was inserted.")

