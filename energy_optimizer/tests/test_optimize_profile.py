import unittest
import torch
import numpy as np
import pandas as pd
from ..optimize_profile import optimize_pump_profile, load_trained_model

class TestOptimizeProfile(unittest.TestCase):
    def setUp(self):
        # Example test data
        self.test_profile = np.array([-20.0] * 24)
        self.test_prices = np.array([
            10, 8, 5, 5, 5, 8, 15,      # Night (low)
            30, 90, 95, 85, 60,         # Morning peak
            40, 35, 30, 30, 35,         # Midday valley
            50, 80, 85, 80, 75, 70, 20  # Evening peak
        ])
    
    def test_optimization_constraints(self):
        """Test if optimization results respect all constraints."""
        try:
            model = load_trained_model('energy_model.pth')
            results = optimize_pump_profile(model, self.test_profile, self.test_prices)
            
            # Test shape
            self.assertEqual(len(results), 24)
            
            # Test adjustments in peak hours
            peak_hours = (self.test_prices > np.mean(self.test_prices))
            adjustments = (results['Optimized_Profile'] - results['Original_Profile']) / np.abs(results['Original_Profile'])
            peak_adjustments = adjustments[peak_hours]
            self.assertTrue(np.all(np.abs(peak_adjustments) <= 0.1))
            
            # Test adjustments in valley hours
            valley_hours = ~peak_hours
            valley_adjustments = adjustments[valley_hours]
            self.assertTrue(np.all(np.abs(valley_adjustments) <= 0.3))
            
            # Test total volume conservation
            original_volume = np.sum(results['Original_Profile'])
            optimized_volume = np.sum(results['Optimized_Profile'])
            self.assertAlmostEqual(original_volume, optimized_volume, places=2)
            
        except FileNotFoundError:
            self.skipTest("Model file not found. Run training first.")

if __name__ == '__main__':
    unittest.main()