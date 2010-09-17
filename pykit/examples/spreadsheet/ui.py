from os import path

from pykit.driver.cocoa import PyKitApp, exceptions_to_stderr
from pykit.driver.cocoa_dom import js_function

import monocle.core
from monocle import _o, launch

class Cell(object):
    def render(self, window):
        div = window['document'].createElement("DIV")
        div['innerHTML'] = "<td>hi!</td>"
        return div['firstChild']

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

    jQ('<table id="sheet">').appendTo(jQ("body"))
    document = window["document"]
    table = window.eval("document.getElementById('sheet')")
    for i in range(3):
        tr = document.createElement("TR")
        table.appendChild(tr)
        for j in range(3):
            td = document.createElement("TD")
            tr.appendChild(td)
            td.appendChild(Cell().render(window))

    @js_function
    def do_quit(this, *args):
        wait_to_quit.callback(None)
    jQ('<a href="#">').text('quit').click(do_quit).appendTo(jQ('body'))

    wait_to_quit = monocle.core.Deferred()
    yield wait_to_quit
    app.terminate()

def main():
    app = PyKitApp()
    launch(main_o(app))
    app.run_loop()

if __name__ == '__main__':
    main()
