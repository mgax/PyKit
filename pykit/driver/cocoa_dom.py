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
    def __init__(self, script, insider=None):
        if insider is None:
            insider = JsInsider(script)
        self._insider = insider
        assert isinstance(script, WebKit.WebScriptObject)
        self._s = script

    def __call__(self, javascript_src):
        value = self._s.evaluateWebScript_(javascript_src)
        if isinstance(value, WebKit.WebScriptObject):
            value = ScriptWrapper(value, self._insider)
        return value

    def __getitem__(self, key):
        value = self._s.valueForKey_(key)
        if isinstance(value, WebKit.WebScriptObject):
            value = ScriptWrapper(value, self._insider)
        return value

    def __getattr__(self, key):
        value = self[key]
        ty = self._insider.type_of(value._s)
        assert ty == 'function', ("%r is of type %r instead of %r" %
                                  (value, ty, "function"))
        return ScriptMethodWrapper(self, key)

class ScriptMethodWrapper(object):
    def __init__(self, obj_wrapper, method_name):
        self.obj_wrapper = obj_wrapper
        self.method_name = method_name

    def __call__(self, *args):
        perform_call = self.obj_wrapper._s.callWebScriptMethod_withArguments_
        value = perform_call(self.method_name, args)
        if isinstance(value, WebKit.WebScriptObject):
            value = ScriptWrapper(value, self.obj_wrapper._insider)
        return value

INSIDER_JS = "({ type_of: function(value) { return typeof(value); } });"

class JsInsider(object):
    def __init__(self, script):
        self._js_obj = script.evaluateWebScript_(INSIDER_JS)

    def type_of(self, value):
        return self._js_obj.callWebScriptMethod_withArguments_('type_of',
                                                               [value])
