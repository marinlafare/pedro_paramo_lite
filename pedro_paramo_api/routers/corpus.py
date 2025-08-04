# pedro_paramo_api.routers.corpus.py

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
import numpy as np

from ..database.engine import get_db_session
from ..operations.corpus import Corpus


router = APIRouter()

@router.get("/{version}/{attribute_or_method_name}")
async def api_get_corpus_data(
    version: str,
    attribute_or_method_name: str,
    request: Request,
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Dynamically retrieves a specified attribute or calls a method from a pre-loaded Corpus instance.
    """
    corpus_instance = request.app.state.corpus_cache.get(version)
    if not corpus_instance:
        raise HTTPException(status_code=404, detail=f"Version '{version}' not found or not loaded.")

    allowed_attributes = [
        "author", "year", "editorial", "ISBN", "metadata", "text",
        "n_words", "n_paragraphs", "word_set"
    ]

    allowed_async_methods_with_session = [
        "word_freq", "int_to_word", "word_to_int", "all_paragraphs",
        "all_embeddings", "all_umap"
    ]

    allowed_async_methods_with_session_and_int_arg = [
        "n_paragraph", "n_paragraph_embedding", "n_paragraph_umap"
    ]

    if attribute_or_method_name in allowed_attributes:
        try:
            value = getattr(corpus_instance, attribute_or_method_name)
            if isinstance(value, set):
                value = list(value)
            return {"version": version, attribute_or_method_name: value}
        except AttributeError:
            raise HTTPException(status_code=404, detail=f"Attribute '{attribute_or_method_name}' not found for version '{version}'.")

    elif attribute_or_method_name in allowed_async_methods_with_session:
        try:
            method = getattr(corpus_instance, attribute_or_method_name)
            result = await method(db_session) 

            if isinstance(result, np.ndarray):
                result = result.tolist() 
            elif isinstance(result, set):
                result = list(result)

            return {"version": version, attribute_or_method_name: result}
        except AttributeError:
            raise HTTPException(status_code=404, detail=f"Method '{attribute_or_method_name}' not found for version '{version}'.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error calling method '{attribute_or_method_name}' for version '{version}': {e}")

    elif attribute_or_method_name in allowed_async_methods_with_session_and_int_arg:
        raise HTTPException(status_code=400, detail=f"Method '{attribute_or_method_name}' requires additional arguments (e.g., paragraph number). Please use a specific endpoint for this.")

    else:
        raise HTTPException(status_code=404, detail=f"Attribute or method '{attribute_or_method_name}' is not allowed or does not exist for version '{version}'.")

