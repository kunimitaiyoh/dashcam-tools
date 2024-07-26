import _csv
import argparse
import csv
from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time 
import traceback

from dashcamtools.util import iso8601, resolve_unique_path, temporary_path


null_path = Path("NUL" if os.name == "nt" else "/dev/null")

parser = argparse.ArgumentParser()
parser.add_argument("source_dir", metavar="source-dir", type=Path)
parser.add_argument("target_dir", metavar="target-dir", type=Path)
parser.add_argument("trash_dir", metavar="trash-dir", type=Path)
parser.add_argument("--report", type=Path)
parser.add_argument("--nvenc", action="store_true")

args = parser.parse_args()

source_dir: Path = args.source_dir
target_dir: Path = args.target_dir
trash_dir: Path = args.trash_dir
report: Path = args.report if args.report is not None else null_path
nvenc: bool = args.nvenc

def main():
    def write_report(
            writer: "_csv._writer",
            started_at: datetime,
            name: str,
            status: str,
            mtime: datetime | None = None,
            original_bytes: int | None = None,
            compressed_bytes: int | None = None,
            duration_download: float | None = None,
            duration_compress: float | None = None,
            duration_upload: float | None = None,
            duration: float | None = None,
        ):
        row: list[str| None] = [
            iso8601(started_at),
            name,
            status, 
            iso8601(mtime) if mtime else None,
            str(original_bytes) if original_bytes is not None else None,
            str(compressed_bytes) if compressed_bytes is not None else None, 
            str(duration_download * 1000) if duration_download is not None else None, 
            str(duration_compress * 1000) if duration_compress is not None else None,
            str(duration_upload * 1000) if duration_upload is not None else None,
            str(duration * 1000) if duration is not None else None,
        ]
        writer.writerow([value if value is not None else "" for value in row])

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

    sources = sorted(source_dir.glob("*.mp4"), key=os.path.getmtime)
    for source in sources:
        start = time.perf_counter()
        
        with report.open(mode="a", newline="", encoding="utf-8") as report_file:
            report_writer = csv.writer(report_file)
            started_at = datetime.now(tz=timezone.utc)

            try:
                destination = target_dir / source.name
                if destination.exists():
                    trash_file = move_to_trash(source)
                    print(f"{source.name}: already exists in the destination. skipped. (moved to: {trash_file})")
                    write_report(report_writer, started_at, source.name, "skipped")
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
                        shutil.move(output, destination)
                        upload_end = time.perf_counter()
                        
                        move_to_trash(source)

                        duration_compress = compress_end - compress_start
                        duration = upload_end - start

                        print(f"{source.name}: completed in {duration:.3f} seconds. (compress: {(duration_compress):.3f} seconds)", flush=True)
                        write_report(report_writer, started_at, source.name, "successful", source_mtime, source_stat.st_size, output_stat.st_size, download_end - download_start, duration_compress, upload_end - upload_start, duration)
                        report_file.flush()

            except KeyboardInterrupt as e:
                raise e

            except subprocess.CalledProcessError as e:
                print(f"{source.name}: failed.")
                print(e.stderr, file=sys.stderr)
                write_report(report_writer, started_at, source.name, "failed")
                
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print("".join(traceback.format_exception(exc_type, exc_value, exc_traceback)), file=sys.stderr)
                write_report(report_writer, started_at, source.name, "failed")


if __name__ == "__main__":
    main()
