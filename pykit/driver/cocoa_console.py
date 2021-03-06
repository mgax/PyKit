from Foundation import *
from PyObjCTools import AppHelper

import sys

class FileObserver(NSObject):
    def initWithFileDescriptor_readCallback_errorCallback_(self,
            fileDescriptor, readCallback, errorCallback):
        self = self.init()
        self.readCallback = readCallback
        self.errorCallback = errorCallback
        self.fileHandle = NSFileHandle.alloc().initWithFileDescriptor_(
            fileDescriptor)
        self.nc = NSNotificationCenter.defaultCenter()
        self.nc.addObserver_selector_name_object_(
            self,
            'fileHandleReadCompleted:',
            NSFileHandleReadCompletionNotification,
            self.fileHandle)
        self.fileHandle.readInBackgroundAndNotify()
        return self

    def fileHandleReadCompleted_(self, aNotification):
        ui = aNotification.userInfo()
        newData = ui.objectForKey_(NSFileHandleNotificationDataItem)
        if newData is None:
            if self.errorCallback is not None:
                self.errorCallback(self, ui.objectForKey_(NSFileHandleError))
            self.close()
        else:
            self.fileHandle.readInBackgroundAndNotify()
            if self.readCallback is not None:
                self.readCallback(self, str(newData))

    def close(self):
        self.nc.removeObserver_(self)
        if self.fileHandle is not None:
            self.fileHandle.closeFile()
            self.fileHandle = None
        # break cycles in case these functions are closed over
        # an instance of us
        self.readCallback = None
        self.errorCallback = None

    def __del__(self):
        # Without this, if a notification fires after we are GC'ed
        # then the app will crash because NSNotificationCenter
        # doesn't retain observers.  In this example, it doesn't
        # matter, but it's worth pointing out.
        self.close()

def setup_input():
    from monocle.experimental import Channel

    line_input = Channel(10)

    def quit():
        sys.stdout.write("bye!\n")
        sys.stdout.flush()
        import AppKit
        AppKit.NSApp.terminate_(AppKit.NSApp)

    def handle_line(observer, data):
        if not data:
            return quit()
        line_input.send(data)

    def handle_error(err):
        sys.stdout.write("error!\n")

    FileObserver.alloc().initWithFileDescriptor_readCallback_errorCallback_(
        sys.stdin.fileno(), handle_line, handle_error).retain()

    return line_input.recv

from monocle import _o

@_o
def repl(locals):
    import code

    read_line = setup_input()
    console = code.InteractiveConsole(locals)

    def prompt(cont=False):
        sys.stdout.write("=.. " if cont else "=>> ")
        sys.stdout.flush()

    cont = False
    while True:
        prompt(cont)
        data = yield read_line()
        assert data.endswith('\n')
        line = data[:-1]
        cont = console.push(line)
