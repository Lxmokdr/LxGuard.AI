"use client"

import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import {
    CheckCircle2,
    XCircle,
    Loader2,
    AlertCircle,
    Trash2,
    ShieldCheck
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { api } from "@/lib/api"

interface Triple {
    subject: string
    predicate: string
    object: string
    verified: boolean
    subject_uri?: string
    predicate_uri?: string
    object_uri?: string
}

export function TripleValidation() {
    const [triples, setTriples] = useState<Triple[]>([])
    const [loading, setLoading] = useState(true)
    const [actioning, setActioning] = useState<string | null>(null)

    const fetchTriples = async () => {
        try {
            const response = await api.knowledge.getGraph()

            // Handle different response formats (data field or direct payload)
            const graphLinks = response.data?.links || response.links || []

            const mapped = graphLinks.map((l: any) => ({
                subject: l.source,
                predicate: l.label,
                object: l.target,
                verified: l.verified,
                subject_uri: l.subject_uri,
                predicate_uri: l.predicate_uri,
                object_uri: l.object_uri
            }))
            setTriples(mapped)
        } catch (err) {
            console.error("Failed to fetch triples:", err)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchTriples()
    }, [])

    const handleAction = async (triple: Triple, action: "approve" | "reject") => {
        const tripleId = `${triple.subject}-${triple.predicate}-${triple.object}`
        setActioning(tripleId)

        try {
            await api.knowledge.manageTriple({
                subject: triple.subject,
                predicate: triple.predicate,
                object: triple.object,
                action: action,
                subject_uri: triple.subject_uri,
                predicate_uri: triple.predicate_uri,
                object_uri: triple.object_uri
            })

            // Refresh list
            await fetchTriples()
        } catch (err) {
            console.error(`Failed to ${action} triple:`, err)
        } finally {
            setActioning(null)
        }
    }

    if (loading) {
        return (
            <div className="h-[400px] flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-secondary animate-spin" />
            </div>
        )
    }

    return (
        <div className="space-y-4">
            <div className="flex items-center gap-2 text-sm text-muted-foreground font-mono mb-6">
                <ShieldCheck className="w-4 h-4 text-secondary" />
                HUMAN-IN-THE-LOOP VALIDATION QUEUE
            </div>

            <div className="overflow-hidden rounded-lg border border-border/50">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="bg-muted/50 border-b border-border/50">
                            <th className="p-4 text-xs font-mono uppercase tracking-wider text-muted-foreground">Subject</th>
                            <th className="p-4 text-xs font-mono uppercase tracking-wider text-muted-foreground">Predicate</th>
                            <th className="p-4 text-xs font-mono uppercase tracking-wider text-muted-foreground">Object</th>
                            <th className="p-4 text-xs font-mono uppercase tracking-wider text-muted-foreground">Status</th>
                            <th className="p-4 text-xs font-mono uppercase tracking-wider text-muted-foreground text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-border/30">
                        {triples.length === 0 ? (
                            <tr>
                                <td colSpan={4} className="p-8 text-center text-muted-foreground italic">
                                    Queue is empty. No triples pending validation.
                                </td>
                            </tr>
                        ) : (
                            triples.map((triple, i) => {
                                const tripleId = `${triple.subject}-${triple.predicate}-${triple.object}`
                                return (
                                    <motion.tr
                                        key={tripleId}
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        className="hover:bg-white/5 transition-colors"
                                    >
                                        <td className="p-4 text-sm font-medium text-white">{triple.subject}</td>
                                        <td className="p-4 text-sm font-mono text-primary/80">{triple.predicate}</td>
                                        <td className="p-4 text-sm text-muted-foreground">{triple.object}</td>
                                        <td className="p-4">
                                            {triple.verified ? (
                                                <span className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-secondary/10 border border-secondary/30 text-[10px] font-bold text-secondary uppercase tracking-wider">
                                                    <CheckCircle2 className="w-3 h-3" />
                                                    Verified
                                                </span>
                                            ) : (
                                                <span className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-white/5 border border-white/10 text-[10px] font-bold text-muted-foreground uppercase tracking-wider">
                                                    <Loader2 className="w-3 h-3" />
                                                    Pending
                                                </span>
                                            )}
                                        </td>
                                        <td className="p-4 text-right">
                                            <div className="flex items-center justify-end gap-2">
                                                <Button
                                                    size="sm"
                                                    variant="ghost"
                                                    disabled={actioning === tripleId}
                                                    onClick={() => handleAction(triple, "approve")}
                                                    className="h-8 w-8 p-0 text-secondary hover:text-secondary/80 hover:bg-secondary/10"
                                                >
                                                    {actioning === tripleId ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle2 className="h-4 w-4" />}
                                                </Button>
                                                <Button
                                                    size="sm"
                                                    variant="ghost"
                                                    disabled={actioning === tripleId}
                                                    onClick={() => handleAction(triple, "reject")}
                                                    className="h-8 w-8 p-0 text-destructive hover:text-destructive/80 hover:bg-destructive/10"
                                                >
                                                    <XCircle className="h-4 w-4" />
                                                </Button>
                                            </div>
                                        </td>
                                    </motion.tr>
                                )
                            })
                        )}
                    </tbody>
                </table>
            </div>

            <div className="p-4 rounded-lg bg-secondary/5 border border-secondary/20 flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-secondary shrink-0 mt-0.5" />
                <p className="text-xs text-secondary leading-relaxed">
                    Rejecting a triple will permanently remove it from the induced knowledge graph.
                    Approved triples are marked as verified and will take precedence during reasoning.
                </p>
            </div>
        </div>
    )
}
