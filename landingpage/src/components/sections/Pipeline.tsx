import { useEffect, useMemo, useRef, useState } from "react";
import { motion, useInView, useScroll, useTransform, useMotionValueEvent } from "framer-motion";
import { Shield, Languages, Tags, BookOpenCheck, Library, Sparkles, CheckCircle2, ScrollText } from "lucide-react";
import { SectionHeading } from "@/components/lx/SectionHeading";

const presets = [
  "Show me Q3 revenue by region",
  "Reset the admin password",
  "Summarize last week's incidents",
  "Export PII for user 4821",
];

const stages = [
  { key: "security", label: "Security", icon: Shield, hint: "PII + injection guard" },
  { key: "nlp", label: "NLP Core", icon: Languages, hint: "semantic intent parsing" },
  { key: "expert", label: "Expert Agent", icon: BookOpenCheck, hint: "ontology + rules validation" },
  { key: "arbitration", label: "Arbitration", icon: Tags, hint: "conflict resolution" },
  { key: "retrieve", label: "Retrieve", icon: Library, hint: "pgvector semantic search" },
  { key: "planning", label: "Planning", icon: ScrollText, hint: "answer contract creation" },
  { key: "generate", label: "Generate", icon: Sparkles, hint: "constrained synthesis" },
  { key: "validate", label: "Validate", icon: CheckCircle2, hint: "self-critique + audit" },
] as const;

type StageKey = typeof stages[number]["key"];

function classify(q: string) {
  const low = q.toLowerCase();
  if (low.includes("password") || low.includes("pii") || low.includes("export")) {
    return { mode: "Blocked", trust: 12, denied: true, reason: "Policy violation: privileged or sensitive operation" };
  }
  if (low.includes("revenue") || low.includes("report") || low.includes("summarize")) {
    return { mode: "Full", trust: 96, denied: false, reason: "Grounded answer with citations" };
  }
  return { mode: "LLM", trust: 78, denied: false, reason: "Direct response — no retrieval needed" };
}

export const Pipeline = () => {
  const sectionRef = useRef<HTMLElement>(null);
  const innerRef = useRef<HTMLDivElement>(null);
  const inView = useInView(innerRef, { amount: 0.35, once: false });

  // Scroll-driven parallax for the input + result cards
  const { scrollYProgress } = useScroll({ target: sectionRef, offset: ["start end", "end start"] });
  const inputY = useTransform(scrollYProgress, [0, 1], [30, -30]);
  const resultY = useTransform(scrollYProgress, [0, 1], [40, -20]);

  const [presetIdx, setPresetIdx] = useState(0);
  const query = presets[presetIdx];
  const result = useMemo(() => classify(query), [query]);

  const [activeIdx, setActiveIdx] = useState(-1);
  const [done, setDone] = useState(false);

  // Track the scroll specifically for the pipeline container
  const { scrollYProgress: stageProgress } = useScroll({ target: innerRef, offset: ["start 75%", "end 35%"] });

  useMotionValueEvent(stageProgress, "change", (latest) => {
    if (latest <= 0.05) {
      setActiveIdx(-1);
      setDone(false);
    } else if (latest >= 0.95) {
      setActiveIdx(-1);
      setDone(true);
    } else {
      // Map the 0.05 -> 0.95 range perfectly across the stages
      const index = Math.floor(((latest - 0.05) / 0.9) * stages.length);
      setActiveIdx(Math.min(Math.max(index, 0), stages.length - 1));
      setDone(false);
    }
  });

  return (
    <section ref={sectionRef} id="pipeline" className="scroll-mt-nav relative py-28 sm:py-36">
      <div className="container">
        <SectionHeading
          eyebrow="Live Pipeline"
          title={<>Watch a query <span className="text-gradient">become a signed answer.</span></>}
          description="Sample prompts cycle automatically — every stage classifies, validates, retrieves, generates and verifies in front of you."
        />

        <div ref={innerRef} className="mx-auto mt-14 max-w-5xl">
          {/* Input — display only, auto-cycles */}
          <motion.div style={{ y: inputY }} className="glass-strong rounded-2xl p-4 sm:p-5">
            <div className="relative">
              <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 font-mono text-xs text-primary">›</span>
              <motion.div
                key={query}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                className="w-full rounded-xl border border-hairline bg-surface/80 px-8 py-3 font-mono text-sm text-foreground"
              >
                {query}
                <span className="ml-1 inline-block h-3 w-1.5 animate-pulse bg-primary align-middle" />
              </motion.div>
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              {presets.map((p, i) => (
                <button
                  key={p}
                  onClick={() => setPresetIdx(i)}
                  className={`rounded-full border px-3 py-1 text-xs transition-colors hover:border-primary/50 cursor-pointer ${
                    presetIdx === i
                      ? "border-primary/60 bg-primary/10 text-primary"
                      : "border-hairline bg-surface/60 text-muted-foreground"
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>
          </motion.div>

          {/* Stages */}
          <div className="relative mt-10">
            <div className="pointer-events-none absolute left-0 right-0 top-1/2 hidden h-px -translate-y-1/2 bg-gradient-to-r from-transparent via-hairline to-transparent sm:block" />
            <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
              {stages.map((s, i) => {
                const Icon = s.icon;
                const isActive = activeIdx === i;
                const isPast = activeIdx > i || done;
                return (
                  <motion.div
                    key={s.key}
                    animate={{ y: isActive ? -6 : 0, scale: isActive ? 1.02 : 1 }}
                    transition={{ type: "spring", stiffness: 260, damping: 22 }}
                    className={`relative rounded-2xl border p-4 transition-all ${
                      isActive
                        ? "border-primary/60 bg-primary/5 shadow-neon"
                        : isPast
                        ? "border-primary/30 bg-surface"
                        : "border-hairline glass"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-[10px] uppercase tracking-[0.22em] text-muted-foreground">
                        0{i + 1}
                      </span>
                      <Icon className={`h-4 w-4 ${isPast || isActive ? "text-primary" : "text-muted-foreground"}`} />
                    </div>
                    <div className="mt-3 font-display text-sm font-semibold">{s.label}</div>
                    <div className="text-[11px] text-muted-foreground">{s.hint}</div>
                    {isActive && (
                      <span className="absolute inset-x-3 -bottom-px h-px overflow-hidden">
                        <span className="block h-px w-full animate-[shimmer_1.2s_linear_infinite] bg-[linear-gradient(90deg,transparent,hsl(var(--primary)),transparent)] bg-[length:200%_100%]" />
                      </span>
                    )}
                  </motion.div>
                );
              })}
            </div>
          </div>

          {/* Result */}
          <motion.div
            style={{ y: resultY }}
            initial={false}
            animate={{ opacity: done ? 1 : 0.45 }}
            className="mt-10 grid gap-4 md:grid-cols-[1fr_280px]"
          >
            <div className="glass rounded-2xl p-6">
              <div className="flex items-center gap-2 font-mono text-[11px] uppercase tracking-[0.2em] text-primary">
                <span className="h-1.5 w-1.5 rounded-full bg-primary shadow-neon" /> Synthesized response
              </div>
              <motion.p
                key={query + (done ? "-done" : "-pending")}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-3 text-sm text-foreground/90 leading-relaxed"
              >
                {done
                  ? result.denied
                    ? `🚫 Request blocked. ${result.reason}. The audit log captured this attempt with full context.`
                    : `Routed via the ${result.mode} pipeline. ${result.reason}. All citations verified against the retrieved evidence.`
                  : "Streaming through the layers…"}
              </motion.p>
              <div className="mt-4 flex flex-wrap gap-2 text-[11px] font-mono">
                {[`mode: ${result.mode.toLowerCase()}`, `latency: 184ms`, `citations: 3`, `signed: ed25519`].map((t) => (
                  <span key={t} className="rounded-full border border-hairline bg-surface px-2.5 py-1 text-muted-foreground">
                    {t}
                  </span>
                ))}
              </div>
            </div>
            <div className="glass-strong rounded-2xl p-6 text-center">
              <div className="font-mono text-[11px] uppercase tracking-[0.2em] text-primary">Trust score</div>
              <div className="mt-3 font-display text-5xl font-semibold text-gradient">{done ? result.trust : 0}</div>
              <div className="mt-1 text-xs text-muted-foreground">/ 100 deterministic</div>
              <div className="mt-4 h-1.5 w-full overflow-hidden rounded-full bg-muted">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: done ? `${result.trust}%` : 0 }}
                  transition={{ duration: 0.8 }}
                  className="h-full bg-gradient-neon"
                />
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};