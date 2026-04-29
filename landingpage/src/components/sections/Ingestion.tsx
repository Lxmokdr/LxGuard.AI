import { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { FileText, Scissors, Binary, Database, Activity } from "lucide-react";
import { SectionHeading } from "@/components/lx/SectionHeading";

const stages = [
  { icon: FileText, label: "Upload", note: "PDF · DOCX · MD" },
  { icon: Scissors, label: "Chunk", note: "semantic + overlap" },
  { icon: Binary, label: "Embed", note: "ollama · 1024d" },
  { icon: Database, label: "Index", note: "pgvector · ACL" },
];

const feed = [
  { type: "added", file: "policies/2025-q4-finance.md" },
  { type: "updated", file: "runbooks/incident-response.pdf" },
  { type: "removed", file: "drafts/legacy-pricing.docx" },
  { type: "added", file: "research/architecture-notes.md" },
  { type: "updated", file: "knowledge/onboarding.pdf" },
];

const colorFor = (t: string) =>
  t === "added" ? "text-primary" : t === "updated" ? "text-neon-violet" : "text-muted-foreground";

export const Ingestion = () => {
  const ref = useRef<HTMLElement>(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start end", "end start"] });
  const yL = useTransform(scrollYProgress, [0, 1], [60, -40]);
  const yR = useTransform(scrollYProgress, [0, 1], [20, -80]);

  return (
  <section ref={ref} id="ingestion" className="scroll-mt-nav relative py-28 sm:py-36">
    <div className="container">
      <SectionHeading
        eyebrow="Real-Time Sync"
        title={<>Your knowledge base, <span className="text-gradient">always live.</span></>}
        description="A filesystem watchdog streams new and changed documents through the ingestion pipeline within seconds."
      />

      <div className="mx-auto mt-14 grid max-w-6xl gap-5 lg:grid-cols-[1.4fr_1fr]">
        {/* Pipeline */}
        <motion.div style={{ y: yL }} className="glass-strong relative overflow-hidden rounded-2xl p-6">
          <div className="absolute inset-0 grid-bg opacity-30" />
          <div className="relative">
            <div className="font-mono text-[11px] uppercase tracking-[0.2em] text-primary">Ingestion pipeline</div>
            <h3 className="mt-1 font-display text-xl font-semibold">File → Chunk → Embed → Index</h3>

            <div className="mt-8 grid grid-cols-4 gap-3">
              {stages.map((s, i) => {
                const Icon = s.icon;
                return (
                  <motion.div
                    key={s.label}
                    initial={{ opacity: 0, y: 10 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.08 }}
                    className="rounded-2xl border border-hairline bg-surface/70 p-3 text-center"
                  >
                    <span className="mx-auto mb-2 flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-neon shadow-neon">
                      <Icon className="h-4 w-4 text-background" />
                    </span>
                    <div className="font-display text-sm font-semibold">{s.label}</div>
                    <div className="text-[10px] text-muted-foreground">{s.note}</div>
                  </motion.div>
                );
              })}
            </div>

            {/* moving dot rail */}
            <div className="relative mt-6 h-1 overflow-hidden rounded-full bg-muted">
              <motion.span
                className="absolute top-0 h-full w-12 rounded-full bg-gradient-neon"
                animate={{ left: ["-12%", "100%"] }}
                transition={{ duration: 3.2, repeat: Infinity, ease: "easeInOut" }}
              />
            </div>
          </div>
        </motion.div>

        {/* Watchdog feed */}
        <motion.div style={{ y: yR }} className="glass rounded-2xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="font-mono text-[11px] uppercase tracking-[0.2em] text-primary">Watchdog</div>
              <h3 className="mt-1 font-display text-xl font-semibold">Live file events</h3>
            </div>
            <span className="inline-flex items-center gap-1.5 rounded-full border border-hairline bg-surface px-2.5 py-1 text-[11px] font-mono text-primary">
              <Activity className="h-3 w-3 animate-pulse" /> watching
            </span>
          </div>
          <ul className="mt-5 space-y-2 font-mono text-[11px]">
            {feed.map((e, i) => (
              <motion.li
                key={e.file}
                initial={{ opacity: 0, x: 10 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="flex items-center justify-between rounded-lg border border-hairline bg-surface/60 px-2.5 py-2"
              >
                <span className={`uppercase tracking-[0.18em] ${colorFor(e.type)}`}>{e.type}</span>
                <span className="truncate text-muted-foreground">{e.file}</span>
              </motion.li>
            ))}
          </ul>
        </motion.div>
      </div>
    </div>
  </section>
  );
};