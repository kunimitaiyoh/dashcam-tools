import { UsageError } from "clipanion";
import { chmodSync, existsSync, mkdirSync, mkdtempSync, readdirSync, rmSync, utimesSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";

import { Db, openDatabase } from "../../db/connection";
import { storages, videoFiles } from "../../db/schema";
import { migrateDatabase } from "../db/migrate";
import { syncFiles } from "./sync";

describe("syncFiles", () => {
  let root: string;
  let db: Db;

  beforeEach(() => {
    root = mkdtempSync(join(tmpdir(), "dashcams-sync-"));
    mkdirSync(join(root, "inbox"));
    db = openDatabase(":memory:");
    migrateDatabase(db);
    db.insert(storages).values({ id: "test", type: "local", connection: null, path: root }).run();
  });

  afterEach(() => {
    if (existsSync(join(root, "raw"))) chmodSync(join(root, "raw"), 0o755);
    rmSync(root, { recursive: true, force: true });
  });

  const putInbox = (name: string, content = "x"): void => writeFileSync(join(root, "inbox", name), content);

  it("規則に合うファイルを登録して raw へ移動する", () => {
    putInbox("00004929_2409141309_NF.MP4", "abc");
    utimesSync(join(root, "inbox", "00004929_2409141309_NF.MP4"), 1_700_000_000, 1_700_000_000.5);

    const outcomes = syncFiles(db, "test");

    expect(outcomes).toEqual([{ kind: "registered", name: "00004929_2409141309_NF.MP4" }]);
    expect(readdirSync(join(root, "inbox"))).toEqual([]);
    expect(existsSync(join(root, "raw", "00004929_2409141309_NF.MP4"))).toBe(true);

    const row = db.select().from(videoFiles).get();
    expect(row).toMatchObject({
      id: "00004929_2409141309_NF.MP4",
      storageId: "test",
      rawPath: "raw/00004929_2409141309_NF.MP4",
      rawSize: 3,
      eventType: "normal",
      direction: "front",
    });
    expect(row?.timestamp.epochMilliseconds).toBe(Temporal.Instant.from("2024-09-14T04:09:00Z").epochMilliseconds);
    expect(row?.mtime.epochMilliseconds).toBe(1_700_000_000_500);
  });

  it("登録済みの id は無視する", () => {
    putInbox("00004929_2409141309_NF.MP4");
    syncFiles(db, "test");
    putInbox("00004929_2409141309_NF.MP4", "second");

    expect(syncFiles(db, "test")).toEqual([{ kind: "ignored-registered", name: "00004929_2409141309_NF.MP4" }]);
    expect(existsSync(join(root, "inbox", "00004929_2409141309_NF.MP4"))).toBe(true);
    expect(db.select().from(videoFiles).all()).toHaveLength(1);
  });

  it("raw に同名ファイルが残っていれば登録せず無視する", () => {
    mkdirSync(join(root, "raw"));
    writeFileSync(join(root, "raw", "00004929_2409141309_NF.MP4"), "old");
    putInbox("00004929_2409141309_NF.MP4", "new");

    expect(syncFiles(db, "test")).toEqual([{ kind: "ignored-raw-exists", name: "00004929_2409141309_NF.MP4" }]);
    expect(db.select().from(videoFiles).all()).toHaveLength(0);
    expect(existsSync(join(root, "inbox", "00004929_2409141309_NF.MP4"))).toBe(true);
  });

  it("規則に合わない名前はスキップする", () => {
    putInbox("notes.txt");
    expect(syncFiles(db, "test")).toEqual([{ kind: "skipped-name", name: "notes.txt" }]);
    expect(existsSync(join(root, "inbox", "notes.txt"))).toBe(true);
  });

  it("移動に失敗すれば登録をロールバックする", () => {
    mkdirSync(join(root, "raw"));
    chmodSync(join(root, "raw"), 0o555);
    putInbox("00004929_2409141309_NF.MP4");

    const [outcome] = syncFiles(db, "test");
    expect(outcome).toMatchObject({ kind: "failed", name: "00004929_2409141309_NF.MP4" });
    expect(db.select().from(videoFiles).all()).toHaveLength(0);
    expect(existsSync(join(root, "inbox", "00004929_2409141309_NF.MP4"))).toBe(true);
  });

  it("未登録のストレージは UsageError", () => {
    expect(() => syncFiles(db, "nope")).toThrow(UsageError);
  });

  it("inbox がなければ UsageError", () => {
    rmSync(join(root, "inbox"), { recursive: true });
    expect(() => syncFiles(db, "test")).toThrow(UsageError);
  });
});
