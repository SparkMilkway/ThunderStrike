import Cocoa
import WebKit

final class AppDelegate: NSObject, NSApplicationDelegate, WKScriptMessageHandler {
    private var window: NSWindow!

    // 与游戏侧约定：window.webkit.messageHandlers.thunderStrike.postMessage({type:'resize', w, h})
    // w/h 为 CSS px，只会是 480×640 / 600×800 / 720×960 / 960×1280 四档之一
    private static let messageName = "thunderStrike"
    // 内容区最小尺寸 = 游戏内部画布 480×640
    private static let minContent = NSSize(width: 480, height: 640)
    // 无 localStorage 记录时的默认窗口内容尺寸
    private static let defaultContent = NSSize(width: 600, height: 800)
    // 首次应用存储尺寸时不做动画，避免启动瞬间窗口跳动
    private var hasAppliedInitialSize = false

    func applicationDidFinishLaunching(_ notification: Notification) {
        window = NSWindow(
            contentRect: NSRect(origin: .zero, size: AppDelegate.defaultContent),
            styleMask: [.titled, .closable, .miniaturizable, .resizable],
            backing: .buffered,
            defer: false
        )
        window.title = "雷霆战机 · Thunder Strike"
        window.minSize = AppDelegate.minContent
        window.backgroundColor = NSColor(red: 0.043, green: 0.067, blue: 0.125, alpha: 1.0)
        window.center()

        // Web 与 Mac 共用 web/index.html 内的同一套视觉外壳。
        // 原生壳只标记运行环境并处理窗口尺寸，不再注入第二套 CSS。
        let runtimeJs = """
        (function markMacRuntime() {
          if (document.documentElement) {
            document.documentElement.dataset.runtime = 'mac';
          } else {
            document.addEventListener('DOMContentLoaded', markMacRuntime, { once: true });
          }
        })();
        """
        // 启动时读取游戏侧写入的分辨率预设 localStorage.ts_display（JSON: {"w":720,"h":960}）
        // 存在则通过同一消息通道请求壳调整初始窗口尺寸
        let restoreJs = """
        (function() {
          try {
            var raw = localStorage.getItem('ts_display');
            if (!raw) return;
            var d = JSON.parse(raw);
            if (d && d.w > 0 && d.h > 0 &&
                window.webkit && window.webkit.messageHandlers &&
                window.webkit.messageHandlers.\(AppDelegate.messageName)) {
              window.webkit.messageHandlers.\(AppDelegate.messageName)
                .postMessage({type: 'resize', w: d.w, h: d.h});
            }
          } catch (e) {}
        })();
        """

        let config = WKWebViewConfiguration()
        config.userContentController.addUserScript(
            WKUserScript(source: runtimeJs, injectionTime: .atDocumentStart, forMainFrameOnly: true)
        )
        config.userContentController.addUserScript(
            WKUserScript(source: restoreJs, injectionTime: .atDocumentEnd, forMainFrameOnly: true)
        )
        config.userContentController.add(self, name: AppDelegate.messageName)
        config.preferences.setValue(true, forKey: "developerExtrasEnabled")

        let webView = WKWebView(frame: window.contentView!.bounds, configuration: config)
        webView.autoresizingMask = [.width, .height]
        window.contentView!.addSubview(webView)

        if let url = Bundle.main.url(forResource: "game", withExtension: "html") {
            webView.loadFileURL(url, allowingReadAccessTo: url.deletingLastPathComponent())
        } else {
            webView.loadHTMLString("<body style='background:#0b1120;color:#fff;font-family:sans-serif'><h3>game.html 缺失，请重新打包</h3></body>", baseURL: nil)
        }

        window.makeKeyAndOrderFront(nil)
        window.makeFirstResponder(webView)
        NSApp.activate(ignoringOtherApps: true)
    }

    // MARK: - WKScriptMessageHandler（游戏侧 resize 契约）

    func userContentController(_ userContentController: WKUserContentController,
                               didReceive message: WKScriptMessage) {
        guard message.name == AppDelegate.messageName,
              let body = message.body as? [String: Any],
              (body["type"] as? String) == "resize",
              let w = (body["w"] as? NSNumber)?.doubleValue,
              let h = (body["h"] as? NSNumber)?.doubleValue,
              w > 0, h > 0 else { return }
        applyContentSize(NSSize(width: w, height: h), animated: hasAppliedInitialSize)
        hasAppliedInitialSize = true
    }

    /// 把窗口内容尺寸平滑调整到目标值（钳制在屏幕可用区域内），并保持窗口中心不动。
    /// 游戏画面 letterbox 由游戏自己处理，壳只负责窗口尺寸。
    private func applyContentSize(_ size: NSSize, animated: Bool) {
        guard let window = window else { return }
        let visible = (window.screen ?? NSScreen.main)?.visibleFrame
            ?? NSRect(x: 0, y: 0, width: size.width, height: size.height)

        let w = min(max(size.width, AppDelegate.minContent.width), visible.width)
        let h = min(max(size.height, AppDelegate.minContent.height), visible.height)

        // 以当前窗口中心为锚点计算新 frame
        let currentFrame = window.frame
        let center = NSPoint(x: currentFrame.midX, y: currentFrame.midY)
        var newFrame = window.frameRect(forContentRect: NSRect(x: 0, y: 0, width: w, height: h))
        newFrame.origin = NSPoint(x: center.x - newFrame.width / 2,
                                  y: center.y - newFrame.height / 2)

        // 钳制到屏幕可用区域，防止标题栏被顶出屏幕
        if newFrame.maxX > visible.maxX { newFrame.origin.x = visible.maxX - newFrame.width }
        if newFrame.minX < visible.minX { newFrame.origin.x = visible.minX }
        if newFrame.maxY > visible.maxY { newFrame.origin.y = visible.maxY - newFrame.height }
        if newFrame.minY < visible.minY { newFrame.origin.y = visible.minY }

        if newFrame.size == currentFrame.size { return }

        if animated {
            NSAnimationContext.runAnimationGroup { ctx in
                ctx.duration = 0.25
                ctx.timingFunction = CAMediaTimingFunction(name: .easeInEaseOut)
                window.animator().setFrame(newFrame, display: true)
            }
        } else {
            window.setFrame(newFrame, display: true)
        }
    }

    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        return true
    }
}

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.setActivationPolicy(.regular)
app.run()
