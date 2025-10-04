# app/models/base.py - Independent base model without circular imports
from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy import MetaData

metadata_obj = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

class Base(DeclarativeBase):
    metadata = metadata_obj

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()