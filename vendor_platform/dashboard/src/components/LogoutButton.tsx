"use client"
import { LogOut } from "lucide-react"

export default function LogoutButton() {
    return (
        <button onClick={() => { localStorage.removeItem("vendor_token"); window.location.href = "/login" }}
            className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-zinc-500 hover:text-red-400 w-full transition-colors">
            <LogOut className="w-4 h-4" />Sign out
        </button>
    )
}
