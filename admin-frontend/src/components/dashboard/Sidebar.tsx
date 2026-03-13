"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useMemo } from "react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
    LayoutDashboard,
    FileText,
    ShieldAlert,
    Database,
    Settings,
    Network,
    Brain,
    ShieldCheck,
    Users
} from "lucide-react"
import { motion } from "framer-motion"
import { useAuth } from "@/contexts/AuthContext"

export function Sidebar() {
    const pathname = usePathname()
    const { user, logout } = useAuth()

    const routes = useMemo(() => [
        { label: "Dashboard", icon: LayoutDashboard, href: "/dashboard" },
        { label: "Rules Engine", icon: ShieldAlert, href: "/rules" },
        { label: "Documents", icon: Database, href: "/documents" },
        { label: "Users", icon: ShieldCheck, href: "/users" },
        { label: "Audit Logs", icon: FileText, href: "/audit" },
        { label: "Database Explorer", icon: Database, href: "/database" },
        { label: "Monitoring", icon: Network, href: "/monitoring" },
        { label: "Knowledge Base", icon: Brain, href: "/knowledge" },
        { label: "Settings", icon: Settings, href: "/settings" },
    ], [])

    return (
        <div className="w-72 h-screen p-6 border-r border-border bg-card flex flex-col">
            <div className="mb-10 flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center">
                    <Brain className="w-6 h-6 text-primary-foreground" />
                </div>
                <div>
                    <h2 className="text-sm font-bold tracking-tight">
                        CORE ADMIN
                    </h2>
                    <p className="text-[10px] text-muted-foreground font-mono uppercase tracking-widest">
                        Hybrid Architecture
                    </p>
                </div>
            </div>

            <nav className="flex-1 space-y-2 px-2 overflow-y-auto custom-scrollbar">
                {routes.map((route) => (
                    <Link key={route.href} href={route.href}>
                        <Button
                            variant="ghost"
                            className={cn(
                                "w-full justify-start transition-all duration-200 gap-3 group relative",
                                pathname === route.href ? "bg-primary/10 text-primary" : "hover:bg-muted"
                            )}
                        >
                            <route.icon className={cn("h-4 w-4", pathname === route.href ? "text-primary" : "text-muted-foreground group-hover:text-primary")} />
                            <span className="font-medium">{route.label}</span>
                            {pathname === route.href && (
                                <motion.div
                                    layoutId="active-pill"
                                    className="absolute right-0 w-1 h-6 bg-primary rounded-l-full"
                                />
                            )}
                        </Button>
                    </Link>
                ))}
            </nav>

            <div className="mt-auto space-y-4">
                <div className="p-4 border border-border rounded-xl bg-muted/30 flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                        <Users className="w-4 h-4 text-primary" />
                    </div>
                    <div className="text-[10px] overflow-hidden">
                        <p className="font-semibold truncate">{user?.username || 'Admin User'}</p>
                        <p className="text-muted-foreground uppercase tracking-tighter">{user?.role || 'administrator'}</p>
                    </div>
                </div>

                <Button
                    variant="outline"
                    className="w-full border-red-500/20 text-red-500 hover:bg-red-500/10 hover:text-red-500 justify-start gap-3"
                    onClick={logout}
                >
                    <ShieldCheck className="w-4 h-4 rotate-180" />
                    <span>Logout Session</span>
                </Button>
            </div>
        </div>
    )
}
