"""
Script to populate the database with test users:
- 1 admin: admin1@optiroute.com
- 2 drivers: driver1@optiroute.com, driver2@optiroute.com
- 6 users: user1@optiroute.com, user2@optiroute.com, ..., user6@optiroute.com
All accounts use password: "password"
"""

import os
import sys
from passlib.context import CryptContext
from sqlalchemy import Column, DateTime, Integer, String, create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://optiroute:optiroute123@postgres:5432/optiroute",
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=False)
    surname = Column(String, index=False)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="user")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_test_users():
    """Create test users in the database"""
    db = SessionLocal()
    
    try:
        # Check if tables exist
        Base.metadata.create_all(bind=engine)
        
        # Define users to create
        users_to_create = [
            # Admin
            {
                "name": "Admin",
                "surname": "Administrator",
                "email": "admin1@optiroute.com",
                "password": "password",
                "role": "admin"
            },
            # Drivers
            {
                "name": "Driver",
                "surname": "One",
                "email": "driver1@optiroute.com",
                "password": "password",
                "role": "driver"
            },
            {
                "name": "Driver",
                "surname": "Two",
                "email": "driver2@optiroute.com",
                "password": "password",
                "role": "driver"
            },
            # Regular users
            {
                "name": "User",
                "surname": "One",
                "email": "user1@optiroute.com",
                "password": "password",
                "role": "user"
            },
            {
                "name": "User",
                "surname": "Two",
                "email": "user2@optiroute.com",
                "password": "password",
                "role": "user"
            },
            {
                "name": "User",
                "surname": "Three",
                "email": "user3@optiroute.com",
                "password": "password",
                "role": "user"
            },
            {
                "name": "User",
                "surname": "Four",
                "email": "user4@optiroute.com",
                "password": "password",
                "role": "user"
            },
            {
                "name": "User",
                "surname": "Five",
                "email": "user5@optiroute.com",
                "password": "password",
                "role": "user"
            },
            {
                "name": "User",
                "surname": "Six",
                "email": "user6@optiroute.com",
                "password": "password",
                "role": "user"
            },
        ]
        
        created_count = 0
        skipped_count = 0
        
        for user_data in users_to_create:
            # Check if user already exists
            existing = db.query(UserDB).filter(UserDB.email == user_data["email"]).first()
            
            if existing:
                print(f"⏭️  Skipping {user_data['email']} - already exists")
                skipped_count += 1
                continue
            
            # Create new user
            hashed_password = get_password_hash(user_data["password"])
            new_user = UserDB(
                name=user_data["name"],
                surname=user_data["surname"],
                email=user_data["email"],
                password=hashed_password,
                role=user_data["role"]
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            print(f"✅ Created {user_data['role']}: {user_data['email']} (ID: {new_user.id})")
            created_count += 1
        
        print(f"\n📊 Summary:")
        print(f"   Created: {created_count}")
        print(f"   Skipped: {skipped_count}")
        print(f"   Total: {len(users_to_create)}")
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Starting user population script...\n")
    create_test_users()
    print("\n✨ Done!")
