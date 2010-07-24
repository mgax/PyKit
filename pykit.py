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

from monocle import _o

@_o
def other_coroutine():
    print "coroutine start"
    import monocle.util
    yield monocle.util.sleep(3)
    print "coroutine continue"
    yield 13
    print "coroutine done"

def setup_monocle():
    def not_implemented(*args, **kwargs):
        print "NOT IMPLEMENTED!"
        raise NotImplementedError

    import monocle.stack.eventloop

    monocle.stack.eventloop.queue_task = AppHelper.callLater
    monocle.stack.eventloop.run = not_implemented
    monocle.stack.eventloop.halt = not_implemented

    def prnt(result):
        print ":)"
    other_coroutine().add_callback(prnt)


if __name__ == '__main__':
    setup_monocle()
    main()
