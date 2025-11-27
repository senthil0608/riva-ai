# Riva AI - Academic Coach

AI-powered academic coaching platform built with **Google ADK** (Agent Development Kit) and **Gemini 2.0**.

## 🎯 What is Riva AI?

Riva AI helps students manage their academic workload through intelligent AI agents that:
- Fetch assignments from Google Classroom
- Analyze student proficiency across subjects
- Create personalized daily study schedules
- Provide homework hints (never direct answers!)
- Generate summaries for parents

## 🏗️ Architecture

### Backend: Google ADK Agents

**6 AI Agents powered by Gemini:**

1. **Classroom Sync** - Fetches assignments from Google Classroom API
2. **Skill Mastery** - Analyzes student proficiency (needs_support, on_track, strong)
3. **Daily Planner** - Creates intelligent study schedules
4. **Guided Learning** - Provides hints without giving answers
5. **Parent Insight** - Generates summaries for parents
6. **Aura Orchestrator** - Coordinates all agents (SequentialWorkflow)

### Frontend: Next.js UI

**Modern React application:**
- Student dashboard with daily schedule
- Parent dashboard with progress tracking
- Guided learning interface with photo/voice input
- Real-time AI responses

### Observability

**Production-ready monitoring:**
- Structured JSON logging (Google Cloud Logging compatible)
- OpenTelemetry tracing (Google Cloud Trace support)
- Prometheus metrics at `/metrics`

## 🚀 Quick Start

### Prerequisites

- Python 3.13.9
- Node.js 18+
- Google Cloud project (for Gemini API)

### 1. Backend Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# Run server
python3 server.py
```

**Access:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Metrics: http://localhost:8000/metrics

### 2. Frontend Setup

```bash
cd riva-ui
npm install
npm run dev
```

**Access:** http://localhost:3000

### 3. Google Classroom (Optional)

See [GOOGLE_CLASSROOM.md](GOOGLE_CLASSROOM.md) for setup instructions.

## 📁 Project Structure

```
riva_ai/
├── agents/                    # 6 Google ADK Agents
│   ├── aura_orchestrator_agent.py
│   ├── classroom_sync_agent.py
│   ├── daily_planner_agent.py
│   ├── guided_learning_agent.py
│   ├── skill_mastery_agent.py
│   └── parent_insight_agent.py
├── tools/                     # Tool functions
│   ├── google_classroom_tool.py
│   ├── ocr_tool.py
│   ├── speech_to_text_tool.py
│   └── calendar_mapper_tool.py
├── core/                      # Core infrastructure
│   ├── adk_config.py         # ADK configuration
│   └── observability/        # Logging, tracing, metrics
├── riva-ui/                   # Next.js frontend
│   ├── app/                  # Pages and routes
│   ├── components/           # React components
│   └── public/               # Static assets
├── server.py                  # FastAPI backend
├── main.py                    # Demo script
└── requirements.txt           # Python dependencies
```

## 🔧 Configuration

### Environment Variables

```bash
# Required
GOOGLE_API_KEY=your_gemini_api_key

# Optional
GEMINI_MODEL=gemini-2.0-flash-exp
LOG_LEVEL=INFO
ENABLE_TRACING=true
ENABLE_METRICS=true
GOOGLE_CLASSROOM_CREDENTIALS=credentials.json
```

### Get Gemini API Key

1. Visit: https://aistudio.google.com/app/apikey
2. Create API key
3. Add to `.env` file

## 📡 API Reference

### POST /aura

**Student Dashboard:**
```json
{
  "role": "student",
  "action": "get_dashboard",
  "studentId": "demo-student"
}
```

**Response:**
```json
{
  "assignments": [...],
  "skill_profile": {"Math": "needs_support", "ELA": "on_track"},
  "daily_plan": [...],
  "parent_summary": {...}
}
```

**Guided Hint:**
```json
{
  "role": "student",
  "action": "guided_hint",
  "question": "How do I solve 3x + 5 = 20?"
}
```

**Response:**
```json
{
  "problem_text": "3x + 5 = 20",
  "hint": "Start by identifying what you need to find..."
}
```

## 🧪 Testing

```bash
# Run demo
python3 main.py

# Test API
curl http://localhost:8000/health

# Test agent
curl -X POST http://localhost:8000/aura \
  -H "Content-Type: application/json" \
  -d '{"role":"student","action":"get_dashboard","studentId":"test"}'
```

## 📊 Monitoring

### Logs

Structured JSON logs to stdout:
```json
{
  "timestamp": "2024-11-25T19:00:00Z",
  "severity": "INFO",
  "message": "Agent classroom_sync started",
  "agent_name": "classroom_sync",
  "student_id": "demo-student"
}
```

### Metrics

Prometheus metrics at `/metrics`:
```
riva_agent_executions_total{agent_name="classroom_sync",status="success"} 42
riva_agent_duration_seconds_sum{agent_name="classroom_sync"} 12.5
riva_api_requests_total{endpoint="/aura",method="POST",status_code="200"} 100
```

### Traces

OpenTelemetry traces (console or Google Cloud Trace):
- Agent execution spans
- Tool call spans
- API request spans

## 🎨 Frontend Features

### Student Dashboard
- Daily schedule with time slots
- All assignments with due dates
- Difficulty tags per subject
- Guided learning interface

### Parent Dashboard
- Weekly progress summary
- Stress level monitoring
- Subject proficiency overview

### Guided Learning
- Photo upload for homework problems
- Voice input for questions
- AI-powered hints (no direct answers)

## 🛠️ Tech Stack

**Backend:**
- Google ADK (Agent Development Kit)
- Gemini 2.0 Flash
- FastAPI
- Python 3.13.9
- OpenTelemetry
- Prometheus

**Frontend:**
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS (if used)

**APIs:**
- Google Classroom API
- Google Gemini API
- Google Cloud Trace (optional)
- Google Cloud Logging (optional)

## 📚 Documentation

- [GOOGLE_CLASSROOM.md](GOOGLE_CLASSROOM.md) - Google Classroom integration
- [OBSERVABILITY.md](OBSERVABILITY.md) - Logging, tracing, metrics
- [riva-ui/README.md](riva-ui/README.md) - Frontend documentation

## 🚀 Deployment

### Backend (Google Cloud Run)

```bash
gcloud run deploy riva-backend \
  --source . \
  --set-env-vars GOOGLE_API_KEY=$GOOGLE_API_KEY
```

### Frontend (Vercel)

```bash
cd riva-ui
vercel
```

## 🔒 Security

- API keys in environment variables (never committed)
- OAuth credentials in `.gitignore`
- CORS configured for frontend
- Input validation with Pydantic

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

Part of the Riva AI project.

## 🆘 Support

For issues or questions:
1. Check documentation files
2. Review API docs at `/docs`
3. Check logs and metrics
4. Open an issue on GitHub

---

**Built with Google ADK and Gemini 2.0** 🤖✨
