"use client"
import { useState } from "react"
import { useRouter } from "next/navigation"

const API = process.env.NEXT_PUBLIC_VENDOR_API_URL || "http://localhost:8002"

export default function LoginPage() {
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("")
    const [error, setError] = useState("")
    const router = useRouter()

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault()
        setError("")
        const form = new URLSearchParams()
        form.append("username", email)
        form.append("password", password)
        try {
            const res = await fetch(`${API}/admin/auth/login`, {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: form.toString(),
            })
            if (!res.ok) throw new Error("Invalid credentials")
            const data = await res.json()
            localStorage.setItem("vendor_token", data.access_token)
            localStorage.setItem("vendor_login_time", Date.now().toString())
            router.push("/")
        } catch (err: any) {
            setError(err.message)
        }
    }

    return (
        <div className="min-h-screen bg-zinc-950 flex items-center justify-center">
            <form onSubmit={handleLogin} className="w-full max-w-sm bg-zinc-900 border border-white/10 rounded-2xl p-8 space-y-5">
                <div>
                    <h1 className="text-2xl font-bold text-white">LxGuard.AI Vendor Console</h1>
                    <p className="text-zinc-500 text-sm mt-1">Sign in to manage enterprise licenses</p>
                </div>
                {error && <div className="bg-red-500/10 text-red-400 border border-red-500/20 rounded p-3 text-sm">{error}</div>}
                <input
                    type="email" value={email} onChange={e => setEmail(e.target.value)} required
                    placeholder="admin@vendor.com"
                    className="w-full bg-zinc-800 border border-white/10 rounded-lg px-4 py-2.5 text-white text-sm placeholder-zinc-500 focus:outline-none focus:border-indigo-500"
                />
                <input
                    type="password" value={password} onChange={e => setPassword(e.target.value)} required
                    placeholder="Password"
                    className="w-full bg-zinc-800 border border-white/10 rounded-lg px-4 py-2.5 text-white text-sm placeholder-zinc-500 focus:outline-none focus:border-indigo-500"
                />
                <button type="submit" className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-lg py-2.5 transition-colors">
                    Sign In
                </button>
            </form>
        </div>
    )
}
