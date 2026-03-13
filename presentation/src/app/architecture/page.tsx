"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
    User,
    Building2,
    Cloud,
    ArrowRight,
    ArrowLeft,
    Database,
    Lock,
    Cpu,
    ShieldAlert,
    Layers
} from "lucide-react";

export default function ArchitecturePage() {
    const containerVariants = {
        hidden: { opacity: 0 },
        show: {
            opacity: 1,
            transition: {
                staggerChildren: 0.4
            }
        }
    };

    const itemVariants = {
        hidden: { opacity: 0, y: 20 },
        show: { opacity: 1, y: 0, transition: { duration: 0.8, ease: "easeOut" } }
    };

    return (
        <div className="max-h-screen bg-black text-white p-8 md:p-10 relative overflow-hidden flex flex-col items-center">
            {/* Background Mesh */}
            <div className="absolute inset-0 bg-[linear-gradient(to_right,#4f4f4f2e_1px,transparent_1px),linear-gradient(to_bottom,#4f4f4f2e_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_50%,#000_70%,transparent_100%)] opacity-20 pointer-events-none"></div>

            <div className="w-full max-w-7xl relative z-10">
                <div className="flex justify-between items-center mb-10  ">
                    <Link
                        href="/"
                        className="flex items-center text-zinc-400 hover:text-white transition-colors group"
                    >
                        <ArrowLeft className="w-5 h-5 mr-2 group-hover:-translate-x-1 transition-transform" />
                        Retour au titre
                    </Link>
                    <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-cyan-400 tracking-tight">
                        Architecture de Haut Niveau
                    </h2>
                    <div className="flex flex-col sm:flex-row gap-4 items-end">

                        <Link
                            href="/pipeline"
                            className="flex items-center text-emerald-400 hover:text-emerald-300 transition-colors group text-sm font-medium"
                        >
                            Explorer le pipeline à 8 couches
                            <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
                        </Link>
                    </div>
                </div>

                {/* Diagram Area */}
                <motion.div
                    variants={containerVariants}
                    initial="hidden"
                    animate="show"
                    className="grid grid-cols-1 lg:grid-cols-3 gap-8 relative items-center justify-items-center"
                >

                    {/* Node 1: User / Edge */}
                    <motion.div variants={itemVariants} className="w-full max-w-sm flex flex-col items-center group relative">
                        <div className="absolute -inset-4 bg-indigo-500/10 rounded-2xl blur-xl group-hover:bg-indigo-500/20 transition-all duration-500"></div>
                        <div className="p-8 bg-zinc-900/80 backdrop-blur-sm border border-zinc-800 rounded-2xl w-full flex flex-col items-center relative z-10 shadow-2xl">
                            <div className="p-4 bg-indigo-500/20 rounded-full mb-6">
                                <User className="w-12 h-12 text-indigo-400" />
                            </div>
                            <h3 className="text-2xl font-bold mb-2">Utilisateur Final</h3>
                            <p className="text-center text-zinc-400 mb-6 text-sm">
                                Interface Chatbot (React) & Streaming en temps réel
                            </p>
                            <div className="flex gap-2">
                                <span className="px-3 py-1 bg-zinc-800 rounded-full text-xs text-zinc-300">HTTPS</span>
                                <span className="px-3 py-1 bg-zinc-800 rounded-full text-xs text-zinc-300">SSE</span>
                            </div>
                        </div>
                    </motion.div>

                    {/* Connection 1 */}
                    <div className="hidden lg:flex w-full justify-center items-center text-zinc-600 relative">
                        <div className="absolute w-full h-0.5 bg-gradient-to-r from-indigo-500/50 via-zinc-700 to-emerald-500/50"></div>
                        <motion.div
                            animate={{ x: [0, 100, 0] }}
                            transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                            className="relative z-10 bg-indigo-500 rounded-full w-3 h-3 shadow-[0_0_15px_rgba(99,102,241,0.8)]"
                        />
                    </div>

                    {/* Node 2: Enterprise AI */}
                    <motion.div variants={itemVariants} className="w-full max-w-sm flex flex-col items-center group relative lg:col-start-2">
                        <div className="absolute -inset-4 bg-emerald-500/10 rounded-2xl blur-xl group-hover:bg-emerald-500/20 transition-all duration-500"></div>
                        <div className="p-8 bg-zinc-900/80 backdrop-blur-sm border border-emerald-900/50 rounded-2xl w-full flex flex-col items-center relative z-10 shadow-2xl">
                            <div className="p-4 bg-emerald-500/20 rounded-full mb-6">
                                <Building2 className="w-12 h-12 text-emerald-400" />
                            </div>
                            <h3 className="text-2xl font-bold mb-2 text-emerald-50">Cœur d'IA d'Entreprise</h3>
                            <p className="text-center text-zinc-400 mb-6 text-sm">
                                LxGuard.AI Governance Pipeline
                            </p>
                            <div className="grid grid-cols-2 gap-3 w-full">
                                <div className="flex items-center gap-2 px-3 py-2 bg-zinc-800/80 rounded border border-zinc-700/50 text-xs text-zinc-300">
                                    <Database className="w-3 h-3 text-emerald-500" /> BD de Vecteurs
                                </div>
                                <div className="flex items-center gap-2 px-3 py-2 bg-zinc-800/80 rounded border border-zinc-700/50 text-xs text-zinc-300">
                                    <Cpu className="w-3 h-3 text-emerald-500" /> LLM Local
                                </div>
                                <div className="flex items-center gap-2 px-3 py-2 bg-zinc-800/80 rounded border border-zinc-700/50 text-xs text-zinc-300">
                                    <ShieldAlert className="w-3 h-3 text-emerald-500" /> Moteur de Règles
                                </div>
                                <div className="flex items-center gap-2 px-3 py-2 bg-zinc-800/80 rounded border border-zinc-700/50 text-xs text-zinc-300">
                                    <Lock className="w-3 h-3 text-emerald-500" /> Auth Keycloak
                                </div>
                            </div>
                        </div>
                    </motion.div>

                    {/* Connection 2 */}
                    <div className="hidden lg:flex w-full justify-center items-center text-zinc-600 relative lg:col-start-3 lg:row-start-1 -ml-16 mr-16">
                        <div className="absolute w-full h-0.5 bg-gradient-to-r from-emerald-500/50 via-zinc-700 to-cyan-500/50"></div>
                        <motion.div
                            animate={{ x: [-50, 50, -50] }}
                            transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
                            className="relative z-10 bg-cyan-500 rounded-full w-3 h-3 shadow-[0_0_15px_rgba(6,182,212,0.8)]"
                        />
                    </div>

                    {/* Node 3: Remote Vendor Platform */}
                    <motion.div variants={itemVariants} className="w-full max-w-sm flex flex-col items-center group relative lg:col-start-3 lg:row-start-1">
                        <div className="absolute -inset-4 bg-cyan-500/10 rounded-2xl blur-xl group-hover:bg-cyan-500/20 transition-all duration-500"></div>
                        <div className="p-8 bg-zinc-900/80 backdrop-blur-sm border border-cyan-900/50 rounded-2xl w-full flex flex-col items-center relative z-10 shadow-2xl">
                            <div className="p-4 bg-cyan-500/20 rounded-full mb-6">
                                <Cloud className="w-12 h-12 text-cyan-400" />
                            </div>
                            <h3 className="text-2xl font-bold mb-2 text-cyan-50">Plateforme Fournisseur Distante</h3>
                            <p className="text-center text-cyan-100/60 mb-6 text-sm">
                                Contrôle des Licences & Surveillance de la Télémétrie
                            </p>
                            <div className="w-full space-y-2">
                                <div className="w-full flex justify-between px-3 py-2 bg-zinc-800/80 rounded border border-zinc-700/50 text-xs text-zinc-300">
                                    <span>Battements de Cœur Cryptographiques</span>
                                    <span className="text-green-400">● En Ligne</span>
                                </div>
                                <div className="w-full flex justify-between px-3 py-2 bg-zinc-800/80 rounded border border-zinc-700/50 text-xs text-zinc-300">
                                    <span>Révocation de Licence</span>
                                    <span className="text-cyan-500">Active</span>
                                </div>
                            </div>
                        </div>
                    </motion.div>

                </motion.div>

                {/* Legend / Info Footer */}
                <motion.div
                    variants={itemVariants}
                    initial="hidden"
                    animate="show"
                    className="mt-10 text-center max-w-2xl mx-auto"
                >
                    <p className="text-zinc-400 leading-relaxed font-light">
                        L'architecture hybride garantit que les données sensibles de l'entreprise ne quittent jamais le <strong className="text-emerald-400 font-medium">Cœur d'IA d'Entreprise</strong>. La <strong className="text-cyan-400 font-medium">Plateforme Fournisseur Distante</strong> vérifie uniquement les licences cryptographiques et agrège les métriques de santé anonymisées.
                    </p>
                </motion.div>

            </div>
        </div>
    );
}
