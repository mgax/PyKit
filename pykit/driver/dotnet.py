import traceback
import functools

import System.Windows.Forms as Forms

def print_exc(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            traceback.print_exc()
    try:
        wrapper = functools.wraps(func)(wrapper)
    except:
        pass
    return wrapper

def call_later(timeout, callback, *args, **kwargs):
    """ Call `func` on main thread. Print any exeptions to stderr. """
    from System.Timers import Timer
    timer = Timer(timeout * 1000)
    @print_exc
    def timer_fired(*evt_args):
        call_on_main(lambda: callback(*args, **kwargs))
    timer.Elapsed += timer_fired
    timer.AutoReset = False
    timer.Start()

def setup_monocle():
    def not_implemented(*args, **kwargs):
        print "NOT IMPLEMENTED!"
        raise NotImplementedError
    import monocle.stack.eventloop
    monocle.stack.eventloop.queue_task = call_later
    monocle.stack.eventloop.run = not_implemented
    monocle.stack.eventloop.halt = not_implemented

def init():
    setup_monocle()
    from System.Reflection import Assembly
    Assembly.LoadFrom(r'WebKitBrowser.dll')

def call_on_main(func):
    import sys
    print>>sys.stderr, "No main loop available; running on caller's thread."
    func()

def app_loop():
    Forms.Application.EnableVisualStyles()
    dummy_control = Forms.Control()
    dummy_control.Handle # force the handle to be created
    global call_on_main
    @print_exc
    def call_on_main(func):
        dummy_control.Invoke(Forms.MethodInvoker(func))
    Forms.Application.Run()

def terminate():
    Forms.Application.Exit()

class PyKitApp(object):
    def __init__(self):
        init()

    def run_loop(self):
        app_loop()

    def create_window(self, **kwargs):
        raise NotImplementedError()
        #return create_window(**kwargs)

    def terminate(self):
        terminate()
