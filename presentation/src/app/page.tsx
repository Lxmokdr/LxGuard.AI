"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { BrainCircuit, ShieldCheck, Server } from "lucide-react";

export default function TitleCard() {
    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-black via-zinc-900 to-indigo-950 px-4">
            {/* Dynamic Background Effects */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-600/20 rounded-full blur-3xl opacity-50 mix-blend-screen animate-pulse duration-[5000ms]"></div>
                <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-emerald-600/20 rounded-full blur-3xl opacity-50 mix-blend-screen animate-pulse duration-[7000ms] delay-1000"></div>
            </div>

            <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 1.2, ease: "easeOut" }}
                className="relative z-10 text-center max-w-5xl"
            >
                <div className="flex justify-center gap-6 mb-8 text-indigo-400">
                    <BrainCircuit className="w-16 h-16 sm:w-20 sm:h-20" strokeWidth={1.5} />
                    <ShieldCheck className="w-16 h-16 sm:w-20 sm:h-20" strokeWidth={1.5} />
                </div>

                <h1 className="text-5xl sm:text-7xl font-extrabold tracking-tight mb-6 bg-clip-text text-transparent bg-gradient-to-r from-white via-indigo-100 to-zinc-400 drop-shadow-sm">
                    Hybrid NLP-Expert Agent
                </h1>

                <motion.p
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 1, delay: 0.8 }}
                    className="text-2xl sm:text-3xl text-zinc-300 font-light tracking-wide mb-16"
                >
                    Complete System Overview
                </motion.p>

                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.8, delay: 1.5 }}
                >
                    <Link
                        href="/architecture"
                        className="group relative inline-flex items-center justify-center px-8 py-4 font-semibold text-white transition-all duration-300 bg-indigo-600 border border-transparent rounded-full hover:bg-indigo-700 hover:shadow-[0_0_30px_rgba(79,70,229,0.5)] focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-gray-900"
                    >
                        <span className="mr-3 text-lg">View Architecture Diagram</span>
                        <Server className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </Link>
                </motion.div>
            </motion.div>

            <div className="absolute bottom-8 text-zinc-600 text-sm font-medium uppercase tracking-widest">
                Confidential & Proprietary • v4.0
            </div>
        </div>
    );
}
