import { UsageError } from "clipanion";
import { describe, expect, it } from "vitest";

import type { Storage } from "./db/schema";
import { Findmnt, resolveStorageRoot, smbUrlToSource } from "./mounts";

const findmntOf = (filesystems: readonly { source: string; target: string }[]): Findmnt => () =>
  filesystems.length === 0 ? undefined : JSON.stringify({ filesystems });

describe("smbUrlToSource", () => {
  it("URL を findmnt の SOURCE 表記に直す", () => {
    expect(smbUrlToSource("smb://blanca.local/共有")).toBe("//blanca.local/共有");
    expect(smbUrlToSource("smb://blanca.local/%E5%85%B1%E6%9C%89")).toBe("//blanca.local/共有");
  });
});

describe("resolveStorageRoot", () => {
  it("local はパスそのもの", () => {
    const storage: Storage = { id: "a", type: "local", connection: null, path: "/srv/dashcam" };
    expect(resolveStorageRoot(storage, findmntOf([]))).toBe("/srv/dashcam");
  });

  it("removable はマウント先に相対パスを結合する", () => {
    const storage: Storage = { id: "usb", type: "removable", connection: "A728-D803", path: "dashcam" };
    const findmnt = findmntOf([{ source: "/dev/sdb1", target: "/media/bard/USB" }]);
    expect(resolveStorageRoot(storage, findmnt)).toBe("/media/bard/USB/dashcam");
  });

  it("removable が未マウントなら UsageError", () => {
    const storage: Storage = { id: "usb", type: "removable", connection: "A728-D803", path: "dashcam" };
    expect(() => resolveStorageRoot(storage, findmntOf([]))).toThrow(UsageError);
  });

  it("smb は SOURCE が一致する cifs マウントを使う", () => {
    const storage: Storage = { id: "nas", type: "smb", connection: "smb://blanca.local/共有", path: "Y-4K" };
    const findmnt = findmntOf([
      { source: "//blanca.local/太陽", target: "/mnt/taiyo" },
      { source: "//blanca.local/共有", target: "/mnt/kyoyu" },
    ]);
    expect(resolveStorageRoot(storage, findmnt)).toBe("/mnt/kyoyu/Y-4K");
  });

  it("smb が未マウントなら UsageError", () => {
    const storage: Storage = { id: "nas", type: "smb", connection: "smb://blanca.local/共有", path: "Y-4K" };
    expect(() => resolveStorageRoot(storage, findmntOf([{ source: "//other/share", target: "/mnt/x" }]))).toThrow(UsageError);
  });

  it("接続先が null なら UsageError", () => {
    const storage: Storage = { id: "nas", type: "smb", connection: null, path: "Y-4K" };
    expect(() => resolveStorageRoot(storage, findmntOf([]))).toThrow(UsageError);
  });
});
