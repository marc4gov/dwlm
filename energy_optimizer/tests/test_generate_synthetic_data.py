import unittest
import numpy as np
from ..generate_synthetic_data import generate_synthetic_prices, generate_synthetic_profile, analyze_profile_patterns

class TestDataGeneration(unittest.TestCase):
    def test_price_patterns(self):
        """Test if generated prices follow expected patterns."""
        num_days = 10
        prices = generate_synthetic_prices(num_days)
        
        self.assertEqual(prices.shape, (num_days, 24))
        
        # Test for each day
        for day_prices in prices:
            # Morning peak (8-11) should be higher than average
            morning_peak = day_prices[8:12]
            self.assertTrue(np.mean(morning_peak) > np.mean(day_prices))
            
            # Evening peak (18-23) should be higher than average
            evening_peak = day_prices[18:23]
            self.assertTrue(np.mean(evening_peak) > np.mean(day_prices))
            
            # Night valley (0-7) should be lower than average
            night_valley = day_prices[0:8]
            self.assertTrue(np.mean(night_valley) < np.mean(day_prices))
            
            # Midday valley (12-16) should be lower than average
            midday_valley = day_prices[12:17]
            self.assertTrue(np.mean(midday_valley) < np.mean(day_prices))
            
            # All prices should be positive
            self.assertTrue(np.all(day_prices >= 0))

    def test_profile_patterns(self):
        """Test if generated profiles maintain physical constraints."""
        # First analyze a simple profile
        patterns = analyze_profile_patterns(pd.DataFrame({
            'hour': range(24),
            'value': [-20.0] * 24
        }))
        
        profile = generate_synthetic_profile(patterns)
        
        # Test shape
        self.assertEqual(len(profile), 24)
        
        # Test if values stay within reasonable bounds
        self.assertTrue(np.all(profile >= patterns['min_value'] * 1.5))
        self.assertTrue(np.all(profile <= patterns['max_value'] * 1.5))
        
        # Test if transitions are smooth enough
        transitions = np.abs(np.diff(profile))
        self.assertTrue(np.all(transitions < 30))  # No huge jumps

if __name__ == '__main__':
    unittest.main()