"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FileText, Scissors, Database, CheckCircle, ChevronLeft, ChevronRight } from "lucide-react";
import { useSlideNav } from "../useSlideNav";

const CHUNKS = ["Art. 47 - Congé", "Procédure RH §3", "Décret 2021-112", "Guide interne", "Contrat cadre", "Annexe B"];
const NODES = [
    { x: 18, y: 22 }, { x: 38, y: 12 }, { x: 62, y: 28 }, { x: 82, y: 18 },
    { x: 12, y: 58 }, { x: 32, y: 68 }, { x: 54, y: 52 }, { x: 76, y: 62 },
    { x: 28, y: 82 }, { x: 62, y: 78 }, { x: 84, y: 48 }, { x: 50, y: 45 },
];
const ACTIVE = new Set([2, 5, 7, 11]);
const STEPS = [
    { num: 1, icon: FileText, label: "Importation", desc: "PDFs détectés auto (Watchdog)", color: "#6366f1" },
    { num: 2, icon: Scissors, label: "Smart Chunking", desc: "Segments avec overlap config", color: "#1abc9c" },
    { num: 3, icon: Database, label: "Vectorisation", desc: "pgvector → réseau de connaissances", color: "#f1c40f" },
];
const MAX_PHASE = 3;

function NavBar({ phase, max, onNext, onPrev }: { phase: number; max: number; onNext(): void; onPrev(): void }) {
    return (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 flex items-center gap-5 z-50">
            <button onClick={onPrev} className="p-3 rounded-full transition-all hover:scale-110"
                style={{ background: "rgba(26,188,156,0.15)", border: "1px solid rgba(26,188,156,0.3)" }}>
                <ChevronLeft className="w-5 h-5 text-teal-400" />
            </button>
            <div className="flex gap-1.5">
                {Array.from({ length: max + 1 }, (_, i) => (
                    <div key={i} className={`h-1.5 rounded-full transition-all duration-200 ${i === phase ? "w-5 bg-teal-500" : i < phase ? "w-2 bg-teal-900" : "w-2 bg-zinc-800"}`} />
                ))}
            </div>
            <button onClick={onNext} className="p-3 rounded-full transition-all hover:scale-110"
                style={{ background: "linear-gradient(135deg,#4f46e5,#1abc9c)", boxShadow: "0 0 18px rgba(26,188,156,0.35)" }}>
                <ChevronRight className="w-5 h-5 text-white" />
            </button>
        </div>
    );
}

export default function Scene4Knowledge() {
    const [phase, setPhase] = useState(0);
    const { handleNext, handlePrev } = useSlideNav(phase, setPhase, MAX_PHASE, "/chatbot", "/pipeline");

    return (
        <div className="min-h-screen grid-bg bg-[#0a0b1a] text-white overflow-y-auto pb-28">
            <div className="absolute inset-0 pointer-events-none opacity-50"
                style={{ background: "radial-gradient(ellipse 70% 50% at 50% 80%, rgba(26,188,156,0.06), transparent)" }} />

            <div className="relative z-10 max-w-6xl mx-auto px-6 py-10">
                <h1 className="text-2xl sm:text-3xl font-black font-display text-gradient-teal text-center mb-8">
                    Ingestion & Vectorisation des Connaissances
                </h1>

                {/* Step cards — always rendered, opacity controlled by phase */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
                    {STEPS.map((s, i) => {
                        const active = phase === i + 1;
                        const done = phase > i + 1;
                        const locked = phase < i + 1;
                        return (
                            <div key={s.num} className="glass-card rounded-2xl p-6 flex flex-col items-center text-center gap-4 transition-all duration-400"
                                style={{
                                    borderColor: !locked ? `${s.color}30` : "rgba(63,63,70,0.25)",
                                    opacity: locked ? 0.25 : 1,
                                    boxShadow: active ? `0 0 28px ${s.color}18` : "none",
                                }}>
                                <div className="w-14 h-14 rounded-2xl flex items-center justify-center"
                                    style={{ background: !locked ? `${s.color}14` : "rgba(39,39,42,0.5)", border: `1px solid ${!locked ? s.color + "28" : "rgba(63,63,70,0.25)"}` }}>
                                    <s.icon className="w-7 h-7" style={{ color: !locked ? s.color : "#52525b" }} strokeWidth={1.5} />
                                </div>
                                <div>
                                    <div className="text-xs font-bold uppercase tracking-widest mb-1" style={{ color: !locked ? s.color : "#52525b" }}>Étape {s.num}</div>
                                    <h3 className="text-base font-bold text-white mb-1">{s.label}</h3>
                                    <p className="text-xs text-zinc-500">{s.desc}</p>
                                </div>
                                {done && <CheckCircle className="w-5 h-5 text-teal-400" />}
                            </div>
                        );
                    })}
                </div>

                {/* Phase 2 — chunks */}
                <AnimatePresence>
                    {phase >= 2 && (
                        <motion.div key="chunks" initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.45 }} className="mb-8">
                            <p className="text-center text-xs text-zinc-600 uppercase tracking-widest mb-4">Segments extraits</p>
                            <div className="flex flex-wrap justify-center gap-2">
                                {CHUNKS.map((chunk, i) => (
                                    <motion.div key={chunk} initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: i * 0.07, type: "spring", stiffness: 300 }}
                                        className="px-3 py-1.5 rounded-lg text-xs font-mono"
                                        style={{ background: "rgba(26,188,156,0.08)", border: "1px solid rgba(26,188,156,0.22)", color: "#5eead4" }}>
                                        {chunk}
                                    </motion.div>
                                ))}
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Phase 3 — vector network (static SVG, no animated circles) */}
                <AnimatePresence>
                    {phase >= 3 && (
                        <motion.div key="net" initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.5 }}
                            className="glass-card rounded-2xl p-4 relative overflow-hidden" style={{ height: 220 }}>
                            <p className="text-xs text-zinc-600 uppercase tracking-widest text-center mb-1">Réseau de connaissances vectoriel</p>
                            <svg className="absolute inset-0 w-full h-full opacity-80" viewBox="0 0 100 100" preserveAspectRatio="none">
                                {NODES.map((n, i) =>
                                    NODES.slice(i + 1, i + 3).map((m, j) => (
                                        <line key={`${i}-${j}`} x1={n.x} y1={n.y} x2={m.x} y2={m.y}
                                            stroke={ACTIVE.has(i) ? "rgba(241,196,15,0.35)" : "rgba(26,188,156,0.14)"}
                                            strokeWidth="0.4" />
                                    ))
                                )}
                                {NODES.map((n, i) => (
                                    <circle key={i} cx={n.x} cy={n.y} r={ACTIVE.has(i) ? "1.4" : "0.9"}
                                        fill={ACTIVE.has(i) ? "#f1c40f" : "#1abc9c"}
                                        style={{ filter: ACTIVE.has(i) ? "drop-shadow(0 0 3px #f1c40f)" : "none" }} />
                                ))}
                            </svg>
                            <div className="absolute bottom-3 left-0 right-0 flex justify-center gap-4">
                                {[{ label: "Filtres Symboliques", color: "#6366f1" }, { label: "Similarité Vectorielle", color: "#f1c40f" }].map(b => (
                                    <span key={b.label} className="px-3 py-1 rounded-full text-xs font-semibold"
                                        style={{ background: `${b.color}12`, border: `1px solid ${b.color}28`, color: b.color }}>
                                        {b.label}
                                    </span>
                                ))}
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            <NavBar phase={phase} max={MAX_PHASE} onNext={handleNext} onPrev={handlePrev} />
        </div>
    );
}
