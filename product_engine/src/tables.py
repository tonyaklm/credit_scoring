from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import PrimaryKeyConstraint, UniqueConstraint, ForeignKeyConstraint, Index
from sqlalchemy import DateTime
import datetime


class Base(DeclarativeBase):
    pass


class Client(Base):
    __tablename__ = 'client'
    id: Mapped[int] = mapped_column(primary_key=True)

    client_name: Mapped[str] = mapped_column(nullable=False)
    client_age: Mapped[int] = mapped_column(nullable=False)
    client_phone_number: Mapped[str] = mapped_column(nullable=False)
    client_passport_number: Mapped[str] = mapped_column(nullable=False, unique=True)
    client_salary: Mapped[float] = mapped_column(nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('id', name='client_pkey'),
        UniqueConstraint('client_passport_number'),
        Index('passport_index' 'client_passport_number'),
    )


class Product(Base):
    __tablename__ = 'product'
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    code: Mapped[str] = mapped_column(nullable=False, unique=True)
    min_term: Mapped[int] = mapped_column(nullable=False)
    max_term: Mapped[int] = mapped_column(nullable=False)
    min_principal: Mapped[float] = mapped_column(nullable=False)
    max_principal: Mapped[float] = mapped_column(nullable=False)
    min_interest: Mapped[float] = mapped_column(nullable=False)
    max_interest: Mapped[float] = mapped_column(nullable=False)
    min_origination: Mapped[float] = mapped_column(nullable=False)
    max_origination: Mapped[float] = mapped_column(nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('id', name='product_pkey'),
        UniqueConstraint('code'),
        Index('code_index' 'code')
    )


class Agreement(Base):
    __tablename__ = 'agreement'
    id: Mapped[int] = mapped_column(primary_key=True)
    product_code: Mapped[str] = mapped_column(nullable=False)
    client_id: Mapped[int] = mapped_column(nullable=False)
    term: Mapped[int] = mapped_column(nullable=False)
    principal: Mapped[float] = mapped_column(nullable=False)
    interest: Mapped[float] = mapped_column(nullable=False)
    origination: Mapped[float] = mapped_column(nullable=False)
    activation_time: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('id', name='agreement_pkey'),
        Index('product_index' 'product_code'),
        Index('client_index' 'client_id'),
        ForeignKeyConstraint(['product_code'], ['product.code']),
        ForeignKeyConstraint(['client_id'], ['client.id'])
    )
