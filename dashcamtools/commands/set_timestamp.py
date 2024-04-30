import argparse
from datetime import datetime
import os
from pathlib import Path
import sys
from win32_setctime import setctime


parser = argparse.ArgumentParser()
parser.add_argument("glob", type=str)
parser.add_argument("source_dir", metavar="source-dir", type=Path)
parser.add_argument("target_dir", metavar="target-dir", type=Path)
parser.add_argument("-q", "--quiet", action="store_true")

args = parser.parse_args()

glob: str = args.glob
source_dir: Path = args.source_dir
target_dir: Path = args.target_dir
quiet: bool = args.quiet

def main():
    def format(timestamp: float) -> str:
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    
    for source in source_dir.glob(glob):
        target = target_dir / source.name
        if not target.exists():
            if not quiet:
                print(f"{source.name}: file does not exist in the target.", file=sys.stderr)
            continue

        source_stat = source.stat()
        target_stat = target.stat()

        if (target_stat.st_mtime - source_stat.st_mtime) == 0.0 and (target_stat.st_ctime - source_stat.st_ctime) == 0.0:
            if not quiet:
                print(f"{source.name}: timestamp is already set. skipped.")
            continue

        print(f"{source.name}: {format(source_stat.st_mtime)} {format(source_stat.st_ctime)}")
        os.utime(target, (source_stat.st_atime, source_stat.st_mtime))
        setctime(target, source_stat.st_ctime)


if __name__ == "__main__":
    main()
