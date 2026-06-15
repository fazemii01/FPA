import sqlite3

def main():
    try:
        conn = sqlite3.connect("test.db")
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables in database: {tables}")
        
        for table in tables:
            # Get columns
            cursor.execute(f"PRAGMA table_info({table});")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Query rows matching CLICK FINGER or CONSULTING
            for col in columns:
                try:
                    cursor.execute(f"SELECT * FROM {table} WHERE CAST({col} AS TEXT) LIKE '%CLICK%' OR CAST({col} AS TEXT) LIKE '%CONSULTING%';")
                    rows = cursor.fetchall()
                    if rows:
                        print(f"Found match in table '{table}', column '{col}':")
                        for r in rows:
                            print(f"  {r}")
                except Exception as col_err:
                    pass
                    
        conn.close()
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    main()
