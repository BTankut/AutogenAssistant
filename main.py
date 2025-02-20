import streamlit as st
import json
from config import DEFAULT_AGENT_ROLES, init_session_state
from api import OpenRouterAPI
from agents import Agent, CoordinatorAgent, AgentGroup
from utils import format_conversation, create_metrics_charts, update_metrics

# Page configuration
st.set_page_config(
    page_title="Multi-Agent Dashboard",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
init_session_state()

# Sidebar
with st.sidebar:
    st.title("🤖 Agent Configuration")

    # API Key input
    api_key = st.text_input("OpenRouter API Key", 
                           value=st.session_state.api_key,
                           type="password")

    if api_key:
        st.session_state.api_key = api_key
        api = OpenRouterAPI(api_key)

        # Fetch available models
        models_response = api.get_models()
        if models_response["success"]:
            available_models = {
                model["id"]: model["id"]
                for model in models_response["models"]
            }
            st.session_state.available_models = available_models
        else:
            st.error("Failed to fetch models from OpenRouter")
            st.session_state.available_models = {}

        # Initialize AgentGroup if not exists
        if 'agent_group' not in st.session_state:
            st.session_state.agent_group = AgentGroup(api)

        # Coordinator setup
        if not st.session_state.coordinator:
            st.subheader("Setup Coordinator")
            if st.session_state.available_models:
                coordinator_model = st.selectbox(
                    "Coordinator Model",
                    list(st.session_state.available_models.keys()),
                    key="coordinator_model"
                )

                if st.button("Setup Coordinator"):
                    coordinator = CoordinatorAgent(
                        name="Coordinator",
                        model=st.session_state.available_models[coordinator_model],
                        system_message=DEFAULT_AGENT_ROLES["coordinator"]["system_message"]
                    )
                    st.session_state.agent_group.add_agent(coordinator)
                    st.session_state.coordinator = coordinator
                    st.success("Coordinator agent setup successfully!")

        # Agent creation
        st.subheader("Create New Agent")
        agent_name = st.text_input("Agent Name")

        # Show roles with descriptions
        roles = [role for role in DEFAULT_AGENT_ROLES.keys() if role != "coordinator"]
        
        agent_role = st.selectbox(
            "Role", 
            roles,
            format_func=lambda x: f"{x.title()}: {DEFAULT_AGENT_ROLES[x]['description']}"
        )

        if st.session_state.available_models:
            agent_model = st.selectbox("Model", list(st.session_state.available_models.keys()))

            if st.button("Add Agent"):
                role_config = DEFAULT_AGENT_ROLES[agent_role]
                new_agent = Agent(
                    name=agent_name,
                    role=agent_role,
                    model=st.session_state.available_models[agent_model],
                    system_message=role_config["system_message"]
                )
                st.session_state.agent_group.add_agent(new_agent)
                st.session_state.current_agents.append(agent_name)
                st.success(f"Agent {agent_name} added successfully!")
        else:
            st.warning("No models available. Please check your API key.")

# Main content
st.title("Multi-Agent Dashboard")

if not st.session_state.api_key:
    st.warning("Please enter your OpenRouter API key in the sidebar.")
else:
    # Create tabs
    tab1, tab2 = st.tabs(["Chat", "Metrics"])

    with tab1:
        # Chat interface
        st.subheader("Agent Conversation")

        if 'agent_group' in st.session_state:
            agents = st.session_state.agent_group.get_agents()

            if agents:
                # Chat mode selection
                chat_mode = st.radio(
                    "Chat Mode",
                    ["Single Agent", "Collective (Coordinated)"],
                    horizontal=True
                )

                # Display available agents
                st.subheader("Available Agents")
                for agent_name, agent in agents.items():
                    st.write(f"• **{agent_name}** ({agent.role})")

                # Message input
                user_input = st.text_area("Your message")

                if chat_mode == "Single Agent":
                    selected_agent = st.selectbox(
                        "Select agent to respond", 
                        list(agents.keys())
                    )

                    if st.button("Send"):
                        if user_input:
                            # Add user message
                            agents[selected_agent].add_message("user", user_input)

                            # Get agent response
                            response = st.session_state.agent_group.get_response(
                                selected_agent
                            )

                            if response["success"]:
                                # Add agent response
                                agents[selected_agent].add_message(
                                    "assistant", 
                                    response["response"]
                                )

                                # Update metrics
                                update_metrics(
                                    st.session_state.metrics,
                                    response,
                                    agents[selected_agent].model
                                )

                                # Save conversation
                                st.session_state.conversations.append({
                                    "mode": "single",
                                    "agent": selected_agent,
                                    "messages": agents[selected_agent].get_messages()
                                })
                            else:
                                st.error(f"Error: {response['error']}")

                else:  # Collective mode
                    if not st.session_state.coordinator:
                        st.warning("Please set up a coordinator agent first.")
                    else:
                        if st.button("Send to All"):
                            if user_input:
                                with st.spinner("Getting coordinated response..."):
                                    # Get collective response
                                    response = st.session_state.agent_group.get_collective_response(
                                        user_input
                                    )

                                    if response["success"]:
                                        # Display coordinator's analysis
                                        st.write("Coordinator's Analysis:")
                                        st.write(response["coordinator_analysis"])

                                        # Display agent responses
                                        for agent_response in response["responses"]:
                                            st.write(f"\n**{agent_response['agent']}**:")
                                            st.write(agent_response['response'])

                                        # Update metrics
                                        update_metrics(
                                            st.session_state.metrics,
                                            {
                                                "success": True,
                                                "tokens": response["tokens"],
                                                "time": response["time"]
                                            },
                                            "collective"
                                        )

                                        # Save conversation
                                        st.session_state.conversations.append({
                                            "mode": "collective",
                                            "user_input": user_input,
                                            "coordinator_analysis": response["coordinator_analysis"],
                                            "responses": response["responses"]
                                        })
                                    else:
                                        st.error(f"Error: {response['error']}")

                # Display conversation history
                st.subheader("Conversation History")
                for conv in st.session_state.conversations:
                    if conv["mode"] == "single":
                        with st.expander(f"Single Agent Conversation with {conv['agent']}"):
                            st.markdown(format_conversation(conv['messages']))
                    else:
                        with st.expander("Collective Conversation"):
                            st.write("**User**:", conv["user_input"])
                            st.write("\n**Coordinator Analysis**:", conv["coordinator_analysis"])
                            for resp in conv["responses"]:
                                st.write(f"\n**{resp['agent']}**:", resp["response"])
            else:
                st.info("Add agents using the sidebar to start chatting!")

    with tab2:
        # Metrics display
        st.subheader("Performance Metrics")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Tokens Used", st.session_state.metrics['total_tokens'])
        with col2:
            if st.session_state.metrics['response_times']:
                avg_time = sum(st.session_state.metrics['response_times']) / \
                          len(st.session_state.metrics['response_times'])
                st.metric("Average Response Time (s)", f"{avg_time:.2f}")

        # Display charts
        create_metrics_charts(st.session_state.metrics)