# Insightful Console - Next.js Expert Agent Interface

This is the frontend interface for the Next.js Expert Agent. It visualizes the agent's reasoning process, expert rules, and knowledge retrieval in real-time.

## Features

- **Neuro-Console**: Split-screen UI showing the "Brain" of the AI.
- **Rule Trace**: Visual animation of expert rules triggering.
- **Knowledge Retrieval**: Displays the exact documentation files used.
- **Real-time Diagnostics**: Connects to the Python Expert Agent backend on port 8001.

## Getting Started

1.  Ensure the Python backend is running (`Expert_Agent/api.py`).
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Start the development server:
    ```bash
    npm run dev
    ```

## Technology Stack

- Vite
- React
- TypeScript
- Tailwind CSS
- Lucide React
