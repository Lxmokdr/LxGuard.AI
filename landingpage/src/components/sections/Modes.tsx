import { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { Layers, Globe2, Zap, LucideIcon } from "lucide-react";
import { SectionHeading } from "@/components/lx/SectionHeading";

type Mode = {
  id: "full" | "external" | "llm";
  name: string;
  icon: LucideIcon;
  tagline: string;
  desc: string;
  metrics: { k: string; v: string }[];
};

const modes: Mode[] = [
  {
    id: "full",
    name: "Full Mode",
    icon: Layers,
    tagline: "Deep, structured, fully audited.",
    desc: "Run the entire 8-layer pipeline with retrieval, validation and signed audit trail. Best for high-stakes decisions.",
    metrics: [
      { k: "Latency", v: "~600ms" },
      { k: "Trust", v: "98/100" },
      { k: "Citations", v: "Required" },
    ],
  },
  {
    id: "external",
    name: "External Mode",
    icon: Globe2,
    tagline: "Knowledge-graph powered.",
    desc: "Combine internal sources with curated external graphs and live web fetchers, still routed through validation and audit.",
    metrics: [
      { k: "Latency", v: "~900ms" },
      { k: "Trust", v: "92/100" },
      { k: "Sources", v: "Hybrid" },
    ],
  },
  {
    id: "llm",
    name: "LLM Mode",
    icon: Zap,
    tagline: "Direct, fast, lightweight.",
    desc: "Skip retrieval for low-risk conversational queries. Validation and audit still wrap the response.",
    metrics: [
      { k: "Latency", v: "~180ms" },
      { k: "Trust", v: "78/100" },
      { k: "Use", v: "Conversation" },
    ],
  },
];

function ModeVisual({ id }: { id: Mode["id"] }) {
  if (id === "full")
    return (
      <div className="relative h-full w-full overflow-hidden rounded-2xl">
        <div className="absolute inset-0 grid-bg opacity-50" />
        {[...Array(5)].map((_, i) => (
          <div
            key={i}
            className="absolute left-1/2 -translate-x-1/2 rounded-full border border-primary/40"
            style={{ width: 80 + i * 50, height: 80 + i * 50, top: `calc(50% - ${(80 + i * 50) / 2}px)` }}
          >
            <div className="absolute inset-0 animate-pulse-glow rounded-full" style={{ animationDelay: `${i * 0.3}s` }} />
          </div>
        ))}
        <div className="absolute left-1/2 top-1/2 h-10 w-10 -translate-x-1/2 -translate-y-1/2 rounded-full bg-gradient-neon shadow-neon" />
      </div>
    );
  if (id === "external")
    return (
      <div className="relative h-full w-full overflow-hidden rounded-2xl">
        <svg viewBox="0 0 300 300" className="absolute inset-0 h-full w-full">
          <defs>
            <radialGradient id="g-ext" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="hsl(189 94% 55% / 0.6)" />
              <stop offset="100%" stopColor="transparent" />
            </radialGradient>
          </defs>
          <circle cx="150" cy="150" r="120" fill="url(#g-ext)" />
          {[...Array(12)].map((_, i) => {
            const a = (i / 12) * Math.PI * 2;
            const x = 150 + Math.cos(a) * 110;
            const y = 150 + Math.sin(a) * 110;
            return (
              <g key={i}>
                <line x1="150" y1="150" x2={x} y2={y} stroke="hsl(189 94% 60% / 0.4)" strokeWidth="0.6" />
                <circle cx={x} cy={y} r="3" fill="hsl(271 81% 70%)">
                  <animate attributeName="opacity" values="0.3;1;0.3" dur="2s" begin={`${i * 0.15}s`} repeatCount="indefinite" />
                </circle>
              </g>
            );
          })}
          <circle cx="150" cy="150" r="6" fill="hsl(189 94% 70%)" />
        </svg>
      </div>
    );
  return (
    <div className="relative h-full w-full overflow-hidden rounded-2xl">
      <div className="absolute inset-0 grid-bg opacity-30" />
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="font-mono text-xs text-primary">
          {"> generating".split("").map((c, i) => (
            <span key={i} className="inline-block animate-fade-in" style={{ animationDelay: `${i * 0.05}s` }}>
              {c}
            </span>
          ))}
          <span className="ml-1 inline-block h-3 w-1.5 animate-pulse bg-primary align-middle" />
        </div>
      </div>
      <span className="absolute inset-x-0 top-0 h-12 bg-gradient-to-b from-primary/30 to-transparent animate-scan-line" />
    </div>
  );
}

/**
 * Each mode card is sticky-stacked so as the user scrolls,
 * the next card slides up over the previous — no buttons required.
 */
const ModeCard = ({ mode, i, total }: { mode: Mode; i: number; total: number }) => {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start end", "end start"] });
  // gentle parallax on the visual within the card
  const visualY = useTransform(scrollYProgress, [0, 1], [40, -40]);
  // a subtle scale-down for the previous card before the next stacks over it
  const scale = useTransform(scrollYProgress, [0.5, 1], [1, 0.95]);
  const opacity = useTransform(scrollYProgress, [0.5, 1], [1, 0.55]);
  const Icon = mode.icon;
  // Slightly different sticky offsets so cards visibly stack
  const stickyTop = 96 + i * 24;

  return (
    <div ref={ref} className="sticky" style={{ top: stickyTop }}>
      <motion.article
        style={{ scale, opacity }}
        className="glass-strong relative mx-auto grid max-w-5xl gap-6 overflow-hidden rounded-3xl p-6 sm:p-8 lg:grid-cols-2"
      >
        <div className="pointer-events-none absolute right-6 top-6 font-mono text-[11px] uppercase tracking-[0.22em] text-muted-foreground">
          {String(i + 1).padStart(2, "0")} / {String(total).padStart(2, "0")}
        </div>

        <motion.div style={{ y: visualY }} className="relative aspect-[4/3] overflow-hidden rounded-2xl border border-hairline">
          <ModeVisual id={mode.id} />
        </motion.div>

        <div className="flex flex-col justify-center">
          <div className="flex items-center gap-3">
            <span className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-neon shadow-neon">
              <Icon className="h-5 w-5 text-background" />
            </span>
            <div>
              <div className="font-mono text-[11px] uppercase tracking-[0.2em] text-primary">{mode.tagline}</div>
              <h3 className="font-display text-2xl font-semibold sm:text-3xl">{mode.name}</h3>
            </div>
          </div>
          <p className="mt-4 text-sm text-muted-foreground leading-relaxed sm:text-base">{mode.desc}</p>
          <div className="mt-6 grid grid-cols-3 gap-3">
            {mode.metrics.map((m) => (
              <div key={m.k} className="rounded-xl border border-hairline bg-surface/60 p-3 text-center">
                <div className="text-[10px] uppercase tracking-[0.18em] text-muted-foreground">{m.k}</div>
                <div className="mt-1 font-display text-base font-semibold text-foreground">{m.v}</div>
              </div>
            ))}
          </div>
        </div>
      </motion.article>
    </div>
  );
};

export const Modes = () => (
  <section id="modes" className="scroll-mt-nav relative py-28 sm:py-36">
    <div className="container">
      <SectionHeading
        eyebrow="Three Execution Modes"
        title={<>Same governance. <span className="text-gradient">Different speeds.</span></>}
        description="Scroll to switch modes — from deep audited reasoning to instant conversational responses."
      />

      <div className="relative mx-auto mt-16 max-w-5xl space-y-10">
        {modes.map((m, i) => (
          <ModeCard key={m.id} mode={m} i={i} total={modes.length} />
        ))}
        {/* trailing spacer so the last card has room to settle */}
        <div aria-hidden className="h-[40vh]" />
      </div>
    </div>
  </section>
);