from flaskext.mysql import MySQL

class QueryExecutor:


    LOGIN_QUERY ="""SELECT * FROM motovrn.mv2_users where username = \"{}\" 
               and password =\"{}\";"""

    ALL_POSTS_QUERY = """SELECT * FROM motovrn.mv2_posts, motovrn.mv2_topics, motovrn.mv2_forums
        where topic_id = mv2_topics.id and mv2_topics.forum_id = 1 LIMIT 20;"""

    def __init__(self, app):
        mysql = MySQL()
        mysql.init_app(app)
        self.conn = mysql.connect()
        self.cursor = self.conn.cursor()

    def loginQuery(self, login, password):

        self.cursor.execute(self.LOGIN_QUERY.format(login, password))
        columnNames = [column[0] for column in self.cursor.description]
        print(columnNames)
        return dict(zip(columnNames, self.cursor.fetchall()[0]))

    def allPostQuery(self):
        self.cursor.execute(self.ALL_POSTS_QUERY)
        columnNames = [column[0] for column in self.cursor.description]
        result = []
        for record in self.cursor.fetchall():
            result.append(dict(zip(columnNames, record)))
        return result

    def __del__(self):
        self.conn.close()