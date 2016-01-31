from pyo import *  # NOQA


class TriangleTable(PyoTableObject):
    def __init__(self, order=10, size=8192):
        pyoArgsAssert(self, "II", order, size)
        PyoTableObject.__init__(self, size)
        self._order = order
        list = ([1./i for i in range(1, (order+1))] +
                [i/1. for i in range(1, (order+1))])
        self._base_objs = [HarmTable_base(list, size)]

    def setOrder(self, x):
        """
        Change the `order` attribute and redraw the waveform.

        :Args:

        x : int
        New number of harmonics

        """
        pyoArgsAssert(self, "I", x)
        self._order = x
        list = []
        list = ([1./i for i in range(1, (order+1))] +
                [i/1. for i in range(1, (order+1))])
        [obj.replace(list) for obj in self._base_objs]
        self.refreshView()

    @property
    def order(self):
        """int. Number of harmonics square waveform is made of."""
        return self._order

    @order.setter
    def order(self, x):
        self.setOrder(x)
