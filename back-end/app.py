from flask import Flask
from flask import g
import pyodbc
import json

app = Flask(__name__)
app.run(debug=True)

server = 'pay-r.database.windows.net'
database = 'pay-r'
username = 'pay-r'
password = 'Party123'
driver= '{SQL Server}'

def get_db():
    if not hasattr(g, 'conn'):
        g.conn = get_db_connection()

    return g.conn

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'connection'):
        g.conn.close()
    
def get_db_connection():
    return pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)

@app.route('/')
def hello_world():
    return 'Weclome to Pay-R'

@app.route('/shops')
def shops():
    conn = get_db()
    cursor = conn.cursor()
    rows = cursor.execute('SELECT * FROM shops').fetchall()
    shops = [{ 'id': row.id, 'name': row.name, 'email': row.email, 'phone': row.phone} for row in rows]
    return json.dumps(shops)
