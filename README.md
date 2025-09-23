# Quiply Backend

An advanced AI-powered conversation and scenario simulation platform built with FastAPI. Quiply enables realistic practice sessions for various conversation scenarios including job interviews, debates, dating, and sales pitches.

## Features

### 🎯 Multiple Scenario Types
- **Interview Practice** - Realistic job interview simulations
- **Debate Scenarios** - Structured debate environments
- **Dating Conversations** - Speed dating and relationship scenarios
- **Sales Training** - "Sell me this pen" and pitch practice
- **Investor Pitches** - Startup pitch simulations
- **Personal Development** - Casual conversation practice

### 🤖 AI Provider Integration
- **OpenAI** - GPT models for text generation
- **Anthropic Claude** - Advanced reasoning capabilities
- **ElevenLabs** - High-quality voice synthesis
- **Google AI** - Gemini model support

### 🔊 Audio Processing
- **Speech-to-Text** - Whisper integration for voice input
- **Speaker Diarization** - Multi-speaker conversation handling
- **Voice Synthesis** - Natural voice responses

### 📊 Evaluation Framework
- **AI-Powered Assessment** - Automated conversation analysis
- **Custom Criteria** - Configurable evaluation metrics
- **Performance Tracking** - Detailed feedback and scoring

## Quick Start

### Prerequisites
- Python 3.10-3.12
- [uv](https://github.com/astral-sh/uv) package manager
- Firebase project with Admin SDK
- API keys for AI providers (OpenAI, Anthropic, etc.)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/akauper/quiply-backend.git
   cd quiply-backend
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys and configuration
   ```

4. **Firebase Setup**
   - Create a Firebase project
   - Download the Admin SDK service account key
   - Update `GOOGLE_APPLICATION_CREDENTIALS` in `.env`

5. **Run the application**
   ```bash
   uv run python startup.py
   ```

The API will be available at `http://localhost:5005` with docs at `http://localhost:5005/docs`.

## Configuration

### Required Environment Variables

See `.env.example` for all configuration options. Key variables include:

- `OPENAI_API_KEY` - OpenAI API access
- `ANTHROPIC_API_KEY` - Anthropic Claude API access
- `ELEVEN_LABS_API_KEY` - Voice synthesis
- `GOOGLE_APPLICATION_CREDENTIALS` - Firebase Admin SDK path
- `GOOGLE_API_KEY` - Google AI services

### Optional Configuration

- `PINECONE_API_KEY` - Vector database for embeddings
- `HF_TOKEN` - Hugging Face model access
- `SERPAPI_API_KEY` - Web search capabilities

## Architecture

### Core Components

```
src/
├── framework/          # AI evaluation and generation framework
│   ├── evaluation/     # Assessment and scoring system
│   ├── runnables/      # AI provider integrations
│   └── prompting/      # Prompt management
├── scenario/           # Conversation scenario engine
│   ├── base/          # Core scenario framework
│   └── scenarios/     # Specific scenario implementations
├── fastapi_app/       # Web API and routes
│   ├── routes/        # API endpoints
│   └── middlewares/   # Authentication and CORS
├── services/          # Backend services
│   ├── storage/       # Data persistence
│   └── stt/          # Speech-to-text processing
├── models/            # Data models and schemas
└── websocket/         # Real-time communication
```

### Key Technologies

- **FastAPI** - Modern web framework
- **WebSockets** - Real-time communication
- **Firebase** - Authentication and data storage
- **Pydantic** - Data validation and serialization
- **PyTorch** - Machine learning models
- **Vector Databases** - Qdrant/Milvus for embeddings

## API Endpoints

### Scenario Management
- `GET /api/scenario/configs` - List available scenarios
- `POST /api/scenario/instances` - Create scenario instance
- `WebSocket /ws/scenario/{instance_id}` - Real-time conversation

### User Management
- `GET /api/user/profile` - User profile data
- `POST /api/user/account` - Account management

### Debug & Evaluation
- `POST /api/debug/evaluation` - Run evaluations
- `POST /api/debug/llm-response` - Test AI responses

## Development

### Running Tests
```bash
uv run pytest
```

### Code Quality
```bash
# Linting
uv run ruff check

# Type checking
uv run mypy src/
```

### Development Tools
The `tools/` directory contains utilities for:
- Creating test users and scenarios
- Converting data formats
- Evaluating model performance
- Managing app packages

## Deployment

### Environment Setup
1. Configure production environment variables
2. Set up Firebase project for production
3. Configure AI provider API limits
4. Set up vector database instances

### Docker (Optional)
```bash
# Build image
docker build -t quiply-backend .

# Run container
docker run -p 5005:5005 --env-file .env quiply-backend
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints throughout
- Write comprehensive tests
- Document complex functionality

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:
- Development setup
- Coding standards
- Pull request process
- How to report bugs and request features

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions or issues, please [open an issue](https://github.com/akauper/quiply-backend/issues) on GitHub.

---

**Note**: This project requires various AI provider API keys. Please ensure you have appropriate usage limits and billing configured for production use.