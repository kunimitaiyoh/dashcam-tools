from contextlib import contextmanager
from datetime import datetime
import os
from pathlib import Path
from typing import Generator
import tempfile

@contextmanager
def temporary_path(suffix: str | None = None) -> Generator[Path, None, None]:
    temp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    path = Path(temp.name)
    try:
        temp.close()
        yield path
    finally:
        path.unlink(missing_ok=True)

def resolve_unique_path(destination: Path) -> Path:
    if not destination.exists():
        return destination
    
    parent = destination.parent
    stem = destination.stem
    suffix = destination.suffix
    
    index = 1
    while True:
        new_path = parent / f"{stem} ({index}){suffix}"
        if not new_path.exists():
            return new_path
        index += 1

def iso8601(datetime: datetime) -> str:
    return datetime.isoformat(timespec="milliseconds").replace("+00:00", "Z")
