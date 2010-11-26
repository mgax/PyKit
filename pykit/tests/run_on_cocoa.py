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
    for name in dir(test_simple_dom):
        if not name.startswith('test'):
            continue
        dom_test = getattr(test_simple_dom, name)
        try:
            yield dom_test(window)
        except Exception, e:
            print "E",
            tracebacks.append(monocle.core.format_tb(e))
        else:
            sys.stdout.write(".")
            sys.stdout.flush()
        count += 1

    for tb in tracebacks:
        print tb

    if tracebacks:
        result = "%d errors" % len(tracebacks)
    else:
        result = "pass"
    print "\nran %d tests: %s" % (count, result)

    app.terminate()

def main():
    app = PyKitApp()
    launch(main_o, app)
    app.run_loop()
