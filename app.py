from datetime import timedelta

from flask import Flask, request
from config import Config
import json
import hashlib
import base64

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

from postDTO import PostDTO, PostEncoder, ShortPostDTO
from userDTO import UserDTO
from eventDTO import EventDTO
from loginResultDTO import LoginResultDTO
from queryExecutor import QueryExecutor

application = Flask(__name__)

application.config.from_object(Config)
application.config["JWT_SECRET_KEY"] = "super-secret"
jwt = JWTManager(application)

application.config['JSON_AS_ASCII'] = False
application.config['JWT_TOKEN_LOCATION'] = ['headers', 'query_string']
application.config['MYSQL_DATABASE_USER'] = 'root'
application.config['MYSQL_DATABASE_DB'] = 'motovrn'
application.config['MYSQL_DATABASE_PASSWORD'] = 'Sa230200'
application.config['MYSQL_DATABASE_HOST'] = 'localhost'
application.config['USE_SHA1'] = True
application.config['TOKEN_EXPIRE'] = timedelta(days = 7)
queryExecutor = QueryExecutor(application, application.config['MYSQL_DATABASE_DB'])

@application.route("/login", methods = ['POST'])
def login() :
   request_data = request.get_json()

   login = request_data['login']
   password = request_data['password']
   if login == "" or password == "":
       return "empty login and password", 401
   passwordCode = hashlib.sha1(password.encode()) if application.config['USE_SHA1'] else hashlib.md5(password.encode())
   passwordCode = passwordCode.hexdigest()
   record = queryExecutor.loginQuery(login, passwordCode)
   if record is None:
       return "wrong data", 401
   exp = timedelta(days=7)
   access_token = create_access_token(identity = login, expires_delta=exp)
   result = LoginResultDTO(record['id'], record['username'], record['password'], access_token)
   return json.dumps(result, ensure_ascii=False, indent=4, cls=PostEncoder)



@application.route("/get_all_dalnoboy/<int:fromIndex>", methods =['GET'], endpoint = "get_all_posts")
@jwt_required
def get_all_posts(fromIndex) :
    get_jwt_identity()
    result = queryExecutor.allPostQuery(fromIndex, 20)
    return serialize_posts(result)

@application.route("/get_all_news/<int:fromIndex>" , methods = ['GET'], endpoint = "get_all_news")
@jwt_required
def get_all_news(fromIndex):
    get_jwt_identity()
    result = queryExecutor.allNewsQuery(fromIndex, 20)
    return serialize_posts(result)

@application.route("/get_all_short_posts_dalnoboy/<int:fromIndex>", methods =['GET'], endpoint = "get_all_short_posts_dalnoboy")
@jwt_required
def get_all_short_posts_dalnoboy(fromIndex):
    get_jwt_identity()
    result = queryExecutor.shortPostInfoQuery(fromIndex, 20)
    return serialize_short_posts(result)

@application.route("/get_message_from_post/<int:postId>", methods =['GET'], endpoint = "get_message_from_post")
@jwt_required
def get_message_from_post(postId):
    get_jwt_identity()
    result = queryExecutor.messageFromPostQuery(postId)
    print(result)
    return result

@application.route("/get_all_events/", methods =['GET'], endpoint = "get_all_events")
@jwt_required
def get_all_events():
    get_jwt_identity()
    result = queryExecutor.allEvents()
    return serialize_events(result)

def serialize_posts(records):
    result = []
    for record in records:
        result.append(PostDTO(record['subject'], record['message'], UserDTO(record['poster_id'], record['poster']), record['posted']))
    return json.dumps(result, ensure_ascii=False, indent=4, cls=PostEncoder)


def serialize_short_posts(records):
    result = []
    for record in records:
        result.append(ShortPostDTO(record['id'], record['subject'], UserDTO(record['poster_id'], record['poster']), record['posted']))
    return json.dumps(result, ensure_ascii=False, indent=4, cls=PostEncoder)

def serialize_events(records):
    result = []
    for record in records:
        result.append(EventDTO(record['id'], record['subject']))
    return json.dumps(result, ensure_ascii=False, indent=4, cls=PostEncoder)

def generate_token(login, password) :
    tokenString = login + password
    message_bytes = tokenString.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    return base64_message


#CGIHandler().run(application)