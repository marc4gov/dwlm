import unittest
import torch
import numpy as np
from ..energy_policy import EnergyPolicy

class TestEnergyPolicy(unittest.TestCase):
    def setUp(self):
        self.model = EnergyPolicy(hidden_size=64)
        self.batch_size = 2
        self.hours = 24
        
    def test_output_constraints(self):
        """Test if model output respects the constraints."""
        profiles = torch.randn(self.batch_size, self.hours)
        prices = torch.randn(self.batch_size, self.hours)
        mean_prices = torch.mean(prices, dim=1, keepdim=True)
        
        actions = self.model(profiles, prices)
        
        # Test output shape
        self.assertEqual(actions.shape, (self.batch_size, self.hours))
        
        # Test constraints in expensive hours
        expensive_hours = prices >= mean_prices
        self.assertTrue(torch.all(torch.abs(actions[expensive_hours]) <= 0.1))
        
        # Test constraints in cheap hours
        cheap_hours = prices < mean_prices
        self.assertTrue(torch.all(torch.abs(actions[cheap_hours]) <= 0.3))

if __name__ == '__main__':
    unittest.main()