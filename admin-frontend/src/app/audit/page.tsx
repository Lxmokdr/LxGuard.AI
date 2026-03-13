"use client";

import { useState, useEffect } from "react";
import { Search, Download, Eye, Filter, Calendar } from "lucide-react";
import { api } from "@/lib/api";
import type { AuditLog } from "@/lib/types";

export default function AuditPage() {
    const [logs, setLogs] = useState<AuditLog[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState("");
    const [filterDecision, setFilterDecision] = useState<"all" | "approved" | "rejected" | "flagged">("all");
    const [selectedTrace, setSelectedTrace] = useState<any>(null);

    useEffect(() => {
        loadLogs();
        // Auto-refresh every 5 seconds
        const interval = setInterval(loadLogs, 5000);
        return () => clearInterval(interval);
    }, []);

    const loadLogs = async () => {
        try {
            const data = await api.audit.getLogs();
            setLogs(data.data?.items || []);
        } catch (error) {
            console.error("Failed to load audit logs:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleViewTrace = async (traceId: string) => {
        try {
            const trace = await api.audit.getTrace(traceId);
            setSelectedTrace(trace.data);
        } catch (error) {
            console.error("Failed to load trace:", error);
        }
    };

    const handleExport = async () => {
        try {
            const blob = await api.audit.export({ format: "csv" });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `audit-logs-${new Date().toISOString()}.csv`;
            a.click();
        } catch (error) {
            console.error("Failed to export logs:", error);
        }
    };

    const filteredLogs = logs.filter((log) => {
        const matchesSearch =
            log.query.toLowerCase().includes(searchTerm.toLowerCase()) ||
            log.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
            log.intent.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesFilter = filterDecision === "all" || log.decision === filterDecision;
        return matchesSearch && matchesFilter;
    });

    const getDecisionBadge = (decision: string) => {
        switch (decision) {
            case "approved":
                return "bg-green-500/20 text-green-400";
            case "rejected":
                return "bg-red-500/20 text-red-400";
            case "flagged":
                return "bg-yellow-500/20 text-yellow-400";
            default:
                return "bg-gray-500/20 text-gray-400";
        }
    };

    const getRiskBadge = (risk: string) => {
        switch (risk) {
            case "low":
                return "bg-blue-500/20 text-blue-400";
            case "medium":
                return "bg-yellow-500/20 text-yellow-400";
            case "high":
                return "bg-orange-500/20 text-orange-400";
            case "critical":
                return "bg-red-500/20 text-red-400";
            default:
                return "bg-gray-500/20 text-gray-400";
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-muted-foreground">Loading audit logs...</div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Audit Logs</h1>
                    <p className="text-muted-foreground mt-1">
                        Complete audit trail of all system queries and decisions
                    </p>
                </div>
                <button
                    onClick={handleExport}
                    className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
                >
                    <Download className="w-4 h-4" />
                    Export Logs
                </button>
            </div>

            {/* Filters */}
            <div className="flex gap-4">
                <div className="flex-1 relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <input
                        type="text"
                        placeholder="Search by query, user, or intent..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 bg-card border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                </div>
                <select
                    value={filterDecision}
                    onChange={(e) => setFilterDecision(e.target.value as any)}
                    className="px-4 py-2 bg-card border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                >
                    <option value="all">All Decisions</option>
                    <option value="approved">Approved</option>
                    <option value="rejected">Rejected</option>
                    <option value="flagged">Flagged</option>
                </select>
            </div>

            {/* Logs Table */}
            <div className="bg-card border border-border rounded-lg overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-accent">
                            <tr>
                                <th className="px-4 py-3 text-left text-sm font-semibold">Timestamp</th>
                                <th className="px-4 py-3 text-left text-sm font-semibold">User</th>
                                <th className="px-4 py-3 text-left text-sm font-semibold">Query</th>
                                <th className="px-4 py-3 text-left text-sm font-semibold">Intent</th>
                                <th className="px-4 py-3 text-left text-sm font-semibold">Decision</th>
                                <th className="px-4 py-3 text-left text-sm font-semibold">Risk</th>
                                <th className="px-4 py-3 text-left text-sm font-semibold">Time</th>
                                <th className="px-4 py-3 text-right text-sm font-semibold">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-border">
                            {filteredLogs.length === 0 ? (
                                <tr>
                                    <td colSpan={8} className="px-4 py-8 text-center text-muted-foreground">
                                        No audit logs found
                                    </td>
                                </tr>
                            ) : (
                                filteredLogs.map((log) => (
                                    <tr key={log.id} className="hover:bg-accent/50 transition-colors">
                                        <td className="px-4 py-3 text-sm">
                                            {new Date(log.timestamp).toLocaleString()}
                                        </td>
                                        <td className="px-4 py-3">
                                            <div>
                                                <div className="font-medium text-sm">{log.username}</div>
                                                <div className="text-xs text-muted-foreground">{log.user_role}</div>
                                            </div>
                                        </td>
                                        <td className="px-4 py-3 max-w-xs">
                                            <div className="text-sm truncate" title={log.query}>
                                                {log.query}
                                            </div>
                                        </td>
                                        <td className="px-4 py-3">
                                            <span className="text-sm font-medium">{log.intent}</span>
                                        </td>
                                        <td className="px-4 py-3">
                                            <span className={`px-2 py-1 rounded text-xs font-medium ${getDecisionBadge(log.decision)}`}>
                                                {log.decision}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3">
                                            <span className={`px-2 py-1 rounded text-xs font-medium ${getRiskBadge(log.security_check?.risk_level || "unknown")}`}>
                                                {log.security_check?.risk_level || "unknown"}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3 text-sm text-muted-foreground">
                                            {log.performance.total_time_ms}ms
                                        </td>
                                        <td className="px-4 py-3">
                                            <div className="flex items-center justify-end">
                                                <button
                                                    onClick={() => handleViewTrace(log.trace_id)}
                                                    className="p-2 hover:bg-accent rounded-lg transition-colors"
                                                    title="View Trace"
                                                >
                                                    <Eye className="w-4 h-4" />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Trace Modal */}
            {selectedTrace && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <div className="bg-card border border-border rounded-lg w-full max-w-4xl max-h-[80vh] overflow-y-auto">
                        <div className="sticky top-0 bg-card border-b border-border p-4 flex items-center justify-between">
                            <h2 className="text-xl font-bold">Reasoning Trace</h2>
                            <button
                                onClick={() => setSelectedTrace(null)}
                                className="px-4 py-2 bg-accent rounded-lg hover:bg-accent/80 transition-colors"
                            >
                                Close
                            </button>
                        </div>
                        <div className="p-4">
                            <pre className="text-xs bg-background p-4 rounded-lg overflow-x-auto">
                                {JSON.stringify(selectedTrace, null, 2)}
                            </pre>
                        </div>
                    </div>
                </div>
            )}

            {/* Stats */}
            <div className="grid grid-cols-4 gap-4">
                <div className="bg-card border border-border rounded-lg p-4">
                    <div className="text-2xl font-bold">{logs.length}</div>
                    <div className="text-sm text-muted-foreground">Total Queries</div>
                </div>
                <div className="bg-card border border-border rounded-lg p-4">
                    <div className="text-2xl font-bold text-green-400">
                        {logs.filter((l) => l.decision === "approved").length}
                    </div>
                    <div className="text-sm text-muted-foreground">Approved</div>
                </div>
                <div className="bg-card border border-border rounded-lg p-4">
                    <div className="text-2xl font-bold text-red-400">
                        {logs.filter((l) => l.decision === "rejected").length}
                    </div>
                    <div className="text-sm text-muted-foreground">Rejected</div>
                </div>
                <div className="bg-card border border-border rounded-lg p-4">
                    <div className="text-2xl font-bold text-yellow-400">
                        {logs.filter((l) => l.decision === "flagged").length}
                    </div>
                    <div className="text-sm text-muted-foreground">Flagged</div>
                </div>
            </div>
        </div>
    );
}
