#!/bin/bash
# 雷霆战机 Mac App 构建脚本
#
# 用法：
#   cd mac
#   bash build.sh
#
# 说明：
#   - 游戏源文件为 ../web/index.html（单文件 HTML5 游戏）
#   - 构建产物为 mac/雷霆战机.app，双击即可运行
#   - 图标原图为 mac/icon_1024.png，构建时用 sips + iconutil 生成 AppIcon.icns
#   - 最后使用 ad-hoc 签名（codesign --sign -），无需开发者证书
#   - 游戏更新后重新运行本脚本即可

set -e
cd "$(dirname "$0")"

APP="雷霆战机.app"
GAME_HTML="../web/index.html"
ICON_SRC="icon_1024.png"

# 检查游戏源文件是否存在
if [ ! -f "$GAME_HTML" ]; then
  echo "错误：找不到游戏源文件 $GAME_HTML"
  exit 1
fi

echo "==> 组装 .app 目录结构"
rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cp Info.plist "$APP/Contents/Info.plist"
cp "$GAME_HTML" "$APP/Contents/Resources/game.html"

echo "==> 生成图标"
if command -v iconutil >/dev/null 2>&1 && [ -f "$ICON_SRC" ]; then
  # 用 sips 从 1024px 原图缩放生成 iconset 各尺寸，再打包为 icns
  rm -rf AppIcon.iconset
  mkdir AppIcon.iconset
  for spec in "16 16" "32 16@2x" "32 32" "64 32@2x" "128 128" "256 128@2x" "256 256" "512 256@2x" "512 512" "1024 512@2x"; do
    px=$(echo $spec | cut -d' ' -f1)
    name=$(echo $spec | cut -d' ' -f2)
    sips -z $px $px "$ICON_SRC" --out "AppIcon.iconset/icon_${name/x/@}.png" >/dev/null 2>&1 || true
  done
  # iconset 标准命名
  mv AppIcon.iconset/icon_16.png AppIcon.iconset/icon_16x16.png 2>/dev/null || true
  mv AppIcon.iconset/icon_16@2x.png AppIcon.iconset/icon_16x16@2x.png 2>/dev/null || true
  mv AppIcon.iconset/icon_32.png AppIcon.iconset/icon_32x32.png 2>/dev/null || true
  mv AppIcon.iconset/icon_32@2x.png AppIcon.iconset/icon_32x32@2x.png 2>/dev/null || true
  mv AppIcon.iconset/icon_128.png AppIcon.iconset/icon_128x128.png 2>/dev/null || true
  mv AppIcon.iconset/icon_128@2x.png AppIcon.iconset/icon_128x128@2x.png 2>/dev/null || true
  mv AppIcon.iconset/icon_256.png AppIcon.iconset/icon_256x256.png 2>/dev/null || true
  mv AppIcon.iconset/icon_256@2x.png AppIcon.iconset/icon_256x256@2x.png 2>/dev/null || true
  mv AppIcon.iconset/icon_512.png AppIcon.iconset/icon_512x512.png 2>/dev/null || true
  mv AppIcon.iconset/icon_512@2x.png AppIcon.iconset/icon_512x512@2x.png 2>/dev/null || true
  iconutil -c icns AppIcon.iconset -o "$APP/Contents/Resources/AppIcon.icns" || echo "图标生成失败，跳过"
  rm -rf AppIcon.iconset
else
  echo "无 iconutil 或图标原图 $ICON_SRC，跳过图标"
fi

echo "==> 编译 Swift 壳"
swiftc -O -whole-module-optimization main.swift -o "$APP/Contents/MacOS/ThunderStrike" -framework Cocoa -framework WebKit

echo "==> 签名（ad-hoc）"
codesign --force --sign - "$APP" >/dev/null 2>&1 || true

echo "==> 完成: $(pwd)/$APP"
