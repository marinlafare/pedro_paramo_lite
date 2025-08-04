# main.py
import os
from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession # Import AsyncSession for type hinting

# Import necessary components from your database setup
from pedro_paramo_api.database.engine import init_db, get_db_session, engine # Import engine for direct check
from pedro_paramo_api.routers import corpus # Your router
from pedro_paramo_api.operations.corpus import Corpus # Import Corpus class
from pedro_paramo_api.operations.sources import get_versions_names # To get all version names


@asynccontextmanager
async def lifespan(app: FastAPI):
    # This block runs on application startup
    print('... Starting Pedro Paramo API ...')

    # Initialize the database connection and tables
    try:
        await init_db()
        print('... Database initialization completed successfully ...')
    except Exception as e:
        print(f'!!! Critical Error during database initialization: {e} !!!')
        # Depending on your needs, you might want to exit here if DB is essential
        # import sys; sys.exit(1)

    # --- NEW: Initialize Corpus cache ---
    app.state.corpus_cache = {}
    print('... Pre-loading Corpus versions into memory ...')
    try:
        # Get a database session to fetch version names
        # Use async for to correctly manage the async generator
        async for session in get_db_session():
            version_names_list = await get_versions_names(session)

            if not version_names_list:
                print("Warning: No versions found in the database to pre-load.")
                # If there are no versions, we still want to break out of the session loop
            else:
                for version_dict in version_names_list:
                    version_name = version_dict.get('version_name')
                    if version_name:
                        try:
                            # Create and cache each Corpus instance
                            corpus_instance = await Corpus.create(session, version_name)
                            app.state.corpus_cache[version_name] = corpus_instance
                            print(f"  - Loaded Corpus for version: {version_name}")
                        except Exception as e:
                            print(f"  - Failed to load Corpus for version {version_name}: {e}")
            break # Break out of the async for loop after processing
    except Exception as e:
        print(f"!!! Error during Corpus pre-loading: {e} !!!")
    # --- END NEW ---

    print('... PEDRO_PARAMO ON ... (allegedly, maybe)')
    yield # Application serves requests
    # This block runs on application shutdown
    print('... Server PEDRO_PARAMO DOWN YO!...')

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return '... PEDRO_PARAMO RUNNING YO ...'

# Include your router
app.include_router(corpus.router)
