from os import path

from pykit.driver.cocoa import PyKitApp, exceptions_to_stderr
from pykit.driver.cocoa_dom import js_function

import monocle.core
from monocle import _o, launch

class Cell(object):
    def __init__(self, jQ):
        self.ui = jQ('<td>hi!</td>')

@exceptions_to_stderr
@_o
def main_o(app):
    import monocle.util
    wkw = yield app.create_window()
    window = wkw.window

    @js_function
    def console_log(this, *args):
        print ' '.join(repr(a) for a in args)
    window['console'] = window.eval('({})')
    window['console']['log'] = console_log

    jquery_path = path.join(path.dirname(__file__), 'jquery-1.4.2.min.js')
    with open(jquery_path, 'rb') as f:
        window.eval(f.read())
    jQ = window.jQuery

    table = jQ('<table id="sheet">').appendTo(jQ("body"))
    for i in range(3):
        tr = jQ('<tr>').appendTo(table)
        for j in range(3):
            cell = Cell(jQ)
            cell.ui.appendTo(tr)

    @js_function
    def do_quit(this, *args):
        wait_to_quit.callback(None)
    jQ('body').prepend(jQ('<a href="#">').text('quit').click(do_quit), '<br>')

    wait_to_quit = monocle.core.Deferred()
    yield wait_to_quit
    app.terminate()

def main():
    app = PyKitApp()
    launch(main_o(app))
    app.run_loop()

if __name__ == '__main__':
    main()
