from typing import Iterable, Sequence

from sqlalchemy import func, delete, select, Delete, Select
from sqlalchemy.orm import Session

from dashcamtools.orm import Log, Report, VideoFile
from dashcamtools.util import Snowflake

class VideoFileRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def add(self, video: VideoFile) -> VideoFile:
        self.db.add(video)
        return video
    
    def find_by_name(self, name: str) -> VideoFile | None:
        return self.db.execute(select(VideoFile).filter(VideoFile.name == name)).scalar()

    def list_by_names(self, names: Iterable[str]) -> Sequence[VideoFile]:
        query = select(VideoFile).filter(VideoFile.name.in_(names)).order_by(Video.mtime.asc())
        return self.db.execute(query).scalars().all()

    def fill_attributes_all(self) -> None:
        query = select(VideoFile).filter(VideoFile.is_rear == None or VideoFile.is_rear == None or VideoFile.recorded_at == None)
        for video in self.db.execute(query).scalars().all():
            video.fill_attributes()
            print(video)
            print(video.recorded_at)

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
