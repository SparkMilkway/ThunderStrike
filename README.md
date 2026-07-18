# 雷霆战机 Thunder Strike

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Platform: Web/macOS](https://img.shields.io/badge/Platform-Web%20%2F%20macOS-blue.svg)
![Engine: Vanilla JS](https://img.shields.io/badge/Engine-Vanilla%20JS%20%2B%20Canvas%202D-orange.svg)

雷电2 风格的纵版弹幕射击游戏。单文件 HTML5 实现，vanilla JS + Canvas 2D 渲染、WebAudio 全合成音乐与音效，**零外部依赖、无需构建、无需联网**，下载即玩。

---

## 特性

- **单人与本地双人合作**：双人同屏协作，双人靠近时触发合体强化火力
- **三种特色武器**
  - 火神炮：散射弹幕，近距压制
  - 电浆鞭：锁定敌人后弹簧物理甩鞭激光，视觉与打击感拉满
  - 追踪导弹：自动索敌 + 近炸引信范围伤害
- **3 种 Boss × 3 阶段**：每种 Boss 有三段形态转换与弹幕演出
- **四档难度**：从休闲到硬核，敌机密度与弹幕压力逐级提升
- **WebAudio 全合成音频**：标题 / 战斗 / Boss 三轨音序器音乐自动切换，全部音效由振荡器与噪声实时合成，无任何音频资源文件
- **通关与无尽模式**：通关后有结算场景；也可按 C 续命进入无尽挑战，冲击本地最高分
- **炸弹清屏、补给机道具、触屏支持**

## 操作说明

| 操作 | 1P | 2P |
| --- | --- | --- |
| 移动 | W / A / S / D | 方向键 |
| 炸弹 | 空格 | 回车 |
| 暂停 / 暂停菜单 | P 或 Esc | P 或 Esc |
| 续命 / 进入无尽 | C | C |

移动端支持触屏拖动移动，自动开火。

## 快速开始

### Web 版（推荐）

下载仓库后，直接双击 `web/index.html` 即可在浏览器中游玩。

- 无需构建、无需安装依赖、无需联网
- 支持 Chrome / Edge / Firefox / Safari 等现代浏览器

### Mac 版（原生 App 壳）

```bash
cd mac
bash build.sh
```

生成 `mac/雷霆战机.app`，双击即玩。要求：macOS 12+，已安装 Xcode 命令行工具（`xcode-select --install`）。详见 [mac/README.md](mac/README.md)。

## 目录结构

```
thunder-strike-game/
├── README.md            # 本文件
├── LICENSE              # MIT 许可证
├── CONTRIBUTING.md      # 贡献指南
├── .gitignore
├── web/
│   └── index.html       # 游戏本体（单文件，全部逻辑/渲染/音频合成都在其中）
└── mac/
    ├── main.swift       # Swift + WKWebView 原生壳
    ├── Info.plist       # App 元信息
    ├── icon_1024.png    # 图标原图（构建时生成 .icns）
    ├── build.sh         # 一键构建脚本
    └── README.md        # Mac 版构建说明
```

## 技术要点

- **Canvas 2D**：全部游戏画面（机体、弹幕、爆炸、背景星空）由 Canvas 2D 矢量绘制，无贴图资源
- **WebAudio 音序器**：三轨 chiptune 风格音乐（标题 / 战斗 / Boss）由 WebAudio 振荡器实时音序播放，场景切换自动切轨；射击、爆炸、拾取等音效全部程序合成
- **弹簧物理甩鞭**：电浆鞭使用弹簧-阻尼物理模拟鞭体节点，锁定目标后甩出弧线激光
- **对象池与近炸引信**：弹幕与粒子使用对象池复用；追踪导弹带近炸引信，进入范围即引爆造成 AoE 伤害
- **Swift WKWebView 壳**：Mac 版仅约 60 行 Swift，将游戏 HTML 打包进 `.app`，注入深色主题 CSS，ad-hoc 签名后即可双击运行

## 贡献

欢迎提交 Issue 和 Pull Request，请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

## License

[MIT](LICENSE) © 2026 SparkMilkway

---

## English

**Thunder Strike** (雷霆战机) is a Raiden II–style vertical bullet-hell shmup in a **single HTML file** — vanilla JS + Canvas 2D rendering, fully synthesized WebAudio music and SFX, zero external dependencies. Download and play, no build, no network required.

### Features

- Solo and **local 2-player co-op** (fusion power-up when both players fly close)
- **Three weapons**: Vulcan spread shot, plasma whip (lock-on, spring-physics whip laser), homing missiles with proximity-fuse AoE
- **3 bosses × 3 phases** each
- **4 difficulty levels**
- Fully synthesized 3-track WebAudio music (title / battle / boss, auto-switching) and procedural SFX
- Clear-the-screen bombs, supply-carrier power-ups, local high score, touch support
- **Ending + endless mode**: clear the game for the ending scene, or press C to continue into endless mode

### Controls

| Action | Player 1 | Player 2 |
| --- | --- | --- |
| Move | W / A / S / D | Arrow keys |
| Bomb | Space | Enter |
| Pause menu | P or Esc | P or Esc |
| Continue / Endless | C | C |

Touch controls (drag to move, auto-fire) are supported on mobile.

### Quick Start

- **Web**: download the repo and double-click `web/index.html` — that's it. No build, no dependencies, works offline in any modern browser.
- **macOS**: `cd mac && bash build.sh` to produce `mac/雷霆战机.app` (requires Xcode Command Line Tools). See [mac/README.md](mac/README.md).

### Tech Highlights

- Canvas 2D vector rendering — no image assets at all
- WebAudio sequencer: 3 chiptune tracks (title / battle / boss) with automatic scene switching; every sound effect is synthesized from oscillators and noise
- Spring-damper physics for the plasma whip
- Object pooling for bullets/particles; proximity-fuse homing missiles
- ~60-line Swift WKWebView shell for the native macOS app

### License

[MIT](LICENSE) © 2026 SparkMilkway
