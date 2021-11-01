from flask import Flask, jsonify
from flaskext.mysql import MySQL
from config import Config
import json

from dtos.postDTO import PostDTO, PostEncoder
from dtos.userDTO import UserDTO

app = Flask(__name__)

app.config.from_object(Config)


mysql = MySQL()
app.config['JSON_AS_ASCII'] = False
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_DB'] = input()
app.config['MYSQL_DATABASE_PASSWORD'] = input()
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
conn = mysql.connect()
cursor = conn.cursor()

@app.route("/get_all_posts/", methods =['GET'])
def get_all_posts() :
    cursor.execute("""SELECT * FROM motovrn.mv2_posts, motovrn.mv2_topics, motovrn.mv2_forums
where topic_id = mv2_topics.id and mv2_topics.forum_id = 1 LIMIT 20;""")
    columnNames = [column[0] for column in cursor.description]
    result = []
    for record in cursor.fetchall() :
        result.append(dict(zip(columnNames, record)))

    return serialize_posts(result)


def serialize_posts(records):
    result = []
    for record in records:
        result.append(PostDTO(record['id'], UserDTO(record['poster_id'], record['poster']), record['message']))
    return json.dumps(result, ensure_ascii=False, indent=4, cls=PostEncoder)