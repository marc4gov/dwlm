import torch
import pandas as pd
import numpy as np
from energy_policy import EnergyPolicy
import os

def load_trained_model(model_path: str) -> EnergyPolicy:
    """Load a trained energy policy model."""
    model = EnergyPolicy(hidden_size=64)
    model.load_state_dict(torch.load(model_path))
    model.eval()
    return model

def optimize_pump_profile(model: EnergyPolicy, 
                        base_profile: np.ndarray, 
                        energy_prices: np.ndarray,
                        output_file: str = None) -> pd.DataFrame:
    """
    Generate optimized pump profile based on base profile and energy prices.
    
    Args:
        model: Trained EnergyPolicy model
        base_profile: Array of 24 hourly flow values
        energy_prices: Array of 24 hourly energy prices
        output_file: Optional file path to save results
        
    Returns:
        DataFrame with original and optimized profiles
    """
    with torch.no_grad():
        # Prepare input tensors
        profile_tensor = torch.FloatTensor(base_profile).unsqueeze(0)  # Add batch dimension
        prices_tensor = torch.FloatTensor(energy_prices).unsqueeze(0)
        
        # Generate actions
        actions = model(profile_tensor, prices_tensor)
        
        # Calculate optimized profile
        optimized_profile = base_profile * (1 + actions.squeeze().numpy())
        
        # Calculate cost savings
        original_cost = np.sum(base_profile * energy_prices)
        optimized_cost = np.sum(optimized_profile * energy_prices)
        savings_percent = (original_cost - optimized_cost) / original_cost * 100
        
        # Create results DataFrame
        results = pd.DataFrame({
            'Hour': range(24),
            'Original_Profile': base_profile,
            'Optimized_Profile': optimized_profile,
            'Energy_Prices': energy_prices,
            'Adjustment_Percent': actions.squeeze().numpy() * 100
        })
        
        # Calculate some statistics
        print("\nOptimization Results:")
        print(f"Cost savings: {savings_percent:.2f}%")
        print(f"Average absolute adjustment: {np.mean(np.abs(actions.numpy()))*100:.2f}%")
        print(f"Maximum increase: {np.max(actions.numpy())*100:.2f}%")
        print(f"Maximum decrease: {np.min(actions.numpy())*100:.2f}%")
        
        # Check energy balance
        total_original = np.sum(base_profile)
        total_optimized = np.sum(optimized_profile)
        balance_error = (total_optimized - total_original) / total_original * 100
        print(f"Energy balance error: {balance_error:.2f}%")
        
        # Save to file if requested
        if output_file:
            results.to_csv(output_file, index=False)
            print(f"\nResults saved to: {output_file}")
        
        return results

if __name__ == "__main__":
    # Example usage
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load model
    model_path = os.path.join(script_dir, 'energy_model.pth')
    model = load_trained_model(model_path)
    
    # Example data (you would replace this with your actual data)
    example_profile = np.array([
        -20.48, -20.50, -20.52, -20.48, -20.50, -20.48, -20.47, -20.50,
        -10.25, -15.42, -20.50, -20.53, -20.53, -20.53, -20.57, -20.60,
        -13.72, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, -6.80
    ])
    
    example_prices = np.array([
        13.62, 6.24, 4.16, 3.28, 0.68, 0.00, 0.76, 0.79,
        1.89, 7.50, 27.32, 37.49, 60.10, 63.32, 47.00, 50.10,
        27.64, 79.97, 95.00, 95.00, 81.49, 68.96, 46.37, 38.00
    ])
    
    # Generate optimized profile
    output_file = os.path.join(script_dir, 'optimized_profile.csv')
    results = optimize_pump_profile(model, example_profile, example_prices, output_file)