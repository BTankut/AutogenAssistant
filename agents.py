import json
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

class CoordinatorAgent(Agent):
    def __init__(self, name: str, model: str, system_message: str):
        super().__init__(name, "coordinator", model, system_message)

    def analyze_task(self, user_input: str, api: OpenRouterAPI) -> Dict[str, Any]:
        """Analyze user input to determine which agents should respond"""
        analysis_prompt = f"""User message: {user_input}

        Analyze this message and determine which types of agents should respond.
        Response format: JSON with 'selected_roles' list and 'reasoning'"""

        self.add_message("user", analysis_prompt)
        response = api.generate_completion(
            model=self.model,
            messages=self.get_messages()
        )

        if response["success"]:
            self.add_message("assistant", response["response"])
            try:
                # Parse response to extract selected roles and reasoning
                return {
                    "success": True,
                    "analysis": response["response"]
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to parse analysis: {str(e)}"
                }
        else:
            return {
                "success": False,
                "error": response["error"]
            }

class AgentGroup:
    def __init__(self, api: OpenRouterAPI):
        self.api = api
        self.agents = {}
        self.coordinator = None

    def add_agent(self, agent: Agent):
        if isinstance(agent, CoordinatorAgent):
            self.coordinator = agent
        else:
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

    def get_collective_response(self, user_input: str) -> Dict[str, Any]:
        """Get coordinated responses from multiple agents"""
        if not self.coordinator:
            return {
                "success": False,
                "error": "No coordinator agent available"
            }

        # Get task analysis from coordinator
        analysis = self.coordinator.analyze_task(user_input, self.api)
        if not analysis["success"]:
            return analysis

        responses = []
        total_tokens = 0
        max_time = 0

        # Get responses from selected agents
        for agent_name, agent in self.agents.items():
            agent.add_message("user", user_input)
            response = self.get_response(agent_name)

            if response["success"]:
                responses.append({
                    "agent": agent_name,
                    "response": response["response"]
                })
                total_tokens += response["tokens"]
                max_time = max(max_time, response["time"])

        return {
            "success": True,
            "responses": responses,
            "coordinator_analysis": analysis["analysis"],
            "tokens": total_tokens,
            "time": max_time
        }

    def get_agents(self) -> Dict[str, Agent]:
        return self.agents