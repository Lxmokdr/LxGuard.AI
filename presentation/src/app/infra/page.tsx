"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Server, Database, Cpu, Zap, Box, ChevronLeft, ChevronRight } from "lucide-react";
import { useSlideNav } from "../useSlideNav";

const COMPONENTS = [
    { id: "api", label: "FastAPI", sub: "Backend REST + SSE", icon: Server, color: "#6366f1", x: 50, y: 15 },
    { id: "db", label: "PostgreSQL", sub: "+ pgvector embeddings", icon: Database, color: "#1abc9c", x: 22, y: 48 },
    { id: "redis", label: "Redis", sub: "Cache réponses", icon: Zap, color: "#f59e0b", x: 78, y: 48 },
    { id: "llm", label: "Ollama / LLM", sub: "Inférence locale", icon: Cpu, color: "#a78bfa", x: 50, y: 78 },
    { id: "docker", label: "Docker Compose", sub: "Environnements isolés", icon: Box, color: "#60a5fa", x: 50, y: 48 },
];

// static connection lines (no animated circles)
const CONNECTIONS = [
    { from: 0, to: 1 }, { from: 0, to: 2 }, { from: 0, to: 3 }, { from: 1, to: 3 },
];

const BADGES = [
    { label: "FastAPI", color: "#6366f1" },
    { label: "PostgreSQL + pgvector", color: "#1abc9c" },
    { label: "Redis Cache", color: "#f59e0b" },
    { label: "Ollama LLM", color: "#a78bfa" },
    { label: "Docker Compose", color: "#60a5fa" },
    { label: "Keycloak RBAC", color: "#f43f5e" },
];

const MAX_PHASE = 4;

function NavBar({ phase, max, onNext, onPrev }: { phase: number; max: number; onNext(): void; onPrev(): void }) {
    return (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 flex items-center gap-5 z-50">
            <button onClick={onPrev} className="p-3 rounded-full transition-all hover:scale-110"
                style={{ background: "rgba(99,102,241,0.15)", border: "1px solid rgba(99,102,241,0.3)" }}>
                <ChevronLeft className="w-5 h-5 text-indigo-400" />
            </button>
            <div className="flex gap-1.5">
                {Array.from({ length: max + 1 }, (_, i) => (
                    <div key={i} className={`h-1.5 rounded-full transition-all duration-200 ${i === phase ? "w-5 bg-indigo-500" : i < phase ? "w-2 bg-indigo-900" : "w-2 bg-zinc-800"}`} />
                ))}
            </div>
            <button onClick={onNext} className="p-3 rounded-full transition-all hover:scale-110"
                style={{ background: "linear-gradient(135deg,#4f46e5,#1abc9c)", boxShadow: "0 0 18px rgba(99,102,241,0.4)" }}>
                <ChevronRight className="w-5 h-5 text-white" />
            </button>
        </div>
    );
}

export default function Scene8Infra() {
    const [phase, setPhase] = useState(0);
    const { handleNext, handlePrev } = useSlideNav(phase, setPhase, MAX_PHASE, "/", "/vendor");

    return (
        <div className="min-h-screen grid-bg bg-[#0a0b1a] text-white overflow-y-auto pb-28">
            <div className="absolute inset-0 pointer-events-none opacity-40"
                style={{ background: "radial-gradient(ellipse 80% 80% at 50% 50%, rgba(99,102,241,0.06), transparent 70%)" }} />

            <div className="relative z-10 max-w-6xl mx-auto px-6 py-10">
                <h1 className="text-2xl sm:text-3xl font-black font-display text-gradient-indigo text-center mb-8">
                    Infrastructure & Déploiement
                </h1>

                {/* Diagram */}
                <div className="glass-card rounded-2xl relative overflow-hidden mb-8" style={{ height: 420 }}>
                    {phase === 0 && (
                        <div className="absolute inset-0 flex items-center justify-center">
                            <p className="text-zinc-700 text-sm">Appuyez sur → pour révéler l'architecture</p>
                        </div>
                    )}

                    {/* Static SVG lines — phase 2 */}
                    {phase >= 2 && (
                        <svg className="absolute inset-0 w-full h-full pointer-events-none" viewBox="0 0 100 100" preserveAspectRatio="none">
                            {CONNECTIONS.map(({ from, to }, i) => {
                                const f = COMPONENTS[from], t = COMPONENTS[to];
                                return (
                                    <motion.line key={i} x1={f.x} y1={f.y} x2={t.x} y2={t.y}
                                        stroke={f.color} strokeWidth="0.5" strokeDasharray="3 3" opacity="0.35"
                                        initial={{ pathLength: 0 }} animate={{ pathLength: 1 }}
                                        transition={{ duration: 0.6, delay: i * 0.1 }} />
                                );
                            })}
                        </svg>
                    )}

                    {/* Component nodes — phase 1 */}
                    {COMPONENTS.map((comp, idx) => (
                        <AnimatePresence key={comp.id}>
                            {phase >= 1 && (
                                <motion.div
                                    initial={{ opacity: 0, scale: 0 }} animate={{ opacity: 1, scale: 1 }}
                                    transition={{ type: "spring", stiffness: 260, damping: 18, delay: idx * 0.09 }}
                                    className="absolute flex flex-col items-center gap-1 z-10"
                                    style={{ left: `${comp.x}%`, top: `${comp.y}%`, transform: "translate(-50%,-50%)" }}>
                                    <div className="w-14 h-14 rounded-xl flex items-center justify-center hover:scale-110 transition-transform"
                                        style={{ background: `${comp.color}15`, border: `1px solid ${comp.color}38`, boxShadow: `0 0 18px ${comp.color}22` }}>
                                        <comp.icon className="w-7 h-7" style={{ color: comp.color }} strokeWidth={1.5} />
                                    </div>
                                    <span className="text-xs font-bold text-white whitespace-nowrap">{comp.label}</span>
                                    <span className="text-[10px] text-zinc-600 whitespace-nowrap text-center max-w-[90px]">{comp.sub}</span>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    ))}
                </div>

                {/* Badges — phase 3 */}
                <AnimatePresence>
                    {phase >= 3 && (
                        <motion.div key="badges" initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.5 }}
                            className="flex flex-wrap justify-center gap-3 mb-10">
                            {BADGES.map((t, i) => (
                                <motion.span key={t.label} initial={{ opacity: 0, scale: 0.75 }} animate={{ opacity: 1, scale: 1 }}
                                    transition={{ delay: i * 0.07, type: "spring", stiffness: 300 }}
                                    className="px-3 py-1.5 rounded-full text-xs font-semibold"
                                    style={{ background: `${t.color}12`, border: `1px solid ${t.color}28`, color: t.color }}>
                                    {t.label}
                                </motion.span>
                            ))}
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Final conclusion — phase 4 */}
                <AnimatePresence>
                    {phase >= 4 && (
                        <motion.div key="end" initial={{ opacity: 0, y: 24, scale: 0.96 }} animate={{ opacity: 1, y: 0, scale: 1 }}
                            transition={{ duration: 0.9, ease: "easeOut" }} className="text-center space-y-4">
                            <h2 className="text-4xl sm:text-6xl font-black font-display text-gradient-hero">
                                Hybrid NLP-Expert Agent
                            </h2>
                            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4, duration: 0.8 }}
                                className="flex items-center justify-center gap-4 text-lg font-semibold">
                                <span className="text-gradient-indigo">Sécurisé</span>
                                <span className="text-zinc-700">•</span>
                                <span className="text-gradient-teal">Explicable</span>
                                <span className="text-zinc-700">•</span>
                                <span className="text-gradient-gold">Entreprise IA</span>
                            </motion.div>
                            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.8 }} className="flex justify-center pt-2">
                                <button onClick={() => handleNext()}
                                    className="px-6 py-3 rounded-full text-sm font-semibold hover:scale-105 transition-transform"
                                    style={{ background: "linear-gradient(135deg,#4f46e5,#1abc9c)", boxShadow: "0 0 32px rgba(99,102,241,0.4)" }}>
                                    Recommencer la présentation →
                                </button>
                            </motion.div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            <NavBar phase={phase} max={MAX_PHASE} onNext={handleNext} onPrev={handlePrev} />
        </div>
    );
}
