#pedro_paramo_lite.operations.version_corpus.py


from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Set, Optional, Union
import numpy as np
import ast

from pedro_paramo_api.operations.sources import (
    get_complete_version,
    get_raw_text,
    get_paragraphs,
    get_metadata,
    get_versions_names
)
from pedro_paramo_api.operations.frequencies import get_word_freq_dict
from pedro_paramo_api.database.ask_db import (
    get_all_embeddings,
    get_all_umap_embeddings,
    get_n_paragraph,
    get_n_paragraph_embedding,
    get_n_paragraph_umap
)


class Corpus:
    def __init__(self, version: str, version_data: Dict[str, Any]):
        self.version = version
        self.author = version_data.get('author')
        self.year = version_data.get('year')
        self.editorial = version_data.get('editorial')
        self.ISBN = version_data.get('ISBN')
        self.metadata = version_data.get('version_data')
        self.text = version_data.get('raw_text')
        self.n_words = version_data.get('n_words')
        self.n_paragraphs = version_data.get('n_paragraphs')
        self.word_set = version_data.get('word_set').split('#')

    @classmethod
    async def create(cls, session: AsyncSession, version: str):
        """
        Factory method to create a Corpus instance, fetching data from the database.
        """
        version_data = await get_complete_version(session, version)
        if not version_data:
            raise ValueError(f"Version '{version}' not found in the database.")
        return cls(version=version, version_data=version_data)

    async def word_freq(self, session: AsyncSession) -> Dict[str, int]:
        """Retrieves word frequencies for the corpus version."""
        return await get_word_freq_dict(session, self.version)

    async def int_to_word(self, session: AsyncSession) -> Dict[int, str]:
        """Maps integer IDs to words based on word frequencies."""
        word_freq = await self.word_freq(session)
        return dict(zip(range(len(word_freq)), word_freq.keys()))

    async def word_to_int(self, session: AsyncSession) -> Dict[str, int]:
        """Maps words to integer IDs based on word frequencies."""
        word_freq = await self.word_freq(session)
        return dict(zip(word_freq.keys(), range(len(word_freq))))

    async def all_paragraphs(self, session: AsyncSession) -> Dict[int, str]:
        """Retrieves all paragraphs for the corpus version."""
        return await get_paragraphs(session, self.version) 

    async def all_embeddings(self, session: AsyncSession) -> np.ndarray: 
        """Retrieves all embeddings for the corpus version."""
        return await get_all_embeddings(session, self.version)

    async def all_umap(self, session: AsyncSession) -> np.ndarray:
        """Retrieves all UMAP embeddings for the corpus version."""
        return await get_all_umap_embeddings(session, self.version)

    async def n_paragraph(self, session: AsyncSession, n_paragraph: int) -> Union[str, Any]:
        """Retrieves text for a specific paragraph number."""
        return await get_n_paragraph(session, self.version, n_paragraph)

    async def n_paragraph_embedding(self, session: AsyncSession, n_paragraph: int) -> Union[List[float], str]: 
        """Retrieves embedding for a specific paragraph number."""
        return await get_n_paragraph_embedding(session, self.version, n_paragraph)

    async def n_paragraph_umap(self, session: AsyncSession, n_paragraph: int) -> Union[List[float], str]:
        """Retrieves UMAP embedding for a specific paragraph number."""
        return await get_n_paragraph_umap(session, self.version, n_paragraph)
