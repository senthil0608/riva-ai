# Riva AI

Riva AI is an intelligent student dashboard that integrates with Google Classroom and Google Calendar to help students manage their assignments and schedule. It uses a "Persona" system (Aura) to provide personalized guidance and study plans.

## Features
- **Dashboard:** View daily plans, current assignments, and calendar events.
- **Aura Chat:** Interact with an AI assistant for help and planning.
- **Google Integration:** Syncs with Google Classroom and Calendar.

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Google Cloud Project with Classroom, Calendar, and Gemini APIs enabled.

### Installation
1.  Clone the repository.
2.  Set up your `.env` file with Firebase and Google API credentials.
3.  Run with Docker Compose:
    ```bash
    docker compose up --build
    ```

### Deployment
Use the included deployment script to deploy to Google Cloud Run:
```bash
./deploy.sh [PROJECT_ID] [REGION]
```
