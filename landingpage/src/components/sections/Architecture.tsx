import { useEffect, useRef, useState } from "react";
import { motion, useScroll, useTransform, MotionValue } from "framer-motion";
import {
  Shield, Languages, Tags, BookOpenCheck, Library, Sparkles, CheckCircle2, ScrollText,
} from "lucide-react";
import { SectionHeading } from "@/components/lx/SectionHeading";

const layers = [
  { id: "security", name: "Security", icon: Shield, color: "from-cyan-400 to-sky-500", desc: "PII detection, redaction, and prompt injection filtering before processing.", bullets: ["PII detection", "Prompt injection filtering", "RBAC"] },
  { id: "nlp", name: "NLP Core", icon: Languages, color: "from-sky-400 to-blue-500", desc: "Probabilistic semantic parsing and intent hypothesis generation.", bullets: ["spaCy semantic parsing", "Intent hypothesis", "Entity extraction"] },
  { id: "expert", name: "Expert Agent", icon: BookOpenCheck, color: "from-blue-400 to-indigo-500", desc: "Deterministic validation using formal ontology and production rules.", bullets: ["Formal ontology", "Production rules", "Deterministic checks"] },
  { id: "arbitration", name: "Intent Arbitration", icon: Tags, color: "from-indigo-400 to-violet-500", desc: "Conflict resolution between NLP and symbolic rules, including off-topic guard.", bullets: ["Conflict resolution", "Off-topic guard", "Mode routing"] },
  { id: "retrieval", name: "Retrieval", icon: Library, color: "from-violet-400 to-fuchsia-500", desc: "Multi-tier retrieval combining symbolic filtering and semantic ranking.", bullets: ["pgvector semantic search", "Symbolic filtering", "ACL-aware"] },
  { id: "planning", name: "Answer Planning", icon: ScrollText, color: "from-fuchsia-400 to-pink-500", desc: "Structured answer contract creation outlining the response format and bounds.", bullets: ["Contract creation", "Schema enforcement", "Fact grounding"] },
  { id: "generation", name: "Generation", icon: Sparkles, color: "from-pink-400 to-rose-500", desc: "Controlled LLM synthesis using local models.", bullets: ["Ollama local LLM", "Constrained synthesis", "Citation tracking"] },
  { id: "validation", name: "Validation", icon: CheckCircle2, color: "from-cyan-400 to-violet-500", desc: "Self-critique and quality checks to ensure compliance and hallucination resistance.", bullets: ["Self-critique", "Quality checks", "Audit logging"] },
];

/** A single scroll-revealed layer card with parallax tilt + alternating side. */
const LayerCard = ({ l, i }: { l: typeof layers[number]; i: number }) => {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start end", "end start"] });
  const side = i % 2 === 0;
  const x = useTransform(scrollYProgress, [0, 0.5, 1], [side ? -40 : 40, 0, side ? 30 : -30]);
  const rotate = useTransform(scrollYProgress, [0, 0.5, 1], [side ? -2 : 2, 0, side ? 1.5 : -1.5]);
  const y = useTransform(scrollYProgress, [0, 1], [60, -60]);
  const Icon = l.icon;

  return (
    <motion.div
      ref={ref}
      style={{ x, y, rotate }}
      className={`relative w-full max-w-xl ${side ? "lg:mr-auto" : "lg:ml-auto"}`}
    >
      <div className="glass relative overflow-hidden rounded-3xl p-6 transition-shadow hover:shadow-neon">
        <div className={`absolute -inset-px rounded-3xl bg-gradient-to-br ${l.color} opacity-[0.07] pointer-events-none`} />
        <div className="relative flex items-start gap-4">
          <span className="relative flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl border border-hairline bg-surface-elev">
            <span className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${l.color} opacity-30`} />
            <Icon className="relative h-6 w-6 text-foreground" />
          </span>
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <span className="font-mono text-[10px] uppercase tracking-[0.22em] text-muted-foreground">L{String(i + 1).padStart(2, "0")}</span>
              <span className="h-px w-8 bg-hairline" />
              <span className="font-display text-xl font-semibold">{l.name}</span>
            </div>
            <p className="mt-2 text-sm text-muted-foreground leading-relaxed">{l.desc}</p>
            <ul className="mt-4 grid grid-cols-1 gap-1.5 sm:grid-cols-2">
              {l.bullets.map((b) => (
                <li key={b} className="flex items-start gap-2 text-xs">
                  <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-primary shadow-neon" />
                  <span className="text-foreground/80">{b}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

/** Sticky parallax visual that tracks which layer is in view. */
const StickyVisual = ({ progress }: { progress: ReturnType<typeof useScroll>["scrollYProgress"] }) => {
  const rotate = useTransform(progress, [0, 1], [0, 360]);
  const hue = useTransform(progress, [0, 1], [180, 320]);
  const idx = useTransform(progress, (v) => Math.min(layers.length - 1, Math.floor(v * layers.length)));
  const bg = useTransform(hue, (h) => `radial-gradient(circle, hsl(${h} 94% 65%) 0%, hsl(${h + 60} 81% 50%) 70%, transparent 100%)`);

  return (
    <div className="sticky top-24 hidden lg:block">
      <div className="glass-strong relative aspect-square overflow-hidden rounded-3xl">
        <div className="absolute inset-0 grid-bg opacity-30" />
        {/* concentric rings */}
        {layers.map((_, i) => (
          <motion.span
            key={i}
            className="absolute left-1/2 top-1/2 rounded-full border border-primary/30"
            style={{
              width: 60 + i * 36,
              height: 60 + i * 36,
              x: "-50%",
              y: "-50%",
              rotate,
            }}
          >
            <span
              className="absolute -top-1 left-1/2 h-2 w-2 -translate-x-1/2 rounded-full bg-primary shadow-neon"
              style={{ opacity: 0.4 + (i / layers.length) * 0.6 }}
            />
          </motion.span>
        ))}
        {/* core */}
        <motion.div
          style={{ background: bg }}
          className="absolute left-1/2 top-1/2 h-20 w-20 -translate-x-1/2 -translate-y-1/2 rounded-full blur-xl"
        />
        <div className="absolute left-1/2 top-1/2 h-12 w-12 -translate-x-1/2 -translate-y-1/2 rounded-full bg-gradient-neon shadow-neon" />

        {/* current layer label */}
        <div className="absolute inset-x-6 bottom-6">
          <div className="font-mono text-[10px] uppercase tracking-[0.22em] text-primary">Active layer</div>
          <div className="mt-1 font-display text-2xl font-semibold">
            <CurrentLayerName idx={idx} />
          </div>
        </div>
      </div>
    </div>
  );
};

const CurrentLayerName = ({ idx }: { idx: MotionValue<number> }) => {
  const [name, setName] = useState(layers[0].name);
  useEffect(() => {
    const unsub = idx.on("change", (v) => {
      const i = Math.max(0, Math.min(layers.length - 1, Math.round(v)));
      setName(layers[i].name);
    });
    return () => unsub();
  }, [idx]);
  return <span className="text-gradient">{name}</span>;
};

export const Architecture = () => {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start start", "end end"] });

  return (
    <section id="architecture" className="scroll-mt-nav relative py-28 sm:py-36">
      <div className="container">
        <SectionHeading
          eyebrow="8-Layer Architecture"
          title={<>One pipeline. <span className="text-gradient">Eight checkpoints of trust.</span></>}
          description="Every request flows top-down through deterministic and probabilistic layers. Scroll through each checkpoint."
        />

        <div ref={ref} className="relative mx-auto mt-20 grid max-w-6xl gap-16 lg:grid-cols-[1fr_minmax(320px,420px)] lg:items-start">
          {/* Cards stream */}
          <div className="relative space-y-24">
            {/* central spine */}
            <div className="pointer-events-none absolute left-4 top-0 bottom-0 hidden w-px bg-gradient-to-b from-transparent via-primary/30 to-transparent lg:block" />
            {layers.map((l, i) => (
              <LayerCard key={l.id} l={l} i={i} />
            ))}
          </div>

          {/* Sticky parallax visual */}
          <StickyVisual progress={scrollYProgress} />
        </div>
      </div>
    </section>
  );
};