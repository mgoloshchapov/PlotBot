import numpy as np
from sympy.parsing.sympy_parser import parse_expr
from sympy.utilities import lambdify
from sympy import symbols
import sympy.core
from tokenize import TokenError


# также в парсингей sympy можно добавить собственный синтаксис, что может пригодиться

class Equation():
    """
    Equation class for working with equations
    """

    def __init__(self, expression):
        if isinstance(expression, sympy.Expr):
            # enter sympy expression directly
            self.expression = expression
            self._symbols_update()
        else:
            try:
                # enter expression string
                self.expression = parse_expr(expression)
                self._symbols_update()
            except SyntaxError:
                print('Unable to create equation due to: SyntaxError')
            except TokenError:
                print('Unable to create equation due to: TokenError')

    def _symbols_update(self):
        """
        Gets free symbols from expression and orders alphabetically
        """
        self.symbols_sting = [str(sym) for sym in list(self.expression.free_symbols)]
        self.symbols_sting.sort()
        self.symbols = [symbols(char) for char in self.symbols_sting]

    def lambdify(self):
        """
        returns lambda function, that takes arguments for self.symbols and evaluates the expression.
        """
        return lambdify(self.symbols, self.expression)

    def evaluate(self, **kwargs):
        """
        returns an evaluated sympy expression
        :param kwargs: symbol to be evaluated = value (x=12, y='pi')
        :return: sympy expression with the symbols to be evaluated replaced with the given values
        """
        print(kwargs)
        return self.expression.subs(kwargs)

    def self_evaluate(self, **kwargs):
        """
        replaces self.expression with evaluated expression and recalculates free symbols
        :param kwargs: symbol to be evaluated = value (x=12, y='pi')
        """
        self.expression = self.expression.subs(kwargs)
        self._symbols_update()

    def __str__(self):
        return str(self.expression)


# example code
#
# billy = Equation('cos(x - 1) + y - sin(a)')
# billie_jean = billy.lambdify()
# a = np.array([1, 2, 3])
# b = np.array([2, 3, 4])
# c = np.array([3, 4, 5])
# d = [a, b, c]
# print(billie_jean(*d))
