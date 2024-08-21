from contextlib import contextmanager
from datetime import datetime
import os
from pathlib import Path
from typing import Generator
import tempfile
import time

# 2010-11-04T01:42:54.657Z
ORIGINAL_TIMESTAMP = 1288834974657

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

class Snowflake:
    def __init__(self, machine_id: int) -> None:
        self.machine_id = machine_id
        self.epoch = ORIGINAL_TIMESTAMP
        self.sequence = 0
        self.last_timestamp = -1

        self.machine_id_bits = 10
        self.sequence_bits = 12

        self.max_machine_id = -1 ^ (-1 << self.machine_id_bits)
        self.max_sequence = -1 ^ (-1 << self.sequence_bits)

        self.machine_id_shift = self.sequence_bits
        self.timestamp_shift = self.sequence_bits + self.machine_id_bits

        if self.machine_id > self.max_machine_id or self.machine_id < 0:
            raise ValueError(f"machine_id must be between 0 and {self.max_machine_id}")

    def generate(self) -> int:
        timestamp = self._timestamp()

        if timestamp < self.last_timestamp:
            raise Exception("Clock moved backwards. Refusing to generate id")

        if self.last_timestamp == timestamp:
            self.sequence = (self.sequence + 1) & self.max_sequence
            if self.sequence == 0:
                timestamp = self._wait_next_millis(self.last_timestamp)
        else:
            self.sequence = 0

        self.last_timestamp = timestamp

        snowflake_id = ((timestamp - self.epoch) << self.timestamp_shift) | \
                       (self.machine_id << self.machine_id_shift) | \
                       self.sequence

        return snowflake_id

    def _timestamp(self) -> int:
        return int(time.time() * 1000)

    def _wait_next_millis(self, last_timestamp: int) -> int:
        timestamp = self._timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._timestamp()
        return timestamp


