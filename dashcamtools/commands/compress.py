import _csv
import argparse
import csv
from datetime import datetime, timezone, UTC
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time 
import traceback

from dashcamtools.orm import get_db, Log, LogSeverity, Report, ReportStatus, Video
from dashcamtools.util import iso8601, resolve_unique_path, temporary_path, Snowflake
from dashcamtools.repositories import LogRepository, ReportRepository, VideoRepository

parser = argparse.ArgumentParser()
parser.add_argument("storage_dir", metavar="storage-dir", type=Path)
parser.add_argument("--nvenc", action="store_true")

args = parser.parse_args()

storage_dir: Path = args.storage_dir
nvenc: bool = args.nvenc

source_dir: Path = storage_dir / "Raw"
target_dir: Path = storage_dir / "Archive"
trash_dir: Path = storage_dir / "Trash"
remote_temp_dir: Path = storage_dir / "Temp"

def main():
    def do_compress(input_path: str, output_path: str) -> subprocess.CompletedProcess:
        def resolve_command():
            if nvenc:
                return [
                    "ffmpeg", 
                    "-y", # overwrite
                    "-loglevel", "error",
                    "-i", input_path, 
                    "-map", "0",
                    "-c:v", "h264_nvenc", 
                    "-c:a", "copy",
                    "-cq", "30",
                    "-preset", "p7",
                    "-profile", "high",
                    output_path,
                ]
            else:
                return [
                    "ffmpeg", 
                    "-y", # overwrite
                    "-loglevel", "error",
                    "-i", input_path, 
                    "-map", "0", 
                    "-crf", "28", 
                    "-c:v", "libx264", 
                    "-c:a", "copy", 
                    output_path,
                ]
        return subprocess.run(resolve_command())

    def set_timestamp(source_stat: os.stat_result, output: Path):
        os.utime(output, (source_stat.st_atime, source_stat.st_mtime))

    def move_to_trash(source: Path) -> Path:
        destination = resolve_unique_path(trash_dir / source.name)
        shutil.move(source, destination)
        return destination

    with get_db() as db:
        video_repository = VideoRepository(db)
        report_repository = ReportRepository(db)
        log_repository = LogRepository(db, snowflake=Snowflake(machine_id=0))

        def print_log(text: str, severity: LogSeverity = LogSeverity.INFO):
            try:
                print(text, file=sys.stderr)
                log_repository.create(Log(severity=severity, text=text, timestamp=datetime.now(tz=timezone.utc)))
            except Exception as e:
                print(e, file=sys.stderr)

        print_log(f"Starting job... (storage_dir: {storage_dir}, nvenc: {nvenc})")

        for dir in [source_dir, target_dir, trash_dir, remote_temp_dir]:
            dir.mkdir(parents=True, exist_ok=True)

        # source_dir からすべてのファイルを取得し、それに応じて videos レコードを追加します。
        print_log("First, get all files from the source directory...")
        sources = list(source_dir.glob("*.mp4"))
        source_names = [source.name for source in sources]
        existing_video_names: set[str] = { record.name for record in video_repository.list_by_names(source_names) }
        
        new_source = [source for source in sources if source.name not in existing_video_names]
        print_log(f"Collecting information of {len(new_source)} file(s)...")
        for source in new_source:
            mtime = datetime.fromtimestamp(os.path.getmtime(source), tz=UTC)
            record = Video(name=source.name, mtime=mtime)
            video_repository.add(record)
        db.commit()
        print_log("Collecting information of files completed.")

        source_videos = video_repository.list_by_names(source_names) 
        source_paths = { path.name: path for path in sources }
        for source, video in [(source_paths[source_video.name], source_video) for source_video in source_videos]:
            start = time.perf_counter()
            started_at = datetime.now(tz=timezone.utc)
        
            try:
                destination = target_dir / source.name
                if destination.exists():
                    trash_file = move_to_trash(source)

                    print_log(f"{source.name}: already exists in the destination. skipped. (moved to: {trash_file})")
                    report_repository.create(Report(started_at=started_at, name=source.name, status=ReportStatus.SKIPPED))
                    continue
                
                with temporary_path(suffix=source.suffix) as copy:
                    download_start = time.perf_counter()
                    shutil.copy(source, copy)
                    download_end = time.perf_counter()

                    with temporary_path(suffix=source.suffix) as output:
                        compress_start = time.perf_counter()
                        result = do_compress(str(copy), str(output))
                        result.check_returncode()

                        compress_end = time.perf_counter()
                        
                        source_stat = source.stat()
                        output_stat = output.stat()
                        set_timestamp(source_stat, output)

                        source_mtime = datetime.fromtimestamp(source_stat.st_mtime, tz=timezone.utc)

                        upload_start = time.perf_counter()
                        with temporary_path(suffix=source.suffix, dir=remote_temp_dir) as temp_output:
                            shutil.move(output, temp_output)
                            shutil.move(temp_output, destination)
                        upload_end = time.perf_counter()
                        
                        move_to_trash(source)
                        video.is_archived = True
                        db.commit()

                        duration_compress = compress_end - compress_start
                        duration = upload_end - start

                        print_log(f"{source.name}: completed in {duration:.3f} seconds. (compress: {(duration_compress):.3f} seconds)")
                        
                        codec = "h264_nvenc" if nvenc else "libx264"
                        report_repository.create(Report(started_at=started_at, name=source.name, status=ReportStatus.SUCCESSFUL, mtime=source_mtime, original_bytes=source_stat.st_size, compressed_bytes=output_stat.st_size, codec=codec, duration_download=download_end - download_start, duration_compress=duration_compress, duration_upload=upload_end - upload_start, duration=duration))

            except KeyboardInterrupt as e:
                raise e

            except subprocess.CalledProcessError as e:
                print_log(f"{source.name}: failed.", severity=LogSeverity.ERROR)
                print_log(e.stderr, severity=LogSeverity.ERROR)
                report_repository.create(Report(started_at=started_at, name=source.name, status=ReportStatus.FAILED))
                
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print_log("".join(traceback.format_exception(exc_type, exc_value, exc_traceback)), severity=LogSeverity.ERROR)
                report_repository.create(Report(started_at=started_at, name=source.name, status=ReportStatus.FAILED))

if __name__ == "__main__":
    main()
