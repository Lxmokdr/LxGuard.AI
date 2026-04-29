import { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { Server, Database, Zap, Brain } from "lucide-react";
import { SectionHeading } from "@/components/lx/SectionHeading";

const nodes = [
  { id: "api", name: "FastAPI", role: "Async API gateway", why: "Type-safe Python with first-class async + OpenAPI.", icon: Server, x: 12, y: 30 },
  { id: "db", name: "PostgreSQL + pgvector", role: "Truth store + vector index", why: "One database for transactional data, embeddings and ACLs.", icon: Database, x: 70, y: 18 },
  { id: "cache", name: "Redis", role: "Cache + queue", why: "Sub-ms classification cache and durable task queue.", icon: Zap, x: 18, y: 75 },
  { id: "llm", name: "Ollama LLM", role: "Local inference", why: "Self-hosted, OSS models — no data leaves your perimeter.", icon: Brain, x: 78, y: 70 },
];

export const TechStack = () => {
  const ref = useRef<HTMLElement>(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start end", "end start"] });
  const diagramY = useTransform(scrollYProgress, [0, 1], [80, -80]);
  const rotate = useTransform(scrollYProgress, [0, 1], [-2, 2]);

  return (
  <section ref={ref} id="stack" className="scroll-mt-nav relative py-28 sm:py-36">
    <div className="container">
      <SectionHeading
        eyebrow="Tech Stack"
        title={<>Boring tech, <span className="text-gradient">extraordinary results.</span></>}
        description="A pragmatic stack you can actually run on-prem. No vendor lock-in, no surprises."
      />

      <motion.div style={{ y: diagramY, rotate }} className="relative mx-auto mt-14 max-w-5xl">
        <div className="glass-strong relative aspect-[16/9] overflow-hidden rounded-3xl">
          <div className="absolute inset-0 grid-bg opacity-40" />

          {/* connection lines */}
          <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="absolute inset-0 h-full w-full">
            <defs>
              <linearGradient id="line" x1="0" x2="1">
                <stop offset="0%" stopColor="hsl(189 94% 60% / 0)" />
                <stop offset="50%" stopColor="hsl(189 94% 60% / 0.8)" />
                <stop offset="100%" stopColor="hsl(271 81% 70% / 0)" />
              </linearGradient>
            </defs>
            {[
              ["api", "db"], ["api", "cache"], ["api", "llm"], ["db", "llm"], ["cache", "db"],
            ].map(([a, b]) => {
              const A = nodes.find((n) => n.id === a)!;
              const B = nodes.find((n) => n.id === b)!;
              return (
                <line
                  key={`${a}-${b}`}
                  x1={A.x} y1={A.y} x2={B.x} y2={B.y}
                  stroke="url(#line)" strokeWidth="0.25"
                />
              );
            })}
          </svg>

          {/* traveling pulses */}
          {[...Array(6)].map((_, i) => (
            <motion.span
              key={i}
              className="absolute h-1.5 w-1.5 rounded-full bg-primary shadow-neon"
              initial={{ left: `${nodes[0].x}%`, top: `${nodes[0].y}%`, opacity: 0 }}
              animate={{
                left: [`${nodes[0].x}%`, `${nodes[1].x}%`, `${nodes[3].x}%`, `${nodes[2].x}%`, `${nodes[0].x}%`],
                top: [`${nodes[0].y}%`, `${nodes[1].y}%`, `${nodes[3].y}%`, `${nodes[2].y}%`, `${nodes[0].y}%`],
                opacity: [0, 1, 1, 1, 0],
              }}
              transition={{ duration: 6, repeat: Infinity, delay: i * 1, ease: "easeInOut" }}
            />
          ))}

          {/* nodes */}
          {nodes.map((n) => {
            const Icon = n.icon;
            return (
              <div
                key={n.id}
                className="group absolute -translate-x-1/2 -translate-y-1/2"
                style={{ left: `${n.x}%`, top: `${n.y}%` }}
              >
                <div className="glass-strong relative w-44 sm:w-52 rounded-2xl p-3 transition-transform hover:-translate-y-1">
                  <div className="flex items-center gap-2">
                    <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-neon shadow-neon">
                      <Icon className="h-4 w-4 text-background" />
                    </span>
                    <div className="min-w-0">
                      <div className="truncate font-display text-sm font-semibold">{n.name}</div>
                      <div className="truncate text-[10px] uppercase tracking-[0.18em] text-muted-foreground">{n.role}</div>
                    </div>
                  </div>
                  <div className="mt-2 hidden text-[11px] text-muted-foreground sm:block">{n.why}</div>
                </div>
              </div>
            );
          })}
        </div>
      </motion.div>
    </div>
  </section>
  );
};