# 🍔 Product Ideation Agent

AI-powered product ideation assistant for the Food & Beverage industry.

## Features

- 🔍 **Real-time Trend Research** - Web search for latest F&B trends
- 💡 **Product Concept Generation** - AI-powered innovative ideas
- 🎯 **Intent Classification** - Smart routing based on user needs
- 💬 **Conversational Interface** - Natural chat experience
- 💾 **Conversation Persistence** - SQLite database storage
- ☁️ **Azure Deployment** - Production-ready cloud hosting

## Live Demo

**URL:** https://product-ideation-agent.yellowsmoke-3ff74350.eastus.azurecontainerapps.io/ui

## Tech Stack

- **Backend:** Python 3.11, FastAPI, LangGraph, LangChain
- **AI:** OpenAI GPT-4o-mini
- **Database:** SQLite (SQLAlchemy)
- **Frontend:** HTML/CSS/JavaScript
- **Tools:** DuckDuckGo Search, BeautifulSoup
- **Deployment:** Azure Container Apps, Docker

## Project Structure
```
product-ideation-agent/
├── src/
│   ├── agents/          # LangGraph agent nodes and workflow
│   ├── api/             # FastAPI application
│   ├── database/        # Database models and operations
│   ├── models/          # Pydantic schemas and state definitions
│   └── tools/           # External tools (web search)
├── frontend/            # Chat UI
├── data/                # SQLite database
├── tests/               # Unit tests
├── Dockerfile           # Docker configuration
├── requirements.txt     # Python dependencies
└── main.py             # Application entry point
```

## Local Development

### Prerequisites

- Python 3.11+
- Docker Desktop
- OpenAI API key

### Setup

1. **Clone the repository:**
```bash
   git clone https://github.com/YOUR-USERNAME/product-ideation-agent.git
   cd product-ideation-agent
```

2. **Create virtual environment:**
```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
```

3. **Install dependencies:**
```bash
   pip install -r requirements.txt
```

4. **Configure environment:**
```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
```

5. **Run locally:**
```bash
   python main.py
```

6. **Access:**
   - Health: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Chat UI: http://localhost:8000/ui

## Docker Deployment
```bash
# Build
docker build -t product-ideation-agent .

# Run
docker run -p 8000:8000 --env-file .env product-ideation-agent
```

## Azure Deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment instructions.

## Documentation

- [Technical Specification](docs/TECHNICAL_SPEC.md)
- [User Manual](docs/USER_MANUAL.md)
- [API Documentation](docs/API.md)

## Usage Examples

### Trend Research
```
User: "What are the top dessert trends for 2025?"
Agent: [Provides trend analysis with data and examples]
```

### Product Concepts
```
User: "Generate 3 plant-based burger concepts"
Agent: [Creates detailed product concepts with positioning]
```

### Competitive Analysis
```
User: "What is Starbucks doing with plant-based options?"
Agent: [Researches and analyzes competitor offerings]
```

## Environment Variables
```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini
APP_NAME=Product Ideation Agent
ENVIRONMENT=production
DATABASE_URL=sqlite:///./data/agent.db
```

## Architecture
```
User → Chat UI → FastAPI → LangGraph Agent → OpenAI GPT-4o-mini
                              ├─> Web Search (DDGS)
                              └─> SQLite Database
```

## Cost Optimization

- Auto-scales to 0 replicas when idle (no cost)
- Estimated monthly cost: $10-30 for light usage
- $200 Azure credits last 10-12 months

## Contributing

This is a proprietary project by Cognithic AI Labs.

## License

Copyright © 2025 Cognithic AI Labs. All rights reserved.

## Contact

**Cognithic AI Labs**
- Email: hello@cognithicailabs.com
- Website: [Coming Soon]

## Roadmap

### Phase 2 (Next 3 months)
- [ ] User authentication
- [ ] PostgreSQL migration
- [ ] PDF report generation
- [ ] Admin dashboard

### Phase 3 (6 months)
- [ ] Multi-tenant support
- [ ] POS system integration
- [ ] Mobile app
- [ ] Multi-language support

## Version

**Current Version:** 1.0.0  
**Last Updated:** November 16, 2025

---

Built with ❤️ by Cognithic AI Labs