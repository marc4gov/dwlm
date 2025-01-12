import numpy as np
import gym
from gym import spaces
from typing import Tuple, Dict, Any

class EnergyEnv:
    def __init__(self):
        # Observatie ruimte: energie profiel + prijzen (24 + 24 = 48 waarden)
        self.observation_space = spaces.Box(
            low=0, 
            high=float('inf'), 
            shape=(48,), 
            dtype=np.float32
        )
        
        # Actie ruimte: 24 aanpassingen tussen -0.1 en 0.1 (10%)
        self.action_space = spaces.Box(
            low=-0.1, 
            high=0.1, 
            shape=(24,), 
            dtype=np.float32
        )
        
        self.reset()
    
    def reset(self) -> np.ndarray:
        """Reset de environment."""
        self.current_step = 0
        self.energy_debt = 0.0
        self.base_profile = np.zeros(24)
        self.prices = np.zeros(24)
        return np.zeros(48)  # Gecombineerd profiel en prijzen
    
    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, Dict[str, Any]]:
        """
        Voer een actie uit in de environment.
        
        Args:
            action: Array van 24 aanpassingen tussen -0.1 en 0.1
            
        Returns:
            observation: Nieuwe observatie
            reward: Behaalde reward
            done: Of de episode klaar is
            info: Extra informatie
        """
        # Update energie schuld
        self.energy_debt += action.sum()
        
        # Bereken kosten
        original_cost = np.sum(self.base_profile * self.prices)
        adjusted_profile = self.base_profile * (1 + action)
        new_cost = np.sum(adjusted_profile * self.prices)
        
        # Bereken reward
        cost_savings = original_cost - new_cost
        balance_penalty = abs(self.energy_debt) * 1000  # Zware penalty voor onbalans
        reward = cost_savings - balance_penalty
        
        # Check of we klaar zijn
        done = self.current_step >= 23
        
        # Update state
        self.current_step += 1
        
        # Combineer profiel en prijzen voor observatie
        observation = np.concatenate([self.base_profile, self.prices])
        
        return observation, reward, done, {
            'energy_debt': self.energy_debt,
            'cost_savings': cost_savings,
            'balance_penalty': balance_penalty
        }
        
    def set_profile_and_prices(self, profile: np.ndarray, prices: np.ndarray):
        """Set het basisprofiel en prijzen voor de huidige episode."""
        assert len(profile) == 24 and len(prices) == 24
        self.base_profile = profile
        self.prices = prices