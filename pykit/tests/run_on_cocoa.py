import sys
import traceback

from monocle import _o, launch
import monocle.core

from pykit.driver.cocoa import PyKitApp, exceptions_to_stderr

@_o
def run_tests(tests_to_run, *args):
    count = 0
    tracebacks = []
    for test in tests_to_run:
        try:
            yield test(*args)
        except Exception, e:
            if hasattr(e, '_monocle'):
                tb = monocle.core.format_tb(e)
            else:
                tb = traceback.format_exc()
            tracebacks.append(tb)
            print "E",
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

@exceptions_to_stderr
@_o
def main_o(app):
    window = yield app.create_window()

    def all_tests():
        import test_simple_dom
        for name in dir(test_simple_dom):
            if not name.startswith('test'):
                continue
            yield getattr(test_simple_dom, name)

    yield run_tests(all_tests(), window)

    app.terminate()

def main():
    app = PyKitApp()
    launch(main_o, app)
    app.run_loop()
