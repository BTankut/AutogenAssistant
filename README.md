# Multi-Agent Dashboard with OpenRouter Integration

A comprehensive dashboard for managing and interacting with multiple AI agents using OpenRouter API. This application provides a streamlined interface for coordinated AI interactions with advanced configuration options and real-time progress tracking.

## 🌟 Features

### Core Functionality
- **Multi-Agent System**: Coordinate multiple AI agents with different roles and capabilities
- **Dynamic Model Selection**: Choose from various OpenRouter models for each agent
- **Coordinated Responses**: Get collective responses from multiple agents orchestrated by a coordinator
- **Real-time Progress Tracking**: Visual feedback on processing status and agent responses

### User Interface
- **Interactive Chat Interface**: Easy-to-use chat interface for both single and collective agent interactions
- **Collapsible Views**: Expandable sections for detailed analysis and responses
- **Performance Metrics**: Track token usage and response times
- **Visual Analytics**: Charts and graphs for performance monitoring

### Agent Types
- **Coordinator**: Analyzes tasks and orchestrates other agents
- **Human Assistant**: Represents user interests and manages task delegation
- **Code Assistant**: Specializes in programming and code review
- **Critic**: Provides thoughtful analysis and feedback

## 🚀 Getting Started

### Prerequisites
- Python 3.11
- OpenRouter API key

### Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables:
```bash
OPENROUTER_API_KEY=your_api_key_here
```

4. Run the application:
```bash
streamlit run main.py
```

## 💡 Usage Guide

### Setting Up Agents

1. **Configure Coordinator**:
   - Select a model for the coordinator agent
   - Click "Setup Coordinator" to initialize

2. **Add Specialized Agents**:
   - Choose an agent role (Human Assistant, Code Assistant, Critic)
   - Select a model for the agent
   - Click "Add Agent" to create

### Chat Modes

1. **Single Agent Mode**:
   - Select specific agent to interact with
   - Send messages directly to chosen agent
   - View individual responses

2. **Collective Mode**:
   - Engage with all configured agents
   - Get coordinated responses
   - View progress in real-time
   - Access detailed analysis in expandable sections

### Viewing Results

- **Summary View**: Quick overview of combined agent responses
- **Detailed Analysis**: Expandable sections for in-depth information
- **Performance Metrics**: Track token usage and response times
- **Conversation History**: Review past interactions in collapsible sections

## 📊 Performance Monitoring

- Track total tokens used
- Monitor average response times
- View model usage distribution
- Analyze response time trends

## 🛠 Technical Stack

- **Frontend**: Streamlit
- **API Integration**: OpenRouter API
- **Data Visualization**: Plotly
- **Progress Tracking**: Custom implementation

## 🔐 Security

- Secure API key management
- Environment variable configuration
- No data persistence for sensitive information

## 📝 Notes

- The application automatically saves model selections for each agent role
- Reset chat functionality maintains agent configurations while clearing conversation history
- Progress tracking provides real-time feedback during collective responses

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
