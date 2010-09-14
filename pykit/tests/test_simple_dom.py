from monocle import _o
import monocle.util

@_o
def test_dom_behaviour(window):
    body = window.dom.firstChild.firstChild.nextSibling
    body.innerHTML = "<div>hello <em>world!</em></div>"
    yield monocle.util.sleep(.5)
    div = body.firstChild
    assert div.nodeName == 'DIV'
    assert div.innerText == "hello world!"
    assert div.innerHTML == "hello <em>world!</em>"

@_o
def test_javascript(window):
    assert window.script('1+1') == 2
    assert window.script('var c = 33; window.c - 20;') == 13

    window.script('document.firstChild.innerHTML = "asdf";')
    assert window.dom.firstChild.innerHTML == "asdf"

    dic = window.script('var pykittest_dict = {a: 13, b: {c: 22}}; '
                        'pykittest_dict')
    assert dic['a'] == 13 and dic['b']['c'] == 22

all_tests = [test_dom_behaviour, test_javascript]
