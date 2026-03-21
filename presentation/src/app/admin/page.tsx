"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { LayoutDashboard, Users, FolderOpen, GitBranch, Activity, ChevronLeft, ChevronRight } from "lucide-react";
import { useSlideNav } from "../useSlideNav";

const MAX_PHASE = 5;

function Bar({ v, delay, color }: { v: number; delay: number; color: string }) {
    return (
        <motion.div initial={{ height: 0 }} animate={{ height: `${v}%` }}
            transition={{ duration: 0.7, delay, ease: "easeOut" }}
            className="w-5 rounded-t flex-shrink-0" style={{ background: color, opacity: 0.85, alignSelf: "flex-end" }} />
    );
}

const BARS = [{ v: 40, c: "#6366f1" }, { v: 65, c: "#6366f1" }, { v: 55, c: "#6366f1" }, { v: 80, c: "#1abc9c" }, { v: 70, c: "#1abc9c" }, { v: 90, c: "#1abc9c" }, { v: 75, c: "#f1c40f" }];

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

export default function Scene6Admin() {
    const [phase, setPhase] = useState(0);
    const { handleNext, handlePrev } = useSlideNav(phase, setPhase, MAX_PHASE, "/vendor", "/chatbot");

    return (
        <div className="min-h-screen grid-bg bg-[#0a0b1a] text-white pb-28">
            <div className="absolute inset-0 pointer-events-none opacity-40"
                style={{ background: "radial-gradient(ellipse 60% 40% at 80% 30%, rgba(99,102,241,0.07), transparent)" }} />

            <div className="relative z-10 max-w-6xl mx-auto px-6 py-10">
                <div className="flex flex-col items-center gap-2 mb-8">
                    <h1 className="text-2xl sm:text-3xl font-black font-display text-gradient-indigo text-center">
                        Console d'Administration Entreprise
                    </h1>
                    <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.5 }}
                        className="px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-[10px] font-black text-emerald-400 uppercase tracking-widest">
                        Données 100% Souveraines
                    </motion.div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {/* Phase 1 — Metrics */}
                    <AnimatePresence>
                        {phase >= 1 && (
                            <motion.div key="metrics" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.5 }}
                                className="glass-card rounded-2xl p-5" style={{ borderColor: "rgba(99,102,241,0.2)" }}>
                                <div className="flex items-center gap-2 mb-4">
                                    <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: "rgba(99,102,241,0.15)", border: "1px solid rgba(99,102,241,0.25)" }}>
                                        <LayoutDashboard className="w-4 h-4 text-indigo-400" />
                                    </div>
                                    <span className="text-sm font-bold text-white">Tableau de Bord</span>
                                    <div className="ml-auto w-2 h-2 rounded-full bg-indigo-500" />
                                </div>
                                {[{ l: "Requêtes / heure", v: "1,247", t: "+12%" }, { l: "Cache hits", v: "84%", t: "+5%" }, { l: "Temps moyen", v: "1.2s", t: "-8%" }].map(m => (
                                    <div key={m.l} className="flex justify-between items-center text-xs py-1">
                                        <span className="text-zinc-500">{m.l}</span>
                                        <div className="flex items-center gap-1">
                                            <span className="text-white font-semibold">{m.v}</span>
                                            <span className="text-teal-400">{m.t}</span>
                                        </div>
                                    </div>
                                ))}
                                <div className="flex items-end gap-1 pt-2 h-14">
                                    {BARS.map((b, i) => <Bar key={i} v={b.v} delay={0.15 + i * 0.07} color={b.c} />)}
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* Phase 2 — Users */}
                    <AnimatePresence>
                        {phase >= 2 && (
                            <motion.div key="users" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.5 }}
                                className="glass-card rounded-2xl p-5" style={{ borderColor: "rgba(26,188,156,0.2)" }}>
                                <div className="flex items-center gap-2 mb-4">
                                    <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: "rgba(26,188,156,0.15)", border: "1px solid rgba(26,188,156,0.25)" }}>
                                        <Users className="w-4 h-4 text-teal-400" />
                                    </div>
                                    <span className="text-sm font-bold text-white">Utilisateurs</span>
                                    <div className="ml-auto w-2 h-2 rounded-full bg-teal-500" />
                                </div>
                                <div className="space-y-2">
                                    {[{ n: "Marie Dupont", r: "Admin", c: "#f1c40f" }, { n: "Jean Martin", r: "Analyste", c: "#1abc9c" }, { n: "Sophie Leroy", r: "Utilisateur", c: "#818cf8" }, { n: "Paul Bernard", r: "Auditeur", c: "#60a5fa" }].map(u => (
                                        <div key={u.n} className="flex items-center gap-2 text-xs">
                                            <div className="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold flex-shrink-0" style={{ background: `${u.c}20`, color: u.c }}>{u.n[0]}</div>
                                            <span className="text-zinc-300 flex-1">{u.n}</span>
                                            <span className="px-1.5 py-0.5 rounded-full text-[10px]" style={{ background: `${u.c}15`, color: u.c }}>{u.r}</span>
                                        </div>
                                    ))}
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* Phase 3 — Docs */}
                    <AnimatePresence>
                        {phase >= 3 && (
                            <motion.div key="docs" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.5 }}
                                className="glass-card rounded-2xl p-5" style={{ borderColor: "rgba(245,158,11,0.2)" }}>
                                <div className="flex items-center gap-2 mb-4">
                                    <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: "rgba(245,158,11,0.15)", border: "1px solid rgba(245,158,11,0.25)" }}>
                                        <FolderOpen className="w-4 h-4 text-amber-400" />
                                    </div>
                                    <span className="text-sm font-bold text-white">Documents</span>
                                    <div className="ml-auto w-2 h-2 rounded-full bg-amber-500" />
                                </div>
                                <div className="space-y-2">
                                    {[{ n: "Ressources Humaines", c: "47 PDF", p: 80 }, { n: "Réglementation", c: "23 PDF", p: 55 }, { n: "Procédures Internes", c: "89 PDF", p: 100 }].map((d, i) => (
                                        <div key={d.n} className="space-y-1">
                                            <div className="flex justify-between text-xs"><span className="text-zinc-400">{d.n}</span><span className="text-amber-400 font-semibold">{d.c}</span></div>
                                            <div className="h-1 rounded-full bg-zinc-800">
                                                <motion.div initial={{ width: 0 }} animate={{ width: `${d.p}%` }} transition={{ duration: 0.7, delay: 0.1 + i * 0.1 }} className="h-full rounded-full" style={{ background: "#f59e0b" }} />
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* Phase 4 — Rules */}
                    <AnimatePresence>
                        {phase >= 4 && (
                            <motion.div key="rules" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.5 }}
                                className="glass-card rounded-2xl p-5" style={{ borderColor: "rgba(167,139,250,0.2)" }}>
                                <div className="flex items-center gap-2 mb-4">
                                    <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: "rgba(167,139,250,0.15)", border: "1px solid rgba(167,139,250,0.25)" }}>
                                        <GitBranch className="w-4 h-4 text-violet-400" />
                                    </div>
                                    <span className="text-sm font-bold text-white">Moteur de Règles</span>
                                    <div className="ml-auto w-2 h-2 rounded-full bg-violet-500" />
                                </div>
                                <div className="space-y-2">
                                    {["R-001 Domaines actifs", "R-045 Garde accès RH", "R-089 Filtre hors-sujet", "R-112 Audit SIEM"].map(r => (
                                        <div key={r} className="flex items-center justify-between text-xs">
                                            <span className="text-zinc-400">{r}</span>
                                            <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold" style={{ background: "rgba(26,188,156,0.14)", color: "#1abc9c" }}>● Actif</span>
                                        </div>
                                    ))}
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* Phase 5 — Audit log */}
                    <AnimatePresence>
                        {phase >= 5 && (
                            <motion.div key="audit" initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.5 }}
                                className="glass-card rounded-2xl p-5 lg:col-span-2" style={{ borderColor: "rgba(52,211,153,0.2)" }}>
                                <div className="flex items-center gap-2 mb-4">
                                    <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: "rgba(52,211,153,0.15)", border: "1px solid rgba(52,211,153,0.25)" }}>
                                        <Activity className="w-4 h-4 text-emerald-400" />
                                    </div>
                                    <span className="text-sm font-bold text-white">Journaux d'Audit</span>
                                    <div className="ml-auto w-2 h-2 rounded-full bg-emerald-500" />
                                </div>
                                <div className="space-y-1.5 font-mono text-[10px]">
                                    {["2026-03-14 23:10:12 [INFO] Query processed — user:marie", "2026-03-14 23:10:09 [INFO] Cache hit — key:proc_conge", "2026-03-14 23:09:55 [WARN] Intent blocked — off-topic", "2026-03-14 23:09:41 [INFO] Rule R-045 triggered", "2026-03-14 23:09:30 [INFO] Document indexed — rh_2024.pdf"].map((log, i) => (
                                        <div key={i} className="text-zinc-500">{log}</div>
                                    ))}
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>

            <NavBar phase={phase} max={MAX_PHASE} onNext={handleNext} onPrev={handlePrev} />
        </div>
    );
}
