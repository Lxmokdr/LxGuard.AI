"use client"

import { useState } from "react"
import { DocumentList } from "@/components/knowledge/DocumentList"
import { UploadWizard } from "@/components/knowledge/UploadWizard"
import { KnowledgeGraph } from "@/components/knowledge/KnowledgeGraph"
import { TripleValidation } from "@/components/knowledge/TripleValidation"
import { Button } from "@/components/ui/button"
import { Upload, Database } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"

export default function KnowledgePage() {
    const [uploadOpen, setUploadOpen] = useState(false)
    const [activeTab, setActiveTab] = useState<"docs" | "graph" | "hitl">("docs")

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-8"
        >
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight text-white flex items-center gap-3">
                        <Database className="w-8 h-8 text-primary" />
                        Knowledge Base
                    </h2>
                    <p className="text-muted-foreground font-mono text-sm mt-1">
                        CENTRAL REPOSITORY & SEMANTIC INDEXING
                    </p>
                </div>
                <div className="flex items-center space-x-2">
                    <Button
                        onClick={() => setUploadOpen(true)}
                        className="bg-primary/20 text-primary border border-primary/30 hover:bg-primary/30 glow-border-cyan gap-2"
                    >
                        <Upload className="h-4 w-4" />
                        Ingest New Document
                    </Button>
                </div>
            </div>

            {/* Tab Navigation */}
            <div className="flex items-center gap-4 border-b border-border/50 pb-4">
                <button
                    onClick={() => setActiveTab("docs")}
                    className={`text-sm font-mono px-4 py-2 rounded-lg transition-all ${activeTab === "docs"
                        ? "bg-primary/10 text-primary border border-primary/30 glow-border-cyan"
                        : "text-muted-foreground hover:text-white"
                        }`}
                >
                    DOCUMENTS
                </button>
                <button
                    onClick={() => setActiveTab("graph")}
                    className={`text-sm font-mono px-4 py-2 rounded-lg transition-all ${activeTab === "graph"
                        ? "bg-primary/10 text-primary border border-primary/30 glow-border-cyan"
                        : "text-muted-foreground hover:text-white"
                        }`}
                >
                    KNOWLEDGE GRAPH
                </button>
                <button
                    onClick={() => setActiveTab("hitl")}
                    className={`text-sm font-mono px-4 py-2 rounded-lg transition-all ${activeTab === "hitl"
                        ? "bg-secondary/10 text-secondary border border-secondary/30 glow-border-emerald"
                        : "text-muted-foreground hover:text-white"
                        }`}
                >
                    HITL VALIDATION
                </button>
            </div>

            <AnimatePresence mode="wait">
                <motion.div
                    key={activeTab}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    className="glass-card p-6"
                >
                    {activeTab === "docs" && <DocumentList />}
                    {activeTab === "graph" && <KnowledgeGraph />}
                    {activeTab === "hitl" && <TripleValidation />}
                </motion.div>
            </AnimatePresence>

            <UploadWizard open={uploadOpen} onOpenChange={setUploadOpen} />
        </motion.div>
    )
}

