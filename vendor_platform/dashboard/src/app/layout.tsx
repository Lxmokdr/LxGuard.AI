import type { Metadata } from "next"
import Link from "next/link"
import { LayoutDashboard, Users, Key, Monitor, Activity } from "lucide-react"
import LogoutButton from "../components/LogoutButton"
import "./globals.css"

export const metadata: Metadata = {
    title: "Vendor Control Dashboard",
    description: "Enterprise license management and monitoring",
}

const NAV = [
    { href: "/", label: "Dashboard", icon: LayoutDashboard },
    { href: "/customers", label: "Customers", icon: Users },
    { href: "/licenses", label: "Licenses", icon: Key },
    { href: "/instances", label: "Instances", icon: Monitor },
    { href: "/metrics", label: "Metrics", icon: Activity },
]

export default function RootLayout({ children }: { children: React.ReactNode }) {
    return (
        <html lang="en">
            <body className="bg-zinc-950 text-zinc-100 min-h-screen flex">
                <aside className="w-56 shrink-0 border-r border-white/5 bg-zinc-900 flex flex-col py-6">
                    <div className="px-5 mb-8">
                        <p className="text-xs font-mono text-indigo-400 uppercase tracking-widest">Vendor Console</p>
                        <p className="text-lg font-bold text-white mt-0.5">Control Panel</p>
                    </div>
                    <nav className="flex-1 space-y-1 px-3">
                        {NAV.map(({ href, label, icon: Icon }) => (
                            <Link key={href} href={href}
                                className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-zinc-400 hover:text-white hover:bg-white/5 transition-colors">
                                <Icon className="w-4 h-4" />{label}
                            </Link>
                        ))}
                    </nav>
                    <div className="px-3 mt-4">
                        <LogoutButton />
                    </div>
                </aside>
                <main className="flex-1 p-8 overflow-auto">{children}</main>
            </body>
        </html>
    )
}
