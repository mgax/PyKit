import WebKit

class ScriptException(Exception):
    pass

class ScriptWrapper(object):
    def __init__(self, obj, insider=None, call_ctx=None):
        if insider is None:
            insider = JsInsider(obj)
        self.__dict__['_insider'] = insider
        assert isinstance(obj, WebKit.WebScriptObject)
        self.__dict__['_obj'] = obj
        self.__dict__['_call_ctx'] = call_ctx

    def wrap_if_needed(self, value, call_ctx=None):
        if isinstance(value, WebKit.WebScriptObject):
            value = ScriptWrapper(value, self._insider, call_ctx)
        return value

    def __getitem__(self, key):
        value = self._obj.valueForKey_(key)
        return self.wrap_if_needed(value)

    def __setitem__(self, key, value):
        self._obj.setValue_forKey_(value, key)

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, key):
        try:
            value = self._obj.valueForKey_(key)
        except KeyError:
            raise AttributeError(key)
        else:
            return self.wrap_if_needed(value, self)

    def __call__(self, *args):
        js_this = self._call_ctx._obj
        js_func = self._obj
        js_args = [ (a._obj if isinstance(a, ScriptWrapper) else a)
                       for a in args ]
        ret = self._insider('apply', js_this, js_func, js_args)

        is_exc = ret.valueForKey_('is_exc')
        assert isinstance(is_exc, bool)

        if is_exc:
            raise ScriptException(ret.valueForKey_('exc'))
        else:
            return self.wrap_if_needed(ret.valueForKey_('out'))

    def _callback(self, func):
        wrapper = CallbackWrapper.wrapperWithCallable_scriptWrapper(func, self)
        return self._insider('make_callback', wrapper)

    def __repr__(self):
        return "<JavaScript %s>" % (self._insider('to_str', self._obj),)

INSIDER_JS = """({
    type_of: function(value) { return typeof(value); },
    to_str: function(value) { return ""+value; },
    apply: function(ctx, func, args) {
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

class JsInsider(object):
    def __init__(self, obj):
        self._obj = obj.evaluateWebScript_(INSIDER_JS)

    def __call__(self, name, *args):
        return self._obj.callWebScriptMethod_withArguments_(name, args)

class CallbackWrapper(WebKit.NSObject):
    @classmethod
    def wrapperWithCallable_scriptWrapper(cls, callback, wrapper):
        self = cls.new()
        self.callback = callback
        self.wrapper = wrapper
        return self

    def calledWithContext_arguments_(self, this, arguments):
        length = int(arguments.valueForKey_('length'))
        def arg(i):
            value = arguments.webScriptValueAtIndex_(i)
            return self.wrapper.wrap_if_needed(value)

        self.callback(self.wrapper.wrap_if_needed(this),
                      *[arg(i) for i in range(length)])

    def isSelectorExcludedFromWebScript_(self, selector):
        if selector == 'calledWithContext:arguments:':
            return False
        else:
            return True
