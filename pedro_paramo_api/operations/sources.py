# pedro_paramo_api/operations/sources.py

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any, List, Union

# Assuming open_request is defined in ask_db.py
from ..database.ask_db import open_request

# Assuming your Version model is defined in models.py
# This import is kept for consistency, even if not directly used by these specific functions.
from ..database.models import Version


async def get_versions_names(session: AsyncSession) -> List[Dict[str, Any]]:
    """
    Retrieves all available version names from the database.

    Args:
        session (AsyncSession): The database session.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each containing a 'version_name'.
    """
    versions = await open_request(session, "select version_name from version", fetch_as_dict=True)
    return versions


async def get_raw_text(session: AsyncSession, version: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves the raw text for a specific version from the database.

    Args:
        session (AsyncSession): The database session.
        version (str): The name of the version.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing the 'raw_text' if found,
                                  otherwise None.
    """
    data = await open_request(session,
                              """
                              SELECT raw_text FROM version
                              WHERE version.version_name = :version_name
                              """,
                              params={"version_name": version},
                              fetch_as_dict=True)
    return data[0] if data else None


async def get_paragraphs(session: AsyncSession, version: str) -> Dict[int, str]:
    """
    Retrieves all paragraphs for a given version, sorted by paragraph number.

    Args:
        session (AsyncSession): The database session.
        version (str): The name of the version.

    Returns:
        Dict[int, str]: A dictionary where keys are paragraph numbers (int)
                        and values are paragraph text (str).
    """
    data = await open_request(session,
                              """
                              SELECT n_paragraph, text FROM paragraph
                              WHERE version_name = :version_name
                              """,
                              params={"version_name": version},
                              fetch_as_dict=True)

    if not data:
        return {} # Return an empty dictionary if no data is found

    # Sort the list of dictionaries by n_paragraph
    sorted_data = sorted(data, key=lambda x: x["n_paragraph"])

    # Create the dictionary from the sorted list
    result_dict = {x["n_paragraph"]: x["text"] for x in sorted_data}

    return result_dict


async def get_metadata(session: AsyncSession, version: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves metadata for a specific version from the database.

    Args:
        session (AsyncSession): The database session.
        version (str): The name of the version.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing the 'version_data' if found,
                                  otherwise None.
    """
    data = await open_request(session,
                              """
                              SELECT version_data FROM version
                              WHERE version.version_name = :version_name
                              """,
                              params={"version_name": version},
                              fetch_as_dict=True)
    return data[0] if data else None


async def get_complete_version(session: AsyncSession, version_name: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves complete version data (all columns) from the database.

    Args:
        session (AsyncSession): The database session.
        version_name (str): The name of the version to retrieve.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing all version data if found,
                                  otherwise None.
    """
    data = await open_request(session,
                              """
                              SELECT * FROM version
                              WHERE version.version_name = :version_name
                              """,
                              params={"version_name": version_name},
                              fetch_as_dict=True)
    return data[0] if data else None
