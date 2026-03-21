"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { BrainCircuit, ShieldCheck, FileText, Cloud, Users, ChevronLeft, ChevronRight } from "lucide-react";
import { useSlideNav } from "../useSlideNav";

const NODES = [
    { id: "user", label: "Utilisateur", sub: "Interface Chatbot React", icon: Users, color: "#818cf8" },
    { id: "ai", label: "Cœur IA d'Entreprise", sub: "LxGuard.AI Pipeline 8 couches", icon: BrainCircuit, color: "#1abc9c" },
    { id: "vendor", label: "Plateforme Fournisseur", sub: "Contrôle Licences & Télémétrie", icon: Cloud, color: "#f1c40f" },
];
const ICONS = [
    { icon: BrainCircuit, label: "IA", color: "#818cf8" },
    { icon: ShieldCheck, label: "Sécurité", color: "#1abc9c" },
    { icon: FileText, label: "Connaissance", color: "#f1c40f" },
];
const MAX_PHASE = 3;

function NavBar({ phase, max, onNext, onPrev }: { phase: number; max: number; onNext(): void; onPrev(): void }) {
    return (
        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex items-center gap-5 z-50">
            <button onClick={onPrev} className="p-3 rounded-full transition-all hover:scale-110"
                style={{ background: "rgba(26,188,156,0.15)", border: "1px solid rgba(26,188,156,0.3)" }}>
                <ChevronLeft className="w-5 h-5 text-teal-400" />
            </button>
            <div className="flex gap-1.5">
                {Array.from({ length: max + 1 }, (_, i) => (
                    <div key={i} className={`h-1.5 rounded-full transition-all duration-300 ${i === phase ? "w-5 bg-teal-500" : i < phase ? "w-2 bg-teal-900" : "w-2 bg-zinc-800"}`} />
                ))}
            </div>
            <button onClick={onNext} className="p-3 rounded-full transition-all hover:scale-110"
                style={{ background: "linear-gradient(135deg,#4f46e5,#1abc9c)", boxShadow: "0 0 18px rgba(99,102,241,0.3)" }}>
                <ChevronRight className="w-5 h-5 text-white" />
            </button>
        </div>
    );
}

export default function Scene2Solution() {
    const [phase, setPhase] = useState(0);
    const { handleNext, handlePrev } = useSlideNav(phase, setPhase, MAX_PHASE, "/pipeline", "/");

    return (
        <div className="scene-container grid-bg overflow-hidden">
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] rounded-full opacity-50"
                    style={{ background: "radial-gradient(ellipse, rgba(26,188,156,0.06) 0%, rgba(99,102,241,0.04) 40%, transparent 70%)" }} />
            </div>

            <div className="relative z-10 w-full max-w-6xl mx-auto px-6 flex flex-col items-center gap-10">
                {/* Title */}
                <motion.div initial={{ opacity: 0, y: -24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.9 }} className="text-center space-y-3">
                    <div className="flex flex-col items-center justify-center gap-6 overflow-hidden">
                        <div className="flex justify-center">
                            {"LxGuard.AI".split("").map((char, i) => (
                                <motion.span
                                    key={i}
                                    initial={{ y: 80, opacity: 0, filter: "blur(10px)" }}
                                    animate={{ y: 0, opacity: 1, filter: "blur(0px)" }}
                                    transition={{
                                        duration: 0.8,
                                        delay: 0.1 + i * 0.05,
                                        ease: [0.215, 0.61, 0.355, 1],
                                        type: "spring", stiffness: 100, damping: 15
                                    }}
                                    className="text-5xl sm:text-7xl font-black font-display text-gradient-hero leading-none inline-block origin-bottom animate-glint drop-shadow-[0_0_20px_rgba(99,102,241,0.3)]"
                                >
                                    {char === " " ? "\u00A0" : char}
                                </motion.span>
                            ))}
                        </div>
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1 }} className="flex gap-4">
                            {["Interface UX", "Gouvernance IA", "Contrôle Fournisseur"].map(l => (
                                <span key={l} className="px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-[10px] font-black uppercase tracking-widest text-indigo-300">
                                    {l}
                                </span>
                            ))}
                        </motion.div>
                    </div>
                    <motion.p
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.8, duration: 1 }}
                        className="text-lg text-zinc-400 font-light"
                    >
                        Architecture hybride neuro-symbolique sécurisée
                    </motion.p>
                </motion.div>

                {/* Nodes */}
                <div className="w-full flex flex-col lg:flex-row items-center justify-between gap-6 relative">
                    {/* Static connection bar (no animated circles) */}
                    {phase >= 2 && (
                        <div className="hidden lg:block absolute inset-y-0 left-0 right-0 pointer-events-none">
                            <div className="absolute top-1/2 left-[30%] right-[30%] h-px"
                                style={{ background: "linear-gradient(90deg, rgba(129,140,248,0.3), rgba(26,188,156,0.3), rgba(241,196,15,0.2))" }} />
                        </div>
                    )}
                    {NODES.map((node, i) => (
                        <AnimatePresence key={node.id}>
                            {phase >= i + 1 && (
                                <motion.div
                                    initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                                    transition={{ duration: 0.55, ease: "easeOut" }}
                                    className="glass-card rounded-2xl p-6 flex flex-col items-center text-center gap-4 w-full lg:w-72 relative group"
                                    style={{ borderColor: `${node.color}30` }}>
                                    <div className="w-16 h-16 rounded-2xl flex items-center justify-center"
                                        style={{ background: `${node.color}15`, border: `1px solid ${node.color}30`, boxShadow: `0 0 24px ${node.color}20` }}>
                                        <node.icon className="w-8 h-8" style={{ color: node.color }} strokeWidth={1.5} />
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-bold text-white mb-1">{node.label}</h3>
                                        <p className="text-xs text-zinc-500">{node.sub}</p>
                                    </div>
                                    {node.id === "ai" && (
                                        <div className="flex flex-wrap gap-1 justify-center">
                                            {["NLP", "Règles", "LLM Local", "pgvector"].map(t => (
                                                <span key={t} className="px-2 py-0.5 rounded-full text-xs font-medium"
                                                    style={{ background: "rgba(26,188,156,0.1)", color: "#1abc9c", border: "1px solid rgba(26,188,156,0.2)" }}>
                                                    {t}
                                                </span>
                                            ))}
                                        </div>
                                    )}
                                </motion.div>
                            )}
                        </AnimatePresence>
                    ))}
                </div>

                {/* Icons — phase 3 */}
                <AnimatePresence>
                    {phase >= 3 && (
                        <motion.div key="icons" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.5 }}
                            className="flex items-center gap-8">
                            {ICONS.map((item, i) => (
                                <motion.div key={i} initial={{ opacity: 0, scale: 0 }} animate={{ opacity: 1, scale: 1 }}
                                    transition={{ delay: i * 0.1, type: "spring", stiffness: 280, damping: 18 }}
                                    className="flex flex-col items-center gap-2">
                                    <div className="w-12 h-12 rounded-xl flex items-center justify-center"
                                        style={{ background: `${item.color}15`, border: `1px solid ${item.color}30`, boxShadow: `0 0 16px ${item.color}20` }}>
                                        <item.icon className="w-6 h-6" style={{ color: item.color }} strokeWidth={1.5} />
                                    </div>
                                    <span className="text-xs text-zinc-500">{item.label}</span>
                                </motion.div>
                            ))}
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            <NavBar phase={phase} max={MAX_PHASE} onNext={handleNext} onPrev={handlePrev} />
        </div>
    );
}
