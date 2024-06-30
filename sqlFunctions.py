import sqlite3
from sqlite3 import Error


def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
        execute_query(connection, create_users_table)
        execute_query(connection, create_themes_table)
        execute_query(connection, create_books_table)
        execute_query(connection, create_library_table)
        print("Created Tables")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        result = None
        return result


def insert_elements_table(c, table, kwargs):
    keys = kwargs.keys()
    query = "INSERT INTO {} ({}) VALUES (".format(table, ", ".join(keys))
    nbr = len(keys)
    for i, arg in enumerate(kwargs.values()):
        query += "'" + str(arg) + "'"
        if i < nbr-1:
            query += ", "

    query += ");"
    execute_query(c, query)


def get_elements(c, elt, tables, joined=None, wher=None, grp=None):
    """
    SELECT
      description as Post,
      COUNT(likes.id) as Likes
    FROM
      likes,
      posts
    WHERE
      posts.id = likes.post_id
    GROUP BY
      likes.post_id
    """
    if isinstance(elt, dict):
        eltlist = ''
        t = len(elt)
        for i, key in enumerate(elt):
            eltlist += key + '.' + elt[key]
            if i < t-1:
                eltlist += ', '
    elif isinstance(elt, list):
        eltlist = ', '.join(elt)
    elif isinstance(elt, str):
        eltlist = elt

    init = "SELECT {} FROM {}".format(eltlist, ', '.join(tables))
    # tO TEST
    if joined is not None:
        val = ""
        t = len(joined)
        for i, key in enumerate(joined):
            val += "INNER JOIN " + key + " ON " + joined[key]
            if i < t-1:
                val += ', '
        init += val

    if wher is not None:
        val = " WHERE "
        i = 0
        for key in wher:
            if i > 0:
                val += " AND "
            val += key + "='" + str(wher[key]) + "'"
            i += 1
        init += val

    if grp is not None:
        val = " GROUP BY {}".format(grp)
        init += val

    init += ";"
    results = execute_read_query(c, init)

    return results


def update_table_elt(c, table, elt, wher):
    # UPDATE
    # employees
    # SET
    # lastname = 'Smith'
    # WHERE
    # employeeid = 3;
    init = "UPDATE {} SET ".format(table)
    if isinstance(elt, dict):
        eltlist = ''
        t = len(elt)
        for i, key in enumerate(elt):
            value = elt[key]
            if value:
                eltlist += key + "='" + value  + "'"
                if i < t - 1:
                    eltlist += ', '
    if not eltlist:
        return

    init += eltlist

    val = " WHERE "
    i = 0
    for key, item in wher.items():
        if i > 0:
            val += ' AND '
        if isinstance(item, str):
            val += key + "='" + item + "'"
        else:
            val += key + "=" + str(item)
        i += 1
    init += val

    init += ";"
    execute_query(c, init)


def get_header_table(c, table):
    query = "SELECT * FROM {}".format(table)
    cursor = c.execute(query)

    names = [description[0] for description in cursor.description]

    return names



# title, creator, description, publisher, subject
create_users_table = """
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT,
  password TEXT
);
"""

create_themes_table = """
CREATE TABLE IF NOT EXISTS themes (
  subtype TEXT,
  type TEXT
);
"""

create_books_table = """
CREATE TABLE IF NOT EXISTS books (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  theme TEXT,
  author TEXT NOT NULL,
  publisher TEXT,
  series TEXT,
  tome TEXT,
  title TEXT NOT NULL,
  description TEXT,
  language TEXT,
  cover TEXT,
  FOREIGN KEY (theme) REFERENCES theme (subtype)
);
"""

create_library_table = """
CREATE TABLE IF NOT EXISTS library (
  book_id INTEGER,
  rating INTEGER,
  read TEXT,
  user_id INTEGER,
  FOREIGN KEY (book_id) REFERENCES books (id),
  FOREIGN KEY (user_id) REFERENCES users (id)
);
"""
