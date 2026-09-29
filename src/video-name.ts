import type { Direction, EventType } from "./db/schema";

const PATTERN = /^(?<sequence>\d{8})_(?<year>\d{2})(?<month>\d{2})(?<day>\d{2})(?<hour>\d{2})(?<minute>\d{2})_(?<event>[NGS])(?<direction>[FR])\.MP4$/i;

export const RECORDER_TIME_ZONE = "Asia/Tokyo";

const EVENT_TYPE_BY_CODE: Readonly<Record<string, EventType>> = { N: "normal", G: "gravitational", S: "switch" };
const DIRECTION_BY_CODE: Readonly<Record<string, Direction>> = { F: "front", R: "rear" };

export interface VideoNameAttributes {
  readonly timestamp: Temporal.Instant;
  readonly eventType: EventType;
  readonly direction: Direction;
}

export function parseVideoName(name: string): VideoNameAttributes | undefined {
  const groups = PATTERN.exec(name)?.groups;
  if (groups === undefined) return undefined;

  const { year, month, day, hour, minute, event, direction } = groups;
  const timestamp = Temporal.ZonedDateTime.from({
    timeZone: RECORDER_TIME_ZONE,
    year: 2000 + Number(year),
    month: Number(month),
    day: Number(day),
    hour: Number(hour),
    minute: Number(minute),
  }, { overflow: "reject" }).toInstant();

  return {
    timestamp,
    eventType: EVENT_TYPE_BY_CODE[event.toUpperCase()],
    direction: DIRECTION_BY_CODE[direction.toUpperCase()],
  };
}
