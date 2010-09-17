from collections import namedtuple

import WebKit

class ScriptException(Exception):
    pass

INSIDER_JS = """({
    to_str: function(value) { return ""+value; },
    js_apply: function(ctx, func, args) {
        try {
            var out = func.apply(ctx, args);
            if(out === undefined) out = null;
            return {is_exc: false, out: out};
        } catch(e) {
            return {is_exc: true, exc: ""+e};
        }
    },
    make_callback: function(wrapper) {
        var callback = function() {
            wrapper.calledWithContext_arguments_(this, arguments);
        };
        return callback;
    }
});"""

class ScriptBridge(object):
    """
    Wrap the global JavaScript object and help bridge Python and JS semantics
    """

    def __init__(self, js_window):
        self.js_insider = js_window.evaluateWebScript_(INSIDER_JS)
        self.window = ScriptWrapper(js_window, self, js_window)
        self.js_window = js_window

    def _call_insider(self, name, args):
        return self.js_insider.callWebScriptMethod_withArguments_(name, args)

    def to_str(self, *args):
        return self._call_insider('to_str', args)

    def js_apply(self, *args):
        return self._call_insider('js_apply', args)

    def make_callback(self, *args):
        return self._call_insider('make_callback', args)

def wrap_js_objects(obj, bridge, this=None):
    """
    Filter that wraps plain JS objects (WebKit.WebScriptObject) into
    ScriptWrapper objects; other objects are passed through.
    """
    if isinstance(obj, WebKit.WebScriptObject):
        if this is None:
            this = bridge.js_window
        obj = ScriptWrapper(obj, bridge, this)
    return obj

# container for private information of a ScriptWrapper instance
ScriptWrapperPrivate = namedtuple('ScriptWrapperPrivate', 'js_obj bridge this')

class ScriptWrapper(object):
    __slots__ = ('__pykit_private__',)

    def __init__(self, js_obj, bridge, this):
        assert isinstance(js_obj, WebKit.WebScriptObject)
        assert isinstance(this, WebKit.WebScriptObject)
        priv = ScriptWrapperPrivate(js_obj, bridge, this)
        object.__setattr__(self, '__pykit_private__', priv)

    def __getitem__(self, key):
        priv = self.__pykit_private__
        value = priv.js_obj.valueForKey_(key)
        return wrap_js_objects(value, priv.bridge)

    def __setitem__(self, key, value):
        self.__pykit_private__.js_obj.setValue_forKey_(value, key)

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, key):
        priv = self.__pykit_private__
        try:
            value = priv.js_obj.valueForKey_(key)
        except KeyError:
            raise AttributeError(key)
        else:
            return wrap_js_objects(value, priv.bridge, priv.js_obj)

    def __call__(self, *args):
        priv = self.__pykit_private__

        def unwrap(obj):
            if isinstance(obj, ScriptWrapper):
                return obj.__pykit_private__.js_obj
            elif isinstance(obj, js_function):
                return obj.callback_for_bridge(priv.bridge)
            else:
                return obj

        ret = priv.bridge.js_apply(priv.this, priv.js_obj, map(unwrap, args))

        is_exc = ret.valueForKey_('is_exc')
        assert isinstance(is_exc, bool)

        if is_exc:
            raise ScriptException(ret.valueForKey_('exc'))
        else:
            return wrap_js_objects(ret.valueForKey_('out'), priv.bridge)

    def __repr__(self):
        priv = self.__pykit_private__
        return "<JavaScript %s>" % (priv.bridge.to_str(priv.js_obj),)

    def __eq__(self, other):
        # TODO: needs a unit test
        if isinstance(other, ScriptWrapper):
            return bool(self.__pykit_private__.js_obj
                        is other.__pykit_private__.js_obj)
        else:
            return False


class JsMethod(WebKit.NSObject):
    @classmethod
    def newWithPyFunc_bridge_(cls, func, bridge):
        self = cls.new()
        self.func = func
        self.bridge = bridge
        return self

    def calledWithContext_arguments_(self, this, args):
        arg_n = args.webScriptValueAtIndex_
        py_args = [ wrap_js_objects(arg_n(i), self.bridge)
                    for i in xrange(int(args.valueForKey_('length'))) ]

        self.func(wrap_js_objects(this, self.bridge), *py_args)

    def isSelectorExcludedFromWebScript_(self, selector):
        return bool(selector != 'calledWithContext:arguments:')

class js_function(object):
    """ decorate `func` to be callable from JavaScript """

    def __init__(self, func):
        self.func = func

    def callback_for_bridge(self, bridge):
        function_wrapper =  JsMethod.newWithPyFunc_bridge_(self.func, bridge)
        return bridge.make_callback(function_wrapper)
