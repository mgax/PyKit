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
            Foundation.NSMakeRect(900, 20, 400, 400),
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

    demo_coroutine()

    AppHelper.runEventLoop() # or maybe `app.run()`

from monocle import _o
import monocle.util

def setup_monocle():
    def not_implemented(*args, **kwargs):
        print "NOT IMPLEMENTED!"
        raise NotImplementedError

    import monocle.stack.eventloop

    monocle.stack.eventloop.queue_task = AppHelper.callLater
    monocle.stack.eventloop.run = not_implemented
    monocle.stack.eventloop.halt = not_implemented

class MyEventHandler(Foundation.NSObject):
    def handleEvent_(self, event):
        print "handling teh event"
        print event.x(), event.y()

@_o
def demo_coroutine():
    yield monocle.util.sleep(1)
    doc = webview.mainFrameDocument()
    body = doc.firstChild().firstChild().nextSibling()
    body.addEventListener___("click", MyEventHandler.alloc().init(), False)


if __name__ == '__main__':
    setup_monocle()
    main()
