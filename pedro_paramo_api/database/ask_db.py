# pedro_paramo_api/database/ask_db.py

import asyncpg
# from .db_interface import DBInterface # Removed: No longer directly managing sessions here
from .models import Version
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession # Import AsyncSession for type hinting
from urllib.parse import urlparse
from typing import Tuple, Set, List, Dict, Any, Union
import ast
import numpy as np

# Removed get_async_db_session() as engine.py now provides get_db_session

async def open_request(session: AsyncSession, # Session is now passed as an argument
                       sql_question: str,
                       params: Union[Tuple[Any, ...], Dict[str, Any], None] = None,
                       fetch_as_dict: bool = False) -> Union[List[Dict[str, Any]], List[Tuple[Any, ...]], None]:
    """
    Executes a SQL query asynchronously using SQLAlchemy's AsyncSession.
    """
    try:
        # Use async with session.begin() to start and manage a transaction
        async with session.begin(): # Transaction management is now within this function
            result = await session.execute(text(sql_question), params)

            if result.returns_rows:
                if fetch_as_dict:
                    column_names = result.keys()
                    results = [dict(zip(column_names, row)) for row in result.fetchall()]
                    return results
                else:
                    return result.fetchall()
            else:
                return None
    except Exception as e:
        # The transaction will be automatically rolled back on an exception
        print(f"Error in open_request: {e}")
        raise

async def get_n_paragraph(session: AsyncSession, version: str, n_paragraph: int): # Session added
    n_paragraph = int(n_paragraph)
    data = await open_request(session, # Pass session
                              """SELECT text FROM paragraph WHERE n_paragraph = :n_p
                                 AND version_name = :v_n;
                              """, params = {"n_p":n_paragraph,"v_n":version})
    if not data: # Simplified check for empty data
        return f"this paragraph: {n_paragraph} doesn't exist"
    return data[0][0]

async def get_n_paragraph_embedding(session: AsyncSession, version: str, n_paragraph: int): # Session added
    n_paragraph = int(n_paragraph)
    data = await open_request(session, # Pass session
                              """SELECT embedding FROM paragraph WHERE n_paragraph = :n_p
                                 AND version_name = :v_n;
                              """, params = {"n_p":n_paragraph,"v_n":version})
    if not data: # Simplified check for empty data
        return f"this paragraph: {n_paragraph} doesn't exist"
    raw_embedding_value = data[0][0]

    try:
        embedding_list = ast.literal_eval(str(raw_embedding_value))
        return embedding_list
    except (ValueError, SyntaxError) as e:
        return f"Error parsing UMAP embedding for paragraph {n_paragraph} in version {version}: {e}"

async def get_all_embeddings(session: AsyncSession, version: str): # Session added
    """
    Retrieves all embeddings for a given version, returning them
    as a NumPy array (matrix), sorted by n_paragraph. Ensures embeddings are
    parsed as Python lists (vectors) before converting to NumPy.

    Args:
        session (AsyncSession): The database session.
        version (str): The name of the version to retrieve embeddings for.

    Returns:
        np.ndarray: A 2D NumPy array where each row is an embedding vector,
                    sorted by their original n_paragraph.
        str: An error message if the version doesn't exist or no data is found.
    """

    query = """
        SELECT n_paragraph, embedding FROM paragraph
        WHERE version_name = :v_n;
    """

    data = await open_request(session, query, params={"v_n": version}) # Pass session

    if not data:
        return f"This version: {version} doesn't exist or has no paragraphs."

    # Sort the data by 'n_paragraph' (which is at index 0)
    sorted_data = sorted(data, key=lambda x: x[0])

    embeddings_list = []
    for item in sorted_data:
        n_paragraph = item[0]
        raw_embedding_value = item[1]

        try:
            embedding_list_item = ast.literal_eval(str(raw_embedding_value))
            embeddings_list.append(embedding_list_item)
        except (ValueError, SyntaxError) as e:
            print(f"Warning: Could not parse embedding for paragraph {n_paragraph} in version {version}. Error: {e}. Skipping this embedding.")
            continue

    if not embeddings_list:
        return f"No valid embeddings found for version: {version} after parsing."

    return np.array(embeddings_list, dtype=np.float32)

async def get_all_umap_embeddings(session: AsyncSession, version: str): # Session added
    """
    Retrieves all UMAP embeddings for a given version, returning them
    as a NumPy array (matrix), sorted by n_paragraph. Ensures UMAP embeddings are
    parsed as Python lists (vectors) before converting to NumPy.

    Args:
        session (AsyncSession): The database session.
        version (str): The name of the version to retrieve UMAP embeddings for.

    Returns:
        np.ndarray: A 2D NumPy array where each row is a UMAP embedding vector,
                    sorted by their original n_paragraph.
        str: An error message if the version doesn't exist or no data is found.
    """

    query = """
        SELECT n_paragraph, umap FROM paragraph
        WHERE version_name = :v_n;
    """

    data = await open_request(session, query, params={"v_n": version}) # Pass session

    if not data:
        return f"This version: {version} doesn't exist or has no UMAP embeddings."

    # Sort the data by 'n_paragraph' (which is at index 0)
    sorted_data = sorted(data, key=lambda x: x[0])

    umap_embeddings_list = []
    for item in sorted_data:
        n_paragraph = item[0]
        raw_umap_embedding_value = item[1]

        try:
            umap_embedding_list_item = ast.literal_eval(str(raw_umap_embedding_value))
            umap_embeddings_list.append(umap_embedding_list_item)
        except (ValueError, SyntaxError) as e:
            print(f"Warning: Could not parse UMAP embedding for paragraph {n_paragraph} in version {version}. Error: {e}. Skipping this embedding.")
            continue

    if not umap_embeddings_list:
        return f"No valid UMAP embeddings found for version: {version} after parsing."

    return np.array(umap_embeddings_list, dtype=np.float32)

async def get_n_paragraph_umap(session: AsyncSession, version: str, n_paragraph: int): # Session added
    n_paragraph = int(n_paragraph)

    query = """
        SELECT umap FROM paragraph
        WHERE n_paragraph = :n_p AND version_name = :v_n;
    """

    data = await open_request(session, query, params={"n_p": n_paragraph, "v_n": version}) # Pass session

    if not data:
        return f"This paragraph: {n_paragraph} in version: {version} doesn't exist."

    raw_umap_embedding_value = data[0][0]

    try:
        umap_embedding_list = ast.literal_eval(str(raw_umap_embedding_value))
        return umap_embedding_list
    except (ValueError, SyntaxError) as e:
        return f"Error parsing UMAP embedding for paragraph {n_paragraph} in version {version}: {e}"
