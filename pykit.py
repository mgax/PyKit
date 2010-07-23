import objc
import Foundation
import AppKit
import WebKit

from PyObjCTools import AppHelper

class WindowDelegate(Foundation.NSObject):
    def windowWillClose_(self, notification):
        AppKit.NSApp.terminate_(self)

def main():
    app = AppKit.NSApplication.sharedApplication()

    window = AppKit.NSWindow.alloc()
    mask = ( AppKit.NSTitledWindowMask |
             AppKit.NSClosableWindowMask |
             AppKit.NSMiniaturizableWindowMask |
             AppKit.NSResizableWindowMask )
    window = window.initWithContentRect_styleMask_backing_defer_(
            Foundation.NSMakeRect(13, 13, 400, 400),
            mask,
            AppKit.NSBackingStoreBuffered,
            False)

    webview = WebKit.WebView.alloc().init()
    window.setContentView_(webview)

    window.setDelegate_(WindowDelegate.alloc().init().retain())
    window.makeKeyAndOrderFront_(app)

    url = AppKit.NSURL.URLWithString_('about:blank').retain()
    webview.mainFrame().loadHTMLString_baseURL_("Hello world!", url)

    from console import setup_repl
    setup_repl(webview)

    AppHelper.runEventLoop() # or maybe `app.run()`

if __name__ == '__main__':
    main()
