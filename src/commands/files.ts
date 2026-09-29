import { Command, Option } from "clipanion";

import { SyncOutcome, syncFiles } from "../actions/files/sync";
import { loadConfig } from "../config";
import { openDatabase } from "../db/connection";

const countBy = (outcomes: readonly SyncOutcome[], kind: SyncOutcome["kind"]): number =>
  outcomes.filter((outcome) => outcome.kind === kind).length;

export class SyncFilesCommand extends Command {
  static paths = [["files", "sync"]];
  static usage = Command.Usage({
    description: "ストレージの inbox にある動画ファイルをデータベースに登録し、raw へ移動する",
    details: `
      inbox の各ファイルについて、データベースに登録してから raw へ移動する。移動に失敗した登録は取り消す。
      既に登録済みの名前、raw に同名ファイルが残っている名前、規則に合わない名前は何もせず報告する。
      1 件でも失敗があれば終了コードは 1。
    `,
  });

  storageId = Option.String({ required: true });

  async execute(): Promise<number> {
    const config = loadConfig();
    const outcomes = syncFiles(openDatabase(config.database.path), this.storageId, { onOutcome: (outcome) => this.report(outcome) });

    const summary = ["registered", "ignored-registered", "ignored-raw-exists", "skipped-name", "failed"] as const;
    this.context.stdout.write(`${summary.map((kind) => `${kind}: ${countBy(outcomes, kind)}`).join(", ")}\n`);
    return countBy(outcomes, "failed") > 0 ? 1 : 0;
  }

  private report(outcome: SyncOutcome): void {
    switch (outcome.kind) {
      case "registered":
        this.context.stdout.write(`registered: ${outcome.name}\n`);
        return;
      case "ignored-registered":
        this.context.stdout.write(`ignored (already registered): ${outcome.name}\n`);
        return;
      case "ignored-raw-exists":
        this.context.stderr.write(`ignored (already exists in raw): ${outcome.name}\n`);
        return;
      case "skipped-name":
        this.context.stderr.write(`skipped (name does not match): ${outcome.name}\n`);
        return;
      case "failed":
        this.context.stderr.write(`failed: ${outcome.name}: ${outcome.error instanceof Error ? outcome.error.message : String(outcome.error)}\n`);
        return;
    }
  }
}
