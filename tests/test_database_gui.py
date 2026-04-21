"""Test database integration with GUI components for real-world database apps."""
import unittest
import sys
import os
import tempfile
import sqlite3

sys.path.insert(0, '/workspace')

from rp_runtime.database import PSQLite
from rp_runtime.gui import PForm, PListView, PStringGrid


class TestDatabaseGUIIntegration(unittest.TestCase):
    """Test that database and GUI components work together for database apps."""
    
    def setUp(self):
        """Create a temporary SQLite database for testing."""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        self.db_path = self.temp_db.name
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                age INTEGER
            )
        ''')
        
        test_users = [
            (1, 'John Doe', 'john@example.com', 30),
            (2, 'Jane Smith', 'jane@example.com', 25),
            (3, 'Bob Johnson', 'bob@example.com', 35),
            (4, 'Alice Brown', 'alice@example.com', 28),
            (5, 'Charlie Wilson', 'charlie@example.com', 42)
        ]
        cursor.executemany('INSERT INTO users VALUES (?, ?, ?, ?)', test_users)
        
        cursor.execute('''
            CREATE TABLE products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL,
                quantity INTEGER
            )
        ''')
        
        test_products = [
            (1, 'Laptop', 999.99, 10),
            (2, 'Mouse', 29.99, 50),
            (3, 'Keyboard', 79.99, 30)
        ]
        cursor.executemany('INSERT INTO products VALUES (?, ?, ?, ?)', test_products)
        
        conn.commit()
        conn.close()
        
        self.db = PSQLite()
        self.db.connect(self.db_path)
    
    def tearDown(self):
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
        if hasattr(self, 'db') and self.db:
            try:
                self.db.close()
            except:
                pass
    
    def test_database_connection(self):
        """Test that database connects successfully."""
        self.assertEqual(self.db.connected, 1)
        self.assertGreater(self.db.tablecount, 0)
    
    def test_database_query(self):
        """Test basic query execution."""
        result = self.db.query("SELECT * FROM users")
        self.assertEqual(result, 1)
        self.assertEqual(self.db.rowcount, 5)
        self.assertEqual(self.db.colcount, 4)
    
    def test_fetch_rows(self):
        """Test fetching rows from query results."""
        self.db.query("SELECT * FROM users")
        
        rows = []
        while self.db.fetchrow():
            row_data = {
                'id': self.db.row(0),
                'name': self.db.row(1),
                'email': self.db.row(2),
                'age': self.db.row(3)
            }
            rows.append(row_data)
        
        self.assertEqual(len(rows), 5)
        self.assertEqual(rows[0]['name'], 'John Doe')
        self.assertEqual(rows[2]['email'], 'bob@example.com')
    
    def test_listview_populate_from_database(self):
        """Test populating a PListView with database query results."""
        form = PForm()
        listview = PListView(form)
        
        listview.clear()
        listview.widget['columns'] = ()
        listview._columns = []
        
        listview.addcolumn('ID', 50)
        listview.addcolumn('Name', 150)
        listview.addcolumn('Email', 200)
        listview.addcolumn('Age', 50)
        
        self.db.query("SELECT * FROM users ORDER BY id")
        
        while self.db.fetchrow():
            listview.additem(
                self.db.row(0),
                self.db.row(1),
                self.db.row(2),
                self.db.row(3)
            )
        
        self.assertEqual(listview.itemcount, 5)
        self.assertEqual(listview.getitem(0)[0], '1')
        self.assertEqual(listview.getitem(0)[1], 'John Doe')
        self.assertEqual(listview.getitem(4)[3], '42')
        
        form.close()
    
    def test_listview_column_operations(self):
        """Test listview column manipulation."""
        form = PForm()
        listview = PListView(form)
        
        listview.clear()
        listview.widget['columns'] = ()
        listview._columns = []
        
        col1 = listview.addcolumn('First', 100)
        col2 = listview.addcolumn('Second', 150)
        col3 = listview.addcolumn('Third', 200)
        
        self.assertEqual(col1, 0)
        self.assertEqual(col2, 1)
        self.assertEqual(col3, 2)
        
        listview.setcolumnwidth(0, 120)
        listview.setcolumnwidth(1, 180)
        
        listview.setcolumntext(0, 'Updated First')
        listview.setcolumntext(2, 'Updated Third')
        
        listview.additem('A1', 'B1', 'C1')
        listview.additem('A2', 'B2', 'C2')
        
        self.assertEqual(listview.itemcount, 2)
        
        form.close()
    
    def test_listview_selection(self):
        """Test listview selection operations."""
        form = PForm()
        listview = PListView(form)
        
        listview.clear()
        listview.widget['columns'] = ()
        listview._columns = []
        listview.addcolumn('Item', 100)
        
        for i in range(5):
            listview.additem(f'Item {i}')
        
        listview.selectedindex = 2
        self.assertEqual(listview.selectedindex, 2)
        
        form.close()
    
    def test_listview_insert_delete(self):
        """Test inserting and deleting listview items."""
        form = PForm()
        listview = PListView(form)
        
        listview.clear()
        listview.widget['columns'] = ()
        listview._columns = []
        listview.addcolumn('Value', 100)
        
        listview.additem('First')
        listview.additem('Second')
        listview.additem('Fourth')
        
        listview.insertitem(2, 'Third')
        
        self.assertEqual(listview.itemcount, 4)
        self.assertEqual(listview.getitem(2)[0], 'Third')
        
        listview.deleteitem(1)
        self.assertEqual(listview.itemcount, 3)
        self.assertEqual(listview.getitem(1)[0], 'Third')
        
        listview.clear()
        self.assertEqual(listview.itemcount, 0)
        
        form.close()
    
    def test_stringgrid_operations(self):
        """Test PStringGrid for data display."""
        form = PForm()
        grid = PStringGrid(form)
        
        grid.cols = 3
        
        grid.addrow('Row1-Col1', 'Row1-Col2', 'Row1-Col3')
        grid.addrow('Row2-Col1', 'Row2-Col2', 'Row2-Col3')
        grid.addrow('Row3-Col1', 'Row3-Col2', 'Row3-Col3')
        
        self.assertEqual(grid.rows, 3)
        
        form.close()
    
    def test_database_field_properties(self):
        """Test database field metadata access."""
        self.db.query("SELECT * FROM products")
        
        fields = []
        while self.db.fetchfield():
            fields.append(self.db.field.name)
        
        self.assertEqual(len(fields), 4)
        self.assertIn('id', fields)
        self.assertIn('name', fields)
        self.assertIn('price', fields)
    
    def test_rowseek_operations(self):
        """Test row navigation in database results."""
        self.db.query("SELECT * FROM users ORDER BY id")
        
        self.db.rowseek(3)
        self.assertTrue(self.db.fetchrow())
        self.assertEqual(self.db.row(1), 'Bob Johnson')
        
        self.db.rowseek(0)
        self.assertTrue(self.db.fetchrow())
        self.assertEqual(self.db.row(1), 'John Doe')
    
    def test_complex_query_with_joins(self):
        """Test complex queries suitable for real-world apps."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                product_id INTEGER,
                quantity INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        ''')
        cursor.execute("INSERT INTO orders VALUES (1, 1, 1, 2)")
        cursor.execute("INSERT INTO orders VALUES (2, 2, 2, 5)")
        cursor.execute("INSERT INTO orders VALUES (3, 1, 3, 1)")
        conn.commit()
        conn.close()
        
        self.db.close()
        self.db.connect(self.db_path)
        
        query = """
            SELECT u.name, p.name as product, o.quantity
            FROM orders o
            JOIN users u ON o.user_id = u.id
            JOIN products p ON o.product_id = p.id
        """
        result = self.db.query(query)
        self.assertEqual(result, 1)
        self.assertEqual(self.db.rowcount, 3)
        
        rows = []
        while self.db.fetchrow():
            rows.append((self.db.row(0), self.db.row(1), self.db.row(2)))
        
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0][0], 'John Doe')
        self.assertEqual(rows[0][1], 'Laptop')
    
    def test_update_query(self):
        """Test UPDATE queries for data modification."""
        self.db.query("UPDATE users SET age = 31 WHERE name = 'John Doe'")
        self.db.query("SELECT age FROM users WHERE name = 'John Doe'")
        
        if self.db.fetchrow():
            age = self.db.row(0)
            self.assertEqual(age, '31')
    
    def test_delete_query(self):
        """Test DELETE queries."""
        self.db.query("SELECT * FROM users")
        initial_count = self.db.rowcount
        
        self.db.query("DELETE FROM users WHERE id = 5")
        
        self.db.query("SELECT * FROM users")
        self.assertEqual(self.db.rowcount, initial_count - 1)


class TestDatabaseRobustness(unittest.TestCase):
    """Test database component robustness for production use."""
    
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        self.db_path = self.temp_db.name
        self.db = PSQLite()
    
    def tearDown(self):
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
        if hasattr(self, 'db') and self.db:
            try:
                self.db.close()
            except:
                pass
    
    def test_error_handling_invalid_query(self):
        """Test that invalid queries are handled gracefully."""
        self.db.connect(self.db_path)
        self.db.query("CREATE TABLE test (id INTEGER)")
        
        error_caught = False
        def on_error(msg):
            nonlocal error_caught
            error_caught = True
        
        self.db.onerror = on_error
        result = self.db.query("INVALID SQL QUERY")
        
        self.assertEqual(result, 0)
        self.assertTrue(error_caught)
    
    def test_transaction_commit(self):
        """Test that transactions are committed properly."""
        self.db.connect(self.db_path)
        self.db.query("CREATE TABLE test (id INTEGER, value TEXT)")
        
        self.db.query("INSERT INTO test VALUES (1, 'test1')")
        self.db.query("INSERT INTO test VALUES (2, 'test2')")
        
        self.db.close()
        self.db.connect(self.db_path)
        
        self.db.query("SELECT COUNT(*) FROM test")
        if self.db.fetchrow():
            count = int(self.db.row(0))
            self.assertEqual(count, 2)
    
    def test_null_value_handling(self):
        """Test handling of NULL values in database."""
        self.db.connect(self.db_path)
        self.db.query("CREATE TABLE test (id INTEGER, value TEXT)")
        self.db.query("INSERT INTO test VALUES (1, NULL)")
        self.db.query("INSERT INTO test VALUES (2, 'not null')")
        
        self.db.query("SELECT * FROM test ORDER BY id")
        
        self.assertTrue(self.db.fetchrow())
        val1 = self.db.row(1)
        self.assertEqual(val1, "")
        
        self.assertTrue(self.db.fetchrow())
        val2 = self.db.row(1)
        self.assertEqual(val2, "not null")
    
    def test_large_result_set(self):
        """Test handling of large result sets."""
        self.db.connect(self.db_path)
        self.db.query("CREATE TABLE large_test (id INTEGER, value TEXT)")
        
        for i in range(1000):
            self.db.query(f"INSERT INTO large_test VALUES ({i}, 'value_{i}')")
        
        self.db.query("SELECT * FROM large_test")
        self.assertEqual(self.db.rowcount, 1000)
        
        count = 0
        while self.db.fetchrow():
            count += 1
        
        self.assertEqual(count, 1000)


if __name__ == '__main__':
    unittest.main(verbosity=2)
