#!/usr/bin/env python3
"""雷霆战机 gameplay GIF 录制服务器。

用法：
    python3 tools/record_gif.py --duration 12 --fps 10 --out assets/gameplay.gif --script gameplay

流程：
    1. 在仓库根目录起本地静态服务器（tools/recorder.html 由此加载 ../web/index.html，保证同源）；
    2. 自动 `open` 打开用户默认浏览器进入录制页（游戏依赖 WebAudio /
       requestAnimationFrame，必须是真浏览器；窗口前置几秒属正常）；
    3. 接收录制页 POST 上来的 PNG 帧（/frame?i=N），存入临时目录；
    4. 收到 /finish（或超时兜底）后调用 ffmpeg 两阶段
       palettegen + paletteuse 合成高质量 GIF，打印文件大小。
"""
import argparse
import base64
import functools
import http.server
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FFMPEG = '/opt/homebrew/bin/ffmpeg'
MAX_GIF_BYTES = 8 * 1024 * 1024  # README 内嵌 GIF 建议 < 8MB


class State:
    """录制会话状态（一次运行只服务一个录制页）。"""

    def __init__(self):
        self.lock = threading.Lock()
        self.frames_dir = tempfile.mkdtemp(prefix='ts_frames_')
        self.frame_count = 0
        self.name = 'gameplay'
        self.finish_event = threading.Event()


STATE = State()


class Handler(http.server.SimpleHTTPRequestHandler):
    """静态托管仓库根目录 + 帧上传 / 完成通知端点。"""

    def log_message(self, fmt, *args):  # 静态请求静默，只保留我们自己的打印
        pass

    # ---- 帧上传 ----
    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        length = int(self.headers.get('Content-Length') or 0)
        body = self.rfile.read(length) if length else b''

        if parsed.path == '/begin':
            with STATE.lock:
                STATE.name = qs.get('name', ['gameplay'])[0]
                STATE.frame_count = 0
                # 清空临时目录里可能残留的旧帧
                for f in os.listdir(STATE.frames_dir):
                    os.remove(os.path.join(STATE.frames_dir, f))
            print('[rec] 录制开始：name=%s' % STATE.name)
            self._reply(200, b'ok')

        elif parsed.path == '/frame':
            try:
                idx = int(qs.get('i', ['0'])[0])
            except ValueError:
                self._reply(400, b'bad index')
                return
            text = body.decode('ascii', 'replace')
            if ',' in text:
                text = text.split(',', 1)[1]  # 去掉 data:image/png;base64, 前缀
            try:
                png = base64.b64decode(text)
            except Exception:
                self._reply(400, b'bad base64')
                return
            path = os.path.join(STATE.frames_dir, 'frame_%05d.png' % idx)
            with open(path, 'wb') as f:
                f.write(png)
            with STATE.lock:
                STATE.frame_count = max(STATE.frame_count, idx + 1)
            self._reply(200, b'ok')

        elif parsed.path == '/finish':
            with STATE.lock:
                n = STATE.frame_count
            print('[rec] 收到 /finish：共 %d 帧' % n)
            STATE.finish_event.set()
            self._reply(200, b'ok')

        else:
            self._reply(404, b'not found')

    def _reply(self, code, payload):
        self.send_response(code)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        # 允许录制页跨端口调试时也能 POST（同源场景下无害）
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(payload)


def make_gif(frames_dir, fps, width, out_path):
    """ffmpeg 两阶段：palettegen 生成调色板，paletteuse 应用，保证 GIF 画质。"""
    pattern = os.path.join(frames_dir, 'frame_%05d.png')
    palette = os.path.join(frames_dir, 'palette.png')
    vf_scale = 'scale=%d:-1:flags=lanczos' % width

    p1 = [FFMPEG, '-y', '-framerate', str(fps), '-i', pattern,
          '-vf', 'fps=%d,%s,palettegen=max_colors=256:stats_mode=diff' % (fps, vf_scale),
          palette]
    p2 = [FFMPEG, '-y', '-framerate', str(fps), '-i', pattern, '-i', palette,
          '-lavfi', 'fps=%d,%s[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle' % (fps, vf_scale),
          '-loop', '0', out_path]

    for label, cmd in (('palettegen', p1), ('paletteuse', p2)):
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print('[gif] %s 失败：\n%s' % (label, r.stderr[-2000:]))
            return False
    return True


def main():
    ap = argparse.ArgumentParser(description='录制雷霆战机 gameplay GIF')
    ap.add_argument('--duration', type=float, default=12, help='录制时长（秒），默认 12')
    ap.add_argument('--fps', type=int, default=10, help='抓帧/GIF 帧率，默认 10')
    ap.add_argument('--out', default='/tmp/thunder_strike.gif', help='GIF 输出路径')
    ap.add_argument('--script', default='gameplay', help='时间线脚本名（recorder.html 内 SCRIPTS）')
    ap.add_argument('--name', default=None, help='录制标识名，默认同 --script')
    ap.add_argument('--gameq', default='', help="透传给游戏 iframe 的 query，如 'stage=2&god=1&mute=1'（调试用）")
    ap.add_argument('--width', type=int, default=480, help='GIF 宽度，默认 480（游戏原生宽）')
    ap.add_argument('--port', type=int, default=8931, help='本地服务器端口，默认 8931（0=随机）')
    ap.add_argument('--no-open', action='store_true', help='不自动打开浏览器（手动访问打印的 URL）')
    ap.add_argument('--keep-frames', action='store_true', help='保留临时 PNG 帧目录')
    args = ap.parse_args()

    name = args.name or args.script
    out_path = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)

    handler = functools.partial(Handler, directory=REPO_ROOT)
    try:
        server = http.server.ThreadingHTTPServer(('127.0.0.1', args.port), handler)
    except OSError as e:
        if e.errno != 48 or args.port == 0:  # 48 = EADDRINUSE
            raise
        print('[rec] 端口 %d 被占用，改用随机端口' % args.port)
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    port = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()

    url = ('http://localhost:%d/tools/recorder.html?duration=%s&fps=%d&script=%s&name=%s'
           % (port, args.duration, args.fps,
              urllib.parse.quote(args.script), urllib.parse.quote(name)))
    if args.gameq:
        url += '&gameq=' + urllib.parse.quote(args.gameq)
    print('[rec] 服务器已启动（仓库根 %s）' % REPO_ROOT)
    print('[rec] 录制页：%s' % url)
    if not args.no_open:
        subprocess.run(['open', url], check=False)
        print('[rec] 已在默认浏览器打开录制页，请勿关闭该标签页…')

    # 等待 /finish；超时兜底（浏览器被关/脚本出错也能用已有帧合成）
    timeout = args.duration + 120
    if not STATE.finish_event.wait(timeout=timeout):
        print('[rec] 警告：%ds 内未收到 /finish，用已抓到的帧兜底合成' % timeout)

    server.shutdown()
    server.server_close()

    frames = sorted(f for f in os.listdir(STATE.frames_dir) if f.startswith('frame_'))
    n = len(frames)
    expected = round(args.duration * args.fps)
    print('[rec] 抓到 %d 帧（预期 ≈ %d）' % (n, expected))
    if n == 0:
        print('[rec] 错误：一帧都没抓到，终止')
        shutil.rmtree(STATE.frames_dir, ignore_errors=True)
        sys.exit(1)
    if abs(n - expected) > max(3, expected * 0.2):
        print('[rec] 警告：帧数与预期偏差较大（可能掉帧或提前结束）')

    if not make_gif(STATE.frames_dir, args.fps, args.width, out_path):
        shutil.rmtree(STATE.frames_dir, ignore_errors=True)
        sys.exit(1)

    size = os.path.getsize(out_path)
    print('[gif] 输出：%s（%.2f MB，%d 帧 @ %dfps）'
          % (out_path, size / 1024 / 1024, n, args.fps))
    if size > MAX_GIF_BYTES:
        print('[gif] 警告：超过 8MB，建议缩短 --duration 或降低 --fps/--width')

    if args.keep_frames:
        print('[rec] 帧保留在：%s' % STATE.frames_dir)
    else:
        shutil.rmtree(STATE.frames_dir, ignore_errors=True)


if __name__ == '__main__':
    main()
