import objc
import Foundation
import AppKit
import WebKit

from PyObjCTools import AppHelper

class MainThreadHelper(Foundation.NSObject):
    def onMainThread(self):
        self.func()

def main_thread(func, *args, **kwargs):
    """ Schedue `func` to be called on the main thread. """

    pool = Foundation.NSAutoreleasePool.new()

    obj = MainThreadHelper.new()
    obj.func = lambda: func(*args, **kwargs)

    selector = objc.selector(obj.onMainThread, signature='v@:')
    later = obj.performSelectorOnMainThread_withObject_waitUntilDone_
    later(selector, None, False)

#import functools
#from thread import get_ident as current_thread
#
#_main_thread_id = current_thread()
#
#def assert_main_thread(f):
#    """ Make sure the wrapped function is called on the main thread. """
#
#    msg = "%r must be run on main thread" % f
#
#    @functools.wraps(f)
#    def wrapper(*args, **kwargs):
#        assert current_thread() == _main_thread_id, msg
#        return f(*args, **kwargs)
#
#    return wrapper

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

    AppHelper.runEventLoop() # or maybe `app.run()`

if __name__ == '__main__':
    main()
