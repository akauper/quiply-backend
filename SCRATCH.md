# Quiply Backend - Project Analysis & Public Release Preparation

## Project Overview
**Quiply Backend** is a sophisticated AI-powered conversation and scenario platform.

### Core Architecture
- **FastAPI** web framework with WebSocket support
- **Python 3.10-3.12** with uv package management
- **Firebase** integration for data storage and authentication
- **Multi-AI Provider Support**: OpenAI, Anthropic, ElevenLabs, Google AI
- **Vector Database**: Qdrant and Milvus for embeddings
- **Audio Processing**: Whisper (speech-to-text), pyannote (diarization)

### Key Components
1. **Framework Layer** (`src/framework/`): Comprehensive AI evaluation and generation framework
2. **Scenario Engine** (`src/scenario/`): Different conversation scenarios (interviews, debates, dating, etc.)
3. **FastAPI App** (`src/fastapi_app/`): REST API and WebSocket handlers
4. **Services** (`src/services/`): Storage, STT, and other backend services
5. **Models** (`src/models/`): Pydantic models for data structures
6. **Automation** (`src/automation/`): Automated testing and scenario execution

### Scenario Types Available
- Interview simulations
- Dating conversations
- Debate scenarios
- Elevator pitch practice
- Investor pitch practice
- "Sell me this pen" scenarios
- Speed dating
- Personal conversations

### Dependencies (Major)
- FastAPI, Uvicorn
- Firebase Admin SDK
- OpenAI, Anthropic AI APIs
- ElevenLabs (voice synthesis)
- PyTorch ecosystem
- Vector databases (Qdrant, Milvus)
- Audio processing libraries

## Project Structure
```
├── src/                    # Main source code
│   ├── framework/          # AI evaluation & generation framework
│   ├── scenario/           # Conversation scenario engine
│   ├── fastapi_app/        # Web API and routes
│   ├── services/           # Backend services
│   ├── models/             # Data models
│   ├── automation/         # Test automation
│   ├── utils/              # Utilities
│   └── websocket/          # WebSocket handling
├── data/                   # Data files and templates
├── test/                   # Test suite
├── tools/                  # Development tools
├── transformer_models/     # ML model storage
└── firestore/              # Firebase config
```

## Current Status for Public Release
- ✅ Project structure analyzed
- ✅ Environment variables properly managed (.env in .gitignore)
- 🔄 Creating cleanup plan for public release

## Cleanup Tasks for Public Release
1. Create .env.example with dummy values
2. Update README with comprehensive documentation
3. Review code for any hardcoded company references
4. Ensure .gitignore is complete
5. Add appropriate license
6. Create development setup documentation