import argparse
from datetime import datetime
import os
from pathlib import Path
import shutil
import sys
import tempfile
from win32_setctime import setctime


parser = argparse.ArgumentParser()
parser.add_argument("source_dir", metavar="source-dir", type=Path)
parser.add_argument("target_dir", metavar="target-dir", type=Path)

args = parser.parse_args()

source_dir: Path = args.source_dir
target_dir: Path = args.destination

def main():
    for source in source_dir.glob("*.mp4"):
        with tempfile.NamedTemporaryFile(suffix=source.suffix) as copy:
            with tempfile.NamedTemporaryFile(suffix=source.suffix) as 
            shutil.copy(source, copy.name)
            
            
            shutil.copy()
            source.

        target = target_dir / source.name
        if target.exists():
            print(f"{source.name}: already exists in the destination.", file=sys.stderr)
            continue

        
        output_file = target_dir / source.name


if __name__ == "__main__":
    main()
