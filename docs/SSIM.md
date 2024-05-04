
```bash
time ffmpeg -i source.mp4 -map 0 -c:a copy -c:v libx264 output-nvenc-default.mp4
time ffmpeg -i source.mp4 -map 0 -c:a copy -c:v h264_nvenc output-nvenc-default.mp4
```

## libx264

```bash
time ffmpeg -i source.mp4 -map 0 -c:a copy -c:v libx264 -crf 23 output-libx-crf23.mp4
time ffmpeg -i source.mp4 -map 0 -c:a copy -c:v libx264 -crf 28 output-libx-crf28.mp4
```

```bash
time ffmpeg -loglevel error -i source.mp4 -map 0 -c:a copy -c:v h264_nvenc output-nvenc-default.mp4

time ffmpeg -loglevel error -i source.mp4 -map 0 -c:a copy -c:v h264_nvenc -cq 28 output-nvenc-cq28.mp4
time ffmpeg -loglevel error -i source.mp4 -map 0 -c:a copy -c:v h264_nvenc -cq 30 output-nvenc-cq30.mp4
time ffmpeg -loglevel error -i source.mp4 -map 0 -c:a copy -c:v h264_nvenc -cq 32 output-nvenc-cq32.mp4
time ffmpeg -loglevel error -i source.mp4 -map 0 -c:a copy -c:v h264_nvenc -qp 28 output-nvenc-qp28.mp4
time ffmpeg -loglevel error -i source.mp4 -map 0 -c:a copy -c:v h264_nvenc -qp 30 output-nvenc-qp30.mp4
time ffmpeg -loglevel error -i source.mp4 -map 0 -c:a copy -c:v h264_nvenc -qp 32 output-nvenc-qp32.mp4
time ffmpeg -loglevel error -i source.mp4 -map 0 -c:a copy -c:v h264_nvenc -cq 28 -qp 28 output-nvenc-cq28-qp28.mp4
time ffmpeg -loglevel error -i source.mp4 -map 0 -c:a copy -c:v h264_nvenc -cq 28 -qp 32 output-nvenc-cq28-qp32.mp4
time ffmpeg -loglevel error -i source.mp4 -map 0 -c:a copy -c:v h264_nvenc -cq 32 -qp 28 output-nvenc-cq32-qp28.mp4
time ffmpeg -loglevel error -i source.mp4 -map 0 -c:a copy -c:v h264_nvenc -cq 32 -qp 32 output-nvenc-cq32-qp32.mp4

time ffmpeg -loglevel error -i source.mp4 -map 0 -c:a copy -c:v h264_nvenc -cq 30 -preset p7 output-cq30-preset_p7.mp4
time ffmpeg -loglevel error -i source.mp4 -map 0 -c:a copy -c:v h264_nvenc -cq 30 -profile high output-cq30-profile_high.mp4
time ffmpeg -loglevel error -i source.mp4 -map 0 -c:a copy -c:v h264_nvenc -cq 30 -b_ref_mode each output-cq30-brefmode_each.mp4
time ffmpeg -loglevel error -i source.mp4 -map 0 -c:a copy -c:v h264_nvenc -cq 30 -b_ref_mode middle output-cq30-brefmode_middle.mp4
time ffmpeg -loglevel error -i source.mp4 -map 0 -c:a copy -c:v h264_nvenc -cq 30 -multipass qres output-cq30-multipass_qres.mp4
time ffmpeg -loglevel error -i source.mp4 -map 0 -c:a copy -c:v h264_nvenc -cq 30 -multipass fullres output-cq30-multipass_fullres.mp4
```

```bash
time ffmpeg -loglevel error -i source.mp4 -map 0 -c:a copy -c:v h264_nvenc -cq 31 -profile high -preset p7 output-cq31-p7-high.mp4
time ffmpeg -loglevel error -i source.mp4 -map 0 -c:a copy -c:v h264_nvenc -cq 32 -profile high -preset p7 output-cq32-p7-high.mp4

ssim output-cq31-p7-high.mp4 output-cq32-p7-high.mp4 source.mp4 > ssim-cq.txt

```

```bash
ssim output-libx-crf23.mp4 output-libx-crf28.mp4 source.mp4 > ssim-libx.txt

ssim output-nvenc-cq28.mp4 output-nvenc-cq30.mp4 output-nvenc-cq32.mp4 output-nvenc-qp28.mp4 output-nvenc-qp30.mp4 output-nvenc-qp32.mp4 output-nvenc-cq28-qp28.mp4 output-nvenc-cq28-qp32.mp4 output-nvenc-cq32-qp28.mp4 output-nvenc-cq32-qp32.mp4 source.mp4 > ssim1.txt
```


