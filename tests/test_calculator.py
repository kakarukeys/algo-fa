import unittest

import pandas as pd

from fa import calculator
from tests.util import PandasTestCase


class TestCalculator(PandasTestCase):
    def test_delta__Series(self):
        result = calculator.delta(pd.Series([3, 2, 8], index=[0, 1, 4]))
        self.assertFrameEqual(result, pd.Series([-1, 6]), check_dtype=False)

    def test_delta__DataFrame(self):
        result = calculator.delta(pd.DataFrame({'a': [3, 2, 8], 'b': [3, 2, 7]}, index=[0, 1, 4]))
        self.assertFrameEqual(result, pd.DataFrame({'a': [-1, 6], 'b': [-1, 5]}), check_dtype=False)

    def test_forward_delta(self):
        self.assertIs(calculator.forward_delta, calculator.delta)

    def test_backward_delta__Series(self):
        result = calculator.backward_delta(pd.Series([3, 2, 8], index=[0, 1, 4]))
        self.assertFrameEqual(result, pd.Series([-1, 6], index=[1, 4]), check_dtype=False)

    def test_backward_delta__DataFrame(self):
        result = calculator.backward_delta(pd.DataFrame({'a': [3, 2, 8], 'b': [3, 2, 7]}, index=[0, 1, 4]))
        self.assertFrameEqual(result, pd.DataFrame({'a': [-1, 6], 'b': [-1, 5]}, index=[1, 4]), check_dtype=False)

    def test_derivative__Series(self):
        result = calculator.derivative(pd.Series([3, 2, 8], index=[0, 1, 4]))
        self.assertFrameEqual(result, pd.Series([-1, 2]), check_dtype=False)

        result = calculator.derivative(pd.Series([3, 2, 8], index=[0, 1, 4]), index_unit=2)
        self.assertFrameEqual(result, pd.Series([-2, 4]), check_dtype=False)

    def test_derivative__DataFrame(self):
        result = calculator.derivative(pd.DataFrame({'a': [3, 2, 8], 'b': [3, 2, 11]}, index=[0, 1, 4]))
        self.assertFrameEqual(result, pd.DataFrame({'a': [-1, 2], 'b': [-1, 3]}), check_dtype=False)

    def test_translate_index(self):
        result = calculator.translate_index(pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]}), 3)
        self.assertFrameEqual(result, pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]}, index=[3, 4, 5]))

    def test_get_deviation__Series(self):
        result = calculator.get_deviations(pd.Series([1.2, 3, 4.8]))
        self.assertFrameEqual(result, pd.Series([-1, 0, 1]), check_dtype=False)

    def test_get_deviation__DataFrame(self):
        result = calculator.get_deviations(pd.DataFrame({'a': [1, 3, 5], 'b': [5, 3, 1]}))
        self.assertFrameEqual(result, pd.DataFrame({'a': [-1, 0, 1], 'b': [1, 0, -1]}), check_dtype=False)

if __name__ == "__main__":
    unittest.main()
