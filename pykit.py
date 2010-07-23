import objc
import Foundation
import AppKit

from PyObjCTools import AppHelper

class WindowDelegate(Foundation.NSObject):
    def windowWillClose_(self, notification):
        AppKit.NSApp.terminate_(self)

def main():
    app = AppKit.NSApplication.sharedApplication()

    mask = ( AppKit.NSTitledWindowMask |
             AppKit.NSClosableWindowMask |
             AppKit.NSMiniaturizableWindowMask |
             AppKit.NSResizableWindowMask )
    w = AppKit.NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            Foundation.NSMakeRect(13, 13, 400, 400),
            mask,
            AppKit.NSBackingStoreBuffered,
            False)
    w.setDelegate_(WindowDelegate.alloc().init().retain())
    w.makeKeyAndOrderFront_(app)
    AppHelper.runEventLoop() # or maybe `app.run()`

if __name__ == '__main__':
    main()
