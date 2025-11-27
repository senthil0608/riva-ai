# Riva.ai - Next.js Frontend

A modern Next.js frontend for the Riva AI academic coaching system, featuring student and parent dashboards powered by the Aura orchestrator.

## Features

- **Student Dashboard**: View daily plans, assignments, and get AI-powered hints
- **Parent Dashboard**: Monitor student progress and stress levels
- **Aura Integration**: Seamless connection to Python/ADK backend
- **Dark Theme**: Modern, accessible UI design

## Project Structure

```
riva-ui/
├── app/
│   ├── layout.tsx              # Root layout with header
│   ├── page.tsx                # Landing page (student/parent selection)
│   ├── student/
│   │   └── page.tsx            # Student dashboard page
│   ├── parent/
│   │   └── page.tsx            # Parent dashboard page
│   └── api/
│       └── aura/
│           └── route.ts        # API proxy to Python backend
├── components/
│   ├── StudentDashboard.tsx    # Student view component
│   ├── ParentDashboard.tsx     # Parent view component
│   └── HintPanel.tsx           # Guided learning hints
├── package.json
├── tsconfig.json
└── .env.local                  # Environment variables
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python Riva AI backend running (see main project)

### Installation

1. **Install dependencies:**
   ```bash
   cd riva-ui
   npm install
   ```

2. **Configure backend URL:**
   
   Edit `.env.local`:
   ```
   AURA_BACKEND_URL=http://localhost:8000/aura
   ```

3. **Run development server:**
   ```bash
   npm run dev
   ```

4. **Open browser:**
   ```
   http://localhost:3000
   ```

## Backend Integration

The Next.js frontend communicates with your Python Aura backend via `/api/aura`.

### Expected Backend API Format

**Endpoint:** `POST http://localhost:8000/aura`

**Student Dashboard Request:**
```json
{
  "role": "student",
  "action": "get_dashboard",
  "studentId": "demo-student"
}
```

**Expected Response:**
```json
{
  "assignments": [
    {
      "id": "a1",
      "title": "Math Worksheet 5",
      "subject": "Math",
      "due": "2025-11-26"
    }
  ],
  "daily_plan": [
    {
      "time": "4:00–4:30 PM",
      "task_id": "a1",
      "title": "Math Worksheet 5",
      "subject": "Math",
      "difficulty_tag": "needs_support"
    }
  ]
}
```

**Parent Summary Request:**
```json
{
  "role": "parent",
  "action": "get_parent_summary",
  "studentId": "demo-student"
}
```

**Expected Response:**
```json
{
  "parent_summary": {
    "summary_text": "Total assignments: 3\nTasks planned for today: 3\nEstimated stress level: Moderate",
    "stress_level": "Moderate"
  }
}
```

**Guided Hint Request:**
```json
{
  "role": "student",
  "action": "guided_hint",
  "question": "How do I solve 3x + 5 = 20?"
}
```

**Expected Response:**
```json
{
  "hint": "Start by identifying what the question is asking. Then write down the known values and see which operation you might use."
}
```

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

### Adding New Features

1. **New Page:** Create file in `app/your-page/page.tsx`
2. **New Component:** Create file in `components/YourComponent.tsx`
3. **New API Route:** Create file in `app/api/your-route/route.ts`

## Deployment

### Vercel (Recommended)

```bash
npm install -g vercel
vercel
```

### Docker

```bash
# Build
docker build -t riva-ui .

# Run
docker run -p 3000:3000 -e AURA_BACKEND_URL=http://your-backend:8000/aura riva-ui
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AURA_BACKEND_URL` | Python Aura backend URL | `http://localhost:8000/aura` |

## Tech Stack

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Inline styles (easily replaceable with Tailwind)
- **State:** React hooks (useState, useEffect)

## Future Enhancements

- [ ] File upload for homework photos (OCR)
- [ ] Voice recording for questions (Speech-to-Text)
- [ ] Real-time notifications
- [ ] Calendar integration
- [ ] Progress charts and analytics
- [ ] Mobile app (React Native)

## License

Part of the Riva AI project.
