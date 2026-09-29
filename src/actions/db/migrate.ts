import { migrate } from "drizzle-orm/better-sqlite3/migrator";
import { join } from "node:path";

import type { Db } from "../../db/connection";
import { packageRoot } from "../../paths";

export const migrationsFolder = join(packageRoot, "drizzle");

export function migrateDatabase(db: Db): void {
  migrate(db, { migrationsFolder });
}
