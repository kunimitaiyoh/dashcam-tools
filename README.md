# Hoarders Dashcam Tools

## 前提
- [Git Bash](https://gitforwindows.org/) のインストール
- [ffmpeg](https://ffmpeg.org/download.html) のインストール
- Poetry のインストール

- `PATH` を設定し、`ffmpeg` コマンドを実行できるようにすること

## コマンド

### `set-timestamp`

```
usage: set-timestamp [-h] [-q] glob source-dir target-dir
```

#### 例

```bash
set-timestamp -q '*.mp4' //blanca/共有/Y-4K/イベント記録 //blanca/共有/Y-4K/イベント記録/アーカイブ
```

```bash
compress --report //blanca/共有/Y-4K/report.csv //blanca/共有/Y-4K/{Raw,Archive,Trash} 2>>error.log | tee -a info.log
```
