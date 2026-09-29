import { integer, sqliteTable, text } from "drizzle-orm/sqlite-core";

import { instantMillis, instantSeconds } from "./columns";

export const STORAGE_TYPES = ["local", "smb", "removable"] as const;
export type StorageType = (typeof STORAGE_TYPES)[number];

export const EVENT_TYPES = ["normal", "gravitational", "switch"] as const;
export type EventType = (typeof EVENT_TYPES)[number];

export const DIRECTIONS = ["front", "rear"] as const;
export type Direction = (typeof DIRECTIONS)[number];

export const storages = sqliteTable("storages", {
  id: text().primaryKey(),
  type: text({ enum: STORAGE_TYPES }).notNull(),
  connection: text(),
  path: text().notNull(),
});

export const videoFiles = sqliteTable("video_files", {
  id: text().primaryKey(),
  storageId: text("storage_id").notNull().references(() => storages.id),
  mtime: instantMillis().notNull(),
  rawPath: text("raw_path").notNull(),
  rawSize: integer("raw_size").notNull(),
  eventType: text("event_type", { enum: EVENT_TYPES }).notNull(),
  direction: text({ enum: DIRECTIONS }).notNull(),
  timestamp: instantSeconds().notNull(),
});

export type Storage = typeof storages.$inferSelect;
export type NewStorage = typeof storages.$inferInsert;
export type VideoFile = typeof videoFiles.$inferSelect;
export type NewVideoFile = typeof videoFiles.$inferInsert;
