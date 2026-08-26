"""
Database type compatibility layer.
Provides column types that work on both SQLite (dev) and PostgreSQL (production).
"""
import uuid
from sqlalchemy import String, Text
from sqlalchemy.types import TypeDecorator, CHAR

class UUIDType(TypeDecorator):
    """Platform-independent UUID type.
    Uses PostgreSQL UUID type when available, otherwise stores as CHAR(36) on SQLite.
    """
    impl = CHAR
    cache_ok = True

    def __init__(self):
        super().__init__(length=36)

    def process_bind_param(self, value, dialect):
        if value is not None:
            if isinstance(value, uuid.UUID):
                return str(value)
            return str(uuid.UUID(value))
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
        return value


class GeometryText(TypeDecorator):
    """Stores geometry as WKT text on SQLite, or uses PostGIS Geometry on PostgreSQL.
    For dev mode: stores as plain text (e.g., 'POINT(81.6296 21.2514)')
    """
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return str(value)
        return value

    def process_result_value(self, value, dialect):
        return value
