import { Command } from "clipanion";

import { migrateDatabase } from "../actions/db/migrate";
import { loadConfig } from "../config";
import { openDatabase } from "../db/connection";

export class MigrateDbCommand extends Command {
  static paths = [["db", "migrate"]];
  static usage = Command.Usage({ description: "データベースに未適用のマイグレーションを適用する" });

  async execute(): Promise<void> {
    const config = loadConfig();
    migrateDatabase(openDatabase(config.database.path));
    this.context.stdout.write(`migrated: ${config.database.path}\n`);
  }
}
