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
import { cn } from "@/lib/utils"
import { api } from "@/lib/api"

export function RecentAlerts() {
    const [logs, setLogs] = useState<any[]>([])
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
        <div className="space-y-4">
            <Table>
                <TableHeader>
                    <TableRow className="border-white/5 hover:bg-transparent">
                        <TableHead className="w-[100px] text-muted-foreground font-mono text-[10px] uppercase">ID</TableHead>
                        <TableHead className="text-muted-foreground font-mono text-[10px] uppercase">Time</TableHead>
                        <TableHead className="text-muted-foreground font-mono text-[10px] uppercase">User</TableHead>
                        <TableHead className="text-muted-foreground font-mono text-[10px] uppercase">Intent</TableHead>
                        <TableHead className="text-muted-foreground font-mono text-[10px] uppercase">Status</TableHead>
                        <TableHead className="text-right text-muted-foreground font-mono text-[10px] uppercase">Reason</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {loading ? (
                        <TableRow>
                            <TableCell colSpan={6} className="text-center py-8 text-muted-foreground font-mono text-xs">
                                SYNCING AUDIT TRACE...
                            </TableCell>
                        </TableRow>
                    ) : logs.map((log: any) => (
                        <TableRow key={log.id} className="border-white/5 hover:bg-white/5 transition-colors">
                            <TableCell className="font-mono text-xs">{log.id}</TableCell>
                            <TableCell className="text-xs text-muted-foreground">{log.time}</TableCell>
                            <TableCell className="text-sm font-medium">{log.user}</TableCell>
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
                            <TableCell className="text-right text-xs text-muted-foreground">{log.reason}</TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </div>
    )
}

