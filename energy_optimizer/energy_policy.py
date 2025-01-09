import torch
import torch.nn as nn

class AdvancedEnergyPolicy(nn.Module):
    def __init__(self, hidden_size: int = 64):
        super().__init__()
        
        # Input layer with standard 48 feature concatenation
        self.input_layer = nn.Sequential(
            nn.Linear(48, hidden_size),
            nn.LayerNorm(hidden_size),
            nn.GELU()
        )
        
        # Network architecture
        self.network = nn.Sequential(
            nn.Linear(hidden_size, hidden_size * 2),
            nn.LayerNorm(hidden_size * 2),
            nn.GELU(),
            nn.Linear(hidden_size * 2, hidden_size),
            nn.LayerNorm(hidden_size),
            nn.GELU(),
            nn.Linear(hidden_size, 24),
            nn.Tanh()  # Constrain between -1 and 1
        )
        
        # Learnable parameters for profile adaptation
        self.profile_adaptation = nn.Parameter(torch.randn(24))
        
    def forward(self, profiles, prices):
        # Ensure float tensors
        profiles = profiles.float()
        prices = prices.float()
        
        # Ensure batch dimension
        if profiles.ndim == 1:
            profiles = profiles.unsqueeze(0)
        if prices.ndim == 1:
            prices = prices.unsqueeze(0)
        
        # Standard concatenation of profiles and prices
        x = torch.cat([profiles, prices], dim=1)
        
        # Initial embedding
        x = self.input_layer(x)
        
        # Network processing
        base_actions = self.network(x)
        
        # Price-sensitive scaling
        price_scale = torch.sigmoid(self.profile_adaptation).unsqueeze(0)
        
        # Constrained and price-sensitive actions
        actions = base_actions * price_scale
        
        # Final constraint
        actions = torch.clamp(actions, min=-0.5, max=0.5)
        
        return actions