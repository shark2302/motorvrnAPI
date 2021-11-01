from dtos import userDTO
import json
from json import JSONEncoder
class PostDTO:
    def __init__(self, id, user, message):
        self.id = id
        self.user = user
        self.message = message

class PostEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__