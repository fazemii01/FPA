import sys
import sqlalchemy as sa
from app.db.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

def ensure_postgresql_enum(db):
    if db.bind.dialect.name == "postgresql":
        try:
            query = sa.text(
                "SELECT 1 FROM pg_type t "
                "JOIN pg_enum e ON t.oid = e.enumtypid "
                "WHERE t.typname = 'userrole' AND e.enumlabel = 'admin_pusat'"
            )
            result = db.execute(query).first()
            if not result:
                print("PostgreSQL 'userrole' enum does not contain 'admin_pusat'. Adding it...")
                connection = db.bind.connect().execution_options(isolation_level="AUTOCOMMIT")
                connection.execution_options(autocommit=True)
                connection.execute(sa.text("ALTER TYPE userrole ADD VALUE 'admin_pusat'"))
                print("Successfully added 'admin_pusat' to 'userrole' enum type.")
        except Exception as e:
            print(f"Warning: Could not alter enum type: {e}. If it already exists, you can ignore this.")

def seed_admin_pusat(email: str, password: str, full_name: str):
    db = SessionLocal()
    try:
        ensure_postgresql_enum(db)

        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"User '{email}' already exists. Promoting role to ADMIN_PUSAT...")
            existing.role = UserRole.ADMIN_PUSAT
            db.commit()
            print(f"User '{email}' has been successfully promoted to ADMIN_PUSAT!")
            return
        
        hashed_password = get_password_hash(password)
        admin_pusat = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=UserRole.ADMIN_PUSAT,
            is_active=True
        )
        db.add(admin_pusat)
        db.commit()
        print(f"Admin Pusat account successfully created!")
        print(f"Email: {email}")
        print(f"Password: {password}")
    except Exception as e:
        print(f"Error seeding admin pusat: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    email = "pusat@alliago.id"
    password = "Alliapusat@1"
    full_name = "Admin Pusat"
    
    if len(sys.argv) > 1:
        email = sys.argv[1]
    if len(sys.argv) > 2:
        password = sys.argv[2]
    if len(sys.argv) > 3:
        full_name = sys.argv[3]
        
    seed_admin_pusat(email, password, full_name)
