import sqlite3
import pymysql

class PMySQL:
    def __init__(self):
        self.connected = 0
        self._connection = None
        self._cursor = None
        self._results = []
        self._fields = []
        self._current_row_index = -1
        
        # IDE Design-Time Properties
        self.left = 0
        self.top = 0
        self.width = 32
        self.height = 32
        
        # Simulated properties
        self.dbcount = 0
        self.colcount = 0
        self.fieldcount = 0
        self.rowcount = 0
        self.tablecount = 0
        self._db_list = []
        self._table_list = []
        
        # Event callbacks
        self._onconnect = None
        self._ondisconnect = None
        self._onerror = None
        self._onquerydone = None

    @property
    def onconnect(self): return self._onconnect
    @onconnect.setter
    def onconnect(self, v): self._onconnect = v

    @property
    def ondisconnect(self): return self._ondisconnect
    @ondisconnect.setter
    def ondisconnect(self, v): self._ondisconnect = v

    @property
    def onerror(self): return self._onerror
    @onerror.setter
    def onerror(self, v): self._onerror = v

    @property
    def onquerydone(self): return self._onquerydone
    @onquerydone.setter
    def onquerydone(self, v): self._onquerydone = v
        
    def db(self, index):
        if 0 <= index < self.dbcount:
            return self._db_list[index]
        return ""
        
    def table(self, index):
        if 0 <= index < self.tablecount:
            return self._table_list[index]
        return ""
        
        # Sub-property simulation for Field.*
        class FieldProps:
            def __init__(self):
                self.name = ""
                self.type = 0
                self.length = 0
                self.decimals = 0
                self.flags = 0
                self.maxlength = 0
                self.table = ""
        self.field = FieldProps()
        
    def connect(self, host=None, user=None, passwd=None, db="", port=None, unixsock="", flags=0):
        host = host if host is not None else getattr(self, 'host', 'localhost')
        user = user if user is not None else getattr(self, 'user', '')
        passwd = passwd if passwd is not None else getattr(self, 'password', '')
        port = port if port is not None else getattr(self, 'port', 3306)
        
        try:
            connect_kwargs = {
                'host': host,
                'user': user,
                'password': passwd,
                'port': port
            }
            if db:
                connect_kwargs['database'] = db
                
            self._connection = pymysql.connect(**connect_kwargs)
            self.connected = 1
            if self._onconnect:
                self._onconnect()
            
            # Fetch databases to populate DB and DBCount
            self._cursor = self._connection.cursor()
            self._cursor.execute("SHOW DATABASES")
            dbs = self._cursor.fetchall()
            self._db_list = [d[0] for d in dbs]
            self.dbcount = len(self._db_list)
            
            if db:
                self.selectdb(db)
                
            return 1
        except Exception as e:
            print(f"PMySQL Connect Error: {e}")
            self.connected = 0
            if self._onerror:
                self._onerror(str(e))
            return 0

    def open(self, host=None, user=None, passwd=None, db="", port=None, unixsock="", flags=0):
        return self.connect(host, user, passwd, db, port)

    def close(self):
        if self._connection:
             self._connection.close()
        self.connected = 0
        self._connection = None
        self._cursor = None
        if self._ondisconnect:
            self._ondisconnect()

    def selectdb(self, db_name):
        if not self._connection: return 0
        try:
            self._connection.select_db(db_name)
            # Fetch tables to populate Table and TableCount
            self._cursor.execute("SHOW TABLES")
            tables = self._cursor.fetchall()
            self._table_list = [t[0] for t in tables]
            self.tablecount = len(self._table_list)
            return 1
        except Exception as e:
            print(f"PMySQL SelectDB Error: {e}")
            return 0

    def createdb(self, db_name):
         if not self._cursor: return 0
         try:
             self._cursor.execute(f"CREATE DATABASE {db_name}")
             return 1
         except:
             return 0
             
    def dropdb(self, db_name):
         if not self._cursor: return 0
         try:
             self._cursor.execute(f"DROP DATABASE {db_name}")
             return 1
         except:
             return 0

    def query(self, query_str):
        if not self._cursor: return 0
        try:
            self._cursor.execute(query_str)
            self._results = self._cursor.fetchall()
            self.rowcount = len(self._results)
            self._fields = self._cursor.description if self._cursor.description else []
            self.colcount = len(self._fields)
            self.fieldcount = self.colcount
            self._current_row_index = -1
            if self._onquerydone:
                self._onquerydone()
            return 1
        except Exception as e:
            print(f"PMySQL Query Error: {e}")
            if self._onerror:
                self._onerror(str(e))
            return 0

    def fetchrow(self):
        if self._current_row_index + 1 < self.rowcount:
            self._current_row_index += 1
            return 1
        return 0

    def fetchfield(self):
        if not hasattr(self, '_current_field_index'):
             self._current_field_index = -1
             
        if self._current_field_index + 1 < self.fieldcount:
             self._current_field_index += 1
             desc = self._fields[self._current_field_index]
             self.field.name = desc[0]
             self.field.type = desc[1]
             self.field.length = desc[3] if desc[3] else 0
             self.field.decimals = desc[5] if desc[5] else 0
             return 1
        return 0
        
    def fieldseek(self, pos):
         self._current_field_index = pos - 1
         
    def rowseek(self, row):
         if 1 <= row <= self.rowcount:
             self._current_row_index = row - 1

    def row(self, col_index):
        if 0 <= self._current_row_index < self.rowcount and 0 <= col_index < self.colcount:
            val = self._results[self._current_row_index][col_index]
            return str(val) if val is not None else ""
        return ""
        
    def rowblob(self, col_index, length=0):
        if 0 <= self._current_row_index < self.rowcount and 0 <= col_index < self.colcount:
            val = self._results[self._current_row_index][col_index]
            return val if val is not None else b""
        return b""

    def escapestring(self, s, length=0):
        return pymysql.converters.escape_string(s)


class PSQLite:

    def __init__(self):
        self._onconnect = None
        self._ondisconnect = None
        self._onerror = None
        self._onquerydone = None

    @property
    def onconnect(self): return self._onconnect
    @onconnect.setter
    def onconnect(self, v): self._onconnect = v

    @property
    def ondisconnect(self): return self._ondisconnect
    @ondisconnect.setter
    def ondisconnect(self, v): self._ondisconnect = v

    @property
    def onerror(self): return self._onerror
    @onerror.setter
    def onerror(self, v): self._onerror = v

    @property
    def onquerydone(self): return self._onquerydone
    @onquerydone.setter
    def onquerydone(self, v): self._onquerydone = v
        
    def connect(self, db_file=None):
        db_file = db_file if db_file is not None else getattr(self, 'db', '')
        if isinstance(db_file, list): 
             db_file = db_file[0] if db_file else ""
             
        try:
            self._connection = sqlite3.connect(db_file)
            self.connected = 1
            self._cursor = self._connection.cursor()
            
            self._cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = self._cursor.fetchall()
            self.table = [t[0] for t in tables]
            self.tablecount = len(self.table)
            self.db = [db_file]
            self.dbcount = 1
            if self._onconnect:
                self._onconnect()
            
            return 1
        except Exception as e:
            print(f"PSQLite Connect Error: {e}")
            self.connected = 0
            if self._onerror:
                self._onerror(str(e))
            return 0
            
    def close(self):
        if self._connection:
             self._connection.close()
        self.connected = 0
        self._connection = None
        self._cursor = None
        if self._ondisconnect:
            self._ondisconnect()

    def query(self, query_str):
        if not self._cursor: return 0
        try:
            self._cursor.execute(query_str)
            self._results = self._cursor.fetchall()
            self.rowcount = len(self._results)
            self._fields = self._cursor.description if self._cursor.description else []
            self.colcount = len(self._fields)
            self.fieldcount = self.colcount
            self._current_row_index = -1
            if query_str.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
                self._connection.commit()
            if self._onquerydone:
                self._onquerydone()
            return 1
        except Exception as e:
            print(f"PSQLite Query Error: {e}")
            if self._onerror:
                self._onerror(str(e))
            return 0

    def fetchrow(self):
        if self._current_row_index + 1 < self.rowcount:
            self._current_row_index += 1
            return 1
        return 0

    def fetchfield(self):
        if not hasattr(self, '_current_field_index'):
             self._current_field_index = -1
             
        if self._current_field_index + 1 < self.fieldcount:
             self._current_field_index += 1
             desc = self._fields[self._current_field_index]
             self.field.name = desc[0]
             return 1
        return 0
        
    def fieldseek(self, pos):
         self._current_field_index = pos - 1
         
    def rowseek(self, row):
         if 1 <= row <= self.rowcount:
             self._current_row_index = row - 1

    def row(self, col_index):
        if 0 <= self._current_row_index < self.rowcount and 0 <= col_index < self.colcount:
            val = self._results[self._current_row_index][col_index]
            return str(val) if val is not None else ""
        return ""
