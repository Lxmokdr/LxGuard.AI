# Frontend - Hybrid NLP-Expert Agent Console

## Overview

This is the **Neuro-Console** frontend for the Hybrid NLP-Expert Agent system. It provides real-time visualization of all 8 layers of the neuro-symbolic architecture.

## Features

### 🎯 Real-Time Reasoning Visualization

**Left Panel (60%)**: Chat Interface
- User queries
- AI responses
- Conversation history

**Right Panel (40%)**: Neuro-Console
- **Confidence Score**: Overall system confidence
- **Processing Time**: Response latency
- **Model Info**: Architecture details
- **Rule Trace**: All 8 layers visualized
- **Knowledge Sources**: Retrieved documents

### 📊 8-Layer Visualization

The console displays reasoning from all layers:

1. **NLP Analysis** - Question type classification
2. **Intent Hypotheses** - Top 2 intents with confidence
3. **Intent Arbitration** - Final selected intent
4. **Symbolic Filter** - Topic-based filtering
5. **Semantic Ranking** - Document scoring
6. **Answer Planning** - Structure and steps
7. **Exclusions** - Forbidden topics
8. **Self-Validation** - Quality checks and score

### ✅ Validation Display

- Shows validation score (0-100%)
- Displays PASSED/FAILED status
- Lists failed validation checks
- Color-coded rule status

## Tech Stack

- **React** + **TypeScript**
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **shadcn/ui** - UI components
- **React Query** - Data fetching

## Setup

### Prerequisites

- Node.js 18+
- Backend API running on port 8001

### Installation

```bash
cd /home/lxmix/Downloads/projet/insightful-console-main

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Configuration

### API Endpoint

The frontend connects to the hybrid API at:
```
http://localhost:8001/api/chat
```

To change this, edit `src/pages/Index.tsx`:
```typescript
const response = await fetch("http://localhost:8001/api/chat", {
  // ...
});
```

## Usage

1. **Start Backend**:
```bash
cd /home/lxmix/Downloads/projet/Expert_Agent
python api_hybrid.py
```

2. **Start Frontend**:
```bash
cd /home/lxmix/Downloads/projet/insightful-console-main
npm run dev
```

3. **Open Browser**: Navigate to `http://localhost:5173`

4. **Ask Questions**: Type Next.js questions and watch the reasoning unfold!

## API Response Mapping

The frontend maps the hybrid API response to UI components:

### Response Structure
```typescript
{
  answer: string,
  reasoning: {
    nlp_analysis: { ... },
    intent_arbitration: { ... },
    retrieval_path: { ... },
    answer_plan: { ... },
    documents: [ ... ]
  },
  validation: { ... },
  confidence: number,
  architecture_info: { ... }
}
```

### UI Mapping

**Rules Panel**:
- Layer 1: NLP Analysis → Analysis rule
- Intent Hypotheses → Analysis rules (top 2)
- Layer 3: Intent Arbitration → Creation rule
- Layer 4: Retrieval (Tier 1 & 2) → Analysis rules
- Layer 5: Answer Planning → Creation rule
- Exclusions → Debug rule
- Layer 7: Validation → Creation/Debug rule
- Failed checks → Debug rules

**Knowledge Sources Panel**:
- Documents from `reasoning.documents`
- Relevance from document score
- Preview shows retrieval method

**Metrics**:
- Confidence from `confidence` field
- Processing time from client measurement
- Model from `architecture_info.type`

## Components

### Main Components

- `src/pages/Index.tsx` - Main page with state management
- `src/components/chat/ChatInterface.tsx` - Chat UI
- `src/components/neuro/NeuroConsole.tsx` - Reasoning visualization
- `src/components/neuro/RuleTrace.tsx` - Rule display
- `src/components/neuro/KnowledgeRetrieval.tsx` - Document display

### Key Features

**Animated Rule Trace**:
- Staggered timestamps
- Color-coded by type (analysis, creation, debug)
- Status indicators (triggered, active, pending)

**Knowledge Sources**:
- Relevance percentage
- Document and section names
- Preview text

**Confidence Meter**:
- Visual gauge
- Percentage display
- Color-coded (green = high, yellow = medium, red = low)

## Styling

The UI uses a **neural/cyberpunk** theme:
- Dark background with ambient glows
- Cyan and emerald accent colors
- Glassmorphism effects
- Smooth animations

## Development

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

### Linting

```bash
npm run lint
```

## Troubleshooting

### "Unable to connect to Hybrid Agent"

**Cause**: Backend not running or wrong port

**Solution**:
```bash
# Check if backend is running
curl http://localhost:8001/api/health

# If not, start it
cd /home/lxmix/Downloads/projet/Expert_Agent
python api_hybrid.py
```

### No rules showing

**Cause**: API response format mismatch

**Solution**: Check browser console for errors. Ensure backend is using the latest `api_hybrid.py`

### Slow responses

**Cause**: LLM generation takes time

**Expected**: 3-6 seconds per query (normal for local LLM)

## Future Enhancements

- [ ] Real-time streaming responses
- [ ] Export reasoning traces
- [ ] Dark/light theme toggle
- [ ] Customizable layout
- [ ] History persistence
- [ ] Multi-language support

## License

MIT

---

**Note**: This frontend is designed specifically for the Hybrid NLP-Expert Agent architecture. It visualizes all 8 layers of reasoning for full transparency and explainability.
