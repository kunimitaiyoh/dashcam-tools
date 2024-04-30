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


def iso8601(datetime: datetime) -> str:
    return datetime.isoformat(timespec="milliseconds").replace("+00:00", "Z")
