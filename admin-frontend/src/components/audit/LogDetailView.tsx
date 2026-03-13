import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { ShieldAlert, ShieldCheck, FileText, Activity } from "lucide-react"
import { cn } from "@/lib/utils"
import { LogEntry } from "./LogDataTable"

interface LogDetailViewProps {
    log: LogEntry | null
    open: boolean
    onOpenChange: (open: boolean) => void
}

export function LogDetailView({ log, open, onOpenChange }: LogDetailViewProps) {
    if (!log) return null

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-2xl bg-black/90 backdrop-blur-2xl border-white/5 text-white">
                <DialogHeader>
                    <div className="flex items-center gap-3 mb-2">
                        <div className="p-2 rounded-lg bg-primary/20 glow-border-cyan">
                            <FileText className="w-5 h-5 text-primary" />
                        </div>
                        <div>
                            <DialogTitle className="text-xl font-bold tracking-tight">Audit Trace: {log.id}</DialogTitle>
                            <DialogDescription className="text-muted-foreground font-mono text-xs uppercase">
                                Full reasoning trace for {log.user}'s query.
                            </DialogDescription>
                        </div>
                    </div>
                </DialogHeader>

                <ScrollArea className="h-[500px] w-full pr-4 mt-4">
                    {/* Meta Info */}
                    <div className="grid grid-cols-2 gap-4 mb-6">
                        <div className="p-3 rounded-lg bg-white/5 border border-white/5">
                            <span className="text-[10px] text-muted-foreground uppercase font-mono block mb-1">Timestamp</span>
                            <span className="font-mono text-sm text-primary">{log.time}</span>
                        </div>
                        <div className="p-3 rounded-lg bg-white/5 border border-white/5">
                            <span className="text-[10px] text-muted-foreground uppercase font-mono block mb-1">User Identity</span>
                            <span className="font-mono text-sm text-secondary">{log.user}</span>
                        </div>
                        <div className="p-3 rounded-lg bg-white/5 border border-white/5">
                            <span className="text-[10px] text-muted-foreground uppercase font-mono block mb-1">Intent</span>
                            <Badge variant="outline" className="border-primary/30 text-primary">{log.intent}</Badge>
                        </div>
                        <div className="p-3 rounded-lg bg-white/5 border border-white/5">
                            <span className="text-[10px] text-muted-foreground uppercase font-mono block mb-1">Status Outcome</span>
                            <Badge
                                className={cn(
                                    "text-[10px] font-bold uppercase",
                                    log.status === "SUCCESS" ? "bg-secondary/20 text-secondary border-secondary/30" :
                                        log.status === "BLOCKED" ? "bg-destructive/20 text-destructive border-destructive/30" :
                                            "bg-muted text-muted-foreground border-border"
                                )}
                            >
                                {log.status}
                            </Badge>
                        </div>
                    </div>

                    <Separator className="my-6 border-white/5" />

                    {/* Layers */}
                    <div className="space-y-6">
                        <div className="space-y-3">
                            <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-widest flex items-center gap-2">
                                <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
                                Layer 1: NLP Analysis
                            </h3>
                            <div className="glass-card p-4 text-sm space-y-2 border-white/10">
                                <div className="flex justify-between items-center">
                                    <span className="text-muted-foreground">Primary Hypothesis</span>
                                    <span className="font-mono text-primary">{log.intent} (0.92)</span>
                                </div>
                                <div className="flex justify-between items-center text-[10px] text-muted-foreground uppercase font-mono">
                                    <span>Secondary Match</span>
                                    <span>System_Default (0.05)</span>
                                </div>
                            </div>
                        </div>

                        <div className="space-y-3">
                            <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-widest flex items-center gap-2">
                                <span className="w-1.5 h-1.5 rounded-full bg-secondary animate-pulse" />
                                Layer 3: Intent Arbitration
                            </h3>
                            <div className="glass-card p-4 text-sm border-white/10 leading-relaxed">
                                <p>Deterministic selection of <strong className="text-secondary">{log.intent}</strong> validated against Expert Rule Engine constraint mapping.</p>
                            </div>
                        </div>

                        <div className="space-y-3">
                            <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-widest flex items-center gap-2">
                                <span className="w-1.5 h-1.5 rounded-full bg-destructive animate-pulse" />
                                Layer 4: RBAC & Policy Enforcement
                            </h3>
                            <div className={cn(
                                "p-4 rounded-lg border text-sm",
                                log.status === "BLOCKED" ? "bg-destructive/10 border-destructive/30" : "bg-secondary/10 border-secondary/30"
                            )}>
                                {log.status === "BLOCKED" ? (
                                    <div className="space-y-2">
                                        <p className="text-destructive font-bold flex items-center gap-2 uppercase text-xs">
                                            <ShieldAlert className="w-4 h-4" />
                                            Constraint Violation Detected
                                        </p>
                                        <p className="text-muted-foreground leading-relaxed">
                                            User ID <span className="text-white font-mono">{log.user}</span> attempted access to restricted intent <span className="text-white font-mono">{log.intent}</span>.
                                            Access denied by policy logic: <span className="text-primary font-mono">{log.reason}</span>.
                                        </p>
                                    </div>
                                ) : (
                                    <div className="space-y-2">
                                        <p className="text-secondary font-bold flex items-center gap-2 uppercase text-xs">
                                            <ShieldCheck className="w-4 h-4" />
                                            Authorization Verified
                                        </p>
                                        <p className="text-muted-foreground leading-relaxed">
                                            Identity confirmed and mapped to intent <span className="text-white font-mono">{log.intent}</span>.
                                            No active constraints found for this trace.
                                        </p>
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="space-y-3">
                            <h3 className="text-xs font-bold text-muted-foreground uppercase tracking-widest flex items-center gap-2">
                                <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
                                Layer 8: Final Reasoning Output
                            </h3>
                            <div className="bg-white/5 border border-white/10 p-4 rounded-lg text-sm font-mono text-white/80 leading-relaxed italic">
                                "{log.status === 'BLOCKED'
                                    ? `I am sorry, ${log.user}, but you are not authorized to access information regarding ${log.intent}. This action has been logged for security audit.`
                                    : `Verified access for ${log.user}. Processing retrieval context for ${log.intent} from primary knowledge sink...`}"
                            </div>
                        </div>
                    </div>
                </ScrollArea>
            </DialogContent>
        </Dialog>
    )
}
