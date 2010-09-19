from monocle import _o
import monocle.util

from pykit.driver.cocoa_dom import js_function

@_o
def test_dom_behaviour(ctx):
    body = ctx.window.document.firstChild.firstChild.nextSibling
    body.innerHTML = "<div>hello <em>world!</em></div>"
    yield monocle.util.sleep(.5)
    div = body.firstChild
    assert div.nodeName == 'DIV'
    assert div.innerText == "hello world!"
    assert div.innerHTML == "hello <em>world!</em>"

@_o
def test_javascript(ctx):
    assert ctx.window.eval('1+1') == 2
    assert ctx.window.eval('var c = 33; c - 20;') == 13

    ctx.window.eval('document.firstChild.innerHTML = "asdf";')
    assert ctx.window.document.firstChild.innerHTML == "asdf"

    dic = ctx.window.eval('window.pykittest_dict = {a: 13, b: {c: 22}}; '
                          'pykittest_dict')
    assert dic['a'] == 13 and dic['b']['c'] == 22

    dic['a'] = 25
    assert ctx.window.eval('pykittest_dict.a') == 25

    func = ctx.window.eval('window.pykittest_func = function(n){return n+3;}; '
                           'pykittest_func')

    assert repr(ctx.window.eval('[4, 123]')) == '<JavaScript 4,123>'

    # object comparison: object equal to itself; different objects not equal
    d = ctx.window.eval('({a: {}, b: {}})')
    assert d['a'] == d['a']
    assert d['a'] != d['b']

@_o
def test_javascript_properties(ctx):
    js_eval = ctx.window.eval
    jsob = js_eval('({a: 4})')
    assert repr(jsob) == "<JavaScript [object Object]>"
    assert jsob['a'] == 4
    try:
        jsob['b']
    except Exception, e:
        assert type(e) is KeyError
    else:
        assert False, "should raise KeyError"

    jsob['b'] = 3
    assert jsob['b'] == 3
    assert js_eval('({get_b:function(v){return v.b;}})').get_b(jsob) == 3

    assert jsob.a == 4
    assert jsob.b == 3

    try:
        jsob.c
    except Exception, e:
        assert type(e) is AttributeError
    else:
        assert False, "should raise AttributeError"

    jsob.c = 13
    assert jsob.c == 13
    assert js_eval('({get_c:function(v){return v.c;}})').get_c(jsob) == 13

@_o
def test_javascript_methods(ctx):
    ctx.window.eval('window.pykittest_callback = function(n){return n+6;};')
    assert ctx.window.pykittest_callback(10) == 16

    calls = []
    @js_function
    def call_to_python(this, *args):
        calls.append( (this, args) )
    ctx.window.eval('window.call_me_back = function(f) {\n'
                    '    f(); f(1, 3);\n'
                    '    var ob = {f: f, n: 13}; ob.f(); ob.f("asdf");\n'
                    '};')
    ctx.window.call_me_back(call_to_python)
    assert len(calls) == 4
    assert (calls[0][0].__pykit_private__.js_obj
            is ctx.window.__pykit_private__.js_obj)
    assert calls[1][1] == (1, 3)
    assert calls[2][0]['n'] == 13
    assert calls[3][1] == ("asdf",)

@_o
def test_exceptions_from_javascript(ctx):
    ctx.window.eval('window.crashme = function(){ something.non.existent; }')
    try:
        ctx.window.crashme()
    except Exception, e:
        from pykit.driver.cocoa_dom import ScriptException
        assert isinstance(e, ScriptException)
        assert e.args[0] == "ReferenceError: Can't find variable: something"
    else:
        assert False, "should raise exception"

@_o
def test_exceptions_from_python(ctx):
    @js_function
    def crash_py(this):
        raise ValueError("my error text")

    import sys
    from StringIO import StringIO
    _stderr = sys.stderr
    try:
        sys.stderr = StringIO()
        ret = ctx.window.eval('(function(x) { return x(); })')(crash_py)
        assert ret is None
        err_out = sys.stderr.getvalue()
    finally:
        sys.stderr = _stderr

    assert "ValueError" in err_out
    assert "my error text" in err_out

@_o
def test_javascript_method_arguments(ctx):
    ctx.window.eval('window.whatis = function(arg) { '
                    'return {type: typeof(arg), str: ""+arg}; }')
    what = ctx.window.whatis
    def assert_what(value, js_type, js_str):
        out = what(value)
        assert out['type'] == js_type, "%r != %r" % (out['type'], js_type)
        assert out['str'] == js_str, "%r != %r" % (out['str'], js_str)

    assert_what(1, 'number', '1')
    assert_what("asdf", 'string', 'asdf')
    assert_what([1,2,"asdf"], 'object', '1,2,asdf')
    assert_what({'a': 'b'}, 'object', '{\n    a = b;\n}')
    assert_what(True, 'boolean', 'true')
    assert_what(None, 'object', 'null')

    class C(object):
        def __repr__(self): return "<:)>"
    assert_what(C(), 'object', '<:)>')

    # auto-unwrap wrapped arguments
    assert_what(what, 'function', ('function (arg) { return {type: '
                                   'typeof(arg), str: ""+arg}; }') )

    assert_what(ctx.window['document'], 'object', '[object HTMLDocument]')

@_o
def test_javascript_eval(ctx):
    ev = ctx.window.eval
    assert ev('') is None
    assert ev('null') is None
    assert ev('13') == 13
    assert ev('"hi"') == "hi"
    assert ev('1+2') == 3
    assert ev('(function(){var c=3; return c+5;})()') == 8

    try:
        ev('---')
    except Exception, e:
        from pykit.driver.cocoa_dom import ScriptException
        assert isinstance(e, ScriptException)
        assert e.args[0] == 'SyntaxError: Parse error'
    else:
        assert False, "should raise exception"

all_tests = [test_dom_behaviour, test_javascript,
             test_javascript_properties, test_javascript_methods,
             test_exceptions_from_javascript, test_exceptions_from_python,
             test_javascript_method_arguments, test_javascript_eval]
