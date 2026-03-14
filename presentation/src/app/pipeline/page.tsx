"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ShieldCheck, Network, Brain, Scale, Search, ListTree, Cpu, RefreshCcw, MessageCircle, CheckCircle, ChevronLeft, ChevronRight } from "lucide-react";
import { useSlideNav } from "../useSlideNav";

const LAYERS = [
    { num: 0, name: "Contrôle de Sécurité", icon: ShieldCheck, color: "#6366f1", desc: "RBAC & validation des requêtes" },
    { num: 1, name: "Cœur NLP Avancé", icon: Network, color: "#818cf8", desc: "Analyse sémantique & entités nommées" },
    { num: 2, name: "Cerveau Expert Symbolique", icon: Brain, color: "#1abc9c", desc: "Règles métier déterministes & ontologie" },
    { num: 3, name: "Arbitrage d'Intention", icon: Scale, color: "#f59e0b", desc: "Résout conflits & bloque hors-sujet" },
    { num: 4, name: "Recherche Hybride", icon: Search, color: "#818cf8", desc: "Symbolique + vecteur (pgvector)" },
    { num: 5, name: "Planification Récursive", icon: ListTree, color: "#6366f1", desc: "Formatage & validation des contrats" },
    { num: 6, name: "Génération LLM Contrôlée", icon: Cpu, color: "#a78bfa", desc: "Inférence locale basée sur les faits" },
    { num: 7, name: "Auto-Validation & Audit", icon: RefreshCcw, color: "#34d399", desc: "Anti-hallucination & journal SIEM" },
];

// 0=query bubble, 1-8=layers, 9=response
const MAX_PHASE = LAYERS.length + 1;

function NavBar({ phase, max, onNext, onPrev }: { phase: number; max: number; onNext(): void; onPrev(): void }) {
    return (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 flex items-center gap-5 z-50">
            <button onClick={onPrev} className="p-3 rounded-full transition-all hover:scale-110"
                style={{ background: "rgba(99,102,241,0.15)", border: "1px solid rgba(99,102,241,0.3)" }}>
                <ChevronLeft className="w-5 h-5 text-indigo-400" />
            </button>
            <div className="flex gap-1">
                {Array.from({ length: max + 1 }, (_, i) => (
                    <div key={i} className={`h-1.5 rounded-full transition-all duration-200 ${i === phase ? "w-4 bg-indigo-500" : i < phase ? "w-1.5 bg-indigo-900" : "w-1.5 bg-zinc-800"}`} />
                ))}
            </div>
            <button onClick={onNext} className="p-3 rounded-full transition-all hover:scale-110"
                style={{ background: "linear-gradient(135deg,#4f46e5,#1abc9c)", boxShadow: "0 0 18px rgba(99,102,241,0.4)" }}>
                <ChevronRight className="w-5 h-5 text-white" />
            </button>
        </div>
    );
}

export default function Scene3Pipeline() {
    const [phase, setPhase] = useState(0);
    const { handleNext, handlePrev } = useSlideNav(phase, setPhase, MAX_PHASE, "/documents", "/architecture");

    const activeLayer = phase - 1; // -1 when only query is showing

    return (
        <div className="min-h-screen grid-bg bg-[#0a0b1a] text-white overflow-y-auto pb-28">
            <div className="fixed inset-0 pointer-events-none opacity-60"
                style={{ background: "radial-gradient(ellipse 70% 50% at 50% 0%, rgba(99,102,241,0.07), transparent)" }} />

            <div className="relative z-10 max-w-5xl mx-auto px-6 py-10">
                <h1 className="text-2xl sm:text-3xl font-black font-display text-gradient-indigo text-center mb-8">
                    Pipeline Neuro-Symbolique à 8 Couches
                </h1>

                {/* Query bubble */}
                <div className="flex justify-center mb-6">
                    <div className="flex items-center gap-3 px-5 py-3 rounded-2xl"
                        style={{ background: "rgba(99,102,241,0.14)", border: "1px solid rgba(99,102,241,0.28)" }}>
                        <MessageCircle className="w-4 h-4 text-indigo-400" />
                        <span className="text-sm text-indigo-200">« Quelle est la procédure de congé pour un cadre ? »</span>
                    </div>
                </div>

                {/* Pipeline */}
                <div className="relative">
                    {/* Vertical track */}
                    <div className="absolute left-1/2 -translate-x-1/2 top-0 bottom-0 w-px"
                        style={{ background: "linear-gradient(to bottom, rgba(99,102,241,0.35), rgba(26,188,156,0.35))" }} />

                    {/* Active indicator dot — simple, no motion animation */}
                    {activeLayer >= 0 && activeLayer < LAYERS.length && (
                        <div className="absolute left-1/2 z-20 w-3 h-3 rounded-full -translate-x-1/2 -translate-y-1/2 transition-all duration-300"
                            style={{
                                top: `${(activeLayer / (LAYERS.length - 1)) * 95}%`,
                                background: LAYERS[activeLayer].color,
                                boxShadow: `0 0 14px ${LAYERS[activeLayer].color}`,
                            }} />
                    )}

                    <div className="space-y-3">
                        {LAYERS.map((layer, i) => {
                            const isActive = activeLayer === i;
                            const isPast = activeLayer > i;
                            return (
                                <div key={layer.num}
                                    className={`flex items-center gap-4 ${i % 2 === 0 ? "flex-row" : "flex-row-reverse"}`}>
                                    <div className="w-1/2 flex" style={{ justifyContent: i % 2 === 0 ? "flex-end" : "flex-start" }}>
                                        <div className="w-full max-w-[360px] glass-card rounded-xl p-4 flex items-center gap-3 transition-all duration-300"
                                            style={{
                                                borderColor: isActive || isPast ? `${layer.color}45` : "rgba(63,63,70,0.35)",
                                                background: isActive ? `${layer.color}10` : isPast ? `${layer.color}05` : "rgba(20,20,26,0.5)",
                                                boxShadow: isActive ? `0 0 20px ${layer.color}25` : "none",
                                                opacity: phase < 1 ? 0.2 : 1,
                                            }}>
                                            <div className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0"
                                                style={{ background: isActive || isPast ? `${layer.color}18` : "rgba(39,39,42,0.7)" }}>
                                                {isPast
                                                    ? <CheckCircle className="w-5 h-5" style={{ color: layer.color }} />
                                                    : <layer.icon className="w-5 h-5" style={{ color: isActive ? layer.color : "#52525b" }} />}
                                            </div>
                                            <div>
                                                <div className="flex items-center gap-2">
                                                    <span className="text-xs font-bold px-1.5 py-0.5 rounded" style={{ background: `${layer.color}18`, color: layer.color }}>L{layer.num}</span>
                                                    <span className={`text-sm font-semibold ${isActive ? "text-white" : isPast ? "text-zinc-300" : "text-zinc-600"}`}>{layer.name}</span>
                                                </div>
                                                <p className="text-xs text-zinc-600 mt-0.5">{layer.desc}</p>
                                            </div>
                                        </div>
                                    </div>
                                    {/* Timeline dot */}
                                    <div className="w-4 h-4 rounded-full shrink-0 z-10 border-2 border-[#0a0b1a] transition-all duration-300"
                                        style={{ background: isActive || isPast ? layer.color : "#3f3f46" }} />
                                    <div className="w-1/2" />
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* Response bubble */}
                <AnimatePresence>
                    {phase >= MAX_PHASE && (
                        <motion.div key="resp" initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}
                            className="mt-6 flex justify-center">
                            <div className="flex items-center gap-3 px-5 py-3 rounded-2xl"
                                style={{ background: "rgba(26,188,156,0.11)", border: "1px solid rgba(26,188,156,0.28)" }}>
                                <CheckCircle className="w-4 h-4 text-teal-400" />
                                <span className="text-sm text-teal-200">Réponse vérifiée · Sources citées · Traitement sécurisé</span>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Legend */}
                <div className="flex flex-wrap items-center justify-center gap-4 mt-6">
                    {[{ color: "#1abc9c", label: "Déterministe" }, { color: "#f59e0b", label: "Garde-fou" }, { color: "#a78bfa", label: "Génératif" }].map(l => (
                        <div key={l.label} className="flex items-center gap-2 text-xs text-zinc-500">
                            <div className="w-2 h-2 rounded-full" style={{ background: l.color }} />
                            {l.label}
                        </div>
                    ))}
                </div>
            </div>

            <NavBar phase={phase} max={MAX_PHASE} onNext={handleNext} onPrev={handlePrev} />
        </div>
    );
}
