"""We should need only mysql for the backend (model)"""
import mysql.connector as mysql

def connect(func):
    """This wrapper function connects to the database if it is not already done
       TODO: use this decorator to wrap commit/rollback in a try/except block ?
       see http://www.kylev.com/2009/05/22/python-decorators-and-database-idioms/"""
    def inner_func(conn, *args, **kwargs):
        if conn is None:
            conn = connect_to_db()
        return func(conn, *args, **kwargs)
    return inner_func

def connect_to_db():
    """Connect with hard wired connect credentials"""
    print('New connection to MySQL DB...')
    connection = mysql.connect( host="localhost",user="root",
                                password="1234",database="endnote")
    return connection

def disconnect_from_db(conn=None):
    """disconnect"""
    if conn is not None:
        conn.close()
        print('... connection to MySQL DB closed')

@connect
def executeSQL(conn, sql, read = True):
    """Execute a SQL statement and commit it if we are doing a write"""
    cursor = conn.cursor()
    cursor.execute(sql)
    if not read:
        conn.commit()
        rows = None
    else:
        rows = cursor.fetchall()
    return rows

@connect
def mySQLinsert(conn, filename, filepath):
    """If we can't insert we raise an exception"""
    if filename == "" or filepath == "":
        raise Exception('INSERT STATUS: filename and filepath required')
    cursor = conn.cursor()
    cursor.execute("insert into pdf (filename,filepath) values('" +
                        filename +"','" + filepath +"')")
    cursor.execute("commit")
    conn.close()

@connect
def mySQLdelete(conn, file_id):
    """given id delete the row in the database"""
    if file_id == "":
        raise Exception('DELETE STATUS: ID is compolsary for del')
    executeSQL(conn, "delete from pdf where idpdf = '" + file_id +"'", read=False)

@connect
def mySQLupdate(conn, file_id, varAll):
    """Update the id field with value varAll"""
    # We only update bit fields for now, because we assume that the set
    # table of PDF files is relatively stable

    # In order to update we need at least the ID
    if file_id != "":
        executeSQL(conn, "update pdf set flags = " + str(varAll) +
                         " where idpdf = '" + file_id + "'", read=False)
    else:
        raise Exception('UPDATE STATUS: id required')

@connect
def get_from_id(conn, file_id):
    """Given id find the corresponding row"""
    if file_id != "":
        rows = executeSQL(conn, "select * from pdf where idpdf = '" + file_id +"'")
        if len(rows) == 1:
            return rows
        raise Exception('GET FROM ID STATUS: no records found with ID')
    raise Exception('GET FROM ID STATUS: ID empty')

@connect
def get_from_flags(conn, varAll):
    """Given flags find the corresponding row"""
    rows = executeSQL(conn, "SELECT * FROM endnote.pdf WHERE (flags & " +
                            str(varAll) + ") = " + str(varAll))
    return rows

@connect
def get_from_keywords(conn, keywords, varAll, retAll):
    """Given keywords find the corresponding rows that contain
       the keywords in the order they appear in the list"""
    if len(keywords) > 0:
         # Piece together the SQL REGEX query string
        sql = "^"
        for keyword in keywords[:-1]:
            sql += (keyword + "[[:blank:][:graph:]]*")
        sql += keywords[-1]
        if retAll == 1:
            rows = executeSQL(conn, "SELECT * FROM endnote.pdf WHERE filename REGEXP '" + sql +"'")
        else:
            rows = executeSQL(conn, "SELECT * FROM endnote.pdf WHERE filename REGEXP '" +
                                    sql +"' and (flags & " + str(varAll) + ") = " + str(varAll))
        return rows
    raise Exception("GET STATUS: no keywords supplied keywords")

@connect
def get_from_filepath(conn, filepath, varAll, retAll):
    """Given a filepath find super strings (subfolders) of it in the filepath field"""
    if filepath != "":
        # Then piece together the SQL substring query
        if retAll == 1:
            rows = executeSQL(conn,
            "select * from endnote.pdf where filepath like '" + filepath + "%'")
        else:
            rows = executeSQL(conn, "select * from endnote.pdf where filepath like '" +
                                    filepath + "%' and (flags & " + str(varAll)
                                    + ") = " + str(varAll))
        return rows
    raise Exception("GET STATUS: filepath is empty")

@connect
def mySQLgetSelected(conn, filename):
    """Given a filename find the row in the database"""
    if filename != "":
        rows = executeSQL(conn, "SELECT * FROM endnote.pdf WHERE filename = '" + filename +"'")
        return rows
    raise Exception('GET SELECTED STATUS: filename is empty')

@connect
def update_numbers(conn):
    """update the numbers for rows that have newly got the status printed"""
    MaxNumber = executeSQL(conn, "select max(number) from endnote.pdf where flags & b'100000' != 0")
    if len(MaxNumber) == 1:
        maxNum = 1 if MaxNumber[0][0] is None else int(MaxNumber[0][0])
        rows = executeSQL(conn, "select idpdf from endnote.pdf where flags"
                                "& b'100000' != 0 and number is NULL")
        rows = [(i, x[0]) for i, x in enumerate(rows, maxNum)]
        cursor = conn.cursor()
        cursor.executemany("UPDATE pdf SET number = %s WHERE idpdf = %s ", rows)
        conn.commit()
