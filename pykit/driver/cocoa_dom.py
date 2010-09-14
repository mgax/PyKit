import WebKit

def cocoa_dom_property(name):
    def getter(self):
        value = getattr(self._w, name)()
        if isinstance(value, WebKit.DOMNode):
            value = DomNodeWrapper(value)
        return value

    def setter(self, value):
        if isinstance(value, DomNodeWrapper):
            value = value._w
        method_name = 'set' + name[0].upper() + name[1:] + '_'
        getattr(self._w, method_name)(value)

    getter.func_name = name
    setter.func_name = name
    return property(getter, setter)

class DomNodeWrapper(object):
    def __init__(self, wrapped):
        assert isinstance(wrapped, WebKit.DOMNode)
        self._w = wrapped

for name in ['firstChild', 'nextSibling', 'innerHTML', 'innerText',
             'nodeName']:
    setattr(DomNodeWrapper, name, cocoa_dom_property(name))
del name


class ScriptWrapper(object):
    def __init__(self, obj, insider=None):
        if insider is None:
            insider = JsInsider(obj)
        self._insider = insider
        assert isinstance(obj, WebKit.WebScriptObject)
        self._obj = obj

    def wrap_if_needed(self, value):
        if isinstance(value, WebKit.WebScriptObject):
            value = ScriptWrapper(value, self._insider)
        return value

    def eval(self, javascript_src):
        value = self._obj.evaluateWebScript_(javascript_src)
        return self.wrap_if_needed(value)

    def __getitem__(self, key):
        value = self._obj.valueForKey_(key)
        return self.wrap_if_needed(value)

    def __getattr__(self, key):
        value = self[key]
        ty = self._insider('type_of', value._obj)
        assert ty == 'function', ("%r is of type %r instead of %r" %
                                  (value, ty, "function"))
        return ScriptMethodWrapper(self, key)

    def _callback(self, func):
        wrapper = CallbackWrapper.wrapperWithCallable_scriptWrapper(func, self)
        return self._insider('make_callback', wrapper)

class ScriptMethodWrapper(object):
    def __init__(self, obj_wrapper, method_name):
        self.obj_wrapper = obj_wrapper
        self.method_name = method_name

    def __call__(self, *args):
        _call_with = self.obj_wrapper._obj.callWebScriptMethod_withArguments_
        value = _call_with(self.method_name, args)
        return self.obj_wrapper.wrap_if_needed(value)

INSIDER_JS = """({
    type_of: function(value) { return typeof(value); },
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
