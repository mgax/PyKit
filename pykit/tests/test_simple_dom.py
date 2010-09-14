from monocle import _o
import monocle.util

@_o
def test_dom_behaviour(ctx):
    body = ctx.document.firstChild.firstChild.nextSibling
    body.innerHTML = "<div>hello <em>world!</em></div>"
    yield monocle.util.sleep(.5)
    div = body.firstChild
    assert div.nodeName == 'DIV'
    assert div.innerText == "hello world!"
    assert div.innerHTML == "hello <em>world!</em>"

@_o
def test_javascript(ctx):
    assert ctx.window.eval('1+1') == 2
    assert ctx.window.eval('var c = 33; window.c - 20;') == 13

    ctx.window.eval('document.firstChild.innerHTML = "asdf";')
    assert ctx.document.firstChild.innerHTML == "asdf"

    dic = ctx.window.eval('var pykittest_dict = {a: 13, b: {c: 22}}; '
                          'pykittest_dict')
    assert dic['a'] == 13 and dic['b']['c'] == 22

    func = ctx.window.eval('var pykittest_func = function(n) { return n+3; }; '
                           'pykittest_func')

@_o
def test_javascript_methods(ctx):
    ctx.window.eval('var pykittest_callback = function(n) { return n + 6; };')
    assert ctx.window.pykittest_callback(10) == 16

all_tests = [test_dom_behaviour, test_javascript, test_javascript_methods]
