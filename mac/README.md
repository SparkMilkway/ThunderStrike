# 雷霆战机 · Mac 版构建说明

本目录包含《雷霆战机》的 macOS 原生 App 壳：一个约 60 行的 Swift + WKWebView 程序，把 `web/index.html` 打包成 `.app`，并注入与游戏风格一致的深色主题。

## 构建要求

- macOS 12 或更高版本
- Xcode 命令行工具（提供 `swiftc`、`sips`、`iconutil`、`codesign`）：

  ```bash
  xcode-select --install
  ```

- 无需 Apple 开发者账号：构建产物使用 ad-hoc 签名，仅本机运行

## 构建步骤

```bash
cd mac
bash build.sh
```

成功后生成 `mac/雷霆战机.app`，双击即可游玩。

## 文件说明

| 文件 | 作用 |
| --- | --- |
| `main.swift` | App 壳源码：创建窗口与 WKWebView，加载游戏 HTML，注入深色主题 CSS |
| `Info.plist` | App 元信息（名称、Bundle ID、最低系统版本等） |
| `icon_1024.png` | 图标原图（1024×1024），构建时自动生成 `AppIcon.icns` |
| `build.sh` | 一键构建脚本 |

## 常见问题

- **提示"找不到游戏源文件"**：请确认仓库结构完整，`web/index.html` 与本目录为同级关系。
- **首次打开被 Gatekeeper 拦截**：右键 App →「打开」，或在「系统设置 → 隐私与安全性」中允许运行。
- **游戏更新后如何重新打包**：重新运行 `bash build.sh` 即可，脚本会自动用最新的 `web/index.html` 覆盖包内副本。
