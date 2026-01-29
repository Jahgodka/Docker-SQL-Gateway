import os
import pyodbc
import json
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

# Wait for the database to start up (Docker container timing)
time.sleep(5)

# Connection string setup using environment variables
conn_str = (
    f"DRIVER={{PostgreSQL Unicode}};"
    f"SERVER={os.environ['DB_HOST']};"
    f"DATABASE={os.environ['DB_NAME']};"
    f"UID={os.environ['DB_USER']};"
    f"PWD={os.environ['DB_PASS']};"
    f"PORT={os.environ['DB_PORT']};"
)

def get_data(query, return_columns=False):
    """
    Executes a SQL query and returns rows.
    Optionally returns column names if return_columns is True.
    """
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute(query)
    
    # Fetch data
    rows = cursor.fetchall()
    
    # Fetch column names
    columns = [desc[0] for desc in cursor.description]
    
    conn.close()
    return (rows, columns) if return_columns else rows

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        # 1. List all tables
        if self.path == '/tables' or self.path == '/':
            try:
                rows = get_data("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                data = [row.table_name for row in rows]
            except Exception as e:
                data = {"error": str(e)}

        # 2. Get schema for a specific table
        elif self.path.startswith('/tables/'):
            table_name = self.path.split('/')[-1]
            try:
                # Note: In a production app, input validation should be added here to prevent SQL Injection
                query = f"""
                    SELECT column_name, data_type
                    FROM information_schema.columns 
                    WHERE table_schema = 'public' AND table_name = '{table_name}'
                    ORDER BY ordinal_position
                    """
                rows = get_data(query)
                if not rows:
                    data = {"error": "Table not found"}
                else:
                    data = {
                        "table": table_name,
                        "columns": [
                            {"name": row.column_name, "type": row.data_type} 
                            for row in rows]
                    }
            except Exception as e:
                data = {"error": str(e)}

        # 3. List all columns from all tables
        elif self.path == '/columns':
            try:
                rows = get_data("""
                    SELECT table_name, column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    ORDER BY table_name, ordinal_position
                """)
                data = {}
                for row in rows:
                    data.setdefault(row.table_name, []).append({
                        "column": row.column_name,
                        "type": row.data_type
                    })
            except Exception as e:
                data = {"error": str(e)}

        # 4. Get columns for a specific table
        elif self.path.startswith('/columns/'):
            table_name = self.path.split('/')[-1]
            try:
                query = f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_schema = 'public' AND table_name = '{table_name}'
                    ORDER BY ordinal_position
                """
                rows = get_data(query)
                if not rows:
                    data = {"error": "Table not found"}
                else:
                    data = [{"column": row.column_name, "type": row.data_type} 
                            for row in rows]
            except Exception as e:
                data = {"error": str(e)}
        
        # 5. Get all rows from all tables
        elif self.path == '/rows':
            data = {}
            try:
                tables = get_data("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                for row in tables:
                    table_name = row.table_name
                    query = f"SELECT * FROM {table_name}"
                    rows, columns = get_data(query, return_columns=True)
                    data[table_name] = [dict(zip(columns, r)) for r in rows]
            except Exception as e:
                data = {"error": str(e)}

        # 6. Get rows for a specific table
        elif self.path.startswith('/rows/'):
            table_name = self.path.split('/')[-1]
            try:
                query = f"SELECT * FROM {table_name}"
                rows, columns = get_data(query, return_columns=True)
                data = [dict(zip(columns, r)) for r in rows]
            except Exception as e:
                data = {"error": str(e)}

        else:
            data = {"error": "Endpoint not found. Try /tables, /columns, or /rows"}

        # Return JSON response (default=str handles Date objects)
        self.wfile.write(json.dumps(data, default=str).encode('utf-8'))

if __name__ == '__main__':
    server = HTTPServer(('', 8080), RequestHandler)
    print("HTTP Server running on port 8080...")
    server.serve_forever()