"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Globe, Key, Building2, Activity, ChevronLeft, ChevronRight } from "lucide-react";
import { useSlideNav } from "../useSlideNav";

const COMPANIES = [
    { id: "co1", name: "AXA France", x: 25, y: 30, active: true },
    { id: "co2", name: "BNP Paribas", x: 65, y: 20, active: true },
    { id: "co3", name: "Orange Business", x: 80, y: 55, active: true },
    { id: "co4", name: "Société Générale", x: 45, y: 70, active: false },
    { id: "co5", name: "SNCF", x: 15, y: 65, active: true },
    { id: "co6", name: "EDF", x: 52, y: 38, active: true },
];
const LICENSES = [
    { key: "LXG-A1B2-C3D4-PROD", company: "AXA France", status: "active", color: "#1abc9c" },
    { key: "LXG-E5F6-G7H8-PROD", company: "BNP Paribas", status: "active", color: "#1abc9c" },
    { key: "LXG-I9J0-K1L2-PROD", company: "Société Générale", status: "revoked", color: "#ef4444" },
];
const MAX_PHASE = 3;

function NavBar({ phase, max, onNext, onPrev }: { phase: number; max: number; onNext(): void; onPrev(): void }) {
    return (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 flex items-center gap-5 z-50">
            <button onClick={onPrev} className="p-3 rounded-full transition-all hover:scale-110"
                style={{ background: "rgba(241,196,15,0.15)", border: "1px solid rgba(241,196,15,0.3)" }}>
                <ChevronLeft className="w-5 h-5 text-yellow-400" />
            </button>
            <div className="flex gap-1.5">
                {Array.from({ length: max + 1 }, (_, i) => (
                    <div key={i} className={`h-1.5 rounded-full transition-all duration-200 ${i === phase ? "w-5 bg-yellow-500" : i < phase ? "w-2 bg-yellow-900" : "w-2 bg-zinc-800"}`} />
                ))}
            </div>
            <button onClick={onNext} className="p-3 rounded-full transition-all hover:scale-110"
                style={{ background: "linear-gradient(135deg,#f1c40f,#1abc9c)", boxShadow: "0 0 18px rgba(241,196,15,0.3)" }}>
                <ChevronRight className="w-5 h-5 text-white" />
            </button>
        </div>
    );
}

export default function Scene7Vendor() {
    const [phase, setPhase] = useState(0);
    const { handleNext, handlePrev } = useSlideNav(phase, setPhase, MAX_PHASE, "/infra", "/admin");

    return (
        <div className="min-h-screen grid-bg bg-[#0a0b1a] text-white pb-28">
            <div className="absolute inset-0 pointer-events-none opacity-50"
                style={{ background: "radial-gradient(circle 400px at 50% 50%, rgba(26,188,156,0.1), transparent)" }} />

            <div className="relative z-10 max-w-7xl mx-auto px-6 py-10">
                <h1 className="text-2xl sm:text-3xl font-black font-display text-gradient-gold text-center mb-8">
                    Vendor Control Platform
                </h1>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Network map */}
                    <div className="lg:col-span-2 glass-card rounded-2xl relative overflow-hidden" style={{ minHeight: 360 }}>
                        {/* Hub — always visible */}
                        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-20">
                            <div className="w-16 h-16 rounded-2xl flex items-center justify-center"
                                style={{ background: "rgba(241,196,15,0.15)", border: "1px solid rgba(241,196,15,0.4)", boxShadow: "0 0 28px rgba(241,196,15,0.25)" }}>
                                <Globe className="w-8 h-8" style={{ color: "#f1c40f" }} />
                            </div>
                        </div>

                        {/* Nodes — phase 1 */}
                        <AnimatePresence>
                            {phase >= 1 && COMPANIES.map((co, i) => (
                                <motion.div key={co.id}
                                    initial={{ opacity: 0, scale: 0 }} animate={{ opacity: 1, scale: 1 }}
                                    transition={{ delay: i * 0.1, type: "spring", stiffness: 260, damping: 20 }}
                                    className="absolute z-10"
                                    style={{ left: `${co.x}%`, top: `${co.y}%`, transform: "translate(-50%,-50%)" }}>
                                    {/* Static SVG line to hub */}
                                    <svg className="absolute pointer-events-none" style={{ width: 180, height: 180, left: -90, top: -90 }}>
                                        <line x1="90" y1="90"
                                            x2={90 + (50 - co.x) * 1.8}
                                            y2={90 + (45 - co.y) * 1.8}
                                            stroke={co.active ? "rgba(26,188,156,0.25)" : "rgba(239,68,68,0.18)"}
                                            strokeWidth="1" strokeDasharray="4 4" />
                                    </svg>
                                    <div className="relative w-12 h-12 rounded-xl flex items-center justify-center group cursor-pointer hover:scale-110 transition-transform"
                                        style={{ background: co.active ? "rgba(26,188,156,0.12)" : "rgba(239,68,68,0.1)", border: `1px solid ${co.active ? "rgba(26,188,156,0.35)" : "rgba(239,68,68,0.3)"}`, boxShadow: co.active ? "0 0 14px rgba(26,188,156,0.2)" : "none" }}>
                                        <Building2 className="w-5 h-5" style={{ color: co.active ? "#1abc9c" : "#ef4444" }} />
                                        <div className="absolute -top-7 left-1/2 -translate-x-1/2 whitespace-nowrap text-[10px] font-semibold px-2 py-0.5 rounded-full opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"
                                            style={{ background: "rgba(0,0,0,0.85)", color: co.active ? "#1abc9c" : "#ef4444" }}>
                                            {co.name}
                                        </div>
                                    </div>
                                </motion.div>
                            ))}
                        </AnimatePresence>

                        <div className="absolute bottom-3 left-3 flex items-center gap-3 text-xs text-zinc-600">
                            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-teal-500" /> Active</span>
                            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-red-500" /> Révoquée</span>
                        </div>
                    </div>

                    {/* Side panels */}
                    <div className="flex flex-col gap-4">
                        {/* Stats — phase 2 */}
                        <AnimatePresence>
                            {phase >= 2 && (
                                <motion.div key="stats" initial={{ opacity: 0, x: 24 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.4 }}
                                    className="glass-card rounded-2xl p-4">
                                    <div className="flex items-center gap-2 mb-3">
                                        <Activity className="w-4 h-4" style={{ color: "#f1c40f" }} />
                                        <span className="text-xs font-bold uppercase tracking-widest" style={{ color: "#f1c40f" }}>Vue d'Ensemble</span>
                                    </div>
                                    {[{ l: "Clients", v: "6", c: "#6366f1" }, { l: "Instances", v: "5", c: "#1abc9c" }, { l: "Licences", v: "5", c: "#f1c40f" }].map(s => (
                                        <div key={s.l} className="flex justify-between items-center py-1.5 border-b text-sm" style={{ borderColor: "rgba(63,63,70,0.3)" }}>
                                            <span className="text-zinc-500">{s.l}</span>
                                            <span className="font-bold" style={{ color: s.c }}>{s.v}</span>
                                        </div>
                                    ))}
                                </motion.div>
                            )}
                        </AnimatePresence>

                        {/* Licenses — phase 3 */}
                        <AnimatePresence>
                            {phase >= 3 && (
                                <motion.div key="lic" initial={{ opacity: 0, x: 24 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.4, delay: 0.08 }}
                                    className="glass-card rounded-2xl p-4 flex-1">
                                    <div className="flex items-center gap-2 mb-3">
                                        <Key className="w-4 h-4" style={{ color: "#f1c40f" }} />
                                        <span className="text-xs font-bold uppercase tracking-widest" style={{ color: "#f1c40f" }}>Licences</span>
                                    </div>
                                    <div className="space-y-3">
                                        {LICENSES.map((lic, i) => (
                                            <motion.div key={lic.key} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.12 }}
                                                className="p-3 rounded-xl space-y-1.5"
                                                style={{ background: `${lic.color}08`, border: `1px solid ${lic.color}22` }}>
                                                <div className="flex items-center justify-between">
                                                    <span className="text-[10px] font-bold text-zinc-400">{lic.company}</span>
                                                    <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded-full" style={{ background: `${lic.color}15`, color: lic.color }}>
                                                        {lic.status === "active" ? "● Actif" : "✕ Révoqué"}
                                                    </span>
                                                </div>
                                                <div className="font-mono text-[9px] px-2 py-1 rounded" style={{ background: "rgba(0,0,0,0.4)", color: lic.color }}>{lic.key}</div>
                                                <div className="flex gap-1.5">
                                                    <button className="text-[9px] px-2 py-0.5 rounded" style={{ background: "rgba(26,188,156,0.14)", color: "#1abc9c", border: "1px solid rgba(26,188,156,0.22)" }}>Activer</button>
                                                    <button className="text-[9px] px-2 py-0.5 rounded" style={{ background: "rgba(239,68,68,0.12)", color: "#ef4444", border: "1px solid rgba(239,68,68,0.22)" }}>Révoquer</button>
                                                </div>
                                            </motion.div>
                                        ))}
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                </div>
            </div>

            <NavBar phase={phase} max={MAX_PHASE} onNext={handleNext} onPrev={handlePrev} />
        </div>
    );
}
