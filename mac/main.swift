import Cocoa
import WebKit

final class AppDelegate: NSObject, NSApplicationDelegate {
    private var window: NSWindow!

    func applicationDidFinishLaunching(_ notification: Notification) {
        let contentRect = NSRect(x: 0, y: 0, width: 540, height: 900)
        window = NSWindow(
            contentRect: contentRect,
            styleMask: [.titled, .closable, .miniaturizable, .resizable],
            backing: .buffered,
            defer: false
        )
        window.title = "雷霆战机 · Thunder Strike"
        window.minSize = NSSize(width: 420, height: 700)
        window.backgroundColor = NSColor(red: 0.043, green: 0.067, blue: 0.125, alpha: 1.0)
        window.center()

        // In the Widget host, colors come from Kimi runtime tokens.
        // Inside the standalone app we inject a matching dark theme instead.
        let appCss = """
        body { background: #0b1120 !important; color: #e8eefc !important;
               font-family: -apple-system, "PingFang SC", sans-serif !important; }
        h1 .sub, .help, p.status { color: #93a3c8 !important; }
        p.status output { color: #e8eefc !important; }
        .stage { border-color: #2a3554 !important; }
        .controls button { background: #1a2140 !important; border-color: #39466e !important; color: #e8eefc !important; }
        .controls button.primary { background: #3a7bff !important; color: #ffffff !important; border-color: transparent !important; }
        """
        let js = """
        (function() {
          var s = document.createElement('style');
          s.textContent = String.raw`\(appCss)`;
          document.head.appendChild(s);
        })();
        """
        let config = WKWebViewConfiguration()
        config.userContentController.addUserScript(
            WKUserScript(source: js, injectionTime: .atDocumentEnd, forMainFrameOnly: true)
        )
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

    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        return true
    }
}

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.setActivationPolicy(.regular)
app.run()
