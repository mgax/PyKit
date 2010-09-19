from os import path
from decimal import Decimal as D

from pykit.driver.cocoa import PyKitApp, exceptions_to_stderr
from pykit.driver.cocoa_dom import js_function

import monocle.core
from monocle import _o, launch

def html_quote(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

class Cell(object):
    def __init__(self, x, y, sheet, jQ):
        self.x, self.y = x, y
        self.td = jQ('<td><span class="value"></span></td>')
        self.td.click(js_function(self.on_click))
        self.jQ = jQ
        self.value = ""
        self.sheet = sheet

    def on_click(self, this, event):
        # close any edit view
        if self.jQ(event.target).filter('input.edit-cell').length:
            return
        spreadsheet = self.td.closest('table.spreadsheet')
        self.jQ('input.edit-cell', spreadsheet).remove()

        # create our own edit box
        edit_input = self.jQ('<input class="edit-cell">')
        edit_input.val(unicode(self.value))
        edit_input.keydown(js_function(self.on_keydown))
        edit_input.prependTo(self.td).focus()

    def on_keydown(self, this, event):
        if event.keyCode not in (13, 27):
            return

        if event.keyCode == 13: # enter
            self.value = self.jQ(this).val()

        event.preventDefault()
        event.stopPropagation()
        self.jQ(this).remove()

    @property
    def computed_value(self):
        if self._value.startswith('='):
            return eval(self._value[1:], {'S': self.sheet})
        else:
            return self._value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value
        self.update_ui()

    def update_ui(self):
        try:
            display = html_quote(unicode(self.computed_value))
        except Exception, e:
            display = '<span class="cell-error">%s</span>' % unicode(e)
        else:
            if self._value.startswith('='):
                display = '<span class="computed-cell">%s</span>' % display
        self.td.children('span.value').html(display or u"\u00a0")

class Sheet(object):
    def __init__(self):
        self.cells = {}

    def new_cell(self, x, y, **kwargs):
        c = self.cells[x,y] = Cell(x=x, y=y, **kwargs)
        return c

    def __getitem__(self, key):
        return self.cells[key].computed_value

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
    wkw = yield app.create_window(size=(500, 300), position=(100, 20))
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

    sheet = Sheet()

    table = jQ('<table class="spreadsheet">').appendTo(jQ("body"))
    for x in range(3):
        tr = jQ('<tr>').appendTo(table)
        for y in range(3):
            sheet.new_cell(x=x, y=y, sheet=sheet, jQ=jQ).td.appendTo(tr)

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
