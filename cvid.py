import argparse
from datetime import datetime
from pathlib import Path
import re
import subprocess
import sys
import tempfile

PATTERN_VIDEO_NAME = re.compile(r"^\d{8}_(\d{10})_NF.MP4$", flags=re.I)
FORMAT_TIMESTAMP = "%y%m%d%H%M"

parser = argparse.ArgumentParser()
parser.add_argument("videos")
parser.add_argument("destination")

args = args = parser.parse_args()

videos = Path(args.videos)
destination =  Path(args.destination)

def concatenate_videos(video_paths: list[Path], output_path: Path):
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", encoding="utf-8", delete=False) as file_list_path:
        file_list = "".join([f"file '{str(path)}'\n" for path in video_paths])
        file_list_path.write(file_list)
        file_list_path.flush()
        
        command = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", str(file_list_path.name),
            "-map", "0",
            "-crf", str(28),
            "-c:v", "libx264",
            str(output_path),
        ]
        
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(result.stdout.decode())

def group_videos(paths: list[Path]) -> list[list[Path]]:
    last_timestamp: int | None = None
    groups: list[list[Path]] = []
    group_in_progress: list[Path] = []
    
    for path in paths:
        matched = PATTERN_VIDEO_NAME.search(path.name)
        timestamp = datetime.strptime(matched[1], FORMAT_TIMESTAMP)
        timestamp.replace(year=2000 + timestamp.year)
        unix_minute = int(timestamp.timestamp()) // 60
        
        if last_timestamp is not None and last_timestamp != (unix_minute - 1):
            groups.append(group_in_progress)
            group_in_progress = []
        
        group_in_progress.append(path)
        last_timestamp = unix_minute
    
    # ループの中で最後に作られたグループを追加する
    if last_timestamp is not None:
        groups.append(group_in_progress)

    return groups

def main():
    # p.stem[9:] は、最初の 8 けたの連番を除いたものを得る。
    paths = sorted([video for video in videos.glob("*.mp4") if PATTERN_VIDEO_NAME.search(video.name)], key=lambda p: p.stem[9:])
    groups = group_videos(paths)
    
    for group in groups:
        timestamp = datetime.strptime(PATTERN_VIDEO_NAME.search(group[0].name)[1], FORMAT_TIMESTAMP)
        timestamp.replace(year=2000 + timestamp.year)
        output = destination / f"{timestamp.strftime('%Y%m%d-%H%M')}F.mp4"
        
        if output.exists():
            print(f"File {output.name} already exists. Skipped.", file=sys.stderr)
            continue

        concatenate_videos(group, output)

if __name__ == "__main__":
    main()
