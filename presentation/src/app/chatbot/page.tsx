"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Bot, User, FileText, Tag, Shield, Zap, ChevronLeft, ChevronRight } from "lucide-react";
import { useSlideNav } from "../useSlideNav";

const MODES = ["Base de Connaissance", "Données Liées", "IA Pure"];
const USER_Q = "Quelle est la procédure de congé pour un cadre ?";
const AI_RESP = "La procédure est définie à l'Article 47 du règlement intérieur, section 3.2. Le cadre doit soumettre sa demande 30 jours à l'avance.";
const ENTITIES = ["Congé", "Cadre", "Article 47", "Règlement intérieur"];
const RULES = ["R-012: Hiérarchie documentaire", "R-045: Domaine RH actif", "R-089: Niveau accès validé"];
const SOURCES = ["reglement_interieur.pdf", "procedure_conges.pdf", "guide_rh_2024.pdf"];
const MAX_PHASE = 5;

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

export default function Scene5Chatbot() {
    const [phase, setPhase] = useState(0);
    const [mode, setMode] = useState(0);
    const { handleNext, handlePrev } = useSlideNav(phase, setPhase, MAX_PHASE, "/admin", "/documents");

    return (
        <div className="min-h-screen grid-bg bg-[#0a0b1a] text-white overflow-y-auto pb-28">
            <div className="absolute inset-0 pointer-events-none opacity-50"
                style={{ background: "radial-gradient(ellipse 60% 50% at 30% 50%, rgba(99,102,241,0.06), transparent)" }} />

            <div className="relative z-10 max-w-6xl mx-auto px-6 py-10">
                <h1 className="text-2xl sm:text-3xl font-black font-display text-gradient-indigo text-center mb-8">
                    LxGuard.AI — Interface Chatbot
                </h1>

                <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
                    {/* Chat panel */}
                    <div className="lg:col-span-3 glass-card rounded-2xl overflow-hidden flex flex-col" style={{ minHeight: 460 }}>
                        {/* Mode selector */}
                        <div className="flex items-center gap-1 p-2 border-b" style={{ borderColor: "rgba(63,63,70,0.4)" }}>
                            {MODES.map((m, i) => (
                                <button key={m} onClick={() => setMode(i)}
                                    className="flex-1 py-1.5 px-2 rounded-lg text-xs font-semibold transition-all duration-200"
                                    style={mode === i ? { background: "rgba(99,102,241,0.18)", color: "#a5b4fc", border: "1px solid rgba(99,102,241,0.28)" } : { color: "#52525b" }}>
                                    {m}
                                </button>
                            ))}
                        </div>

                        <div className="flex-1 p-4 space-y-4">
                            {/* User message — phase 1 */}
                            <AnimatePresence>
                                {phase >= 1 && (
                                    <motion.div key="user" initial={{ opacity: 0, x: 16 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.4 }} className="flex justify-end">
                                        <div className="max-w-xs flex items-end gap-2 flex-row-reverse">
                                            <div className="w-7 h-7 rounded-full bg-indigo-500/20 flex items-center justify-center shrink-0">
                                                <User className="w-4 h-4 text-indigo-400" />
                                            </div>
                                            <div className="px-4 py-2.5 rounded-2xl rounded-tr-sm text-sm"
                                                style={{ background: "rgba(99,102,241,0.18)", border: "1px solid rgba(99,102,241,0.25)", color: "#c7d2fe" }}>
                                                {USER_Q}
                                            </div>
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>

                            {/* AI response — phase 2 */}
                            <AnimatePresence>
                                {phase >= 2 && (
                                    <motion.div key="ai" initial={{ opacity: 0, x: -16 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.4 }} className="flex items-start gap-2">
                                        <div className="w-7 h-7 rounded-full flex items-center justify-center shrink-0"
                                            style={{ background: "rgba(26,188,156,0.15)", border: "1px solid rgba(26,188,156,0.3)" }}>
                                            <Bot className="w-4 h-4 text-teal-400" />
                                        </div>
                                        <div className="flex-1 px-4 py-2.5 rounded-2xl rounded-tl-sm text-sm leading-relaxed"
                                            style={{ background: "rgba(24,24,27,0.8)", border: "1px solid rgba(63,63,70,0.4)", color: "#d4d4d8" }}>
                                            {AI_RESP}
                                            <div className="mt-2 flex items-center gap-1 text-xs" style={{ color: "#1abc9c" }}>
                                                <Shield className="w-3 h-3" /> Sources vérifiées · Règles validées
                                            </div>
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>

                        {/* Input bar */}
                        <div className="p-3 border-t" style={{ borderColor: "rgba(63,63,70,0.4)" }}>
                            <div className="flex items-center gap-2 px-3 py-2 rounded-xl"
                                style={{ background: "rgba(39,39,42,0.6)", border: "1px solid rgba(63,63,70,0.4)" }}>
                                <span className="flex-1 text-xs text-zinc-600">Posez une question…</span>
                                <Zap className="w-4 h-4 text-zinc-700" />
                            </div>
                        </div>
                    </div>

                    {/* NeuroConsole */}
                    <div className="lg:col-span-2 flex flex-col gap-4">
                        {/* Entities — phase 3 */}
                        <AnimatePresence>
                            {phase >= 3 && (
                                <motion.div key="ent" initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.45 }}
                                    className="glass-card rounded-2xl p-4">
                                    <div className="flex items-center gap-2 mb-3">
                                        <Tag className="w-4 h-4 text-indigo-400" />
                                        <span className="text-xs font-bold uppercase tracking-widest text-indigo-400">Entités Détectées</span>
                                    </div>
                                    <div className="flex flex-wrap gap-2">
                                        {ENTITIES.map((e, i) => (
                                            <motion.span key={e} initial={{ opacity: 0, scale: 0.75 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: i * 0.07, type: "spring", stiffness: 300 }}
                                                className="px-3 py-1 rounded-full text-xs font-semibold"
                                                style={{ background: "rgba(99,102,241,0.12)", border: "1px solid rgba(99,102,241,0.24)", color: "#a5b4fc" }}>
                                                {e}
                                            </motion.span>
                                        ))}
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        {/* Rules — phase 4 */}
                        <AnimatePresence>
                            {phase >= 4 && (
                                <motion.div key="rules" initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.45 }}
                                    className="glass-card rounded-2xl p-4">
                                    <div className="flex items-center gap-2 mb-3">
                                        <Shield className="w-4 h-4 text-teal-400" />
                                        <span className="text-xs font-bold uppercase tracking-widest text-teal-400">Règles Déclenchées</span>
                                    </div>
                                    <div className="space-y-2">
                                        {RULES.map((r, i) => (
                                            <motion.div key={r} initial={{ opacity: 0, x: 8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.08 }}
                                                className="flex items-center gap-2 text-xs text-zinc-400">
                                                <div className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ background: "#1abc9c" }} /> {r}
                                            </motion.div>
                                        ))}
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        {/* Sources — phase 5 */}
                        <AnimatePresence>
                            {phase >= 5 && (
                                <motion.div key="src" initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.45 }}
                                    className="glass-card rounded-2xl p-4">
                                    <div className="flex items-center gap-2 mb-3">
                                        <FileText className="w-4 h-4 text-yellow-400" />
                                        <span className="text-xs font-bold uppercase tracking-widest text-yellow-400">Sources Utilisées</span>
                                    </div>
                                    <div className="space-y-2">
                                        {SOURCES.map((s, i) => (
                                            <motion.div key={s} initial={{ opacity: 0, x: 8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.08 }}
                                                className="flex items-center gap-2 text-xs" style={{ color: "#f1c40f" }}>
                                                <FileText className="w-3 h-3 flex-shrink-0" /> {s}
                                            </motion.div>
                                        ))}
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        {phase < 3 && (
                            <div className="glass-card rounded-2xl p-6 flex flex-col items-center justify-center gap-2 opacity-20 flex-1">
                                <Tag className="w-8 h-8 text-zinc-600" />
                                <span className="text-xs text-zinc-600">NeuroConsole — en attente</span>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            <NavBar phase={phase} max={MAX_PHASE} onNext={handleNext} onPrev={handlePrev} />
        </div>
    );
}
