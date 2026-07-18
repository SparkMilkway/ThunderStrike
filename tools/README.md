# tools/ — 录制与资产工具

## record_gif.py + recorder.html — gameplay GIF 录制

为 README 录制真实 gameplay GIF 的工具链。`recorder.html` 在浏览器里用 iframe
同源加载游戏，按时间线脚本注入键盘事件（自动驾驶沿正弦轨迹移动，游戏自动开火，
中途放一次炸弹），并把游戏 canvas 逐帧 POST 给 `record_gif.py`；后者用 ffmpeg
两阶段 palettegen + paletteuse 合成 GIF。

### 用法

```bash
python3 tools/record_gif.py --duration 12 --fps 10 --out assets/gameplay.gif --script gameplay
```

运行后会自动 `open` 打开默认浏览器进入录制页（游戏依赖 WebAudio /
requestAnimationFrame，必须是真浏览器；窗口前置几秒属正常，**不要关闭该标签页**）。
录制结束自动合成 GIF 并打印输出路径与文件大小。

### 参数

| 参数 | 默认 | 说明 |
|---|---|---|
| `--duration` | 12 | 录制时长（秒） |
| `--fps` | 10 | 抓帧率 = GIF 帧率 |
| `--out` | /tmp/thunder_strike.gif | GIF 输出路径 |
| `--script` | gameplay | 时间线脚本，可选 `gameplay`（单人+炸弹）/ `menu`（菜单展示）/ `twoplayer`（双人），新脚本加在 `recorder.html` 顶部 `SCRIPTS` |
| `--name` | 同 script | 录制标识名 |
| `--gameq` | — | 透传给游戏 iframe 的 query，如 `--gameq 'stage=2&god=1&mute=1'`（用游戏调试钩子从第 N 关开始录） |
| `--width` | 480 | GIF 宽度（游戏原生 480，等比缩放） |
| `--port` | 8931 | 本地服务器端口，`0` 为随机 |
| `--no-open` | — | 不自动打开浏览器，手动访问打印的 URL |
| `--keep-frames` | — | 保留临时 PNG 帧目录 |

也可以直接改 URL 参数微调：`http://localhost:8931/tools/recorder.html?duration=8&fps=10&script=menu`
（需先单独启动一个静态服务器于仓库根，或借助 `record_gif.py --no-open`）。

### 键位（与 web/index.html 一致）

标题界面 `1` 单人 / `2` 双人；移动 WASD 或方向键；射击为自动开火；
炸弹 `x`/`b`/空格/`q`；暂停 `p`/Escape。

### 依赖

- 托管 Python（标准库即可，无第三方包）
- ffmpeg：`/opt/homebrew/bin/ffmpeg`
- macOS `open` 命令（自动打开浏览器）
- 输出建议 < 8MB（超限时脚本会警告）
