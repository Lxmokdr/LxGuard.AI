
# LxGuard.AI — Immersive 3D Product Site

A futuristic, scroll-driven single-page experience that turns the LxGuard.AI neuro-symbolic architecture into a living, navigable "AI brain." Built with React + React Three Fiber + Tailwind, with GSAP/Framer Motion for choreography.

## Visual direction
- **Theme:** deep space dark (`#05060d` → `#0b0f1f`) with neon cyan `#22d3ee`, electric blue `#3b82f6`, and violet `#a855f7` accents
- **UI:** glassmorphism panels, thin neon borders, soft bloom glows, holographic gradients, subtle grain
- **Type:** Space Grotesk (display) + Inter (body), generous tracking on labels
- **Motion:** slow camera drift, particle data-flows, smooth section morphs, reduced-motion fallback

## Sections

### 1. Hero — "Living AI Brain"
- Fullscreen R3F canvas: glowing icosahedron neural core with orbiting rings, animated particle streams, post-processing bloom
- Parallax camera drift on mouse, scroll-triggered zoom-out reveal
- Title **"LxGuard.AI — Neuro-Symbolic Governance System"**, tagline **"Where Probabilistic Intelligence Meets Deterministic Truth"**, dual CTAs (Explore Architecture / Try Pipeline)

### 2. 8-Layer Architecture
- Vertical 3D stack of 8 translucent rings/nodes around a central spine, rotating slowly
- Hover: ring lifts, glows, shows label; click: side glass panel slides in with description, icon, and key responsibilities
- Layers: Security · NLP · Classification · Expert Rules · Retrieval · Generation · Validation · Audit
- Each has a signature micro-animation (shield pulse, text-particle morph, logic grid firing, floating doc fragments, checkpoint pulse, etc.)
- Continuous animated "data packet" travels top→bottom showing pipeline order

### 3. Interactive Pipeline Simulation
- Input bar: user types a sample query (with preset chips: "Show Q3 revenue", "Reset admin password", etc.)
- Animated horizontal pipeline with 5 stages: Classify → Validate → Retrieve → Generate → Verify
- Each stage lights up sequentially with a visual transformation (tokens, rule checks, doc chunks, generated tokens streaming, validation tick)
- Final card shows synthesized "answer" + trust score + audit trail

### 4. Modes Showcase
- Three holographic cards / scenes toggled with a segmented control:
  - **Full Mode** — full pipeline animation
  - **External Mode** — knowledge-graph nodes lighting up across a globe-like web
  - **LLM Mode** — single fast streaming response
- Smooth crossfade + camera transition between modes

### 5. Security & Governance
- Three visual metaphor blocks:
  - **RBAC** — animated access gates unlocking per role
  - **PII Filtering** — text strings with sensitive tokens redacting in real time
  - **Audit Logs** — vertical timeline streaming live event entries
- Trust/compliance badges row (SOC2, GDPR, ISO style — illustrative)

### 6. Tech Stack & System Architecture
- Holographic floating-panel diagram: FastAPI · PostgreSQL + pgvector · Redis · Ollama LLM
- Animated connection lines with traveling light pulses showing request flow
- Hover panel reveals role + why it was chosen

### 7. Admin & Real-Time Sync
- Document ingestion pipeline animation: File → Chunk → Embed → Index
- "Watchdog" indicator pulsing, with a live-looking feed of file events (added/updated/removed)

### 8. Footer / CTA
- Final neural-core flourish, "Request a Demo" CTA, minimal nav, copyright

## Technical approach
- **Stack:** existing React + Vite + Tailwind + shadcn; add `three`, `@react-three/fiber@^8.18`, `@react-three/drei@^9.122`, `@react-three/postprocessing`, `framer-motion`
- **Structure:**
  - `src/pages/Index.tsx` — section orchestration
  - `src/components/sections/` — Hero, Architecture, Pipeline, Modes, Security, TechStack, Ingestion, Footer
  - `src/components/three/` — NeuralCore, LayerStack, DataParticles, PipelineFlow, ModeScenes, shared materials/shaders
  - `src/components/ui/` — GlassPanel, NeonButton, SectionHeading, Badge variants
- **Design tokens:** extend `index.css` + `tailwind.config.ts` with neon palette, glass utilities, glow shadows, gradient text, custom keyframes (pulse-glow, data-flow, float)
- **Performance:** single shared Canvas where possible per section, `Suspense` + lazy section mounts, `dpr=[1,1.5]`, instanced particles, `prefers-reduced-motion` fallback to static gradients
- **Accessibility:** semantic landmarks, keyboard-focusable layer nodes, aria labels on interactive 3D triggers, reduced-motion respect

## Out of scope (v1)
- Real backend wiring — pipeline simulation is fully client-side / mocked
- Auth, real document upload — visualization only
