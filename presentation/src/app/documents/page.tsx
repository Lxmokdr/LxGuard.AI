"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
    ArrowLeft,
    FileText,
    FolderSync,
    Scissors,
    Database,
    Search,
    ArrowRight,
    RefreshCcw
} from "lucide-react";

export default function DocumentsPage() {
    const containerVariants = {
        hidden: { opacity: 0 },
        show: {
            opacity: 1,
            transition: {
                staggerChildren: 0.2
            }
        }
    };

    const itemVariants = {
        hidden: { opacity: 0, y: 30 },
        show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" } }
    };

    return (
        <div className="min-h-screen bg-black text-white p-8 md:p-16 relative overflow-hidden flex flex-col items-center">
            {/* Background Flow */}
            <div className="absolute top-1/2 left-0 w-full h-96 bg-gradient-to-r from-emerald-900/10 via-teal-900/10 to-indigo-900/10 blur-3xl -translate-y-1/2 pointer-events-none"></div>

            <div className="w-full max-w-6xl relative z-10">
                <div className="flex justify-between items-center mb-16">
                    <Link
                        href="/architecture"
                        className="flex items-center text-zinc-400 hover:text-white transition-colors group"
                    >
                        <ArrowLeft className="w-5 h-5 mr-2 group-hover:-translate-x-1 transition-transform" />
                        Back to Architecture
                    </Link>
                    <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-emerald-400 to-teal-400 tracking-tight">
                        Traitement des Documents
                    </h2>
                    <div className="w-40"></div>
                </div>

                <motion.div
                    variants={containerVariants}
                    initial="hidden"
                    animate="show"
                    className="grid grid-cols-1 md:grid-cols-4 gap-6 items-center"
                >

                    {/* Step 1: Upload */}
                    <motion.div variants={itemVariants} className="flex flex-col items-center text-center group">
                        <div className="w-24 h-24 rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center mb-6 group-hover:border-emerald-500/50 group-hover:bg-emerald-900/20 transition-all duration-300 relative shadow-xl">
                            <FolderSync className="w-10 h-10 text-emerald-400" />
                            <div className="absolute -top-3 -right-3 w-8 h-8 bg-zinc-800 rounded-full flex items-center justify-center border-2 border-black">
                                <FileText className="w-4 h-4 text-zinc-400" />
                            </div>
                        </div>
                        <h3 className="text-lg font-bold mb-2">1. Importation Massive</h3>
                        <p className="text-sm text-zinc-400">
                            Uploads de PDFs ou sélection de dossiers complets. Le service Watchdog détecte les fichiers automatiquement.
                        </p>
                    </motion.div>

                    <div className="hidden md:flex justify-center text-zinc-700">
                        <ArrowRight className="w-8 h-8 animate-pulse text-emerald-600/50" />
                    </div>

                    {/* Step 2: Chunking */}
                    <motion.div variants={itemVariants} className="flex flex-col items-center text-center group">
                        <div className="w-24 h-24 rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center mb-6 group-hover:border-teal-500/50 group-hover:bg-teal-900/20 transition-all duration-300 shadow-xl">
                            <Scissors className="w-10 h-10 text-teal-400" />
                        </div>
                        <h3 className="text-lg font-bold mb-2">2. Découpage Intelligent</h3>
                        <p className="text-sm text-zinc-400">
                            Découpage en segments (chunks) avec gestion du chevauchement (overlap) paramétrable via la console.
                        </p>
                    </motion.div>

                    <div className="hidden md:flex justify-center text-zinc-700">
                        <ArrowRight className="w-8 h-8 animate-pulse text-teal-600/50" />
                    </div>

                    {/* Step 3: Embeddings & DB */}
                    <motion.div variants={itemVariants} className="flex flex-col items-center text-center group">
                        <div className="w-24 h-24 rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center mb-6 group-hover:border-indigo-500/50 group-hover:bg-indigo-900/20 transition-all duration-300 shadow-xl">
                            <Database className="w-10 h-10 text-indigo-400" />
                        </div>
                        <h3 className="text-lg font-bold mb-2">3. Vectorisation pgvector</h3>
                        <p className="text-sm text-zinc-400">
                            Génération d'embeddings sémantiques stockés nativement dans PostgreSQL pour la recherche par similarité.
                        </p>
                    </motion.div>

                </motion.div>

                {/* Feature Highlights */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 1.2, duration: 0.8 }}
                    className="mt-20 grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto"
                >
                    <div className="p-6 rounded-xl border border-zinc-800/50 bg-zinc-900/30">
                        <h4 className="font-bold text-emerald-400 mb-2 flex items-center gap-2">
                            <RefreshCcw className="w-4 h-4" /> Live File Watchdog
                        </h4>
                        <p className="text-sm text-zinc-400">
                            Drop any configuration file or markdown in the <code>docs/</code> directory and the backend automatically re-indexes the knowledge base in real-time.
                        </p>
                    </div>
                    <div className="p-6 rounded-xl border border-zinc-800/50 bg-zinc-900/30">
                        <h4 className="font-bold text-teal-400 mb-2 flex items-center gap-2">
                            <Search className="w-4 h-4" /> Hybrid Retrieval
                        </h4>
                        <p className="text-sm text-zinc-400">
                            Le moteur de recherche combine un filtrage symbolique stricte (basé sur les règles) avec la recherche vectorielle pour extraire le contexte exact.
                        </p>
                    </div>
                </motion.div>

            </div>
        </div>
    );
}
