import argparse

from dashcamtools.orm import get_db
from dashcamtools.repositories import VideoFileRepository

parser = argparse.ArgumentParser()

args = parser.parse_args()

def main():
    with get_db() as db:
        video_repository = VideoFileRepository(db)
        video_repository.fill_attributes_all()
        db.commit()
