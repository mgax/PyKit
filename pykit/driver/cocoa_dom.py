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
        return callback; }
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

def unwrap_js_objects(obj):
    """
    Unwrap any ScriptWrapper objects; everythigng else is passed through.
    """
    if isinstance(obj, ScriptWrapper):
        obj = obj.__pykit_private__.js_obj
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
        ret = priv.bridge.js_apply(priv.this, priv.js_obj,
                                   map(unwrap_js_objects, args))

        is_exc = ret.valueForKey_('is_exc')
        assert isinstance(is_exc, bool)

        if is_exc:
            raise ScriptException(ret.valueForKey_('exc'))
        else:
            return wrap_js_objects(ret.valueForKey_('out'), priv.bridge)

    def _callback(self, func):
        wrapper = CallbackWrapper.wrapperWithCallable_scriptWrapper(func, self)
        return self.__pykit_private__.bridge.make_callback(wrapper)

    def __repr__(self):
        priv = self.__pykit_private__
        return "<JavaScript %s>" % (priv.bridge.to_str(priv.js_obj),)

class CallbackWrapper(WebKit.NSObject):
    @classmethod
    def wrapperWithCallable_scriptWrapper(cls, callback, wrapper):
        self = cls.new()
        self.callback = callback
        self.wrapper = wrapper
        return self

    def calledWithContext_arguments_(self, this, args):
        bridge = self.wrapper.__pykit_private__.bridge
        args_length = int(args.valueForKey_('length'))
        py_args = [ wrap_js_objects(args.webScriptValueAtIndex_(i), bridge)
                    for i in xrange(args_length) ]

        self.callback(wrap_js_objects(this, bridge), *py_args)

    def isSelectorExcludedFromWebScript_(self, selector):
        if selector == 'calledWithContext:arguments:':
            return False
        else:
            return True
