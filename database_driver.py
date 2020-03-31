import sqlite3
from sqlite3 import Error
 
class database:
    def __init__(self, db_file):
        self.db_file = db_file

    def create_connection(self):
        """ create a database connection to a SQLite database """
        self.conn = None
        try:
            self.conn = sqlite3.connect(self.db_file)
            return self.conn
        except Error as e:
            print(e)
     
        return self.conn
     
    def create_table(self, create_table_sql):
        """ create a table from the create_table_sql statement
        :param conn: Connection object
        :param create_table_sql: a CREATE TABLE statement
        :return:
        """
        try:
            conn = self.create_connection()
            c = conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)

    def execute_query(self, query_sql, query_params):
        try:
            conn = self.create_connection()
            curs = conn.cursor()
            curs.execute(query_sql, query_params)
            conn.commit()
            conn.close()
        except Error as e:
            print(e)

    def select(self, query_sql, query_params = ''):
        try:
            conn = self.create_connection()
            curs = conn.cursor()
            curs.execute(query_sql, query_params)
            rows = curs.fetchall()
            conn.close()
        except Error as e:
            print(e)

        return rows