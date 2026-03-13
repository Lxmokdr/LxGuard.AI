"use client"
import { useState, useEffect } from "react"
import { useAuth, apiFetch } from "../../lib/utils"
import { Circle, Ban } from "lucide-react"

export default function InstancesPage() {
    const token = useAuth()
    const [instances, setInstances] = useState<any[]>([])
    const [loading, setLoading] = useState(true)

    const load = () => apiFetch("/admin/instances", token!).then(setInstances).finally(() => setLoading(false))
    useEffect(() => {
        if (!token) {
            window.location.href = "/login"
            return
        }
        load()
    }, [token])

    const disable = async (id: string) => {
        if (!confirm(`Disable instance ${id}? This will revoke its license.`)) return
        await apiFetch(`/admin/instances/${id}/disable`, token!, { method: "POST" }); load()
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-white">Instances</h1>
                <button onClick={load} className="text-xs text-zinc-500 hover:text-zinc-300 border border-white/10 rounded px-3 py-1.5">Refresh</button>
            </div>
            {loading ? <p className="text-zinc-500 animate-pulse">Loading…</p> : (
                <table className="w-full text-sm">
                    <thead><tr className="text-zinc-500 border-b border-white/5 text-left">
                        <th className="pb-3">Status</th><th>Instance ID</th><th>Hostname</th><th>Version</th><th>Last Seen</th><th>Actions</th>
                    </tr></thead>
                    <tbody className="divide-y divide-white/5">
                        {instances.map(i => (
                            <tr key={i.id} className="text-zinc-300">
                                <td className="py-3">
                                    <Circle className={`w-3 h-3 fill-current ${i.online ? "text-emerald-400" : "text-zinc-600"}`} />
                                </td>
                                <td className="font-mono text-xs text-zinc-400">{i.instance_id.slice(0, 16)}…</td>
                                <td className="text-white">{i.hostname || "—"}</td>
                                <td>{i.version || "—"}</td>
                                <td className="text-zinc-500 text-xs">{i.last_seen ? new Date(i.last_seen).toLocaleString() : "Never"}</td>
                                <td>
                                    {i.status !== "disabled" && (
                                        <button onClick={() => disable(i.instance_id)} title="Disable instance" className="text-red-400 hover:text-red-300 flex items-center gap-1 text-xs">
                                            <Ban className="w-3 h-3" /> Disable
                                        </button>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    )
}
