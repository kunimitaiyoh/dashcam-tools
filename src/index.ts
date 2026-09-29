import { Builtins, Cli } from "clipanion";

import { MigrateDbCommand } from "./commands/db";
import { SyncFilesCommand } from "./commands/files";
import { AddStorageCommand } from "./commands/storages";

const cli = Cli.from([
  Builtins.HelpCommand,
  AddStorageCommand,
  SyncFilesCommand,
  MigrateDbCommand,
], { binaryName: "dashcams", binaryLabel: "Dashcam Tools" });

void cli.runExit(process.argv.slice(2), Cli.defaultContext);
