from monocle import _o
import monocle.util

@_o
def test_dom_behaviour(document):
    body = document.firstChild().firstChild().nextSibling()
    body.setInnerHTML_("<div>hello <em>world!</em></div>")
    yield monocle.util.sleep(.5)
    div = body.firstChild()
    assert div.nodeName() == 'DIV'
    assert div.innerText() == "hello world!"
    assert div.innerHTML() == "hello <em>world!</em>"

all_tests = [test_dom_behaviour]
