import unittest
import sys
import os

# Adiciona o diretório app ao path para importar o business_logic
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

from business_logic import calculate_net_revenue

class TestBusinessLogic(unittest.TestCase):

    def test_calculate_net_revenue_no_discount(self):
        # Preço: 10, Qtd: 2, Desc: 0% -> Result: 20
        self.assertEqual(calculate_net_revenue(10.0, 2, 0.0), 20.0)

    def test_calculate_net_revenue_with_discount(self):
        # Preço: 10, Qtd: 2, Desc: 10% -> Result: 18
        self.assertEqual(calculate_net_revenue(10.0, 2, 0.1), 18.0)

    def test_calculate_net_revenue_full_discount(self):
        # Preço: 10, Qtd: 5, Desc: 100% -> Result: 0
        self.assertEqual(calculate_net_revenue(10.0, 5, 1.0), 0.0)

    def test_calculate_net_revenue_zero_quantity(self):
        # Preço: 10, Qtd: 0, Desc: 0% -> Result: 0
        self.assertEqual(calculate_net_revenue(10.0, 0, 0.0), 0.0)

    def test_calculate_net_revenue_negative_price(self):
        with self.assertRaises(ValueError):
            calculate_net_revenue(-10.0, 1, 0.0)

    def test_calculate_net_revenue_rounding(self):
        # Preço: 10.556, Qtd: 1, Desc: 0% -> Result: 10.56
        self.assertEqual(calculate_net_revenue(10.556, 1, 0.0), 10.56)

if __name__ == '__main__':
    unittest.main()
