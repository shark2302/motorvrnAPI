from flaskext.mysql import MySQL

class QueryExecutor:


    LOGIN_QUERY ="""SELECT * FROM {dbName}.mv2_users where username = \"{}\" 
               and password =\"{}\";"""

    POSTS_QUERY = """SELECT mv2_topics.subject, mv2_posts.message, {dbName}.mv2_posts.poster, {dbName}.mv2_posts.poster_id, {dbName}.mv2_posts.posted  FROM {dbName}.mv2_posts, {dbName}.mv2_topics
where {dbName}.mv2_posts.topic_id = mv2_topics.id and mv2_topics.forum_id = {}
and {dbName}.mv2_posts.id = mv2_topics.first_post_id
order by {dbName}.mv2_posts.posted desc limit {}, {}"""

    SHORT_POST_INFO_QUERY = """SELECT mv2_posts.id, mv2_topics.subject, {dbName}.mv2_posts.poster, {dbName}.mv2_posts.poster_id, {dbName}.mv2_posts.posted  FROM {dbName}.mv2_posts, {dbName}.mv2_topics
        where {dbName}.mv2_posts.topic_id = mv2_topics.id and mv2_topics.forum_id = {}
            and {dbName}.mv2_posts.id = mv2_topics.first_post_id
                order by {dbName}.mv2_posts.posted desc limit {}, {} """

    MESSAGE_FROM_POST_QUERY = """SELECT message FROM {dbName}.mv2_posts where id = {};"""

    def __init__(self, app, dbName):
        mysql = MySQL()
        mysql.init_app(app)
        self.conn = mysql.connect()
        self.cursor = self.conn.cursor()
        self.dbName = dbName

    def loginQuery(self, login, password):
        self.cursor.execute(self.LOGIN_QUERY.format(login, password, dbName = self.dbName))
        columnNames = [column[0] for column in self.cursor.description]
        result = self.cursor.fetchall()
        if len(result) == 0:
            return  None
        return dict(zip(columnNames,result[0]))

    def allPostQuery(self, fromIndex, step):
        self.cursor.execute(self.POSTS_QUERY.format( 1, fromIndex, step, dbName = self.dbName))
        columnNames = [column[0] for column in self.cursor.description]
        result = []
        for record in self.cursor.fetchall():
            result.append(dict(zip(columnNames, record)))
        return result

    def allNewsQuery(self, fromIndex, step):
        self.cursor.execute(self.POSTS_QUERY.format(9, fromIndex, step, dbName = self.dbName))
        columnNames = [column[0] for column in self.cursor.description]
        result = []
        for record in self.cursor.fetchall():
            result.append(dict(zip(columnNames, record)))
        return result

    def shortPostInfoQuery(self, fromIndex, step):
        self.cursor.execute(self.SHORT_POST_INFO_QUERY.format( 1, fromIndex, step, dbName = self.dbName))
        columnNames = [column[0] for column in self.cursor.description]
        result = []
        for record in self.cursor.fetchall():
            result.append(dict(zip(columnNames, record)))
        return result

    def messageFromPostQuery(self, postId):
        self.cursor.execute(self.MESSAGE_FROM_POST_QUERY.format(postId, dbName=self.dbName))
        result = self.cursor.fetchall()
        return {'message' : result[0][0]} if len(result) > 0 else {'message' : ''}


    def __del__(self):
        self.conn.close()