from flask import Flask, jsonify
from flaskext.mysql import MySQL
from config import Config

app = Flask(__name__)

app.config.from_object(Config)


mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_DB'] = input()
app.config['MYSQL_DATABASE_PASSWORD'] = input()
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
conn = mysql.connect()
cursor = conn.cursor()

@app.route("/get_all_posts/", methods =['GET'])
def get_all_posts() :
    cursor.execute("SELECT * FROM motovrn.mv2_posts;")
    return jsonify(cursor.fetchall())
