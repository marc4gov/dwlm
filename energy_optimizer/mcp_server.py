import json
import asyncio
import websockets
from datetime import datetime
from typing import Dict, Any, Optional

import torch
import numpy as np
from torch import nn
from pytorchrl.agent import Agent, Storage
from pytorchrl.learner import Learner
from pytorchrl.scheme import Scheme
from pytorchrl.utils.running_mean_std import RunningMeanStd

from energy_env import EnergyEnv
from energy_policy import EnergyPolicy

class MCPServer:
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.context: Dict[str, Any] = {}
        
        # PyTorchRL setup
        self._setup_rl_components()
        
    def _setup_rl_components(self):
        # Environment setup
        self.env = EnergyEnv()
        
        # Policy setup
        self.policy = EnergyPolicy(
            input_size=48,  # 24 uur profiel + 24 uur prijzen
            hidden_size=64,
            output_size=24  # 24 uur aanpassingen
        )
        
        # PyTorchRL components
        self.scheme = Scheme(
            policy=self.policy,
            observation_space=self.env.observation_space,
            action_space=self.env.action_space
        )
        
        self.storage = Storage(
            scheme=self.scheme,
            size=1000  # Buffer grootte
        )
        
        self.learner = Learner(
            scheme=self.scheme,
            storage=self.storage,
            optimizer_class=torch.optim.Adam,
            learning_rate=0.001
        )
        
        self.agent = Agent(
            scheme=self.scheme,
            storage=self.storage,
            learner=self.learner
        )
        
        # Running statistics voor observatie normalisatie
        self.obs_rms = RunningMeanStd(shape=(24,))

    async def handle_connection(self, websocket: websockets.WebSocketServerProtocol, path: str):
        connection_id = str(id(websocket))
        self.connections[connection_id] = websocket
        try:
            async for message in websocket:
                response = await self.handle_message(message, connection_id)
                if response:
                    await websocket.send(json.dumps(response))
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            del self.connections[connection_id]

    async def handle_message(self, message: str, connection_id: str) -> Optional[Dict]:
        try:
            data = json.loads(message)
            msg_type = data.get("type")
            
            if msg_type == "context":
                return await self.handle_context(data, connection_id)
            elif msg_type == "request":
                return await self.handle_request(data, connection_id)
            elif msg_type == "feedback":
                return await self.handle_feedback(data, connection_id)
            else:
                return {
                    "type": "error",
                    "error": f"Onbekend berichttype: {msg_type}",
                    "timestamp": datetime.utcnow().isoformat()
                }
        except json.JSONDecodeError:
            return {
                "type": "error",
                "error": "Ongeldig JSON bericht",
                "timestamp": datetime.utcnow().isoformat()
            }

    async def handle_context(self, data: Dict, connection_id: str) -> Dict:
        context = data.get("context", {})
        self.context[connection_id] = {
            **self.context.get(connection_id, {}),
            **context
        }
        
        if "energy_prices" in context:
            self.obs_rms.update(np.array([context["energy_prices"]]))
        
        return {
            "type": "context_response",
            "success": True,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def handle_request(self, data: Dict, connection_id: str) -> Dict:
        request_id = data.get("request_id")
        context = self.context.get(connection_id, {})
        
        try:
            # Observatie voorbereiden
            energy_prices = np.array(context.get("energy_prices", np.zeros(24)))
            normalized_prices = self.obs_rms.normalize(energy_prices)
            
            # Model inferentie
            with torch.no_grad():
                observation = torch.FloatTensor(normalized_prices)
                action = self.agent.act(observation)
                
            # Convert actie naar energie aanpassing
            adjustment = float(action.numpy()[0])
            
            return {
                "type": "response",
                "request_id": request_id,
                "response": {
                    "action": {
                        "type": "energy_adjustment",
                        "value": adjustment,
                        "percentage": adjustment * 100
                    },
                    "metadata": {
                        "model_version": "1.0",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }
            }
        except Exception as e:
            return {
                "type": "error",
                "request_id": request_id,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def handle_feedback(self, data: Dict, connection_id: str) -> Dict:
        feedback = data.get("feedback", {})
        
        observation = self.context[connection_id].get("energy_prices", np.zeros(24))
        action = feedback.get("action", 0)
        reward = feedback.get("reward", 0)
        next_observation = feedback.get("next_observation", np.zeros(24))
        done = feedback.get("done", False)
        
        self.storage.add(
            observation=observation,
            action=action,
            reward=reward,
            next_observation=next_observation,
            done=done
        )
        
        if len(self.storage) >= self.storage.batch_size:
            self.learner.step()
        
        return {
            "type": "feedback_response",
            "success": True,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def start(self):
        server = await websockets.serve(
            self.handle_connection,
            self.host,
            self.port
        )
        print(f"MCP Server draait op ws://{self.host}:{self.port}")
        await server.wait_closed()

def main():
    server = MCPServer()
    asyncio.get_event_loop().run_until_complete(server.start())

if __name__ == "__main__":
    main()