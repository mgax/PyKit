import monocle.core
from monocle import _o, launch

from pykit.driver.cocoa import (PyKitApp, exceptions_to_stderr,
                                add_event_listener)
from pykit.driver.cocoa_console import repl


def say_hello(evt):
    print "HELLO!"

@exceptions_to_stderr
@_o
def demo_window(app):
    wkw = yield app.create_window()
    body = wkw.document.firstChild.firstChild.nextSibling._w
    add_event_listener(body, "click", say_hello)

@exceptions_to_stderr
@_o
def main():
    env = {'__name__': '__console__', '__doc__': None}
    launch(repl(env))
    launch(demo_window())
    yield monocle.util.sleep(2)

def main():
    app = PyKitApp()
    env = {'__name__': '__console__', '__doc__': None}
    launch(repl(env))
    launch(demo_window(app))
    app.run_loop()

if __name__ == '__main__':
    main()
