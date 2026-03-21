"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FileText, Scissors, Database, CheckCircle, ChevronLeft, ChevronRight } from "lucide-react";
import { useSlideNav } from "../useSlideNav";

const CHUNKS = ["Art. 47 - Congé", "Procédure RH §3", "Décret 2021-112", "Guide interne", "Contrat cadre", "Annexe B"];
const NODES = [
    { x: 30, y: 20 }, { x: 110, y: 15 }, { x: 210, y: 25 }, { x: 310, y: 20 },
    { x: 20, y: 55 }, { x: 90, y: 65 }, { x: 170, y: 50 }, { x: 270, y: 60 },
    { x: 60, y: 80 }, { x: 200, y: 75 }, { x: 320, y: 45 }, { x: 150, y: 42 },
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
                <div className="flex justify-center overflow-hidden mb-8 h-10 items-center text-center">
                    {"Moteur de Connaissance & Vectorisation".split("").map((char, i) => (
                        <motion.span
                            key={i}
                            initial={{ y: 30, opacity: 0 }}
                            animate={{ y: 0, opacity: 1 }}
                            transition={{
                                duration: 0.6,
                                delay: 0.1 + i * 0.03,
                                ease: "easeOut",
                            }}
                            className="text-2xl sm:text-3xl font-black font-display text-gradient-teal inline-block origin-bottom px-[1px]"
                        >
                            {char === " " ? "\u00A0" : char}
                        </motion.span>
                    ))}
                </div>

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
                                    transform: active ? "scale(1.02)" : "scale(1)",
                                }}>
                                <div className="w-14 h-14 rounded-2xl flex items-center justify-center"
                                    style={{ background: !locked ? `${s.color}14` : "rgba(39,39,42,0.5)", border: `1px solid ${!locked ? s.color + "28" : "rgba(63,63,70,0.25)"}` }}>
                                    <s.icon className="w-7 h-7" style={{ color: !locked ? s.color : "#52525b" }} strokeWidth={1.5} />
                                </div>
                                <div className="space-y-1">
                                    <div className="text-[10px] font-bold uppercase tracking-widest" style={{ color: !locked ? s.color : "#52525b" }}>Étape {s.num}</div>
                                    <h3 className="text-base font-bold text-white">{s.label}</h3>
                                    <p className="text-xs text-zinc-500 leading-relaxed">{s.desc}</p>
                                </div>
                                {done && <CheckCircle className="w-5 h-5 text-teal-400" />}
                            </div>
                        );
                    })}
                </div>

                {/* Phase 2 — chunks */}
                <AnimatePresence>
                    {phase >= 2 && (
                        <motion.div key="chunks" initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.45 }}
                            className="mb-10 max-w-4xl mx-auto">
                            <p className="text-center text-[10px] font-bold text-zinc-600 uppercase tracking-[0.2em] mb-4">Segments extraits</p>
                            <div className="flex flex-wrap justify-center gap-3">
                                {CHUNKS.map((chunk, i) => (
                                    <motion.div key={chunk} initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: i * 0.07, type: "spring", stiffness: 300 }}
                                        className="px-4 py-2 rounded-xl text-xs font-mono shadow-lg"
                                        style={{ background: "rgba(26,188,156,0.06)", border: "1px solid rgba(26,188,156,0.2)", color: "#1abc9c" }}>
                                        {chunk}
                                    </motion.div>
                                ))}
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Phase 3 — vector network */}
                <AnimatePresence>
                    {phase >= 3 && (
                        <motion.div key="net" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.5 }}
                            className="glass-card rounded-3xl p-6 relative overflow-hidden max-w-5xl mx-auto shadow-2xl" style={{ height: 280 }}>
                            <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-[0.25em] text-center mb-2">Réseau de connaissances vectoriel</p>
                            <div className="absolute inset-0 top-12 bottom-16 px-4 flex justify-center">
                                <svg className="w-full h-full opacity-60" viewBox="0 0 350 100">
                                    {NODES.map((n, i) =>
                                        NODES.slice(i + 1, i + 3).map((m, j) => (
                                            <line key={`${i}-${j}`} x1={n.x} y1={n.y} x2={m.x} y2={m.y}
                                                stroke={ACTIVE.has(i) ? "rgba(241,196,15,0.4)" : "rgba(26,188,156,0.15)"}
                                                strokeWidth="0.8" />
                                        ))
                                    )}
                                    {NODES.map((n, i) => (
                                        <motion.circle key={i} cx={n.x} cy={n.y}
                                            r={ACTIVE.has(i) ? "2.8" : "1.8"}
                                            fill={ACTIVE.has(i) ? "#f1c40f" : "#1abc9c"}
                                            animate={ACTIVE.has(i) ? {
                                                r: [2.8, 3.5, 2.8],
                                                fill: ["#f1c40f", "#ffffff", "#f1c40f"]
                                            } : {}}
                                            transition={ACTIVE.has(i) ? {
                                                duration: 2,
                                                repeat: Infinity,
                                                delay: i * 0.2
                                            } : {}}
                                            style={{ filter: ACTIVE.has(i) ? "drop-shadow(0 0 8px rgba(241,196,15,0.7))" : "none" }} />
                                    ))}
                                </svg>
                            </div>
                            <div className="absolute bottom-6 left-0 right-0 flex justify-center gap-6">
                                {[{ label: "Filtres Symboliques", color: "#6366f1" }, { label: "Similarité Vectorielle", color: "#f1c40f" }].map(b => (
                                    <span key={b.label} className="px-4 py-1.5 rounded-full text-xs font-bold shadow-lg"
                                        style={{ background: `${b.color}10`, border: `1px solid ${b.color}30`, color: b.color }}>
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
