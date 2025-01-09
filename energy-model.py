from typing import Dict, Any
import torch

class EnergyPolicyModel(Model):
    def __init__(self, model_path: str):
        super().__init__()
        self.model = AdvancedEnergyPolicy(hidden_size=64)
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()

    def invoke(self, request: Dict[str, Any]) -> Dict[str, Any]:
        # Convert input data to tensors
        profiles = torch.FloatTensor(request['profiles'])
        prices = torch.FloatTensor(request['prices'])
        
        # Ensure input shapes are correct
        if profiles.ndim == 1:
            profiles = profiles.unsqueeze(0)
        if prices.ndim == 1:
            prices = prices.unsqueeze(0)
        
        # Get model predictions
        with torch.no_grad():
            actions = self.model(profiles, prices)
        
        # Convert output to list/dict format
        return {
            'actions': actions.numpy().tolist()
        }

    @property
    def metadata(self) -> Dict[str, Any]:
        return {
            'name': 'energy_policy_model',
            'version': '1.0.0',
            'description': 'Energy optimization policy model for pump scheduling',
            'input_schema': {
                'type': 'object',
                'properties': {
                    'profiles': {
                        'type': 'array',
                        'items': {'type': 'array', 'items': {'type': 'number'}},
                        'description': 'Energy profiles for 24 hours'
                    },
                    'prices': {
                        'type': 'array',
                        'items': {'type': 'array', 'items': {'type': 'number'}},
                        'description': 'Energy prices for 24 hours'
                    }
                },
                'required': ['profiles', 'prices']
            },
            'output_schema': {
                'type': 'object',
                'properties': {
                    'actions': {
                        'type': 'array',
                        'items': {'type': 'array', 'items': {'type': 'number'}},
                        'description': 'Recommended actions for 24 hours'
                    }
                }
            }
        }