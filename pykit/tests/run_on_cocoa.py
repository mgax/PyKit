import sys

from monocle import _o, launch
import monocle.core

from pykit.driver.cocoa import PyKitApp, exceptions_to_stderr

@exceptions_to_stderr
@_o
def main_o(app):
    window = yield app.create_window()

    import test_simple_dom
    count = 0
    tracebacks = []
    for dom_test in test_simple_dom.all_tests:
        try:
            yield dom_test(window)
        except Exception, e:
            print "E",
            tracebacks.append(monocle.core.format_tb(e))
        else:
            sys.stdout.write(".")
            sys.stdout.flush()
        count += 1

    print "\nran %d tests" % count
    for tb in tracebacks:
        print tb

    app.terminate()

def main():
    app = PyKitApp()
    launch(main_o(app))
    app.run_loop()
