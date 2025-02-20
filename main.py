import streamlit as st
import json
from config import AVAILABLE_MODELS, DEFAULT_AGENT_ROLES, init_session_state
from api import OpenRouterAPI
from agents import Agent, AgentGroup
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
        
        # Agent creation
        st.subheader("Create New Agent")
        agent_name = st.text_input("Agent Name")
        agent_role = st.selectbox("Role", list(DEFAULT_AGENT_ROLES.keys()))
        agent_model = st.selectbox("Model", list(AVAILABLE_MODELS.keys()))
        
        if st.button("Add Agent"):
            role_config = DEFAULT_AGENT_ROLES[agent_role]
            new_agent = Agent(
                name=agent_name,
                role=agent_role,
                model=AVAILABLE_MODELS[agent_model],
                system_message=role_config["system_message"]
            )
            if 'agent_group' not in st.session_state:
                st.session_state.agent_group = AgentGroup(api)
            st.session_state.agent_group.add_agent(new_agent)
            st.session_state.current_agents.append(agent_name)
            st.success(f"Agent {agent_name} added successfully!")

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
                # Message input
                user_input = st.text_area("Your message")
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
                                "agent": selected_agent,
                                "messages": agents[selected_agent].get_messages()
                            })
                        else:
                            st.error(f"Error: {response['error']}")
                
                # Display conversation history
                st.subheader("Conversation History")
                for conv in st.session_state.conversations:
                    with st.expander(f"Conversation with {conv['agent']}"):
                        st.markdown(format_conversation(conv['messages']))
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
