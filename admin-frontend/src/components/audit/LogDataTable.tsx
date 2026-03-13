"use client"

import { useEffect, useState } from "react"
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Eye, Loader2 } from "lucide-react"
import { api } from "@/lib/api"
import { cn } from "@/lib/utils"

export interface LogEntry {
    id: string
    time: string
    user: string
    intent: string
    status: "SUCCESS" | "BLOCKED" | "FAILURE"
    reason: string
}

interface LogDataTableProps {
    onViewDetail: (log: LogEntry) => void
}

export function LogDataTable({ onViewDetail }: LogDataTableProps) {
    const [logs, setLogs] = useState<LogEntry[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchLogs = async () => {
            try {
                const data = await api.getLogs()
                setLogs(data)
            } catch (error) {
                console.error("Failed to fetch logs:", error)
            } finally {
                setLoading(false)
            }
        }

        fetchLogs()
    }, [])

    return (
        <div className="rounded-md border border-white/5 bg-black/20 overflow-hidden">
            <Table>
                <TableHeader>
                    <TableRow className="border-white/10 hover:bg-transparent">
                        <TableHead className="text-muted-foreground font-mono text-[10px] uppercase">Timestamp</TableHead>
                        <TableHead className="text-muted-foreground font-mono text-[10px] uppercase">User Identity</TableHead>
                        <TableHead className="text-muted-foreground font-mono text-[10px] uppercase">Detected Intent</TableHead>
                        <TableHead className="text-muted-foreground font-mono text-[10px] uppercase">Outcome</TableHead>
                        <TableHead className="text-muted-foreground font-mono text-[10px] uppercase">Logic Code</TableHead>
                        <TableHead className="text-right text-muted-foreground font-mono text-[10px] uppercase">Trace</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {loading ? (
                        <TableRow>
                            <TableCell colSpan={6} className="text-center py-12">
                                <div className="flex flex-col items-center gap-3 text-muted-foreground">
                                    <Loader2 className="w-6 h-6 animate-spin text-primary" />
                                    <span className="font-mono text-xs uppercase tracking-widest">Querying Global Audit Sink...</span>
                                </div>
                            </TableCell>
                        </TableRow>
                    ) : logs.map((log) => (
                        <TableRow key={log.id} className="border-white/5 hover:bg-white/5 transition-colors group">
                            <TableCell className="font-mono text-xs text-muted-foreground">{log.time}</TableCell>
                            <TableCell className="font-medium">{log.user}</TableCell>
                            <TableCell>
                                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-primary/10 text-primary border border-primary/20">
                                    {log.intent?.toUpperCase()}
                                </span>
                            </TableCell>
                            <TableCell>
                                <Badge
                                    className={cn(
                                        "text-[10px] font-bold uppercase",
                                        log.status === "SUCCESS" ? "bg-secondary/20 text-secondary border-secondary/30 hover:bg-secondary/30" :
                                            log.status === "BLOCKED" ? "bg-destructive/20 text-destructive border-destructive/30 hover:bg-destructive/30" :
                                                "bg-muted text-muted-foreground border-border"
                                    )}
                                >
                                    {log.status}
                                </Badge>
                            </TableCell>
                            <TableCell className="font-mono text-[10px] text-muted-foreground">{log.reason}</TableCell>
                            <TableCell className="text-right">
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => onViewDetail(log)}
                                    className="hover:bg-primary/20 text-primary transition-all rounded-lg"
                                >
                                    <Eye className="h-4 w-4 mr-2" />
                                    Details
                                </Button>
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </div>
    )
}

