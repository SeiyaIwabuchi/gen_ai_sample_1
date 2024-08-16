from typing import Dict
import uuid

from agent import Agent


class AgentManager:
    
    def __init__(self) -> None:
        self.agent_instance_pool: Dict[str, Agent] = {}
    

    def create(self, message: str):
        client_id = uuid.uuid4().hex
        self.agent_instance_pool[client_id] = Agent(message)

        return client_id
    
    def get_agent_instance(self, client_id: str) -> Agent:
        return self.agent_instance_pool[client_id]

    def remove(self, client_id: str):
        del self.agent_instance_pool[client_id]

    