import { UsageError } from "clipanion";
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";

import { loadConfig } from "./config";

describe("loadConfig", () => {
  let dir: string;

  beforeEach(() => {
    dir = mkdtempSync(join(tmpdir(), "dashcams-config-"));
  });

  afterEach(() => {
    rmSync(dir, { recursive: true, force: true });
  });

  it("最初に存在する候補だけを読む", () => {
    const first = join(dir, "first.toml");
    const second = join(dir, "second.toml");
    writeFileSync(second, '[database]\npath = "/var/lib/dashcams/second.db"\n');
    expect(loadConfig([first, second])).toEqual({ database: { path: "/var/lib/dashcams/second.db" } });
  });

  it("候補が 1 つも存在しなければ UsageError", () => {
    expect(() => loadConfig([join(dir, "missing.toml")])).toThrow(UsageError);
  });

  it("相対パスは拒否する", () => {
    const file = join(dir, "config.toml");
    writeFileSync(file, '[database]\npath = "./dashcams.db"\n');
    expect(() => loadConfig([file])).toThrow(/database\.path/);
  });

  it("未知の項目は拒否する", () => {
    const file = join(dir, "config.toml");
    writeFileSync(file, '[database]\npath = "/tmp/dashcams.db"\nurl = "x"\n');
    expect(() => loadConfig([file])).toThrow(UsageError);
  });

  it("不正な TOML は下位候補に切り替えず UsageError", () => {
    const first = join(dir, "first.toml");
    const second = join(dir, "second.toml");
    writeFileSync(first, "[database\n");
    writeFileSync(second, '[database]\npath = "/tmp/dashcams.db"\n');
    expect(() => loadConfig([first, second])).toThrow(UsageError);
  });
});
