"use client";

import { useState, useEffect } from "react";
import { Activity, FileText, ShieldAlert, Users, Database, TrendingUp } from "lucide-react";
import Link from "next/link";
import { api } from "@/lib/api";

export default function DashboardPage() {
    const [stats, setStats] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadStats();
    }, []);

    const loadStats = async () => {
        try {
            const data = await api.getStats();
            setStats(data);
        } catch (error) {
            console.error("Failed to load stats:", error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-muted-foreground">Loading dashboard...</div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold">Admin Dashboard</h1>
                <p className="text-muted-foreground mt-1">
                    LxGuard.AI System - Governance & Operations Control
                </p>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-card border border-border rounded-xl p-6 hover:shadow-md transition-all">
                    <div className="flex items-center justify-between mb-4">
                        <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                            <ShieldAlert className="w-6 h-6 text-primary" />
                        </div>
                    </div>
                    <div className="text-3xl font-bold">{stats?.total_rules || 0}</div>
                    <div className="text-sm text-muted-foreground mt-1">Production Rules</div>
                    <Link href="/rules" className="text-xs text-primary hover:underline mt-2 inline-block">
                        Manage Rules →
                    </Link>
                </div>

                <div className="bg-card border border-border rounded-xl p-6 hover:shadow-md transition-all">
                    <div className="flex items-center justify-between mb-4">
                        <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                            <Database className="w-6 h-6 text-primary" />
                        </div>
                    </div>
                    <div className="text-3xl font-bold">{stats?.total_documents || 0}</div>
                    <div className="text-sm text-muted-foreground mt-1">Knowledge Documents</div>
                    <Link href="/documents" className="text-xs text-primary hover:underline mt-2 inline-block">
                        Manage Documents →
                    </Link>
                </div>

                <div className="bg-card border border-border rounded-xl p-6 hover:shadow-md transition-all">
                    <div className="flex items-center justify-between mb-4">
                        <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                            <Users className="w-6 h-6 text-primary" />
                        </div>
                    </div>
                    <div className="text-3xl font-bold">{stats?.total_users || 0}</div>
                    <div className="text-sm text-muted-foreground mt-1">Active Users</div>
                    <Link href="/users" className="text-xs text-primary hover:underline mt-2 inline-block">
                        Manage Users →
                    </Link>
                </div>

                <div className="bg-card border border-border rounded-xl p-6 hover:shadow-md transition-all">
                    <div className="flex items-center justify-between mb-4">
                        <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                            <FileText className="w-6 h-6 text-primary" />
                        </div>
                    </div>
                    <div className="text-3xl font-bold">{stats?.total_queries || 0}</div>
                    <div className="text-sm text-muted-foreground mt-1">Total Queries</div>
                    <Link href="/audit" className="text-xs text-primary hover:underline mt-2 inline-block">
                        View Audit Logs →
                    </Link>
                </div>
            </div>

            {/* Quick Actions */}
            <div>
                <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <Link
                        href="/rules/new"
                        className="bg-card border border-border rounded-xl p-6 hover:shadow-md transition-all group"
                    >
                        <div className="flex items-center gap-3 mb-2">
                            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                                <ShieldAlert className="w-5 h-5 text-primary" />
                            </div>
                            <h3 className="font-semibold">Create New Rule</h3>
                        </div>
                        <p className="text-sm text-muted-foreground">
                            Add a new production rule for intent handling
                        </p>
                    </Link>

                    <Link
                        href="/documents"
                        className="bg-card border border-border rounded-xl p-6 hover:shadow-md transition-all group"
                    >
                        <div className="flex items-center gap-3 mb-2">
                            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                                <Database className="w-5 h-5 text-primary" />
                            </div>
                            <h3 className="font-semibold">Upload Document</h3>
                        </div>
                        <p className="text-sm text-muted-foreground">
                            Add new documents to the knowledge base
                        </p>
                    </Link>

                    <Link
                        href="/monitoring"
                        className="bg-card border border-border rounded-xl p-6 hover:shadow-md transition-all group"
                    >
                        <div className="flex items-center gap-3 mb-2">
                            <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                                <Activity className="w-5 h-5 text-primary" />
                            </div>
                            <h3 className="font-semibold">System Health</h3>
                        </div>
                        <p className="text-sm text-muted-foreground">
                            Monitor system performance and health
                        </p>
                    </Link>
                </div>
            </div>

            {/* System Status */}
            <div>
                <h2 className="text-xl font-semibold mb-4">System Status</h2>
                <div className="bg-card border border-border rounded-lg p-6">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                        <div>
                            <div className="text-sm text-muted-foreground mb-1">Active Rules</div>
                            <div className="text-2xl font-bold">{stats?.active_rules || 0}</div>
                        </div>
                        <div>
                            <div className="text-sm text-muted-foreground mb-1">Avg Response Time</div>
                            <div className="text-2xl font-bold">{stats?.avg_response_time || "—"}</div>
                        </div>
                        <div>
                            <div className="text-sm text-muted-foreground mb-1">Cache Hit Rate</div>
                            <div className="text-2xl font-bold">{stats?.cache_hit_rate || "—"}</div>
                        </div>
                        <div>
                            <div className="text-sm text-muted-foreground mb-1">Error Rate</div>
                            <div className="text-2xl font-bold">{stats?.error_rate || "—"}</div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Recent Activity */}
            <div>
                <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
                <div className="bg-card border border-border rounded-lg p-6">
                    <div className="text-sm text-muted-foreground text-center py-8">
                        Recent activity will appear here
                    </div>
                </div>
            </div>
        </div>
    );
}
