from flask import Flask
import pyodbc

server = 'pay-r.database.windows.net:1433'
database = 'pay-r'
username = 'pay-r'
password = 'Party123'
driver= '{ODBC Driver 13 for SQL Server}'

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Weclome to Pay-R'
    