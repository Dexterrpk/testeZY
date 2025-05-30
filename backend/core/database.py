from sqlmodel import create_engine, Session, SQLModel
from .config import settings

# The database URL is read from the settings
connect_args = {"check_same_thread": False} # Needed only for SQLite
engine = create_engine(settings.DATABASE_URL, echo=True, connect_args=connect_args)

def create_db_and_tables():
    # This function should be called once at startup
    # to create the database and tables if they don't exist.
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

