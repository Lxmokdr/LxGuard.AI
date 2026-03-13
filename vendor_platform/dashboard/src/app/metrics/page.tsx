"use client"
import { useState, useEffect } from "react"
import { useAuth, apiFetch } from "../../lib/utils"

export default function MetricsPage() {
    const token = useAuth()
    const [metrics, setMetrics] = useState<any[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        if (!token) { window.location.href = "/login"; return }
        apiFetch("/admin/metrics?limit=50", token)
            .then(setMetrics)
            .finally(() => setLoading(false))
    }, [token])

    // Group metrics by instance
    const byInstance: Record<string, any[]> = {}
    metrics.forEach(m => {
        const id = m.instance_id.slice(0, 12) + "…"
        if (!byInstance[id]) byInstance[id] = []
        byInstance[id].push(m)
    })

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-white">Metrics</h1>
            {loading ? <p className="text-zinc-500 animate-pulse">Loading…</p> : (
                <div className="space-y-8">
                    {Object.entries(byInstance).map(([id, rows]) => {
                        const latest = rows[0]
                        const totalQueries = rows.reduce((s, r) => s + r.query_count, 0)
                        const totalErrors = rows.reduce((s, r) => s + r.error_count, 0)
                        const avgUptime = Math.round(rows.reduce((s, r) => s + r.uptime, 0) / rows.length)

                        return (
                            <div key={id} className="rounded-xl border border-white/5 bg-white/[0.03] p-5 space-y-4">
                                <div className="flex items-center justify-between">
                                    <p className="font-mono text-sm text-zinc-400">Instance: <span className="text-white">{id}</span></p>
                                    <p className="text-xs text-zinc-600">{rows.length} data points</p>
                                </div>
                                <div className="grid grid-cols-3 gap-4">
                                    <Stat label="Total Queries" value={totalQueries} color="text-cyan-400" />
                                    <Stat label="Total Errors" value={totalErrors} color="text-red-400" />
                                    <Stat label="Avg Uptime" value={`${Math.round(avgUptime / 3600)}h`} color="text-emerald-400" />
                                </div>
                                {/* Mini sparkline */}
                                <div className="flex items-end gap-0.5 h-10">
                                    {rows.slice(0, 30).reverse().map((r, i) => {
                                        const maxQ = Math.max(...rows.map(x => x.query_count), 1)
                                        const h = Math.max(2, Math.round((r.query_count / maxQ) * 40))
                                        return <div key={i} style={{ height: h }} className="flex-1 bg-cyan-500/40 rounded-t" />
                                    })}
                                </div>
                                <p className="text-xs text-zinc-600">Query volume over last {rows.length} heartbeats</p>
                            </div>
                        )
                    })}
                    {Object.keys(byInstance).length === 0 && (
                        <p className="text-zinc-600 text-sm">No metrics yet. Enterprise instances send heartbeats every 5 minutes.</p>
                    )}
                </div>
            )}
        </div>
    )
}

function Stat({ label, value, color }: { label: string; value: any; color: string }) {
    return (
        <div>
            <p className={`text-xl font-bold ${color}`}>{value}</p>
            <p className="text-xs text-zinc-500">{label}</p>
        </div>
    )
}
