"use client"
import { useState, useEffect } from "react"
import { useAuth, apiFetch } from "../page"
import { Plus, Ban,Trash2, CheckCircle, Copy } from "lucide-react"

export default function LicensesPage() {
    const token = useAuth()
    const [licenses, setLicenses] = useState<any[]>([])
    const [customers, setCustomers] = useState<any[]>([])
    const [loading, setLoading] = useState(true)
    const [custId, setCustId] = useState("")
    const [expires, setExpires] = useState("")
    const [maxInst, setMaxInst] = useState("3")
    const [copiedId, setCopiedId] = useState<string | null>(null)

    const load = async () => {
        const [l, c] = await Promise.all([apiFetch("/admin/licenses", token!), apiFetch("/admin/customers", token!)])
        setLicenses(l); setCustomers(c); setLoading(false)
    }
    useEffect(() => { if (!token) { window.location.href = "/login"; return }; load() }, [token])

    const create = async (e: React.FormEvent) => {
        e.preventDefault()
        await apiFetch("/admin/licenses", token!, { method: "POST", body: JSON.stringify({ customer_id: custId, expires_at: expires || null, max_instances: parseInt(maxInst) }) })
        load()
    }

    const setStatus = async (id: string, status: string) => {
        await apiFetch(`/admin/licenses/${id}`, token!, { method: "PUT", body: JSON.stringify({ status }) }); load()
    }

    const deleteLic = async (id: string) => {
        if (!confirm("Delete this license?")) return
        await apiFetch(`/admin/licenses/${id}`, token!, { method: "DELETE" }); load()
    }

    const statusBadge = (s: string) =>
        s === "active" ? <span className="px-2 py-0.5 rounded-full text-xs bg-emerald-500/10 text-emerald-400">Active</span>
            : s === "revoked" ? <span className="px-2 py-0.5 rounded-full text-xs bg-red-500/10 text-red-400">Revoked</span>
                : <span className="px-2 py-0.5 rounded-full text-xs bg-amber-500/10 text-amber-400">Expired</span>

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-white">Licenses</h1>
            <form onSubmit={create} className="flex gap-3 flex-wrap items-end">
                <div className="flex flex-col gap-1">
                    <label className="text-xs text-zinc-500">Customer</label>
                    <select required value={custId} onChange={e => setCustId(e.target.value)} className="input-field">
                        <option value="">— Select —</option>
                        {customers.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                    </select>
                </div>
                <div className="flex flex-col gap-1">
                    <label className="text-xs text-zinc-500">Expires At</label>
                    <input type="date" value={expires} onChange={e => setExpires(e.target.value)} className="input-field" />
                </div>
                <div className="flex flex-col gap-1">
                    <label className="text-xs text-zinc-500">Max Instances</label>
                    <input type="number" min="1" value={maxInst} onChange={e => setMaxInst(e.target.value)} className="input-field w-24" />
                </div>
                <button type="submit" className="btn-primary gap-2 flex items-center"><Plus className="w-4 h-4" />Create</button>
            </form>

            {loading ? <p className="text-zinc-500 animate-pulse">Loading…</p> : (
                <table className="w-full text-sm">
                    <thead><tr className="text-zinc-500 border-b border-white/5 text-left">
                        <th className="pb-3">License Key</th><th>Customer</th><th>Status</th><th>Expires</th><th>Instances</th><th>Actions</th>
                    </tr></thead>
                    <tbody className="divide-y divide-white/5">
                        {licenses.map(l => (
                            <tr key={l.id} className="text-zinc-300">
                                <td className="py-3 font-mono text-xs text-zinc-400 flex items-center gap-2">
                                    {l.license_key.slice(0, 16)}…
                                    <button
                                        onClick={() => {
                                            navigator.clipboard.writeText(l.license_key);
                                            setCopiedId(l.id);
                                            setTimeout(() => setCopiedId(null), 2000);
                                        }}
                                        title="Copy License Key"
                                        className={`${copiedId === l.id ? "text-emerald-400" : "text-zinc-500 hover:text-white"} transition-colors p-1`}
                                    >
                                        {copiedId === l.id ? <CheckCircle className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                                    </button>
                                </td>
                                <td className="text-white">{l.customer_name}</td>
                                <td>{statusBadge(l.status)}</td>
                                <td>{l.expires_at ? new Date(l.expires_at).toLocaleDateString() : "∞"}</td>
                                <td>{l.instance_count} / {l.max_instances}</td>
                                <td className="flex gap-2 py-3">
                                    {l.status === "active"
                                        ? <button onClick={() => setStatus(l.id, "revoked")} title="Revoke" className="text-red-400 hover:text-red-300"><Ban className="w-4 h-4" /></button>
                                        : <button onClick={() => setStatus(l.id, "active")} title="Restore" className="text-emerald-400 hover:text-emerald-300"><CheckCircle className="w-4 h-4" /></button>
                                    }
                                    <button onClick={() => deleteLic(l.id)} title="Delete" className="text-zinc-500 hover:text-red-400"><Trash2 className="w-4 h-4" /></button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    )
}
