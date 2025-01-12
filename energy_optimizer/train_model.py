import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
import pandas as pd
from typing import List, Tuple
from energy_policy import AdvancedEnergyPolicy
import os

class EnergyProfileDataset(Dataset):
    def __init__(self, profiles: np.ndarray, prices: np.ndarray):
        """Initialize dataset with profiles and prices."""
        self.profiles = torch.FloatTensor(profiles)
        self.prices = torch.FloatTensor(prices)
        
    def __len__(self):
        return len(self.profiles)
        
    def __getitem__(self, idx):
        return {
            'profile': self.profiles[idx],
            'prices': self.prices[idx]
        }

def prepare_training_data(daily_profiles: np.ndarray, daily_prices: np.ndarray,
                         train_split: float = 0.8) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Prepare data for training and testing."""
    num_days = len(daily_profiles)
    train_size = int(num_days * train_split)
    
    train_profiles = daily_profiles[:train_size]
    train_prices = daily_prices[:train_size]
    test_profiles = daily_profiles[train_size:]
    test_prices = daily_prices[train_size:]
    
    return train_profiles, train_prices, test_profiles, test_prices

def calculate_energy_balance_violations(actions: torch.Tensor, 
                                        profiles: torch.Tensor, 
                                        prices: torch.Tensor) -> torch.Tensor:
    """
    Advanced balance violation calculation with robust handling.
    """
    batch_size = actions.shape[0]
    
    # Compute price statistics
    mean_prices = prices.mean(dim=1, keepdim=True)
    
    # Initialize violations 
    violations = torch.zeros(batch_size, device=actions.device)
    
    for b in range(batch_size):
        energy_debt = 0.0
        
        for t in range(24):
            # In cheap hours (when negative in flipped profiles means generation)
            if prices[b, t] < mean_prices[b] and actions[b, t] > 0:
                # Compute energy debt (considering flipped profiles)
                current_debt = actions[b, t] * abs(profiles[b, t])
                energy_debt += current_debt
                
                # Look for compensation in next 4 expensive hours
                compensation = 0.0
                comp_slots = 0
                
                for future_t in range(t+1, min(t+8, 24)):
                    if prices[b, future_t] >= mean_prices[b] and comp_slots < 4:
                        # Compute compensation amount
                        max_comp_rate = 0.1  # Limit compensation rate
                        max_comp_amount = abs(profiles[b, future_t]) * max_comp_rate
                        
                        comp_amount = min(
                            abs(current_debt),  # Total debt to compensate
                            max_comp_amount,  # Limit by maximum compensation
                            abs(profiles[b, future_t] * actions[b, future_t])  # Limit by action magnitude
                        )
                        
                        compensation += comp_amount
                        comp_slots += 1
                        
                        if comp_slots >= 4:
                            break
                
                # Check if compensation is insufficient
                if comp_slots < 4 or compensation < current_debt * 0.95:
                    violations[b] += abs(current_debt - compensation)
        
    return violations

def calculate_price_based_reward(profiles: torch.Tensor, 
                                 actions: torch.Tensor, 
                                 prices: torch.Tensor, 
                                 mean_prices: torch.Tensor) -> torch.Tensor:
    """
    Enhanced reward calculation with robust numerical handling.
    """
    # Ensure numerical stability
    profiles = profiles.float()
    actions = actions.float()
    prices = prices.float()
    
    # Compute adjusted profiles with clamped actions
    adjusted_profiles = profiles * (1.0 + actions.clamp(-1.0, 1.0))
    
    # Comprehensive cost analysis with added numerical safeguards
    baseline_cost = torch.sum(profiles * prices, dim=1)
    adjusted_cost = torch.sum(adjusted_profiles * prices, dim=1)
    
    # Robust cost savings calculation
    # Add small epsilon to prevent division by zero
    epsilon = 1e-6
    cost_savings = torch.clamp(
        (baseline_cost - adjusted_cost) / (baseline_cost + epsilon), 
        min=-10, 
        max=10
    )
    
    # Price difference magnitude with added robustness
    price_diff_magnitude = torch.clamp(
        torch.abs(prices - mean_prices) / (mean_prices + epsilon), 
        min=0, 
        max=10
    )
    
    # Asymmetric rewards with numerical stability
    cheap_hour_usage = torch.where(
        prices < mean_prices, 
        torch.abs(actions) * price_diff_magnitude,
        torch.zeros_like(actions)
    ).sum(dim=1)
    
    expensive_hour_compensation = torch.where(
        prices >= mean_prices,
        torch.abs(actions) * price_diff_magnitude,
        torch.zeros_like(actions)
    ).sum(dim=1)
    
    # Adaptive weighting with clamped values
    total_reward = torch.clamp(
        cost_savings * 4.0 +  
        cheap_hour_usage * 1.5 + 
        expensive_hour_compensation * 1.0,
        min=-100,
        max=100
    )
    
    return total_reward

def train_model(model, profiles: np.ndarray, prices: np.ndarray, 
                batch_size: int = 32, epochs: int = 100):
    """Enhanced training loop with adaptive learning techniques."""
    # Convert numpy arrays to torch tensors
    profiles_tensor = torch.tensor(profiles, dtype=torch.float32)
    prices_tensor = torch.tensor(prices, dtype=torch.float32)
    
    # Advanced logging and validation
    print("\nDetailed Input Statistics:")
    print(f"Profiles - Range: [{profiles_tensor.min()}, {profiles_tensor.max()}]")
    print(f"Profiles - Mean: {profiles_tensor.mean():.4f}, Std: {profiles_tensor.std():.4f}")
    print(f"Prices - Range: [{prices_tensor.min()}, {prices_tensor.max()}]")
    print(f"Prices - Mean: {prices_tensor.mean():.4f}, Std: {prices_tensor.std():.4f}")
    
    # Adaptive batch sizing
    batch_size = max(1, min(batch_size, profiles_tensor.shape[0]))
    
    dataset = EnergyProfileDataset(profiles_tensor.numpy(), prices_tensor.numpy())
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    # Advanced optimizer with adaptive learning rate
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=20, gamma=0.9)
    
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        total_rewards = 0
        total_penalties = 0
        
        # Progressive balance penalty starting lower
        balance_weight = min(5000.0, 500.0 + epoch * 50.0)
        
        for batch in dataloader:
            # Ensure tensors are detached and requires_grad is set correctly
            profiles_batch = batch['profile'].float()
            prices_batch = batch['prices'].float()
            
            # Clear any existing gradients
            optimizer.zero_grad()
            
            # Forward pass
            actions = model(profiles_batch, prices_batch)
            
            # Compute mean prices without in-place modification
            mean_prices = torch.mean(prices_batch, dim=1, keepdim=True)
            
            # Compute reward
            reward = calculate_price_based_reward(profiles_batch, actions, prices_batch, mean_prices)
            
            # Calculate penalties with reduced initial weights
            balance_violations = calculate_energy_balance_violations(actions, profiles_batch, prices_batch)
            balance_penalty = torch.mean(balance_violations) * balance_weight
            
            # Compute smoothness penalty
            sequential_shifts = torch.abs(actions[:, 1:] - actions[:, :-1])
            smoothness_penalty = torch.mean(sequential_shifts) * 500.0
            
            # Total loss computation
            loss = -torch.mean(reward) * 2.0 + balance_penalty + smoothness_penalty
            
            # Backward pass with gradient clipping
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            
            # Update weights
            optimizer.step()
            
            # Accumulate metrics
            total_loss += loss.item()
            total_rewards += torch.mean(reward).item()
            total_penalties += (balance_penalty + smoothness_penalty).item()
        
        # Step the learning rate scheduler
        scheduler.step()
        
        # Print epoch metrics
        avg_loss = total_loss / len(dataloader)
        avg_reward = total_rewards / len(dataloader)
        avg_penalty = total_penalties / len(dataloader)
        print(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}, Reward: {avg_reward:.4f}, "
              f"Penalty: {avg_penalty:.4f}, Balance Weight: {balance_weight:.1f}")
    
    return model

def evaluate_model(model, test_profiles: np.ndarray, test_prices: np.ndarray) -> Tuple[float, float, float]:
    """Evaluate model performance with robust error handling."""
    model.eval()
    with torch.no_grad():
        profiles = torch.FloatTensor(test_profiles)
        prices = torch.FloatTensor(test_prices)
        
        # Add small epsilon to prevent division by zero
        epsilon = 1e-6
        
        mean_prices = torch.mean(prices, dim=1, keepdim=True)
        actions = model(profiles, prices)
        
        # Calculate adjusted profiles and savings
        adjusted_profiles = profiles * (1 + actions)
        baseline_cost = torch.sum(profiles * prices, dim=1)
        cost = torch.sum(adjusted_profiles * prices, dim=1)
        
        # Robust savings calculation
        savings_raw = ((baseline_cost - cost) / (baseline_cost + epsilon)) * 100
        savings = torch.clamp(savings_raw, min=-1000, max=1000).mean()
        
        # Existing detailed statistics
        cheap_mask = prices < mean_prices
        expensive_mask = ~cheap_mask
        
        above_mean = actions[expensive_mask]
        below_mean = actions[cheap_mask]
        
        print("\nDetailed statistics:")
        print(f"Average adjustment in expensive hours: {torch.mean(torch.abs(above_mean))*100:.2f}%")
        print(f"Average adjustment in cheap hours: {torch.mean(torch.abs(below_mean))*100:.2f}%")
        
        # Calculate compensation statistics
        balance_violations = calculate_energy_balance_violations(actions, profiles, prices)
        print(f"Average balance violations: {torch.mean(balance_violations):.4f}")
        
        # Calculate hourly changes
        hourly_changes = torch.abs(actions[:, 1:] - actions[:, :-1])
        print(f"Average hour-to-hour change: {torch.mean(hourly_changes)*100:.2f}%")
        
        return (
            savings.item() if not torch.isnan(savings) else 0.0, 
            torch.mean(torch.abs(actions)).item() * 100, 
            torch.mean(balance_violations).item()
        )

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(script_dir, "pump_profiles")
    
    print(f"Looking for data in: {base_dir}")
    
    try:
        # Load data
        profile_path = os.path.join(base_dir, "katwijk_profile_flipped.csv")
        price_path = os.path.join(base_dir, "prices_profile.csv")
        
        profiles_df = pd.read_csv(profile_path)
        prices_df = pd.read_csv(price_path)
        
        # Print dates to verify
        print("\nAvailable Dates in Profiles:")
        print(profiles_df.columns[0])  # Assuming first column is date
        
        # # Remove rows with missing data
        # profiles_df = profiles_df.dropna()
        # prices_df = prices_df.dropna()
        
        # Convert to numpy arrays
        daily_profiles = profiles_df.iloc[:, 0:].values.astype(float)
        daily_prices = prices_df.iloc[:, 0:].values.astype(float)
        
        print(f"\nArray shapes after cleaning:")
        print(f"Profiles shape: {daily_profiles.shape}")
        print(f"Prices shape: {daily_prices.shape}")
        
        # Validate shapes
        if daily_profiles.shape[1] != 24:
            raise ValueError(f"Expected 24 hours in profiles, got {daily_profiles.shape[1]}")
        if daily_prices.shape[1] != 24:
            raise ValueError(f"Expected 24 hours in prices, got {daily_prices.shape[1]}")
        
        # Prepare data
        train_profiles, train_prices, test_profiles, test_prices = prepare_training_data(
            daily_profiles, daily_prices
        )
        
        print(f"\nSplit data shapes:")
        print(f"Train profiles: {train_profiles.shape}")
        print(f"Train prices: {train_prices.shape}")
        print(f"Test profiles: {test_profiles.shape}")
        print(f"Test prices: {test_prices.shape}")
        
        # Train and evaluate
        model = AdvancedEnergyPolicy(hidden_size=64)
        
        train_model(model, train_profiles, train_prices, 
                   batch_size=2, epochs=100)
        
        savings, avg_adjustment, violations = evaluate_model(
            model, test_profiles, test_prices
        )
        
        print(f"\nResults:")
        print(f"Average savings: {savings:.2f}%")
        print(f"Average adjustment: {avg_adjustment:.2f}%")
        print(f"Balance violations: {violations:.4f}")
        
        # Save model
        model_path = os.path.join(script_dir, 'energy_model.pth')
        torch.save(model.state_dict(), model_path)
        print(f"\nModel saved to: {model_path}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        print(traceback.format_exc())