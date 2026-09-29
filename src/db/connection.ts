import Database from "better-sqlite3";
import { BetterSQLite3Database, drizzle } from "drizzle-orm/better-sqlite3";
import { mkdirSync } from "node:fs";
import { dirname } from "node:path";

import * as schema from "./schema";

export type Db = BetterSQLite3Database<typeof schema>;

export function openDatabase(path: string): Db {
  mkdirSync(dirname(path), { recursive: true });
  const client = new Database(path);
  client.pragma("foreign_keys = ON");
  return drizzle({ client, schema });
}
