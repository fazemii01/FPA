import sys
import sqlalchemy as sa
from app.db.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

def ensure_postgresql_enum(db):
    # If using PostgreSQL, check and add 'super_admin' to the 'userrole' enum type
    if db.bind.dialect.name == "postgresql":
        try:
            # Query if 'super_admin' exists in pg_enum for typname 'userrole'
            query = sa.text(
                "SELECT 1 FROM pg_type t "
                "JOIN pg_enum e ON t.oid = e.enumtypid "
                "WHERE t.typname = 'userrole' AND e.enumlabel = 'super_admin'"
            )
            result = db.execute(query).first()
            if not result:
                print("PostgreSQL 'userrole' enum does not contain 'super_admin'. Adding it...")
                # We need to run this outside of a transaction block using autocommit Isolation Level
                connection = db.bind.connect().execution_options(isolation_level="AUTOCOMMIT")
                connection.execute(sa.text("ALTER TYPE userrole ADD VALUE 'super_admin'"))
                print("Successfully added 'super_admin' to 'userrole' enum type.")
        except Exception as e:
            print(f"Warning: Could not alter enum type: {e}. If it already exists, you can ignore this.")

def seed_super_admin(email: str, password: str, full_name: str):
    db = SessionLocal()
    try:
        # Pre-check/create enum value if PostgreSQL
        ensure_postgresql_enum(db)

        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"User '{email}' already exists. Promoting role to SUPER_ADMIN...")
            existing.role = UserRole.SUPER_ADMIN
            db.commit()
            print(f"User '{email}' has been successfully promoted to SUPER_ADMIN!")
            return
        
        hashed_password = get_password_hash(password)
        super_admin = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=UserRole.SUPER_ADMIN,
            is_active=True
        )
        db.add(super_admin)
        db.commit()
        print(f"Super Admin account successfully created!")
        print(f"Email: {email}")
        print(f"Password: {password}")
    except Exception as e:
        print(f"Error seeding super admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    email = "admin@alliago.id"
    password = "Alliagoadmin@1"
    full_name = "Super Admin"
    
    if len(sys.argv) > 1:
        email = sys.argv[1]
    if len(sys.argv) > 2:
        password = sys.argv[2]
    if len(sys.argv) > 3:
        full_name = sys.argv[3]
        
    seed_super_admin(email, password, full_name)
