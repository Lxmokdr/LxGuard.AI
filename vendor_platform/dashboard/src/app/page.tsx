"use client"
import { useState, useEffect } from "react"
import { Users, Key, Monitor, AlertTriangle, Activity, CheckCircle, XCircle } from "lucide-react"

const API = process.env.NEXT_PUBLIC_VENDOR_API_URL || "http://localhost:8002"

function useAuth() {
    const token = typeof window !== "undefined" ? localStorage.getItem("vendor_token") : null
    return token
}

async function apiFetch(path: string, token: string, opts: RequestInit = {}) {
    const res = await fetch(`${API}${path}`, {
        ...opts,
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json", ...opts.headers },
    })
    if (!res.ok) throw new Error(await res.text())
    return res.json()
}

export { useAuth, apiFetch }

export default function DashboardPage() {
    const token = useAuth()
    const [stats, setStats] = useState<any>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        if (!token) { window.location.href = "/login"; return }
        apiFetch("/admin/stats", token)
            .then(setStats)
            .catch(() => setStats(null))
            .finally(() => setLoading(false))
    }, [token])

    const cards = stats ? [
        { label: "Total Customers", value: stats.total_customers, icon: Users, color: "text-blue-400", bg: "bg-blue-500/10" },
        { label: "Active Licenses", value: stats.active_licenses, icon: Key, color: "text-emerald-400", bg: "bg-emerald-500/10" },
        { label: "Online Instances", value: stats.online_instances, icon: Monitor, color: "text-cyan-400", bg: "bg-cyan-500/10" },
        { label: "Total Instances", value: stats.total_instances, icon: Activity, color: "text-violet-400", bg: "bg-violet-500/10" },
    ] : []

    return (
        <div className="space-y-8">
            <div>
                <h1 className="text-3xl font-bold text-white">Vendor Control Dashboard</h1>
                <p className="text-zinc-400 text-sm mt-1">Centralized enterprise license management</p>
            </div>
            {loading ? (
                <div className="text-zinc-500 animate-pulse">Loading stats…</div>
            ) : (
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                    {cards.map(({ label, value, icon: Icon, color, bg }) => (
                        <div key={label} className="rounded-xl border border-white/5 bg-white/[0.03] p-5 flex items-center gap-4">
                            <div className={`p-3 rounded-lg ${bg}`}><Icon className={`w-5 h-5 ${color}`} /></div>
                            <div>
                                <p className="text-2xl font-bold text-white">{value ?? "—"}</p>
                                <p className="text-xs text-zinc-500">{label}</p>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}
