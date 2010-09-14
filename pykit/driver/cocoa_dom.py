class DomNodeWrapper(object):
    def __init__(self, wrapped):
        assert wrapped is not None
        self._w = wrapped

    @property
    def firstChild(self):
        return DomNodeWrapper(self._w.firstChild())

    @property
    def nextSibling(self):
        return DomNodeWrapper(self._w.nextSibling())

    @property
    def innerHTML(self):
        return self._w.innerHTML()

    @innerHTML.setter
    def innerHTML(self, value):
        return self._w.setInnerHTML_(value)

    @property
    def innerText(self):
        return self._w.innerText()

    @property
    def nodeName(self):
        return self._w.nodeName()
