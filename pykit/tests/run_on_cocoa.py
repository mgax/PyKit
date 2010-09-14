import sys

from monocle import _o, launch
import monocle.core

from pykit.driver.cocoa import simple_app, create_window, terminate

@_o
def run_tests():
    window = yield create_window()
    document = window.dom

    import test_simple_dom
    count = 0
    tracebacks = []
    for dom_test in test_simple_dom.all_tests:
        try:
            yield dom_test(document)
        except Exception, e:
            print "E",
            tracebacks.append(monocle.core.format_tb(e))
        else:
            print ".",
        count += 1

    print "\nran %d tests" % count
    for tb in tracebacks:
        print tb

@_o
def async_main():
    try:
        yield run_tests()
    except Exception, e:
        print>>sys.stderr, monocle.core.format_tb(e)
    finally:
        terminate()

def main():
    with simple_app():
        launch(async_main())
