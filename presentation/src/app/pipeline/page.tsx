"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
    ArrowLeft,
    ShieldCheck,
    Brain,
    Scale,
    Search,
    ListTree,
    Cpu,
    RefreshCcw,
    Network
} from "lucide-react";

export default function PipelinePage() {
    const containerVariants = {
        hidden: { opacity: 0 },
        show: {
            opacity: 1,
            transition: {
                staggerChildren: 0.15
            }
        }
    };

    const itemVariants = {
        hidden: { opacity: 0, x: -50 },
        show: { opacity: 1, x: 0, transition: { duration: 0.5, ease: "easeOut" } }
    };

    const layers = [
        { num: 0, name: "Security Check", icon: ShieldCheck, color: "zinc", desc: "RBAC & query safety" },
        { num: 1, name: "Advanced NLP Core", icon: Network, color: "zinc", desc: "Semantic parsing & intents" },
        { num: 2, name: "Symbolic Expert Brain", icon: Brain, color: "emerald", desc: "Deterministic business rules & ontology", highlight: true },
        { num: 3, name: "Intent Arbitration", icon: Scale, color: "amber", desc: "Resolves conflicts & blocks off-topic queries", highlight: true },
        { num: 4, name: "Agent-Driven Retrieval", icon: Search, color: "zinc", desc: "Symbolic + vector search (pgvector)" },
        { num: 5, name: "Recursive Answer Planning", icon: ListTree, color: "zinc", desc: "Structures formatting & validates contracts" },
        { num: 6, name: "Controlled Generation (LLM)", icon: Cpu, color: "indigo", desc: "Local inference grounded in facts", highlight: true },
        { num: 7, name: "Self-Validation Loop", icon: RefreshCcw, color: "zinc", desc: "Hallucination checker & SIEM audit logging" },
    ];

    const getColorClasses = (color: string, isHighlighted: boolean) => {
        switch (color) {
            case "emerald":
                return "border-emerald-500/50 bg-emerald-900/20 text-emerald-400 shadow-[0_0_20px_rgba(16,185,129,0.2)]";
            case "amber":
                return "border-amber-500/50 bg-amber-900/20 text-amber-400 shadow-[0_0_20px_rgba(245,158,11,0.2)]";
            case "indigo":
                return "border-indigo-500/50 bg-indigo-900/20 text-indigo-400 shadow-[0_0_20px_rgba(99,102,241,0.2)]";
            default:
                return "border-zinc-800 bg-zinc-900/50 text-zinc-400";
        }
    };

    return (
        <div className="min-h-screen bg-black text-white p-8 md:p-16 relative overflow-hidden flex flex-col items-center">
            {/* Subtle Background */}
            <div className="absolute top-0 right-0 w-full h-full bg-[radial-gradient(circle_at_top_right,rgba(99,102,241,0.05),transparent_50%)] pointer-events-none"></div>

            <div className="w-full max-w-5xl relative z-10">
                <div className="flex justify-between items-center mb-12">
                    <Link
                        href="/architecture"
                        className="flex items-center text-zinc-400 hover:text-white transition-colors group"
                    >
                        <ArrowLeft className="w-5 h-5 mr-2 group-hover:-translate-x-1 transition-transform" />
                        Back to Architecture
                    </Link>
                    <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-zinc-500 tracking-tight text-center">
                        The 8-Layer Neuro-Symbolic Pipeline
                    </h2>
                    <div className="w-40"></div> {/* Spacer to center title */}
                </div>

                <motion.div
                    variants={containerVariants}
                    initial="hidden"
                    animate="show"
                    className="relative pl-8 md:pl-0"
                >
                    {/* Vertical Connecting Line */}
                    <div className="absolute left-[39px] md:left-1/2 md:-ml-px top-0 bottom-0 w-0.5 bg-zinc-800 rounded-full"></div>

                    <div className="space-y-6">
                        {layers.map((layer, index) => {
                            const baseClasses = getColorClasses(layer.color, layer.highlight || false);

                            return (
                                <motion.div
                                    key={layer.num}
                                    variants={itemVariants}
                                    className={`relative flex items-center justify-between md:justify-normal group ${index % 2 === 0 ? "md:flex-row-reverse" : ""
                                        }`}
                                >

                                    {/* Timeline dot */}
                                    <div className={`absolute left-0 md:left-1/2 w-8 h-8 -ml-4 rounded-full border-4 border-black flex items-center justify-center text-xs font-bold transition-all duration-300 z-10 ${layer.highlight ? `bg-${layer.color}-500 shadow-[0_0_15px_rgba(var(--${layer.color}-500),0.8)]` : "bg-zinc-700"
                                        }`}>
                                        {layer.num}
                                    </div>

                                    {/* Spacer for alternating layout on desktop */}
                                    <div className="hidden md:block w-1/2 px-8"></div>

                                    {/* Card content */}
                                    <div className={`w-full md:w-1/2 pl-12 md:px-8 py-2 relative`}>
                                        <div className={`p-4 rounded-xl border backdrop-blur-sm transition-all duration-500 hover:scale-[1.02] flex items-center gap-4 ${baseClasses}`}>
                                            <div className="p-3 bg-black/40 xl:bg-transparent rounded-lg shrink-0">
                                                <layer.icon className={`w-6 h-6 ${layer.highlight ? `text-${layer.color}-400` : "text-zinc-500"}`} />
                                            </div>
                                            <div>
                                                <h3 className={`text-lg font-bold mb-1 ${layer.highlight ? "text-white" : "text-zinc-200"}`}>
                                                    Layer {layer.num}: {layer.name}
                                                </h3>
                                                <p className={`text-sm leading-snug ${layer.highlight ? `text-${layer.color}-200/80` : "text-zinc-500"}`}>
                                                    {layer.desc}
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                </motion.div>
                            );
                        })}
                    </div>
                </motion.div>

                {/* Highlight Legend */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 1.5, duration: 0.8 }}
                    className="mt-16 flex flex-wrap justify-center gap-6"
                >
                    <div className="flex items-center gap-2 text-sm text-zinc-400">
                        <span className="w-3 h-3 rounded-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]"></span>
                        Deterministic Focus
                    </div>
                    <div className="flex items-center gap-2 text-sm text-zinc-400">
                        <span className="w-3 h-3 rounded-full bg-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.5)]"></span>
                        Policy Guardrail
                    </div>
                    <div className="flex items-center gap-2 text-sm text-zinc-400">
                        <span className="w-3 h-3 rounded-full bg-indigo-500 shadow-[0_0_10px_rgba(99,102,241,0.5)]"></span>
                        Generative Focus
                    </div>
                </motion.div>

            </div>
        </div>
    );
}
