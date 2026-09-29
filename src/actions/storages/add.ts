import { UsageError } from "clipanion";
import { eq } from "drizzle-orm";
import { isAbsolute } from "node:path";

import type { Db } from "../../db/connection";
import { NewStorage, STORAGE_TYPES, Storage, StorageType, storages } from "../../db/schema";

export interface AddStorageArgs {
  readonly id: string;
  readonly type: string;
  readonly connection: string | undefined;
  readonly path: string;
}

const isStorageType = (value: string): value is StorageType => (STORAGE_TYPES as readonly string[]).includes(value);

const isBlank = (value: string): boolean => value.trim().length === 0;

function requireRelativePath(path: string): string {
  if (isBlank(path) || isAbsolute(path)) throw new UsageError("smb / removable ストレージの --path は格納フォルダへの相対パスです");
  return path;
}

function requireSmbUrl(connection: string | undefined): string {
  if (connection === undefined) throw new UsageError("smb ストレージには接続先 (smb://host/share) が必要です");
  const parsed = (() => {
    try {
      return new URL(connection);
    } catch {
      return undefined;
    }
  })();
  if (parsed === undefined || parsed.protocol !== "smb:" || parsed.hostname === "" || !/^\/[^/]+\/?$/.test(parsed.pathname)) {
    throw new UsageError(`接続先は smb://host/share の形式です: ${connection}`);
  }
  return connection;
}

function toRecord(args: AddStorageArgs): NewStorage {
  if (isBlank(args.id)) throw new UsageError("id を指定してください");
  if (!isStorageType(args.type)) throw new UsageError(`type は ${STORAGE_TYPES.join(" | ")} のいずれかです: ${args.type}`);

  switch (args.type) {
    case "local":
      if (args.connection !== undefined) throw new UsageError("local ストレージに接続先は指定できません");
      if (!isAbsolute(args.path)) throw new UsageError("local ストレージの --path は絶対パスです");
      return { id: args.id, type: args.type, connection: null, path: args.path };
    case "smb":
      return { id: args.id, type: args.type, connection: requireSmbUrl(args.connection), path: requireRelativePath(args.path) };
    case "removable":
      if (args.connection === undefined || isBlank(args.connection)) {
        throw new UsageError("removable ストレージにはファイルシステムの UUID が必要です (lsblk -o NAME,UUID,LABEL,MOUNTPOINT で確認)");
      }
      return { id: args.id, type: args.type, connection: args.connection, path: requireRelativePath(args.path) };
  }
}

export function addStorage(db: Db, args: AddStorageArgs): Storage {
  const record = toRecord(args);
  if (db.select({ id: storages.id }).from(storages).where(eq(storages.id, record.id)).get() !== undefined) {
    throw new UsageError(`ストレージ "${record.id}" は既に登録されています`);
  }
  return db.insert(storages).values(record).returning().get();
}
