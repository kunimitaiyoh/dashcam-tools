from contextlib import contextmanager
from datetime import datetime, UTC
import enum
import re
from typing import Optional, Iterator, Type

from sqlalchemy import Dialect, String, Boolean, Text, ForeignKey, Date, Integer, BigInteger, Double, UniqueConstraint, TypeDecorator, create_engine
from sqlalchemy.orm import Mapped, mapped_column, relationship, sessionmaker, Session, declarative_base, sessionmaker, DeclarativeBase
from sqlalchemy.types import DateTime, String

from dashcamtools.settings import DATABASE_URL

PATTERN_VIDEO_NAME = re.compile(r"^(\d{8})_(\d{10})_(N|G|S)(F|R).MP4$", flags=re.I)
FORMAT_TIMESTAMP = "%y%m%d%H%M"


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
    cache_ok = True

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
    cache_ok = True

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

class VideoDirection(enum.Enum):
    FRONT = "front"
    REAR = "rear"

class VideoFile(Base):
    __tablename__ = "video_files"

    name: Mapped[str] = mapped_column(String(255), primary_key=True)
    direction: Mapped[VideoDirection] = mapped_column(StrEnum(VideoDirection), nullable=True)
    is_event: Mapped[bool] = mapped_column(Boolean, nullable=True)
    recorded_at_m: Mapped[int] = mapped_column(Integer, nullable=True, index=True)
    mtime: Mapped[datetime] = mapped_column(UTCTimestamp, nullable=False, index=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    def fill_attributes(self) -> "VideoFile":
        matched = PATTERN_VIDEO_NAME.search(self.name)
        timestamp = datetime.strptime(matched[2], FORMAT_TIMESTAMP)
        
        self.recorded_at_m = int(timestamp.timestamp()) // 60
        self.direction = VideoFile.parse_direction(matched[4])
        self.is_event = VideoFile.parse_event_type(matched[3])
        return self

    @property
    def recorded_at(self) -> datetime:
        return datetime.fromtimestamp(self.recorded_at_m * 60)

    @staticmethod
    def from_name(name: str, mtime: datetime) -> "VideoFile":
        return VideoFile(name=name, mtime=mtime).fill_attributes()

    @staticmethod
    def parse_event_type(value: str) -> bool:
        match value:
            case "N":
                return False
            case "G":
                return True
            case "S":
                return True
            case _:
                raise ValueError()

    @staticmethod
    def parse_direction(value: str) -> VideoDirection:
        match value:
            case "F":
                return VideoDirection.FRONT
            case "R":
                return VideoDirection.REAR
            case _:
                raise ValueError()

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
