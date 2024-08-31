from pathlib import Path


class VideoPart:
    def __init__(self, path: Path, timestamp: int, is_front: str, is_event: bool) -> None:
        self.path = path

        # タイムスタンプ。分単位の整数（エポック秒を 60 でわったもの）。
        self.timestamp = timestamp
        self.is_event = is_event
        self.is_front = is_front

    def __lt__(self, another: "VideoPart"):
        if self.is_front != another.is_front:
            return self.is_front
        
        return self.timestamp < another.timestamp
    
    def is_next_to(self, another: "VideoPart"):
        return self.is_front == another.is_front and (another.timestamp != (self.timestamp - 1))
