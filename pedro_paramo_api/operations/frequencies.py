# pedro_paramo_api.operations.frequencies.py

from sqlalchemy.ext.asyncio import AsyncSession # Import AsyncSession for type hinting
from typing import Dict, Any, List, Union
import re
from collections import OrderedDict, Counter
import unicodedata
# Assuming open_request is defined in ask_db.py
from ..database.ask_db import open_request

def clean_line(string: str = None) -> str:
    apostrophes = {"'", "’", "`"}
    
    cleaned_chars = []
    for char in string:
        # Check if the character is a Unicode letter OR if it's one of the allowed apostrophes
        if unicodedata.category(char).startswith('L') or char in apostrophes:
            cleaned_chars.append(char)
    
    # Join the filtered characters back into a string
    cleaned_string = "".join(cleaned_chars)
    
    # Convert all characters to lowercase (Python's .lower() handles Unicode correctly)
    cleaned_string = cleaned_string.lower()
    
    return cleaned_string

async def get_n_words(session: AsyncSession, version: str) -> Union[int, str]:
    """
    Retrieves the raw text for a version and calculates the number of words.

    Args:
        session (AsyncSession): The database session.
        version (str): The name of the version.

    Returns:
        Union[int, str]: The number of words, or an error message if the version
                         doesn't exist or has no raw text.
    """
    data = await open_request(session, # Pass the session here
                              """
                              SELECT version.raw_text FROM version
                              WHERE version.version_name = :version
                              """,
                              params={"version": version},
                              fetch_as_dict=True)

    if not data or not data[0] or 'raw_text' not in data[0]:
        return f"This version: {version} doesn't exist or has no raw text."

    text = data[0]['raw_text']
    n_words = len(text.split(' ')) # Simple word count by splitting on space

    return n_words


async def get_paragraph_words_freq(session: AsyncSession, version: str) -> Union[Dict[int, int], str]:
    """
    Retrieves the word count for each paragraph of a given version.

    Args:
        session (AsyncSession): The database session.
        version (str): The name of the version.

    Returns:
        Union[Dict[int, int], str]: A dictionary mapping paragraph numbers to their
                                    word counts, or an error message.
    """
    data = await open_request(session, # Pass the session here
                              """
                              SELECT n_paragraph, paragraph.n_words FROM paragraph
                              WHERE paragraph.version_name = :version
                              """,
                              params={"version": version},
                              fetch_as_dict=True)

    if not data:
        return f"No paragraphs found for version: {version}."

    # Create a dictionary from the list of dictionaries
    versions = {x['n_paragraph']: x['n_words'] for x in data}

    return versions


async def get_word_freq_dict(session: AsyncSession, version_name: str) -> Union[OrderedDict, str]:
    """
    Retrieves the raw text for a given version, cleans its words,
    calculates word frequencies, and returns an OrderedDict
    sorted by frequency in descending order.

    Args:
        session (AsyncSession): The database session.
        version_name (str): The name of the version to retrieve word data for.

    Returns:
        Union[OrderedDict, str]: A dictionary where keys are cleaned words (str) and
                                 values are their frequencies (int), sorted by frequency
                                 in descending order, or an error message.
    """

    query = """
        SELECT version.raw_text FROM version
        WHERE version.version_name = :v_n;
    """

    # open_request is expected to return a list of tuples, e.g., [('full raw text string',)]
    data = await open_request(session, query, params={"v_n": version_name}) # Pass the session here

    if not data or not data[0] or not data[0][0]:
        return f"This version: {version_name} doesn't exist or has no raw text data."

    raw_text_string = data[0][0] # Get the full raw text string from the query result

    # Basic word cleaning: replace '#' with space and split
    words_from_text = raw_text_string.replace('#', ' ').split(' ')
    processed_words = [clean_line(word.lower()) for word in words_from_text if len(word)>0] # Filter out empty strings

    if not processed_words:
        return f"No valid words found for version: {version_name} after cleaning."

    word_counts = Counter(processed_words)

    # Sort the items by frequency in descending order
    sorted_word_counts = sorted(word_counts.items(), key=lambda item: item[1], reverse=True)

    # Create an OrderedDict from the sorted list of (word, count) tuples
    word_freq_dict = OrderedDict(sorted_word_counts)

    return word_freq_dict
