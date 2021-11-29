from datetime import datetime
from datetime import timedelta
from datetime import timezone

from flask import Flask, jsonify, request
from flaskext.mysql import MySQL
from config import Config
import json
import hashlib
import base64

from flask_jwt_extended import create_access_token, get_jwt, set_access_cookies
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

from dtos.postDTO import PostDTO, PostEncoder
from dtos.userDTO import UserDTO
from dtos.loginResultDTO import LoginResultDTO
from queryExecutor import QueryExecutor

app = Flask(__name__)

app.config.from_object(Config)
app.config["JWT_SECRET_KEY"] = "super-secret"
jwt = JWTManager(app)

app.config['JSON_AS_ASCII'] = False
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_DB'] = input()
app.config['MYSQL_DATABASE_PASSWORD'] = input()
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['USE_SHA1'] = True
app.config['TOKEN_EXPIRE'] = timedelta(days = 7)
queryExecutor = QueryExecutor(app)

@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + app.config['TOKEN_EXPIRE'])
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        return response

@app.route("/login", methods = ['POST'])
def login() :
   login = request.args.get('login');
   password = request.args.get('password')
   passwordCode = hashlib.sha1(password.encode()) if app.config['USE_SHA1'] else hashlib.md5(password.encode())
   passwordCode = passwordCode.hexdigest()

   record = queryExecutor.loginQuery(login, passwordCode)
   access_token = create_access_token(identity={'login':login, 'password':password})
   result = LoginResultDTO(record['id'], record['username'], record['password'], access_token)
   return json.dumps(result, ensure_ascii=False, indent=4, cls=PostEncoder)



@app.route("/get_all_posts/", methods =['GET'])
@jwt_required()
def get_all_posts() :
    result = queryExecutor.allPostQuery()
    user=get_jwt_identity()
    print(user)
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