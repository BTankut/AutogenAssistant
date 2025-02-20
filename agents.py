from typing import List, Dict, Any
from api import OpenRouterAPI

class Agent:
    def __init__(self, 
                 name: str, 
                 role: str, 
                 model: str, 
                 system_message: str):
        self.name = name
        self.role = role
        self.model = model
        self.system_message = system_message
        self.messages = [{"role": "system", "content": system_message}]

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})

    def get_messages(self) -> List[Dict[str, str]]:
        return self.messages

class AgentGroup:
    def __init__(self, api: OpenRouterAPI):
        self.api = api
        self.agents = {}

    def add_agent(self, agent: Agent):
        self.agents[agent.name] = agent

    def remove_agent(self, agent_name: str):
        if agent_name in self.agents:
            del self.agents[agent_name]

    def get_response(self, agent_name: str) -> Dict[str, Any]:
        if agent_name not in self.agents:
            return {"success": False, "error": "Agent not found"}
        
        agent = self.agents[agent_name]
        return self.api.generate_completion(
            model=agent.model,
            messages=agent.get_messages()
        )

    def get_agents(self) -> Dict[str, Agent]:
        return self.agents
