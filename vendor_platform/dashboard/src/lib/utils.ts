export const API = process.env.NEXT_PUBLIC_VENDOR_API_URL || "http://localhost:8002"

export function useAuth() {
    const token = typeof window !== "undefined" ? localStorage.getItem("vendor_token") : null
    return token
}

export async function apiFetch(path: string, token: string, opts: RequestInit = {}) {
    const res = await fetch(`${API}${path}`, {
        ...opts,
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json", ...opts.headers },
    })
    if (!res.ok) throw new Error(await res.text())
    return res.json()
}
