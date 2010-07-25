from monocle import _o, launch

from pykit.driver.cocoa import simple_app, create_window, add_event_listener
from pykit.driver.cocoa_console import repl


def demo_main():
    with simple_app():
        env = {'__name__': '__console__', '__doc__': None}
        launch(repl(env))
        launch(demo_window())

def say_hello(evt):
    print "HELLO!"

@_o
def demo_window():
    wkw = yield create_window()
    body = wkw.dom.firstChild().firstChild().nextSibling()
    add_event_listener(body, "click", say_hello)


if __name__ == '__main__':
    demo_main()
