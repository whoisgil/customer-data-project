import pymysql
import pymysql.cursors


class DB_Connect():
    """A class for connecting to a database and running parameterized queries safely."""

    def __init__(self, passed_db_username, passed_db_password, passed_database):
        """Stores the database credentials and prepares the connection."""

        self.db_username = passed_db_username
        self.db_password = passed_db_password
        self.database = passed_database
        self.conn = None

    def __connect(self):
        """Creates the database connection when it is first needed."""

        self.conn = pymysql.connect(
            host="localhost",
            user=self.db_username,
            password=self.db_password,
            db=self.database,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )

    def executeQuery(self, passed_query, passed_params=None):
        """Executes an INSERT, UPDATE, or DELETE query."""

        if not self.conn:
            self.__connect()

        with self.conn.cursor() as cursor:
            cursor.execute(passed_query, passed_params)

    def executeManyQuery(self, passed_query, passed_param_list):
        """Executes the same query for multiple sets of parameters."""

        if not self.conn:
            self.__connect()

        with self.conn.cursor() as cursor:
            cursor.executemany(passed_query, passed_param_list)

    def executeSelectQuery(self, passed_query, passed_params=None):
        """Executes a SELECT query and returns the results."""

        if not self.conn:
            self.__connect()

        with self.conn.cursor() as cursor:
            cursor.execute(passed_query, passed_params)
            return cursor.fetchall()

    def commit(self):
        """Commits the current transaction."""

        if self.conn:
            self.conn.commit()

    def rollback(self):
        """Rolls back the current transaction."""

        if self.conn:
            self.conn.rollback()

    def close_connection(self):
        """Closes the database connection."""

        if self.conn:
            self.conn.close()
            self.conn = None