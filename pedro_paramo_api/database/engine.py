# pedro_paramo_api/database/engine.py

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text # Import text for simple connection check
import asyncio
import asyncpg
from urllib.parse import urlparse

# Import Base from your models.py. Ensure models.py defines 'Base = declarative_base()'
# If Base is not defined in models.py, you might need to define it here or import it correctly.
from .models import Base

# Get the database URL from environment variables
# This is the connection string that your application will use.
# It matches the DATABASE_URL defined in docker-compose.yml
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
# Ensure the DATABASE_URL is set, otherwise raise an error
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set. Please check your docker-compose.yml.")

# Define the async engine globally
# It will be initialized in init_db
engine = None

# Define the async sessionmaker globally
AsyncDBSession = sessionmaker(expire_on_commit=False, class_=AsyncSession)

async def init_db():
    """
    Initializes the database engine, checks for database existence,
    creates it if necessary, and ensures tables are created.
    """
    global engine

    # Parse the connection string to extract details for asyncpg connection
    parsed_url = urlparse(SQLALCHEMY_DATABASE_URL)
    db_user = parsed_url.username
    db_password = parsed_url.password
    db_host = parsed_url.hostname
    db_port = parsed_url.port
    db_name = parsed_url.path.lstrip('/')

    temp_conn = None
    try:
        # Connect to a default database (e.g., 'postgres') to perform database creation/check
        temp_conn = await asyncpg.connect(
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            database='postgres' # Connect to a default database to perform creation
        )

        # Check if the target database exists
        db_exists_query = f"SELECT 1 FROM pg_database WHERE datname='{db_name}'"
        db_exists = await temp_conn.fetchval(db_exists_query)

        if not db_exists:
            print(f"Database '{db_name}' does not exist. Creating...")
            # Ensure the database name is correctly quoted for safety
            await temp_conn.execute(f'CREATE DATABASE "{db_name}"')
            print(f"Database '{db_name}' created.")
        else:
            print(f"Database '{db_name}' already exists.")

    except asyncpg.exceptions.DuplicateDatabaseError:
        print(f"Database '{db_name}' already exists (concurrent creation attempt).")
    except Exception as e:
        print(f"Error during database existence check/creation: {e}")
        raise # Re-raise the exception to stop startup if DB is critical
    finally:
        if temp_conn:
            await temp_conn.close() # Ensure the temporary connection is closed

    # Create the SQLAlchemy async engine after ensuring the database exists
    engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)

    # Ensure database tables exist using the new async engine
    async with engine.begin() as conn:
        print("Ensuring database tables exist...")
        await conn.run_sync(Base.metadata.create_all)
        print("Database tables checked/created.")

    # Configure the sessionmaker to use the initialized engine
    AsyncDBSession.configure(bind=engine)
    print("Database initialization complete.")

async def get_db_session() -> AsyncSession:
    """
    Dependency function for FastAPI to get an asynchronous database session.
    """
    async with AsyncDBSession() as session:
        yield session

# Expose the engine globally after init_db is called, for use in main.py's lifespan or other modules.
# This makes it accessible for direct connection checks or other advanced uses.
