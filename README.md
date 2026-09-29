# dashcams

ドライブレコーダーの動画ファイルをローカルの SQLite データベースで管理する CLI。Ubuntu サーバー上で実行する。

## 前提

- [mise](https://mise.jdx.dev/)（`mise.toml` の Node.js と pnpm を使う）
- SMB 共有は cifs でマウント済みであること（後述）
- USB リムーバブルメディアはマウント済みであること

## セットアップ

```sh
mise install
pnpm install
pnpm link --global
```

`dashcams` はこのチェックアウトの TypeScript を tsx で直接実行する。ソース変更後のビルドや再リンクは不要。

## 設定ファイル

次の順に `config.toml` を探し、最初に見つかった 1 ファイルだけを読む。マージはしない。

1. リポジトリルートの `config.toml`（Git 管理外）
2. `~/.config/dashcams/config.toml`

```toml
[database]
path = "/home/<user>/.local/share/dashcams/dashcams.db"
```

`database.path` は SQLite ファイルの絶対パス。親ディレクトリは自動で作る。

## コマンド

| コマンド | 処理 |
|---|---|
| `dashcams db migrate` | 未適用のマイグレーションをデータベースに適用する。初回と、スキーマ更新のたびに実行する |
| `dashcams storages add <id> <type> [接続先] --path <path>` | ストレージを登録する |
| `dashcams files sync <storage-id>` | ストレージの `inbox` にある動画ファイルを登録し `raw` へ移動する |

詳細は各コマンドの `--help`。

### ストレージ

動画ファイルは、ストレージごとに 1 つの格納フォルダの下の固定名サブフォルダに置く。

- `inbox`: 未登録の動画ファイル。人間が置く
- `raw`: 登録済みの動画ファイル。`files sync` が `inbox` から移動する

`type` と接続先、`--path` の意味は次のとおり。

| type | 接続先 | `--path` |
|---|---|---|
| `local` | 指定しない | 格納フォルダの絶対パス |
| `smb` | `smb://host/share` | 共有内の相対パス |
| `removable` | ファイルシステムの UUID | メディアルートからの相対パス |

```sh
dashcams storages add home local --path /srv/dashcam
dashcams storages add nas smb smb://blanca.local/共有 --path Y-4K
dashcams storages add usb removable A728-D803 --path dashcam
```

`smb` と `removable` の実パスは実行時に `findmnt` で解決する。マウントされていなければエラーになる。

UUID は次で確認する。

```sh
lsblk -o NAME,UUID,LABEL,MOUNTPOINT
```

### SMB 共有のマウント

`cifs-utils` を入れ、`/etc/fstab` に書く。資格情報は root だけが読めるファイルに置く。
`findmnt` の SOURCE 列が `//host/share` と一致する必要があるので、fstab の記述は登録した `smb://host/share` と同じホスト名・共有名にする。

```
# /etc/samba/credentials-blanca（chmod 600）
username=<user>
password=<password>
```

```
# /etc/fstab
//blanca.local/共有  /mnt/blanca-share  cifs  credentials=/etc/samba/credentials-blanca,uid=<user>,gid=<group>,_netdev,x-systemd.automount  0  0
```

### `files sync`

`inbox` の各ファイルについて次を行なう。

1. 名前が `NNNNNNNN_YYMMDDhhmm_[NGS][FR].MP4` の規則に合わなければスキップして報告する
2. 同じ名前が登録済みなら無視して報告する
3. `raw` に同じ名前のファイルが残っていれば無視して報告する
4. データベースに登録し、`inbox` から `raw` へ移動する。移動に失敗すれば登録を取り消す

1 件でも失敗があれば終了コードは 1。

ファイル名の時刻はレコーダーのローカル時刻（Asia/Tokyo）として解釈し、`timestamp` は UTC の Unix 秒、`mtime` は Unix ミリ秒で保存する。

## 開発

```sh
pnpm typecheck
pnpm test
pnpm build
```

スキーマ（`src/db/schema.ts`）を変えたら `pnpm db:generate` でマイグレーションを `drizzle/` に生成し、コミットする。

`src/index.ts` でコマンドを登録し、`src/commands/` で引数を定義する。実際の処理は `src/actions/` に置く。

## 配布版

```sh
pnpm pack
pnpm add --global ./dashcams-0.1.0.tgz
```

配布版はビルド済み JavaScript を実行する。ソース版と配布版は同じグローバルインストール先で一つにする（`pnpm remove --global dashcams` で切り替える）。
