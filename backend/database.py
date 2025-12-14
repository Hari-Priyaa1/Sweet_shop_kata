from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base # Import Base from models.py

# SQLite database file creation (it will be created in the backend directory)
SQLALCHEMY_DATABASE_URL = "sqlite:///./sweet_shop.db"

# Create the SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a SessionLocal class to get a database session (the actual connection)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Function to get a database session/dependency injector for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables defined in models.py
def create_db_and_tables():
    Base.metadata.create_all(bind=engine)