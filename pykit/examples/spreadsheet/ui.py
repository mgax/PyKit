from os import path
from collections import namedtuple

from pykit.driver.cocoa import PyKitApp, exceptions_to_stderr
from pykit.driver.cocoa_dom import js_function

import monocle.core
from monocle import _o, launch

Position = namedtuple('Position', 'x y')

class Cell(object):
    def __init__(self, position, jQ):
        self.position = position
        self.td = jQ('<td><span class="value">hi!</span></td>')
        self.td.click(js_function(self.on_click))
        self.jQ = jQ

    def on_click(self, this, event):
        # close any edit view
        spreadsheet = self.td.closest('table.spreadsheet')
        spreadsheet.children('form.edit-cell').remove()

        # create our own edit box
        edit_input = self.jQ('<input>').val(self.value)
        edit_form = self.jQ('<form class="edit-cell">').append(edit_input)
        edit_form.append(self.jQ('<input type="submit" value="save">'))
        edit_input.submit(js_function(self.on_edit_submit))
        self.td.append(edit_form)

    def on_edit_submit(self, this, event):
        # funny thing: it segfaults before we get here.
        event.preventDefault()

    @property
    def value(self):
        return self.td.children('span.value').text()

def path_in_module(name):
    return path.join(path.dirname(__file__), name)

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

    with open(path_in_module('jquery-1.4.2.min.js'), 'r') as jquery_src:
        window.eval(jquery_src.read())
    jQ = window.jQuery

    with open(path_in_module('style.css'), 'r') as style_css:
        jQ('head').append("<style>" + style_css.read() + "</style>")

    table = jQ('<table class="spreadsheet">').appendTo(jQ("body"))
    for x in range(3):
        tr = jQ('<tr>').appendTo(table)
        for y in range(3):
            cell = Cell(Position(x, y), jQ)
            cell.td.appendTo(tr)

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
