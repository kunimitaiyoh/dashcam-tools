import { UsageError } from "clipanion";
import { readFileSync } from "node:fs";
import { homedir } from "node:os";
import { isAbsolute, join } from "node:path";
import { parse } from "smol-toml";
import * as v from "valibot";

import { packageRoot } from "./paths";

const AbsolutePath = v.pipe(v.string(), v.check(isAbsolute, "絶対パスを指定してください"));
const ConfigSchema = v.pipe(v.strictObject({
  database: v.pipe(v.strictObject({ path: AbsolutePath }), v.readonly()),
}), v.readonly());

export type Config = v.InferOutput<typeof ConfigSchema>;

export const defaultConfigCandidates = (): readonly string[] => [
  join(packageRoot, "config.toml"),
  join(homedir(), ".config", "dashcams", "config.toml"),
];

export function loadConfig(candidates: readonly string[] = defaultConfigCandidates()): Config {
  for (const file of candidates) {
    try {
      const result = v.safeParse(ConfigSchema, parse(readFileSync(file, "utf8")));
      if (!result.success) {
        throw new Error(result.issues.map((issue) => `${v.getDotPath(issue) ?? "<root>"}: ${issue.message}`).join("\n"));
      }
      return result.output;
    } catch (error) {
      if (error instanceof Error && "code" in error && error.code === "ENOENT") continue;
      throw new UsageError(`${file}: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
  throw new UsageError(`設定ファイルが見つかりません。探索先:\n${candidates.join("\n")}`);
}
