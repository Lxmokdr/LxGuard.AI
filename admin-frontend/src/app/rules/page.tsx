"use client";

import { useState, useEffect } from "react";
import { Plus, Search, Filter, Play, Power, PowerOff, Edit, Trash2 } from "lucide-react";
import { api } from "@/lib/api";
import type { Rule } from "@/lib/types";

export default function RulesPage() {
    const [rules, setRules] = useState<Rule[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState("");
    const [filterStatus, setFilterStatus] = useState<"all" | "active" | "inactive">("all");

    useEffect(() => {
        loadRules();
    }, []);

    const loadRules = async () => {
        try {
            const data = await api.rules.getAll();
            setRules(Array.isArray(data) ? data : data.data || []);
        } catch (error) {
            console.error("Failed to load rules:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleToggleStatus = async (id: string, currentStatus: boolean) => {
        try {
            await api.rules.toggleStatus(id, !currentStatus);
            await loadRules();
        } catch (error) {
            console.error("Failed to toggle rule status:", error);
        }
    };

    const handleDelete = async (id: string) => {
        if (!confirm("Are you sure you want to delete this rule?")) return;
        try {
            await api.rules.delete(id);
            await loadRules();
        } catch (error) {
            console.error("Failed to delete rule:", error);
        }
    };

    const filteredRules = rules.filter((rule) => {
        const matchesSearch =
            (rule.id || "").toLowerCase().includes(searchTerm.toLowerCase()) ||
            (rule.name || "").toLowerCase().includes(searchTerm.toLowerCase()) ||
            (rule.description || "").toLowerCase().includes(searchTerm.toLowerCase()) ||
            (rule.test_query || "").toLowerCase().includes(searchTerm.toLowerCase());
        const matchesFilter =
            filterStatus === "all" ||
            (filterStatus === "active" && rule.active) ||
            (filterStatus === "inactive" && !rule.active);
        return matchesSearch && matchesFilter;
    });

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-muted-foreground">Loading rules...</div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Rule Management</h1>
                    <p className="text-muted-foreground mt-1">
                        Manage production rules for intent handling and document filtering
                    </p>
                </div>
                <button
                    onClick={() => (window.location.href = "/rules/new")}
                    className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
                >
                    <Plus className="w-4 h-4" />
                    Create Rule
                </button>
            </div>

            {/* Filters */}
            <div className="flex gap-4">
                <div className="flex-1 relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                    <input
                        type="text"
                        placeholder="Search rules by name, ID, description or test query..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 bg-card border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                </div>
                <select
                    value={filterStatus}
                    onChange={(e) => setFilterStatus(e.target.value as any)}
                    className="px-4 py-2 bg-card border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                >
                    <option value="all">All Rules</option>
                    <option value="active">Active Only</option>
                    <option value="inactive">Inactive Only</option>
                </select>
            </div>

            {/* Rules List */}
            <div className="space-y-4">
                {filteredRules.length === 0 ? (
                    <div className="text-center py-12 bg-card rounded-lg border border-border">
                        <p className="text-muted-foreground">No rules found</p>
                    </div>
                ) : (
                    filteredRules.map((rule) => (
                        <div
                            key={rule.id}
                            className="bg-card border border-border rounded-lg p-6 hover:border-primary/50 transition-colors"
                        >
                            <div className="flex items-start justify-between">
                                <div className="flex-1">
                                    <div className="flex items-center gap-3">
                                        <h3 className="text-xl font-bold text-primary">{rule.name || rule.id}</h3>
                                        {rule.name && <span className="text-xs font-mono text-muted-foreground bg-white/5 px-2 py-0.5 rounded">ID: {rule.id}</span>}
                                        <span
                                            className={`px-2 py-1 rounded text-xs font-medium ${rule.active
                                                ? "bg-green-500/20 text-green-400"
                                                : "bg-gray-500/20 text-gray-400"
                                                }`}
                                        >
                                            {rule.active ? "Active" : "Inactive"}
                                        </span>
                                        <span className="px-2 py-1 rounded text-xs font-medium bg-blue-500/20 text-blue-400">
                                            Priority: {rule.priority}
                                        </span>
                                    </div>
                                    <p className="text-muted-foreground mt-2">{rule.description}</p>
                                    <div className="mt-4 flex flex-wrap gap-4 text-sm">
                                        {rule.triggers && rule.triggers.length > 0 && (
                                            <div>
                                                <span className="text-muted-foreground font-medium">Triggers:</span>{" "}
                                                <span className="text-foreground">{rule.triggers.join(", ")}</span>
                                            </div>
                                        )}
                                        {rule.trigger_keywords && rule.trigger_keywords.length > 0 && (
                                            <div>
                                                <span className="text-muted-foreground font-medium">Keywords:</span>{" "}
                                                <span className="text-foreground">{rule.trigger_keywords.join(", ")}</span>
                                            </div>
                                        )}
                                        {rule.test_query && (
                                            <div className="w-full mt-1 p-2 bg-white/5 rounded italic text-muted-foreground border-l-2 border-primary/30">
                                                <span className="not-italic font-medium text-xs uppercase tracking-wider block mb-1">Test Query:</span>
                                                "{rule.test_query}"
                                            </div>
                                        )}
                                    </div>
                                </div>
                                <div className="flex items-center gap-2">
                                    <button
                                        onClick={() => (window.location.href = `/rules/${rule.id}/test`)}
                                        className="p-2 hover:bg-accent rounded-lg transition-colors"
                                        title="Test Rule"
                                    >
                                        <Play className="w-4 h-4" />
                                    </button>
                                    <button
                                        onClick={() => (window.location.href = `/rules/${rule.id}`)}
                                        className="p-2 hover:bg-accent rounded-lg transition-colors"
                                        title="Edit Rule"
                                    >
                                        <Edit className="w-4 h-4" />
                                    </button>
                                    <button
                                        onClick={() => handleToggleStatus(rule.id, rule.active)}
                                        className="p-2 hover:bg-accent rounded-lg transition-colors"
                                        title={rule.active ? "Deactivate" : "Activate"}
                                    >
                                        {rule.active ? (
                                            <PowerOff className="w-4 h-4 text-orange-400" />
                                        ) : (
                                            <Power className="w-4 h-4 text-green-400" />
                                        )}
                                    </button>
                                    <button
                                        onClick={() => handleDelete(rule.id)}
                                        className="p-2 hover:bg-destructive/20 rounded-lg transition-colors"
                                        title="Delete Rule"
                                    >
                                        <Trash2 className="w-4 h-4 text-destructive" />
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4">
                <div className="bg-card border border-border rounded-lg p-4">
                    <div className="text-2xl font-bold">{rules.length}</div>
                    <div className="text-sm text-muted-foreground">Total Rules</div>
                </div>
                <div className="bg-card border border-border rounded-lg p-4">
                    <div className="text-2xl font-bold text-green-400">
                        {rules.filter((r) => r.active).length}
                    </div>
                    <div className="text-sm text-muted-foreground">Active Rules</div>
                </div>
                <div className="bg-card border border-border rounded-lg p-4">
                    <div className="text-2xl font-bold text-gray-400">
                        {rules.filter((r) => !r.active).length}
                    </div>
                    <div className="text-sm text-muted-foreground">Inactive Rules</div>
                </div>
            </div>
        </div>
    );
}
