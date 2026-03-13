export const API = process.env.NEXT_PUBLIC_VENDOR_API_URL || "http://localhost:8002"

const SESSION_DURATION = 60 * 60 * 1000 // 1 hour

export function useAuth() {
    if (typeof window === "undefined") return null
    const token = localStorage.getItem("vendor_token")
    const loginTime = localStorage.getItem("vendor_login_time")

    if (!token || !loginTime || token === "null" || token === "undefined") return null

    // Check if session expired
    if (Date.now() - parseInt(loginTime) > SESSION_DURATION) {
        localStorage.removeItem("vendor_token")
        localStorage.removeItem("vendor_login_time")
        return null
    }

    return token
}

export async function apiFetch(path: string, token: string, opts: RequestInit = {}) {
    // Re-check session before fetching
    const loginTime = typeof window !== "undefined" ? localStorage.getItem("vendor_login_time") : null
    if (loginTime && Date.now() - parseInt(loginTime) > SESSION_DURATION) {
        localStorage.removeItem("vendor_token")
        localStorage.removeItem("vendor_login_time")
        if (typeof window !== "undefined") window.location.href = "/login"
        throw new Error("Session expired")
    }

    const res = await fetch(`${API}${path}`, {
        ...opts,
        headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
            ...opts.headers
        },
    })

    if (res.status === 401) {
        localStorage.removeItem("vendor_token")
        if (typeof window !== "undefined") window.location.href = "/login"
        throw new Error("Session expired. Please log in again.")
    }

    if (!res.ok) throw new Error(await res.text())
    return res.json()
}

