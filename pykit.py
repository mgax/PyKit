from contextlib import contextmanager

from monocle import _o, launch
from monocle.deferred import Deferred

import objc
import Foundation
import AppKit
import WebKit

from PyObjCTools import AppHelper

def _setup_monocle():
    def not_implemented(*args, **kwargs):
        print "NOT IMPLEMENTED!"
        raise NotImplementedError
    import monocle.stack.eventloop
    monocle.stack.eventloop.queue_task = AppHelper.callLater
    monocle.stack.eventloop.run = not_implemented
    monocle.stack.eventloop.halt = not_implemented

def init():
    _setup_monocle()
    AppKit.NSApplication.sharedApplication()

def terminate():
    AppKit.NSApp.terminate_(AppKit.NSApp)

class WebKitWindow(object):
    def _set_up_window(self, rect):
        assert len(rect) == 4
        mask = ( AppKit.NSTitledWindowMask |
                 AppKit.NSClosableWindowMask |
                 AppKit.NSMiniaturizableWindowMask |
                 AppKit.NSResizableWindowMask )
        window = AppKit.NSWindow.alloc()
        window = window.initWithContentRect_styleMask_backing_defer_(
                Foundation.NSMakeRect(*rect),
                mask,
                AppKit.NSBackingStoreBuffered,
                False)

        webview = WebKit.WebView.alloc().init()
        window.setContentView_(webview)
        window.makeKeyAndOrderFront_(AppKit.NSApp)

        url = AppKit.NSURL.URLWithString_('about:blank').retain()
        webview.mainFrame().loadHTMLString_baseURL_("hello world", url)

        self.window = window.retain()
        self.webview = webview.retain()

    @property
    def dom(self):
        return self.webview.mainFrameDocument()

@_o
def create_window(rect):
    w = WebKitWindow()
    w._set_up_window(rect)

    import monocle.util
    while True:
        if w.dom is not None:
            break
        yield monocle.util.sleep(.1)

    yield w # return

def cocoa_app_loop(console=False):
    if console is not False:
        assert type(console) is dict
        from console import setup_repl
        setup_repl(locals=console)

    AppHelper.runEventLoop()

def pykit_demo():
    init()
    launch(demo_coroutine())
    env = {'__name__': '__console__', '__doc__': None}
    cocoa_app_loop(console=env)


class MyEventHandler(Foundation.NSObject):
    @classmethod
    def handlerWithCallback_(cls, callback):
        self = cls.alloc().init()
        self._callback = callback
        return self

    def handleEvent_(self, event):
        self._callback(event)

def add_event_listener(node, event_name, callback, capture=False):
    handler = MyEventHandler.handlerWithCallback_(callback)
    node.addEventListener___(event_name, handler, capture)

@_o
def demo_coroutine():
    wkw = yield create_window(rect=(900, 20, 400, 400))
    body = wkw.dom.firstChild().firstChild().nextSibling()
    def say_hello(evt):
        print "HELLO!"
    add_event_listener(body, "click", say_hello)


if __name__ == '__main__':
    pykit_demo()
