# We should need only mysql for the backend (model)
import mysql.connector as mysql
from mysql.connector import ProgrammingError,OperationalError


# TODO: use this decorator to wrap commit/rollback in a try/except block ?
# see http://www.kylev.com/2009/05/22/python-decorators-and-database-idioms/
def connect(func):
    def inner_func(conn, *args, **kwargs):
        if (conn == None):
            conn = connect_to_db()
        return func(conn, *args, **kwargs)
    return inner_func

def connect_to_db():
    print('New connection to MySQL DB...')
    connection = mysql.connect(host="localhost",user="root",password="1234",database="endnote")
    return connection

def disconnect_from_db(conn=None):
    if conn is not None:
        conn.close()
        print('... connection to MySQL DB closed')

# Execute a SQL statement and commit it if we are doing a write
@connect
def executeSQL(conn, sql, read = True):
    cursor = conn.cursor()
    cursor.execute(sql)
    if not read:
        conn.commit()  
        rows = None
    else:
        rows = cursor.fetchall()
    return rows

# If we can't insert we raise an exception
@connect
def mySQLinsert(conn, filename, filepath):
    if filename == "" or filepath == "":
        raise Exception('INSERT STATUS: filename and filepath required')
    else:
        cursor = conn.cursor()
        cursor.execute("insert into pdf (filename,filepath) values('" + filename +"','" + filepath +"')")
        cursor.execute("commit")
        conn.close()

@connect
def mySQLdelete(conn, id):
    if (id == ""):
        raise Exception('DELETE STATUS: ID is compolsary for del')
    else:
        executeSQL(conn, "delete from pdf where idpdf = '" + id +"'", read=False)

# Update the id field with value varAll
@connect
def mySQLupdate(conn, id, varAll):
    # We only update bit fields for now, because we assume that the set
    # table of PDF files is relatively stable

    # In order to update we need at least the ID
    if id != "":
        executeSQL(conn, "update pdf set flags = " + str(varAll) +  " where idpdf = '" + id + "'", read=False)
    else:
        raise Exception('UPDATE STATUS: id required')

@connect
def getFromId(conn, id):
    if (id != ""):
        rows = executeSQL(conn, "select * from pdf where idpdf = '" + id +"'")
        if (len(rows) == 1):
            return rows
        else:
            raise Exception('GET FROM ID STATUS: no records found with ID')
    else:
        raise Exception('GET FROM ID STATUS: ID empty')

@connect
def getFromFlags(conn, varAll):
    rows = executeSQL(conn, "SELECT * FROM endnote.pdf WHERE (flags & " + str(varAll) + ") = " + str(varAll))
    return rows

@connect
def getFromKeywords(conn, keywords, varAll, retAll):
    if (len(keywords) > 0):
         # Piece together the SQL REGEX query string
        sql = "^"
        for keyword in keywords[:-1]:
            sql += (keyword + "[[:blank:][:graph:]]*")
        sql += keywords[-1]
        if retAll == 1:
            rows = executeSQL(conn, "SELECT * FROM endnote.pdf WHERE filename REGEXP '" + sql +"'")
        else:
            rows = executeSQL(conn, "SELECT * FROM endnote.pdf WHERE filename REGEXP '" + sql +"' and (flags & " + str(varAll) + ") = " + str(varAll))
        return rows
    else:
        raise Exception("GET STATUS: no keywords supplied keywords")

@connect
def getFromFilepath(conn, filepath, varAll, retAll):
    if (filepath != ""):
        # Then piece together the SQL substring query
        if retAll == 1:
            rows = executeSQL(conn, "select * from endnote.pdf where filepath like '" + filepath + "%'")
        else:
            rows = executeSQL(conn, "select * from endnote.pdf where filepath like '" + filepath + "%' and (flags & " + str(varAll) + ") = " + str(varAll))
        return rows
    else:
        raise Exception("GET STATUS: filepath is empty")

@connect
def mySQLgetSelected(conn, filename):
    if (filename != ""):
        rows = executeSQL(conn, "SELECT * FROM endnote.pdf WHERE filename = '" + filename +"'")
        return rows
    else:
        raise Exception('GET SELECTED STATUS: filename is empty')

# update the numbers for rows that have newly got the status printed
@connect
def updateNumbers(conn):
    MaxNumber = executeSQL(conn, "select max(number) from endnote.pdf where flags & b'100000' != 0")
    if (len(MaxNumber) == 1):
        max = 1 if MaxNumber[0][0] == None else int(MaxNumber[0][0])
        rows = executeSQL(conn, "select idpdf from endnote.pdf where flags & b'100000' != 0 and number is NULL")
        rows = [(i, x[0]) for i, x in enumerate(rows, max)]
        cursor = conn.cursor()
        cursor.executemany("UPDATE pdf SET number = %s WHERE idpdf = %s ", rows)
        conn.commit()        
