from flask import Flask, jsonify, request
from flaskext.mysql import MySQL
from config import Config
import json
import hashlib
import base64

from dtos.postDTO import PostDTO, PostEncoder
from dtos.userDTO import UserDTO
from dtos.loginResultDTO import LoginResultDTO

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

@app.route("/login", methods = ['POST'])
def login() :
   login = request.args.get('login');
   password = request.args.get('password')
   passwordCode = hashlib.sha1(password.encode())
   passwordCode = passwordCode.hexdigest()
   print(passwordCode)
   cursor.execute(f"""SELECT * FROM motovrn.mv2_users where username = \"{login}\" 
        and password =\"{passwordCode}\";""")
   columnNames = [column[0] for column in cursor.description]
   record = dict(zip(columnNames, cursor.fetchall()[0]))

   result = LoginResultDTO(record['id'], record['username'], record['password'], generate_token(login, passwordCode))
   return json.dumps(result, ensure_ascii=False, indent=4, cls=PostEncoder)



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

def generate_token(login, password) :
    tokenString = login + password
    message_bytes = tokenString.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    return base64_message