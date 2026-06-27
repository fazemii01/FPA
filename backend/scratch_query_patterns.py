import sqlite3

def main():
    try:
        conn = sqlite3.connect("test.db")
        cursor = conn.cursor()
        
        # Check table schema and contents
        print("Checking fingerprint features in the database...")
        
        # Get table list first
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables: {tables}")
        
        # Query features if the table exists
        if "fingerprint_features" in tables:
            cursor.execute("""
                SELECT ff.id, ff.pattern_type, ff.ridge_count, f.finger_position, f.scan_session_id
                FROM fingerprint_features ff
                JOIN fingerprints f ON ff.fingerprint_id = f.id;
            """)
            rows = cursor.fetchall()
            print(f"Total features in database: {len(rows)}")
            
            # Count patterns
            patterns = {}
            for r in rows:
                ptype = r[1]
                patterns[ptype] = patterns.get(ptype, 0) + 1
            print("Pattern type counts:")
            for p, count in patterns.items():
                print(f"  {p}: {count}")
                
            print("\nSample rows:")
            for r in rows[:15]:
                print(f"  ID: {r[0]} | Pattern: {r[1]} | Ridge Count: {r[2]} | Finger: {r[3]} | Session ID: {r[4]}")
        else:
            print("Table 'fingerprint_features' does not exist in the database.")
            
        conn.close()
    except Exception as e:
        print(f"Error querying database: {e}")

if __name__ == "__main__":
    main()
