from os import path
from collections import namedtuple
from decimal import Decimal as D

from pykit.driver.cocoa import PyKitApp, exceptions_to_stderr
from pykit.driver.cocoa_dom import js_function

import monocle.core
from monocle import _o, launch

Position = namedtuple('Position', 'x y')

def parse(txt):
    if txt[0] == '=':
        return "[formula]"
    try:
        return D(txt)
    except ValueError:
        return txt

class Cell(object):
    def __init__(self, position, jQ):
        self.position = position
        self.td = jQ('<td><span class="value"></span></td>')
        self.td.click(js_function(self.on_click))
        self.jQ = jQ
        self.value = ""

    def on_click(self, this, event):
        # close any edit view
        if not event.target in (this, this.firstChild):
            return
        spreadsheet = self.td.closest('table.spreadsheet')
        self.jQ('input.edit-cell', spreadsheet).remove()

        # create our own edit box
        edit_input = self.jQ('<input class="edit-cell">').val(self.value)
        edit_input.keydown(js_function(self.on_keydown))
        edit_input.prependTo(self.td).focus()

    def on_keydown(self, this, event):
        if event.keyCode not in (13, 27):
            return

        if event.keyCode == 13: # enter
            self.value = parse(self.jQ(this).val())

        event.preventDefault()
        event.stopPropagation()
        self.jQ(this).remove()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value
        self.update_ui()

    def update_ui(self):
        self.td.children('span.value').text(unicode(self._value) or u"\u00a0")

def path_in_module(name):
    return path.join(path.dirname(__file__), name)

def setup_cocoa_app():
    import AppKit
    app = AppKit.NSApplication.sharedApplication()
    app.setActivationPolicy_(0)
    app.setMainMenu_(AppKit.NSMenu.alloc().initWithTitle_("pykit"))
    url = AppKit.NSURL.alloc().initFileURLWithPath_(path_in_module("icon.png"))
    icon = AppKit.NSImage.alloc().initWithContentsOfURL_(url)
    app.setApplicationIconImage_(icon)
    app.activateIgnoringOtherApps_(True) # sort of rude

@exceptions_to_stderr
@_o
def main_o(app):
    setup_cocoa_app()
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
