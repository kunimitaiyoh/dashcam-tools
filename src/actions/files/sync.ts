import { UsageError } from "clipanion";
import { eq } from "drizzle-orm";
import { existsSync, mkdirSync, readdirSync, renameSync, statSync } from "node:fs";
import { join } from "node:path";

import type { Db } from "../../db/connection";
import { NewVideoFile, storages, videoFiles } from "../../db/schema";
import { Findmnt, resolveStorageRoot, runFindmnt } from "../../mounts";
import { parseVideoName } from "../../video-name";

export const INBOX_DIR = "inbox";
export const RAW_DIR = "raw";

export type SyncOutcome =
  | { readonly kind: "registered"; readonly name: string }
  | { readonly kind: "ignored-registered"; readonly name: string }
  | { readonly kind: "ignored-raw-exists"; readonly name: string }
  | { readonly kind: "skipped-name"; readonly name: string }
  | { readonly kind: "failed"; readonly name: string; readonly error: unknown };

export interface SyncOptions {
  readonly findmnt?: Findmnt;
  readonly onOutcome?: (outcome: SyncOutcome) => void;
}

function listInboxNames(inbox: string): readonly string[] {
  return readdirSync(inbox, { withFileTypes: true })
    .filter((entry) => entry.isFile())
    .map((entry) => entry.name)
    .sort();
}

export function syncFiles(db: Db, storageId: string, options: SyncOptions = {}): readonly SyncOutcome[] {
  const storage = db.select().from(storages).where(eq(storages.id, storageId)).get();
  if (storage === undefined) throw new UsageError(`ストレージ "${storageId}" は登録されていません`);

  const root = resolveStorageRoot(storage, options.findmnt ?? runFindmnt);
  const inbox = join(root, INBOX_DIR);
  const raw = join(root, RAW_DIR);
  if (!existsSync(inbox)) throw new UsageError(`inbox フォルダがありません: ${inbox}`);
  mkdirSync(raw, { recursive: true });

  const isRegistered = (name: string): boolean =>
    db.select({ id: videoFiles.id }).from(videoFiles).where(eq(videoFiles.id, name)).get() !== undefined;

  const register = (name: string): void => {
    const attributes = parseVideoName(name);
    if (attributes === undefined) throw new Error(`名前が規則に合いません: ${name}`);

    const source = join(inbox, name);
    const destination = join(raw, name);
    const stat = statSync(source);
    const record: NewVideoFile = {
      id: name,
      storageId: storage.id,
      mtime: Temporal.Instant.fromEpochMilliseconds(Math.floor(stat.mtimeMs)),
      rawPath: `${RAW_DIR}/${name}`,
      rawSize: stat.size,
      eventType: attributes.eventType,
      direction: attributes.direction,
      timestamp: attributes.timestamp,
    };

    // 登録 → 移動。移動に失敗すればロールバックされる。
    db.transaction((tx) => {
      tx.insert(videoFiles).values(record).run();
      renameSync(source, destination);
    });
  };

  const process = (name: string): SyncOutcome => {
    if (parseVideoName(name) === undefined) return { kind: "skipped-name", name };
    if (isRegistered(name)) return { kind: "ignored-registered", name };
    if (existsSync(join(raw, name))) return { kind: "ignored-raw-exists", name };
    try {
      register(name);
      return { kind: "registered", name };
    } catch (error) {
      return { kind: "failed", name, error };
    }
  };

  return listInboxNames(inbox).map((name) => {
    const outcome = process(name);
    options.onOutcome?.(outcome);
    return outcome;
  });
}
