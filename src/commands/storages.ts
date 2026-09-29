import { Command, Option } from "clipanion";

import { addStorage } from "../actions/storages/add";
import { loadConfig } from "../config";
import { openDatabase } from "../db/connection";

export class AddStorageCommand extends Command {
  static paths = [["storages", "add"]];
  static usage = Command.Usage({
    description: "ストレージを登録する",
    details: `
      type は local / smb / removable。
      local は接続先なしで --path に格納フォルダの絶対パスを指定する。
      smb は接続先に smb://host/share を、--path に共有内の相対パスを指定する。
      removable は接続先にファイルシステムの UUID を、--path にメディアルートからの相対パスを指定する。
    `,
    examples: [
      ["ローカル", "$0 storages add home local --path /srv/dashcam"],
      ["SMB", "$0 storages add nas smb smb://blanca.local/共有 --path Y-4K"],
      ["USB", "$0 storages add usb removable A728-D803 --path dashcam"],
    ],
  });

  id = Option.String({ required: true });
  type = Option.String({ required: true });
  connection = Option.String({ required: false });
  storagePath = Option.String("--path", { required: true });

  async execute(): Promise<void> {
    const config = loadConfig();
    const storage = addStorage(openDatabase(config.database.path), {
      id: this.id,
      type: this.type,
      connection: this.connection,
      path: this.storagePath,
    });
    this.context.stdout.write(`added storage: ${storage.id} (${storage.type})\n`);
  }
}
