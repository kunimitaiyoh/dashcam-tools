import argparse
from datetime import datetime
import os
from pathlib import Path
import sys
from win32_setctime import setctime
import re
import statistics
import subprocess

from dashcamtools.util import temporary_path


PATTERN_LINE = re.compile(r"^n:\d+\s+.+\s+All:([\d+\.]+)\s\((.+?)\)$")

parser = argparse.ArgumentParser()
parser.add_argument("targets", type=Path, nargs="+")
parser.add_argument("original", type=Path)

args = parser.parse_args()

targets: list[Path] = args.targets
original: Path = args.original

def main():
    def do_ssim(target: Path, original: Path) -> str:
        command = [
            "ffmpeg",
            "-y",
            "-loglevel", "error",
            "-i", target,
            "-i", original,
            "-filter_complex", f"ssim=f=-",
            "-an",
            "-f", "null",
            "-"
        ]
        result = subprocess.run(command, capture_output=True, text=True).stdout
        return result


    def extract_statistics(name: str, output: str) -> "map[str]":
        alls = []
        dbs = []

        for line in output.splitlines():
            match = PATTERN_LINE.search(line)
            if not match:
                continue
        
            (all, db) = match.groups()
            
            alls.append(float(all))
            dbs.append(float(db))

        min_all = min(alls)
        max_all = max(alls)
        all_mean = statistics.mean(alls)
        all_stddev = statistics.stdev(alls)
        
        min_db = min(dbs)
        max_db = max(dbs)
        db_mean = statistics.mean(dbs)
        db_stddev = statistics.stdev(dbs)

        values = [name, min_all, max_all, all_mean, all_stddev, min_db, max_db, db_mean, db_stddev]
        return map(str, values)

    original_stat = original.stat()

    for target in targets:
        ssim_log = do_ssim(target, original)
        stats = [str(target.stat().st_size), str(original_stat.st_size)] + list(extract_statistics(target.name, ssim_log))
        print("\t".join(stats))

if __name__ == "__main__":
    main()
