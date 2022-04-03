from json import JSONEncoder
class PostDTO:
    def __init__(self, title, message, user, date):
        self.title = title
        self.message = message
        self.user = user
        self.data = date

class ShortPostDTO:
    def __init__(self, title, user, date):
        self.title = title
        self.user = user
        self.data = date

class PostEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
