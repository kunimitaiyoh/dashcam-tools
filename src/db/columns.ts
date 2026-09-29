import { customType } from "drizzle-orm/sqlite-core";

export const instantSeconds = customType<{ data: Temporal.Instant; driverData: number }>({
  dataType: () => "integer",
  toDriver: (value) => Math.floor(value.epochMilliseconds / 1000),
  fromDriver: (value) => Temporal.Instant.fromEpochMilliseconds(value * 1000),
});

export const instantMillis = customType<{ data: Temporal.Instant; driverData: number }>({
  dataType: () => "integer",
  toDriver: (value) => value.epochMilliseconds,
  fromDriver: (value) => Temporal.Instant.fromEpochMilliseconds(value),
});
