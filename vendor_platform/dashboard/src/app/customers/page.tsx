"use client"
import { useState, useEffect } from "react"
import { useAuth, apiFetch } from "../../lib/utils"
import { Plus, Trash2 } from "lucide-react"

export default function CustomersPage() {
    const token = useAuth()
    const [customers, setCustomers] = useState<any[]>([])
    const [loading, setLoading] = useState(true)
    const [name, setName] = useState("")
    const [email, setEmail] = useState("")
    const [orgType, setOrgType] = useState("enterprise")
    const [saving, setSaving] = useState(false)

    const load = () => apiFetch("/admin/customers", token!).then(setCustomers).finally(() => setLoading(false))
    useEffect(() => { if (!token) { window.location.href = "/login"; return }; load() }, [token])

    const create = async (e: React.FormEvent) => {
        e.preventDefault(); setSaving(true)
        await apiFetch("/admin/customers", token!, { method: "POST", body: JSON.stringify({ name, contact_email: email, organization_type: orgType }) })
        setName(""); setEmail(""); setSaving(false); load()
    }

    const remove = async (id: string) => {
        if (!confirm("Delete this customer and all their licenses?")) return
        await apiFetch(`/admin/customers/${id}`, token!, { method: "DELETE" }); load()
    }

    return (
        <div className="space-y-6">
            <h1 className="text-2xl font-bold text-white">Customers</h1>
            <form onSubmit={create} className="flex gap-3 flex-wrap">
                <input required placeholder="Company name" value={name} onChange={e => setName(e.target.value)} className="input-field" />
                <input required type="email" placeholder="Contact email" value={email} onChange={e => setEmail(e.target.value)} className="input-field" />
                <select value={orgType} onChange={e => setOrgType(e.target.value)} className="input-field">
                    <option value="enterprise">Enterprise</option>
                    <option value="smb">SMB</option>
                    <option value="government">Government</option>
                </select>
                <button type="submit" disabled={saving} className="btn-primary gap-2 flex items-center"><Plus className="w-4 h-4" />Add Customer</button>
            </form>
            {loading ? <p className="text-zinc-500 animate-pulse">Loading…</p> : (
                <table className="w-full text-sm">
                    <thead><tr className="text-zinc-500 border-b border-white/5 text-left">
                        <th className="pb-3">Name</th><th>Email</th><th>Type</th><th>Licenses</th><th></th>
                    </tr></thead>
                    <tbody className="divide-y divide-white/5">
                        {customers.map(c => (
                            <tr key={c.id} className="text-zinc-300">
                                <td className="py-3 font-medium text-white">{c.name}</td>
                                <td>{c.contact_email}</td>
                                <td><span className="px-2 py-0.5 rounded-full text-xs bg-indigo-500/10 text-indigo-400">{c.organization_type}</span></td>
                                <td>{c.license_count}</td>
                                <td><button onClick={() => remove(c.id)} className="text-red-400 hover:text-red-300 p-1"><Trash2 className="w-4 h-4" /></button></td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    )
}
