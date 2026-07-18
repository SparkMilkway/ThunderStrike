# 贡献指南

感谢你对《雷霆战机 Thunder Strike》的关注！欢迎提交 Issue 和 Pull Request。

## 提交 Issue

- 报告 Bug 时请附上：操作系统与浏览器版本、复现步骤、期望行为与实际行为，截图或录屏更佳
- 提出新功能建议时，请先说明使用场景与玩法价值

## 提交 Pull Request

1. Fork 本仓库并创建特性分支（如 `feat/new-weapon` 或 `fix/bomb-hitbox`）
2. 遵守现有代码风格：游戏本体是单文件 `web/index.html`，请保持零外部依赖、无需构建的特性
3. 提交前请自测：
   - Web 版：直接在浏览器打开 `web/index.html`，验证主菜单、单/双人、三种武器、Boss 战与结算流程无异常
   - 涉及 Mac 壳改动时：运行 `cd mac && bash build.sh` 验证 App 可正常构建与启动
4. 提交信息请简明描述改动内容与动机
5. 在 PR 描述中说明测试情况（测试过的浏览器 / macOS 版本）

## 行为准则

请保持友善与尊重。任何形式的骚扰或歧视言论都不被接受。
