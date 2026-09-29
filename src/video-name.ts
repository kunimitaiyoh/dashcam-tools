import type { Direction, EventType } from "./db/schema";

// 例: 00004929_2409141309_NF.MP4 → 2024-09-14 13:09、N (normal)、F (front)
const PATTERN = /^\d{8}_(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})_([NGS])([FR])\.MP4$/i;

// ファイル名の時刻はレコーダーのローカル時刻。
export const RECORDER_TIME_ZONE = "Asia/Tokyo";

const EVENT_TYPE_BY_CODE: Readonly<Record<string, EventType>> = { N: "normal", G: "gravitational", S: "switch" };
const DIRECTION_BY_CODE: Readonly<Record<string, Direction>> = { F: "front", R: "rear" };

export interface VideoNameAttributes {
  readonly timestamp: Temporal.Instant;
  readonly eventType: EventType;
  readonly direction: Direction;
}

export function parseVideoName(name: string): VideoNameAttributes | undefined {
  const matched = PATTERN.exec(name);
  if (!matched) return undefined;

  const [, yy, mm, dd, hh, mi, eventCode, directionCode] = matched;
  const timestamp = Temporal.ZonedDateTime.from({
    timeZone: RECORDER_TIME_ZONE,
    year: 2000 + Number(yy),
    month: Number(mm),
    day: Number(dd),
    hour: Number(hh),
    minute: Number(mi),
  }, { overflow: "reject" }).toInstant();

  return {
    timestamp,
    eventType: EVENT_TYPE_BY_CODE[eventCode.toUpperCase()],
    direction: DIRECTION_BY_CODE[directionCode.toUpperCase()],
  };
}
