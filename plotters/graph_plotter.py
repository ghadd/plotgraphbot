import uuid
import matplotlib.pyplot as plt
import sympy as sp
import numpy as np

from pathlib import Path
from tempfile import gettempdir
from uuid import uuid1


class GraphPlotter:
    def __init__(self, **kwargs):
        self.expression = kwargs.get('expression')
        self.xlim = kwargs.get('xlim') or (-10, 10)
        self.ylim = kwargs.get('ylim')
        self.title = kwargs.get('title') or "Plot"
        self.xlab = kwargs.get('xlab') or 'x'
        self.ylab = kwargs.get('ylab') or 'y'

        if not self.expression:
            raise ValueError("No expression was given")

        self.__x = sp.Symbol('x')
        self.__expr = sp.sympify(self.expression)

        self.__function = np.vectorize(sp.lambdify(self.__x, self.__expr))

        assert type(self.xlim) in [list, tuple], \
            'xlim must be a list or a tuple'
        if self.ylim:
            assert type(self.ylim) in [list, tuple], \
                'ylim must be a list or a tuple'

        self.__fig, self.__ax = plt.subplots()
        if self.xlim:
            self.__ax.set_xlim(self.xlim)
        if self.ylim:
            self.__ax.set_ylim(self.ylim)

        self.__ax.set_xlabel(self.xlab)
        self.__ax.set_ylabel(self.ylab)

        self.__ax.set_title(self.title)

    def plot(self):
        if not self.expression:
            raise ValueError("Not expression was provided")

        xs = np.linspace(*self.xlim, int(1e4))
        try:
            ys = self.__function(xs)
        except:
            raise ValueError("Could not resolve your expression.")

        self.__ax.plot(xs, ys)
        self.__ax.grid()

    def save_plot(self) -> str:
        filename = str(Path(gettempdir()) / f'{uuid1()}.png')
        print(f"Saving at {filename}")
        self.__fig.savefig(filename)

        return filename
