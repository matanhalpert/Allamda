from typing import overload, Type, Any
from sqlalchemy.orm import declarative_base

from src.database.session_context import get_current_session


class Base(declarative_base()):
    """
    Custom base class for all SQLAlchemy models.
    This class extends SQLAlchemy's declarative base with custom methods and utilities.
    """
    __abstract__ = True
    
    @classmethod
    @overload
    def get_by[T: Base](cls: Type[T], first: bool = True, **filters: Any) -> T | None: ...
    
    @classmethod
    @overload
    def get_by[T: Base](cls: Type[T], first: bool = False, **filters: Any) -> list[T]: ...
    
    @classmethod
    def get_by[T: Base](
        cls: Type[T], first: bool = False, **filters: Any
    ) -> T | list[T] | None:
        """Flexible query method that filters by model properties."""
        session = get_current_session()
        query = session.query(cls)

        for key, value in filters.items():
            if hasattr(cls, key):
                if isinstance(value, list):
                    query = query.filter(getattr(cls, key).in_(value))
                else:
                    query = query.filter(getattr(cls, key) == value)

        return query.first() if first else query.all()
    
    def to_dict[T: Base](self: T) -> dict[str, Any]:
        """Convert model instance to dictionary with column attributes."""
        result: dict[str, Any] = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name, None)
            result[column.name] = value
        return result
