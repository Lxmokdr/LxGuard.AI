"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AlertTriangle, Lock, FileText, Bot, ChevronLeft, ChevronRight } from "lucide-react";
import { useSlideNav } from "./useSlideNav";

const MAX_PHASE = 4;

const PARTICLES = Array.from({ length: 20 }, (_, i) => ({
    id: i, x: 5 + (i * 5) % 95, y: 70 + (i * 7) % 30,
    size: 3 + (i % 4), delay: (i * 0.4) % 4, duration: 5 + (i % 3),
}));

export default function Scene1Problem() {
    const [phase, setPhase] = useState(0);
    const { handleNext, handlePrev } = useSlideNav(phase, setPhase, MAX_PHASE, "/architecture", "/");

    return (
        <div className="scene-container grid-bg">
            {/* Static glow orbs — no continuous animation */}
            <div className="absolute inset-0 pointer-events-none overflow-hidden">
                <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] rounded-full opacity-40"
                    style={{ background: "radial-gradient(circle, rgba(99,102,241,0.15), transparent 70%)" }} />
                <div className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] rounded-full opacity-30"
                    style={{ background: "radial-gradient(circle, rgba(26,188,156,0.12), transparent 70%)" }} />
                {/* Lightweight particles — CSS only */}
                {PARTICLES.map(p => (
                    <div key={p.id} className="absolute rounded-full animate-float-slow"
                        style={{ left: `${p.x}%`, top: `${p.y}%`, width: p.size, height: p.size, background: "rgba(99,102,241,0.5)", animationDelay: `${p.delay}s`, animationDuration: `${p.duration}s` }} />
                ))}
            </div>
            <div className="absolute left-0 right-0 h-px bg-gradient-to-r from-transparent via-indigo-500/20 to-transparent pointer-events-none animate-scan-line" />

            <div className="relative z-10 w-full max-w-5xl mx-auto px-6 flex flex-col items-center text-center gap-8">
                {/* Title — always visible */}
                <motion.div initial={{ opacity: 0, y: 40 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 1, ease: "easeOut" }} className="space-y-3">
                    <h1 className="text-5xl sm:text-7xl font-black leading-none font-display text-gradient-hero">IA en Entreprise</h1>
                    <p className="text-2xl sm:text-3xl font-light text-zinc-400">
                        Puissante… mais <span className="text-red-400 font-semibold">Risquée.</span>
                    </p>
                </motion.div>

                {/* Phase 1 — Pain points */}
                <AnimatePresence>
                    {phase >= 1 && (
                        <motion.div key="pain" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.5 }}
                            className="grid grid-cols-1 sm:grid-cols-3 gap-4 w-full max-w-3xl">
                            {[
                                { icon: FileText, label: "Procédures Complexes", sub: "Milliers de PDF à traiter", color: "#818cf8" },
                                { icon: Bot, label: "Chatbots Génériques", sub: "Réponses hors contexte", color: "#60a5fa" },
                                { icon: AlertTriangle, label: "AI Hallucination", sub: "Contenu inventé & faux", color: "#f87171" },
                            ].map((item, i) => (
                                <motion.div key={i} initial={{ opacity: 0, scale: 0.88 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: i * 0.1, duration: 0.35 }}
                                    className="glass-card rounded-2xl p-5 flex flex-col items-center gap-3 text-center"
                                    style={{ borderColor: `${item.color}25` }}>
                                    <div className="p-3 rounded-xl" style={{ background: `${item.color}15` }}>
                                        <item.icon className="w-6 h-6" style={{ color: item.color }} strokeWidth={1.5} />
                                    </div>
                                    <span className="text-sm font-semibold text-white">{item.label}</span>
                                    <span className="text-xs text-zinc-500">{item.sub}</span>
                                </motion.div>
                            ))}
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Phase 2 — Wrong AI answer */}
                <AnimatePresence>
                    {phase >= 2 && (
                        <motion.div key="wrong" initial={{ opacity: 0, scale: 0.9, y: 10 }} animate={{ opacity: 1, scale: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.4 }}
                            className="glass-card rounded-3xl p-6 max-w-lg w-full relative overflow-hidden" style={{ borderColor: "rgba(239,68,68,0.35)", boxShadow: "0 0 30px rgba(239,68,68,0.15)" }}>
                            <div className="absolute top-0 left-0 w-full h-1 bg-red-500 animate-pulse" />
                            <div className="flex items-start gap-4">
                                <div className="w-10 h-10 rounded-2xl flex items-center justify-center shrink-0 bg-red-500/10 border border-red-500/20">
                                    <Bot className="w-5 h-5 text-red-400" />
                                </div>
                                <div className="text-left flex-1">
                                    <div className="flex items-center justify-between mb-2">
                                        <div className="text-[10px] text-red-400 font-bold uppercase tracking-[0.2em]">IA Générique non-contrôlée</div>
                                        <motion.div animate={{ scale: [1, 1.1, 1] }} transition={{ repeat: Infinity, duration: 1.5 }}
                                            className="px-2 py-0.5 rounded-md bg-red-500 text-[9px] font-black text-white">ERREUR : HALLUCINATION</motion.div>
                                    </div>
                                    <div className="bg-black/40 p-3 rounded-xl border border-white/5">
                                        <p className="text-sm text-zinc-300">
                                            "Pour les congés cadres, référez-vous à l'
                                            <span className="relative inline-block mx-1">
                                                <span className="text-red-400 font-bold">Article 47</span>
                                                <motion.div initial={{ width: 0 }} animate={{ width: "100%" }} transition={{ delay: 0.6, duration: 0.4 }} className="absolute bottom-1/2 left-0 h-0.5 bg-red-500" />
                                            </span>
                                            du code interne..."
                                        </p>
                                    </div>
                                    <div className="mt-4 flex items-center gap-2 text-xs font-bold text-red-400/80">
                                        <AlertTriangle className="w-4 h-4" />
                                        <span>Donnée factuellement fausse — Danger Légal</span>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Phase 3 — Lock & Risk */}
                <div className="flex flex-wrap justify-center gap-4">
                    <AnimatePresence>
                        {phase >= 3 && (
                            <motion.div key="lock" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.4 }}
                                className="flex items-center gap-3 px-5 py-2.5 rounded-2xl border"
                                style={{ borderColor: "rgba(241,196,15,0.3)", background: "rgba(241,196,15,0.07)" }}>
                                <Lock className="w-5 h-5 text-yellow-400 shadow-[0_0_10px_rgba(241,196,15,0.4)]" />
                                <span className="text-xs font-bold text-yellow-200">Données sensibles verrouillées</span>
                            </motion.div>
                        )}
                        {phase >= 3 && (
                            <motion.div key="risk" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.4, delay: 0.1 }}
                                className="flex items-center gap-3 px-5 py-2.5 rounded-2xl border"
                                style={{ borderColor: "rgba(239,68,68,0.3)", background: "rgba(239,68,68,0.07)" }}>
                                <div className="relative">
                                    <Bot className="w-5 h-5 text-red-400" />
                                    <motion.div animate={{ opacity: [0, 1, 0] }} transition={{ repeat: Infinity, duration: 2 }} className="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full" />
                                </div>
                                <span className="text-xs font-bold text-red-300">Risque de conformité majeur</span>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>

                {/* Phase 4 — Bridge text */}
                <AnimatePresence>
                    {phase >= 4 && (
                        <motion.p key="bridge" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.5 }}
                            className="text-lg font-light" style={{ color: "#a5b4fc" }}>
                            Il existe une meilleure approche →
                        </motion.p>
                    )}
                </AnimatePresence>
            </div>

            {/* Nav */}
            <NavBar phase={phase} max={MAX_PHASE} onNext={handleNext} onPrev={handlePrev} color="indigo" />
        </div>
    );
}

function NavBar({ phase, max, onNext, onPrev, color }: { phase: number; max: number; onNext: () => void; onPrev: () => void; color: string }) {
    const colors: Record<string, { btn: string; dot: string; active: string }> = {
        indigo: { btn: "rgba(99,102,241,0.15)", dot: "bg-indigo-900", active: "bg-indigo-500" },
        teal: { btn: "rgba(26,188,156,0.15)", dot: "bg-teal-900", active: "bg-teal-500" },
        gold: { btn: "rgba(241,196,15,0.15)", dot: "bg-yellow-900", active: "bg-yellow-500" },
    };
    const c = colors[color] ?? colors.indigo;
    return (
        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex items-center gap-5 z-50">
            <button onClick={onPrev} className="p-3 rounded-full transition-all hover:scale-110"
                style={{ background: c.btn, border: `1px solid ${c.btn.replace("0.15", "0.4")}` }}>
                <ChevronLeft className="w-5 h-5 text-white/60" />
            </button>
            <div className="flex gap-1.5">
                {Array.from({ length: max + 1 }, (_, i) => (
                    <div key={i} className={`h-1.5 rounded-full transition-all duration-300 ${i === phase ? `w-5 ${c.active}` : i < phase ? `w-2 ${c.dot}` : "w-2 bg-zinc-800"}`} />
                ))}
            </div>
            <button onClick={onNext} className="p-3 rounded-full transition-all hover:scale-110"
                style={{ background: "linear-gradient(135deg,#4f46e5,#1abc9c)", boxShadow: "0 0 18px rgba(99,102,241,0.4)" }}>
                <ChevronRight className="w-5 h-5 text-white" />
            </button>
        </div>
    );
}

// Export NavBar for reuse
export { NavBar };
