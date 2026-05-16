import datetime
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    city: Mapped[str] = mapped_column(String, index=True)
    source_url: Mapped[str] = mapped_column(String)
    local_path: Mapped[str] = mapped_column(String)
    file_hash: Mapped[str] = mapped_column(String, unique=True, index=True)
    capture_timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
