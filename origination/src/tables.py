from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import PrimaryKeyConstraint, Index
from sqlalchemy import DateTime
import datetime


class Base(DeclarativeBase):
    pass


class Application(Base):
    __tablename__ = 'application'
    id: Mapped[int] = mapped_column(primary_key=True)
    agreement_id: Mapped[int] = mapped_column(nullable=False)
    product_code: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False)
    time_of_application: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('id', name='application_pkey'),
        Index('agreement_index' 'agreement_id'),
        Index('product_index' 'product_code')
    )

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
