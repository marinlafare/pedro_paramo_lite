# pedro_paramo_api/database/db_interface.py


from sqlalchemy.ext.asyncio import AsyncSession # Only need AsyncSession for type hinting
from sqlalchemy.orm import declarative_base # Keep if Base is defined here, otherwise import from models
from sqlalchemy.future import select
from typing import Type, Dict, Any, List, Optional
# from contextlib import asynccontextmanager # Not needed if session is passed in

# IMPORTANT: Ensure Base is imported from where it's defined (likely models.py)
# If Base is defined in models.py, remove this line:
# Base = declarative_base()
# And use:
from .models import Base # Assuming Base is defined in pedro_paramo_api/database/models.py


class DBInterface:
    # Removed _engine and AsyncSessionLocal class attributes
    # Removed initialize_engine_and_session class method

    def __init__(self, model: Type[Base]):
        self.model = model
        # Removed the runtime check for engine/session initialization
        # The expectation is that an AsyncSession will be passed to methods

    # Removed get_session context manager as sessions will be passed directly

    async def create(self, session: AsyncSession, data: Dict[str, Any]) -> Base:
        """Creates a new item in the database."""
        item = self.model(**data)
        session.add(item)
        await session.flush()
        await session.refresh(item)
        return item

    async def create_all(self, session: AsyncSession, data_list: List[Dict[str, Any]]) -> List[Base]:
        """Performs a bulk insert of items into the database."""
        if not data_list:
            print(f"Warning: create_all called with empty data list for {self.model.__name__}. No action taken.")
            return []

        items = [self.model(**data) for data in data_list]
        session.add_all(items)
        # No flush/refresh here for bulk inserts unless specific IDs are needed immediately
        print(f"Successfully performed bulk insert for {len(data_list)} items in {self.model.__name__}.")
        return items

    async def read_all(self, session: AsyncSession) -> List[Base]:
        """Retrieves all items of the model from the database."""
        result = await session.execute(select(self.model))
        return result.scalars().all()

    async def read_by_id(self, session: AsyncSession, item_id: int) -> Optional[Base]:
        """Retrieves an item by its ID."""
        result = await session.execute(
            select(self.model).filter_by(id=item_id)
        )
        return result.scalars().first()

    async def update_by_id(self, session: AsyncSession, item_id: int, new_data: Dict[str, Any]) -> Optional[Base]:
        """Updates an item by its ID with new data."""
        item = await session.get(self.model, item_id)
        if item:
            for key, value in new_data.items():
                setattr(item, key, value)
            await session.flush()
            await session.refresh(item)
            return item
        return None

    async def delete_by_id(self, session: AsyncSession, item_id: int) -> bool:
        """Deletes an item by its ID."""
        item = await session.get(self.model, item_id)
        if item:
            await session.delete(item)
            return True
        return False

    async def read_by_version_name(self, session: AsyncSession, version_name: str) -> Optional[List[Base]]:
        """Retrieves items by version name."""
        result = await session.execute(
            select(self.model).filter_by(version_name=version_name)
        )
        return result.scalars().all()

    async def update_by_version_name(self, session: AsyncSession, version_name: str, new_data: Dict[str, Any]) -> Optional[List[Base]]:
        """Updates items by version name with new data."""
        result = await session.execute(
            select(self.model).filter_by(version_name=version_name)
        )
        items = result.scalars().all()
        if items:
            for item in items:
                for key, value in new_data.items():
                    setattr(item, key, value)
            await session.flush()
            # You might need to refresh each item individually or refetch them
            # for the updated data to be available.
            return items
        return None

    async def delete_by_version_name(self, session: AsyncSession, version_name: str) -> bool:
        """Deletes items by version name."""
        result = await session.execute(
            select(self.model).filter_by(version_name=version_name)
        )
        items = result.scalars().all()
        if items:
            for item in items:
                await session.delete(item)
            return True
        return False



# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.orm import sessionmaker, declarative_base
# from sqlalchemy.future import select
# from typing import Type, Dict, Any, List, Optional
# from contextlib import asynccontextmanager

# Base = declarative_base()

# class DBInterface:
#     _engine = None
#     AsyncSessionLocal = None

#     @classmethod
#     def initialize_engine_and_session(cls, database_url: str):
#         if not database_url:
#             raise ValueError("DATABASE_URL is wrong or something.")
        
#         if cls._engine is None:
#             cls._engine = create_async_engine(database_url, echo=False)
#             cls.AsyncSessionLocal = sessionmaker(
#                 cls._engine, expire_on_commit=False, class_=AsyncSession
#             )
#             print("DBInterface: SQLAlchemy engine and AsyncSessionLocal initialized.")
#         else:
#             print("DBInterface: Engine already initialized, skipping.")

#     def __init__(self, model: Type[Base]):
#         self.model = model
#         if self.__class__._engine is None or self.__class__.AsyncSessionLocal is None:
#             raise RuntimeError(
#                 "Database engine and session not initialized. "
#                 "Call DBInterface.initialize_engine_and_session() during application startup."
#             )

#     @asynccontextmanager
#     async def get_session(self):
#         """Provide a transactional scope around a series of operations."""
#         async with self.AsyncSessionLocal() as session:
#             try:
#                 yield session
#                 await session.commit()
#             except Exception:
#                 await session.rollback()
#                 raise

#     async def create(self, data: Dict[str, Any]) -> Base:
#         async with self.get_session() as session:
#             item = self.model(**data)
#             session.add(item)
#             await session.flush()
#             await session.refresh(item)
#             return item

#     async def create_all(self, data_list: List[Dict[str, Any]]) -> List[Base]:
#         if not data_list:
#             print(f"Warning: create_all called with empty data list for {self.model.__name__}. No action taken.")
#             return []
            
#         async with self.get_session() as session:
#             items = [self.model(**data) for data in data_list]
#             session.add_all(items)
#             print(f"Successfully performed bulk insert for {len(data_list)} items in {self.model.__name__}.")
#             return items

#     async def read_all(self) -> List[Base]:
#         async with self.AsyncSessionLocal() as session:
#             result = await session.execute(select(self.model))
#             return result.scalars().all()

#     async def read_by_id(self, item_id: int) -> Optional[Base]:
#         async with self.AsyncSessionLocal() as session:
#             result = await session.execute(
#                 select(self.model).filter_by(id=item_id)
#             )
#             return result.scalars().first()
    
#     async def update_by_id(self, item_id: int, new_data: Dict[str, Any]) -> Optional[Base]:
#         async with self.get_session() as session:
#             item = await session.get(self.model, item_id)
#             if item:
#                 for key, value in new_data.items():
#                     setattr(item, key, value)
#                 await session.flush()
#                 await session.refresh(item)
#                 return item
#             return None

#     async def delete_by_id(self, item_id: int) -> bool:
#         async with self.get_session() as session:
#             item = await session.get(self.model, item_id)
#             if item:
#                 await session.delete(item)
#                 return True
#             return False

#     async def read_by_version_name(self, version_name: str) -> Optional[List[Base]]:
#         async with self.AsyncSessionLocal() as session:
#             result = await session.execute(
#                 select(self.model).filter_by(version_name=version_name)
#             )
#             return result.scalars().all()

#     async def update_by_version_name(self, version_name: str, new_data: Dict[str, Any]) -> Optional[List[Base]]:
#         async with self.get_session() as session:
#             result = await session.execute(
#                 select(self.model).filter_by(version_name=version_name)
#             )
#             items = result.scalars().all()
#             if items:
#                 for item in items:
#                     for key, value in new_data.items():
#                         setattr(item, key, value)
#                 await session.flush()
#                 # You might need to refresh each item individually or refetch them
#                 # for the updated data to be available.
#                 return items
#             return None

#     async def delete_by_version_name(self, version_name: str) -> bool:
#         async with self.get_session() as session:
#             result = await session.execute(
#                 select(self.model).filter_by(version_name=version_name)
#             )
#             items = result.scalars().all()
#             if items:
#                 for item in items:
#                     await session.delete(item)
#                 return True
#             return False