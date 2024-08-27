from contextlib import contextmanager
from datetime import datetime, UTC
import enum
from typing import Optional, Iterator, Type

from sqlalchemy import Dialect, String, Boolean, Text, ForeignKey, Date, Integer, BigInteger, Double, UniqueConstraint, TypeDecorator, create_engine
from sqlalchemy.orm import Mapped, mapped_column, relationship, sessionmaker, Session

from sqlalchemy import Dialect, String, TypeDecorator, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, DeclarativeBase
from sqlalchemy.types import DateTime, String

from dashcamtools.settings import DATABASE_URL


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base: Type[DeclarativeBase] = declarative_base()

@contextmanager
def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UTCTimestamp(TypeDecorator):
    impl = Text

    def process_bind_param(self, value: datetime | None, dialect):
        if value is not None:
            return value.replace(tzinfo=UTC).isoformat()
        else:
            return None

    def process_result_value(self, value: str | None, dialect):
        if value is not None:
            return datetime.fromisoformat(value)
        else:
            return value

# see: https://qiita.com/methane/items/dd19bc7be27a5e991cca
class StrEnum(TypeDecorator):
    impl = String

    def __init__(self, enum: Type[enum.Enum], *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.enum = enum

    def process_bind_param(self, value: enum.Enum | None, _: Dialect):
        if value is not None:
            return value.value
        else:
            return value

    def process_result_value(self, value: str | None, _: Dialect):
        if value is not None:
            return self.enum(value)
        else:
            return value

class ReportStatus(enum.Enum):
    SKIPPED = "skipped"
    SUCCESSFUL = "successful"
    FAILED = "failed"

class LogSeverity(enum.Enum):
    INFO = "info"
    ERROR = "error"

class Video(Base):
    __tablename__ = "videos"

    name: Mapped[str] = mapped_column(String(255), primary_key=True)
    # is_rear: Mapped[bool] = mapped_column(Boolean, nullable=False)
    # is_event: Mapped[bool] = mapped_column(Boolean, nullable=False)
    # recorded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    mtime: Mapped[datetime] = mapped_column(UTCTimestamp, nullable=False, index=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

class Report(Base):
    __tablename__ = "reports"

    started_at: Mapped[datetime] = mapped_column(UTCTimestamp, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[ReportStatus] = mapped_column(StrEnum(ReportStatus), nullable=False)
    mtime: Mapped[datetime] = mapped_column(UTCTimestamp, nullable=True)
    original_bytes: Mapped[int] = mapped_column(Integer, nullable=True)
    compressed_bytes: Mapped[int] = mapped_column(Integer, nullable=True)
    codec: Mapped[str] = mapped_column(String(255), nullable=True)
    duration_download: Mapped[float] = mapped_column(Double, nullable=True)
    duration_compress: Mapped[float] = mapped_column(Double, nullable=True)
    duration_upload: Mapped[float] = mapped_column(Double, nullable=True)
    duration: Mapped[float] = mapped_column(Double, nullable=True)

class Log(Base):
    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    severity: Mapped[LogSeverity] = mapped_column(StrEnum(LogSeverity), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(UTCTimestamp)

Base.metadata.create_all(bind=engine)
