import os
import sys

# Add backend directory to sys.path so we can import app modules
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.db.database import SessionLocal, engine
from app.models.fingerprint_feature import FingerprintFeature
from app.models.fingerprint import Fingerprint
from sqlalchemy import inspect

def main():
    try:
        # Check if we can connect to the DB
        print("Checking connection to PostgreSQL database...")
        db = SessionLocal()
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"Tables in PostgreSQL database: {tables}")
        
        if "fingerprint_features" in tables:
            features = db.query(FingerprintFeature).all()
            print(f"Total features in database: {len(features)}")
            
            # Count patterns
            patterns = {}
            for f in features:
                ptype = f.pattern_type
                patterns[ptype] = patterns.get(ptype, 0) + 1
            print("Pattern type counts:")
            for p, count in patterns.items():
                print(f"  {p}: {count}")
                
            print("\nSample rows:")
            for f in features[:15]:
                print(f"  ID: {f.id} | Pattern: {f.pattern_type} | Ridge Count: {f.ridge_count} | Quality: {f.quality_score:.2f}% | Session ID: {f.scan_session_id}")
        else:
            print("Table 'fingerprint_features' does not exist in the database.")
            
        db.close()
    except Exception as e:
        print(f"Error querying PostgreSQL database: {e}")

if __name__ == "__main__":
    main()
