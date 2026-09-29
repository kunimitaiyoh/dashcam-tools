import { UsageError } from "clipanion";
import { execFileSync } from "node:child_process";
import { join } from "node:path";

import type { Storage } from "./db/schema";

// findmnt を実行して stdout を返す。該当するマウントがなければ undefined（findmnt は終了コード 1）。
export type Findmnt = (args: readonly string[]) => string | undefined;

export const runFindmnt: Findmnt = (args) => {
  try {
    return execFileSync("findmnt", [...args], { encoding: "utf8", stdio: ["ignore", "pipe", "inherit"] });
  } catch (error) {
    if (error instanceof Error && "status" in error && error.status === 1) return undefined;
    throw error;
  }
};

interface MountEntry {
  readonly source: string;
  readonly target: string;
}

function listMounts(findmnt: Findmnt, args: readonly string[]): readonly MountEntry[] {
  const stdout = findmnt(["--json", "--output", "SOURCE,TARGET", ...args]);
  if (stdout === undefined) return [];
  const parsed: { filesystems?: readonly MountEntry[] } = JSON.parse(stdout);
  return parsed.filesystems ?? [];
}

// smb://host/share → //host/share（findmnt の SOURCE 列の表記）
export function smbUrlToSource(url: string): string {
  const parsed = new URL(url);
  return `//${parsed.hostname}${decodeURIComponent(parsed.pathname)}`;
}

function requireConnection(storage: Storage): string {
  if (storage.connection === null) {
    throw new UsageError(`ストレージ "${storage.id}" (${storage.type}) に接続先が登録されていません`);
  }
  return storage.connection;
}

export function resolveStorageRoot(storage: Storage, findmnt: Findmnt = runFindmnt): string {
  switch (storage.type) {
    case "local":
      return storage.path;
    case "removable": {
      const uuid = requireConnection(storage);
      const mount = listMounts(findmnt, ["--source", `UUID=${uuid}`])[0];
      if (mount === undefined) throw new UsageError(`ストレージ "${storage.id}" のメディア (UUID=${uuid}) はマウントされていません`);
      return join(mount.target, storage.path);
    }
    case "smb": {
      const url = requireConnection(storage);
      const source = smbUrlToSource(url);
      const mount = listMounts(findmnt, ["--types", "cifs"]).find((entry) => entry.source === source);
      if (mount === undefined) throw new UsageError(`ストレージ "${storage.id}" の共有 (${url}) はマウントされていません`);
      return join(mount.target, storage.path);
    }
  }
}
