from typing import Iterable, Sequence

from sqlalchemy import func, delete, select, Delete, Select
from sqlalchemy.orm import Session

from dashcamtools.orm import Log, Report, Video
from dashcamtools.util import Snowflake

class VideoRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def add(self, video: Video) -> Video:
        self.db.add(video)
        return video
    
    def find_by_name(self, name: str) -> Video | None:
        return self.db.execute(select(Video).filter(Video.name == name)).scalar()
    
    def list_by_names(self, names: Iterable[str]) -> Sequence[Video]:
        query = select(Video).filter(Video.name.in_(names))
        return self.db.execute(query).scalars().all()
    
    def list_unarchived(self) -> Sequence[Video]:
        query = select(Video).filter(Video.is_archived == False).order_by(Video.mtime.asc)
        return self.db.execute(query).scalars().all()

class ReportRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, report: Report) -> Report:
        self.db.add(report)
        self.db.commit()
        return report

class LogRepository:
    def __init__(self, db: Session, snowflake: Snowflake):
        self.db = db
        self.snowflake = snowflake

    def create(self, log: Log) -> Log:
        log.id = self.snowflake.generate()

        self.db.add(log)
        self.db.commit()
        return log
