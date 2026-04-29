import { useEffect, useRef, useState } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { Lock, Unlock, EyeOff, ScrollText } from "lucide-react";
import { SectionHeading } from "@/components/lx/SectionHeading";

const roles = [
  { role: "Guest", allowed: false },
  { role: "Analyst", allowed: true },
  { role: "Engineer", allowed: true },
  { role: "Admin", allowed: true },
];

const piiSamples = [
  { raw: "Email: alex@lxguard.ai", red: "Email: ●●●●●@●●●●●●●●●●" },
  { raw: "Card: 4242 4242 4242 4242", red: "Card: ●●●● ●●●● ●●●● 4242" },
  { raw: "SSN: 123-45-6789", red: "SSN: ●●●-●●-●●●●" },
];

const events = [
  "policy.allow · analyst@acme · revenue.q3 ",
  "rule.fire · pii.redact · email + card ",
  "retrieve.ok · 3 chunks · acl-filtered ",
  "generate.sign · ed25519 · trust 96 ",
  "audit.commit · trace 9af2…3c1 ",
];

export const Security = () => {
  const [tick, setTick] = useState(0);
  useEffect(() => {
    const id = setInterval(() => setTick((t) => t + 1), 1800);
    return () => clearInterval(id);
  }, []);

  const sectionRef = useRef<HTMLElement>(null);
  const { scrollYProgress } = useScroll({ target: sectionRef, offset: ["start end", "end start"] });
  const y1 = useTransform(scrollYProgress, [0, 1], [50, -50]);
  const y2 = useTransform(scrollYProgress, [0, 1], [80, -80]);
  const y3 = useTransform(scrollYProgress, [0, 1], [30, -30]);

  return (
    <section ref={sectionRef} id="security" className="scroll-mt-nav relative py-28 sm:py-36">
      <div className="container">
        <SectionHeading
          eyebrow="Security & Governance"
          title={<>Trust, <span className="text-gradient">enforced in code.</span></>}
          description="Every request passes through identity, redaction and audit checkpoints — observable in real time."
        />

        <div className="mx-auto mt-14 grid max-w-6xl gap-5 lg:grid-cols-3">
          {/* RBAC */}
          <motion.div style={{ y: y1 }} className="glass relative overflow-hidden rounded-2xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-mono text-[11px] uppercase tracking-[0.2em] text-primary">RBAC</div>
                <h3 className="mt-1 font-display text-xl font-semibold">Role-aware gates</h3>
              </div>
              <Lock className="h-5 w-5 text-primary" />
            </div>
            <ul className="mt-6 space-y-2">
              {roles.map((r, i) => (
                <motion.li
                  key={r.role}
                  initial={{ opacity: 0, x: -8 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.08 }}
                  className={`flex items-center justify-between rounded-xl border border-hairline bg-surface/60 px-3 py-2 text-sm`}
                >
                  <span className="font-mono text-xs text-muted-foreground">{r.role}</span>
                  <span className={`inline-flex items-center gap-1.5 text-xs ${r.allowed ? "text-primary" : "text-muted-foreground"}`}>
                    {r.allowed ? <Unlock className="h-3.5 w-3.5" /> : <Lock className="h-3.5 w-3.5" />}
                    {r.allowed ? "granted" : "denied"}
                  </span>
                </motion.li>
              ))}
            </ul>
          </motion.div>

          {/* PII */}
          <motion.div style={{ y: y2 }} className="glass relative overflow-hidden rounded-2xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-mono text-[11px] uppercase tracking-[0.2em] text-primary">PII Filter</div>
                <h3 className="mt-1 font-display text-xl font-semibold">Live redaction</h3>
              </div>
              <EyeOff className="h-5 w-5 text-primary" />
            </div>
            <ul className="mt-6 space-y-2 font-mono text-xs">
              {piiSamples.map((p, i) => (
                <li key={p.raw} className="rounded-xl border border-hairline bg-surface/60 p-3">
                  <div className="text-muted-foreground line-through opacity-60">{p.raw}</div>
                  <motion.div
                    key={tick + "-" + i}
                    initial={{ opacity: 0, y: 4 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.15 }}
                    className="mt-1 text-primary"
                  >
                    {p.red}
                  </motion.div>
                </li>
              ))}
            </ul>
          </motion.div>

          {/* Audit */}
          <motion.div style={{ y: y3 }} className="glass relative overflow-hidden rounded-2xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-mono text-[11px] uppercase tracking-[0.2em] text-primary">Audit Log</div>
                <h3 className="mt-1 font-display text-xl font-semibold">Signed timeline</h3>
              </div>
              <ScrollText className="h-5 w-5 text-primary" />
            </div>
            <ul className="mt-6 space-y-2 font-mono text-[11px]">
              {events.map((e, i) => (
                <motion.li
                  key={tick + "-" + i}
                  initial={{ opacity: 0, x: 8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.12 }}
                  className="flex items-start gap-2 rounded-lg border border-hairline bg-surface/60 px-2.5 py-1.5"
                >
                  <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-primary shadow-neon" />
                  <span className="text-muted-foreground"><span className="text-foreground">{e.split(" ")[0]}</span>{" " + e.split(" ").slice(1).join(" ")}</span>
                </motion.li>
              ))}
            </ul>
          </motion.div>
        </div>

        {/* Compliance badges */}
        <div className="mx-auto mt-10 flex max-w-6xl flex-wrap items-center justify-center gap-3">
          {["SOC2 Type II", "GDPR Ready", "ISO 27001", "HIPAA Friendly", "PII Vault"].map((b) => (
            <span key={b} className="rounded-full border border-hairline bg-surface/60 px-3 py-1 font-mono text-[11px] uppercase tracking-[0.18em] text-muted-foreground">
              {b}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
};