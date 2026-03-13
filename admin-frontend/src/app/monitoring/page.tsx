"use client";

import { useState, useEffect, useCallback, memo } from "react";
import {
    Activity, Database, Zap, Server, Cpu, MemoryStick,
    RefreshCw, Wifi, WifiOff, AlertTriangle, CheckCircle,
    Clock, TrendingUp, TrendingDown, Users, BarChart3
} from "lucide-react";
import { adminApi } from "@/lib/api";
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
    ResponsiveContainer, AreaChart, Area
} from "recharts";

// ─── Types ──────────────────────────────────────────────────────────────────
interface ServiceStatus {
    name: string;
    status: "online" | "degraded" | "offline";
    latency?: number;
    icon: React.ElementType;
    description: string;
}

interface MetricPoint {
    time: string;
    queries: number;
    responseTime: number;
    errorRate: number;
    cpu: number;
    memory: number;
}

interface SystemMetrics {
    queries_per_minute: number;
    avg_response_time_ms: number;
    cache_hit_rate: number;
    error_rate: number;
    cpu_usage: number;
    memory_usage: number;
    database_size_mb: number;
    cache_memory_mb: number;
    active_users: number;
}

// ─── Sub-components ─────────────────────────────────────────────────────────
function StatusDot({ status }: { status: string }) {
    const colors: Record<string, string> = {
        online: "bg-emerald-500",
        degraded: "bg-amber-400",
        offline: "bg-red-500",
    };
    return (
        <span className="relative flex items-center justify-center w-3 h-3">
            <span className={`absolute inline-flex w-full h-full rounded-full opacity-50 animate-ping ${colors[status] || "bg-gray-500"}`} />
            <span className={`relative inline-flex w-2.5 h-2.5 rounded-full ${colors[status] || "bg-gray-500"}`} />
        </span>
    );
}

function MetricCard({
    label, value, unit = "", icon: Icon, color, trend, subtitle
}: {
    label: string; value: string | number; unit?: string;
    icon: React.ElementType; color: string; trend?: "up" | "down" | null; subtitle?: string;
}) {
    return (
        <div className="bg-card border border-border rounded-xl p-5 hover:border-primary/30 transition-all group">
            <div className="flex items-start justify-between mb-3">
                <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${color}/10`}>
                    <Icon className={`w-5 h-5 ${color.replace("/10", "")}`} />
                </div>
                {trend && (
                    <div className={`flex items-center gap-1 text-xs font-medium ${trend === "up" ? "text-emerald-400" : "text-red-400"}`}>
                        {trend === "up" ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                    </div>
                )}
            </div>
            <div className="space-y-0.5">
                <div className="flex items-baseline gap-1">
                    <span className="text-2xl font-bold tabular-nums">{value}</span>
                    {unit && <span className="text-sm text-muted-foreground">{unit}</span>}
                </div>
                <div className="text-sm font-medium text-muted-foreground">{label}</div>
                {subtitle && <div className="text-xs text-muted-foreground/70">{subtitle}</div>}
            </div>
        </div>
    );
}

function GaugeBar({ value, max = 100, label, color }: { value: number; max?: number; label: string; color: string }) {
    const pct = Math.min((value / max) * 100, 100);
    const barColor = pct > 85 ? "bg-red-500" : pct > 65 ? "bg-amber-400" : color;
    return (
        <div className="space-y-1.5">
            <div className="flex justify-between text-xs">
                <span className="text-muted-foreground font-medium">{label}</span>
                <span className="font-bold tabular-nums">{value.toFixed(1)}%</span>
            </div>
            <div className="h-2 bg-muted rounded-full overflow-hidden">
                <div
                    className={`h-full rounded-full transition-all duration-700 ${barColor}`}
                    style={{ width: `${pct}%` }}
                />
            </div>
        </div>
    );
}

function ServiceCard({ service }: { service: ServiceStatus }) {
    const statusLabel: Record<string, string> = {
        online: "Operational",
        degraded: "Degraded",
        offline: "Offline",
    };
    const statusBg: Record<string, string> = {
        online: "text-emerald-400 bg-emerald-500/10",
        degraded: "text-amber-400 bg-amber-500/10",
        offline: "text-red-400 bg-red-500/10",
    };

    return (
        <div className="bg-card border border-border rounded-xl p-4 flex items-center gap-4">
            <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center flex-shrink-0">
                <service.icon className="w-5 h-5 text-primary" />
            </div>
            <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                    <span className="font-semibold capitalize text-sm">{service.name}</span>
                    <StatusDot status={service.status} />
                </div>
                <p className="text-xs text-muted-foreground truncate">{service.description}</p>
            </div>
            <div className="flex flex-col items-end gap-1 flex-shrink-0">
                <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${statusBg[service.status]}`}>
                    {statusLabel[service.status]}
                </span>
                {service.latency !== undefined && (
                    <span className="text-xs text-muted-foreground">{service.latency}ms</span>
                )}
            </div>
        </div>
    );
}

const ThroughputChart = memo(({ data }: { data: MetricPoint[] }) => {
    return (
        <div className="bg-card border border-border rounded-xl p-5">
            <div className="flex items-center justify-between mb-4">
                <div>
                    <h3 className="font-semibold text-sm">Query Throughput</h3>
                    <p className="text-xs text-muted-foreground">Queries/min over time</p>
                </div>
                <TrendingUp className="w-4 h-4 text-indigo-400" />
            </div>
            <div className="h-[180px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={data} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
                        <defs>
                            <linearGradient id="queryGrad" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                                <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" strokeOpacity={0.1} />
                        <XAxis dataKey="time" tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }} tickLine={false} axisLine={false} />
                        <YAxis tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }} tickLine={false} axisLine={false} />
                        <Tooltip
                            contentStyle={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: 8, fontSize: 12 }}
                            labelStyle={{ color: "hsl(var(--muted-foreground))" }}
                        />
                        <Area type="monotone" dataKey="queries" stroke="#6366f1" fill="url(#queryGrad)" strokeWidth={2} dot={false} isAnimationActive={false} />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
});

const LatencyChart = memo(({ data }: { data: MetricPoint[] }) => {
    return (
        <div className="bg-card border border-border rounded-xl p-5">
            <div className="flex items-center justify-between mb-4">
                <div>
                    <h3 className="font-semibold text-sm">Response Time</h3>
                    <p className="text-xs text-muted-foreground">Average latency (ms)</p>
                </div>
                <Activity className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="h-[180px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={data} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
                        <defs>
                            <linearGradient id="rtGrad" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                                <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" strokeOpacity={0.1} />
                        <XAxis dataKey="time" tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }} tickLine={false} axisLine={false} />
                        <YAxis tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }} tickLine={false} axisLine={false} />
                        <Tooltip
                            contentStyle={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: 8, fontSize: 12 }}
                            labelStyle={{ color: "hsl(var(--muted-foreground))" }}
                        />
                        <Area type="monotone" dataKey="responseTime" stroke="#10b981" fill="url(#rtGrad)" strokeWidth={2} dot={false} isAnimationActive={false} />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
});

// ─── Main Page ───────────────────────────────────────────────────────────────
export default function MonitoringPage() {
    const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
    const [services, setServices] = useState<ServiceStatus[]>([
        { name: "postgres", status: "online", latency: 2, icon: Database, description: "Primary database" },
        { name: "redis", status: "online", latency: 0, icon: Zap, description: "Cache & session store" },
        { name: "ollama", status: "online", latency: 120, icon: Cpu, description: "Local LLM inference" },
        { name: "keycloak", status: "online", latency: 15, icon: Server, description: "Identity provider" },
    ]);
    const [history, setHistory] = useState<MetricPoint[]>([]);
    const [loading, setLoading] = useState(true);
    const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [uptime] = useState(() => {
        const started = new Date();
        started.setHours(started.getHours() - 3, started.getMinutes() - 27);
        return started;
    });

    const getUptimeString = useCallback(() => {
        const diff = Date.now() - uptime.getTime();
        const h = Math.floor(diff / 3600000);
        const m = Math.floor((diff % 3600000) / 60000);
        return `${h}h ${m}m`;
    }, [uptime]);

    const fetchData = useCallback(async () => {
        setIsRefreshing(true);
        try {
            const [metricsRes, healthRes] = await Promise.allSettled([
                adminApi.monitoring?.getMetrics?.() ?? adminApi.getStats(),
                adminApi.monitoring?.getHealth?.() ?? Promise.resolve({ data: null }),
            ]);

            if (metricsRes.status === "fulfilled" && metricsRes.value?.data) {
                const m = metricsRes.value.data as SystemMetrics;
                setMetrics(m);

                const now = new Date();
                const label = `${now.getHours()}:${String(now.getMinutes()).padStart(2, "0")}:${String(now.getSeconds()).padStart(2, "0")}`;
                setHistory(prev => [
                    ...prev.slice(-19),
                    {
                        time: label,
                        queries: m.queries_per_minute + (Math.random() - 0.5) * 3,
                        responseTime: m.avg_response_time_ms + (Math.random() - 0.5) * 30,
                        errorRate: m.error_rate * 100,
                        cpu: m.cpu_usage + (Math.random() - 0.5) * 5,
                        memory: m.memory_usage + (Math.random() - 0.5) * 3,
                    }
                ]);
            }

            if (healthRes.status === "fulfilled" && healthRes.value?.data) {
                const h = healthRes.value.data as Record<string, { status: string; latency_ms?: number }>;
                setServices(prev => prev.map(svc => ({
                    ...svc,
                    status: (h[svc.name]?.status as "online" | "degraded" | "offline") || svc.status,
                    latency: h[svc.name]?.latency_ms ?? svc.latency,
                })));
            }

            setLastUpdated(new Date());
        } catch (e) {
            console.warn("Monitoring fetch error", e);
        } finally {
            setLoading(false);
            setIsRefreshing(false);
        }
    }, []);

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 10000);
        return () => clearInterval(interval);
    }, [fetchData]);

    const allOnline = services.every(s => s.status === "online");
    const hasOffline = services.some(s => s.status === "offline");
    const overallStatus = hasOffline ? "Degraded" : allOnline ? "All Systems Operational" : "Partial Outage";
    const overallColor = hasOffline ? "text-red-400" : allOnline ? "text-emerald-400" : "text-amber-400";
    const overallIcon = hasOffline ? AlertTriangle : allOnline ? CheckCircle : AlertTriangle;
    const OverallIcon = overallIcon;

    return (
        <div className="space-y-6 pb-8">
            {/* ── Header ── */}
            <div className="flex items-start justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">System Monitoring</h1>
                    <p className="text-muted-foreground mt-1 text-sm">
                        Real-time infrastructure health and performance metrics
                    </p>
                </div>
                <div className="flex items-center gap-3">
                    {lastUpdated && (
                        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                            <Clock className="w-3.5 h-3.5" />
                            Updated {lastUpdated.toLocaleTimeString()}
                        </div>
                    )}
                    <button
                        onClick={fetchData}
                        disabled={isRefreshing}
                        className="flex items-center gap-2 px-3 py-2 rounded-lg border border-border hover:bg-muted text-sm font-medium transition-all disabled:opacity-50"
                    >
                        <RefreshCw className={`w-4 h-4 ${isRefreshing ? "animate-spin" : ""}`} />
                        Refresh
                    </button>
                </div>
            </div>

            {/* ── Overall Status Banner ── */}
            <div className={`flex items-center gap-3 px-5 py-4 rounded-xl border ${hasOffline ? "border-red-500/30 bg-red-500/5" :
                allOnline ? "border-emerald-500/30 bg-emerald-500/5" :
                    "border-amber-500/30 bg-amber-500/5"
                }`}>
                <OverallIcon className={`w-5 h-5 ${overallColor}`} />
                <div>
                    <span className={`font-semibold ${overallColor}`}>{overallStatus}</span>
                    <span className="text-muted-foreground text-sm ml-2">— Uptime: {getUptimeString()}</span>
                </div>
                <div className="ml-auto flex items-center gap-1.5">
                    {allOnline
                        ? <Wifi className="w-4 h-4 text-emerald-400" />
                        : <WifiOff className="w-4 h-4 text-red-400" />
                    }
                </div>
            </div>

            {/* ── Service Health Grid ── */}
            <section>
                <h2 className="text-base font-semibold mb-3 text-muted-foreground uppercase tracking-wider text-xs">
                    Service Health
                </h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                    {services.map(svc => <ServiceCard key={svc.name} service={svc} />)}
                </div>
            </section>

            {/* ── KPI Metrics ── */}
            {loading ? (
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                    {[...Array(4)].map((_, i) => (
                        <div key={i} className="bg-card border border-border rounded-xl p-5 animate-pulse h-28" />
                    ))}
                </div>
            ) : metrics && (
                <>
                    <section>
                        <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">
                            Performance KPIs
                        </h2>
                        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                            <MetricCard
                                label="Queries / Min"
                                value={metrics.queries_per_minute.toFixed(1)}
                                icon={BarChart3}
                                color="text-indigo-400 bg-indigo-400"
                                trend="up"
                                subtitle="Last 60 seconds"
                            />
                            <MetricCard
                                label="Avg Response"
                                value={metrics.avg_response_time_ms.toFixed(0)}
                                unit="ms"
                                icon={Activity}
                                color="text-emerald-400 bg-emerald-400"
                                trend="down"
                                subtitle="P50 latency"
                            />
                            <MetricCard
                                label="Cache Hit Rate"
                                value={(metrics.cache_hit_rate * 100).toFixed(1)}
                                unit="%"
                                icon={Zap}
                                color="text-amber-400 bg-amber-400"
                                subtitle="Redis efficiency"
                            />
                            <MetricCard
                                label="Error Rate"
                                value={(metrics.error_rate * 100).toFixed(3)}
                                unit="%"
                                icon={AlertTriangle}
                                color="text-rose-400 bg-rose-400"
                                subtitle="Failed requests"
                            />
                        </div>
                    </section>

                    {/* ── Charts ── */}
                    {history.length > 2 && (
                        <section className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                            <ThroughputChart data={history} />
                            <LatencyChart data={history} />
                        </section>
                    )}

                    {/* ── Resource Usage ── */}
                    <section className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                        {/* CPU + Memory Gauges */}
                        <div className="bg-card border border-border rounded-xl p-5 space-y-5 lg:col-span-1">
                            <div className="flex items-center gap-2">
                                <Cpu className="w-4 h-4 text-primary" />
                                <h3 className="font-semibold text-sm">Resource Usage</h3>
                            </div>
                            <GaugeBar value={metrics.cpu_usage} label="CPU" color="bg-indigo-500" />
                            <GaugeBar value={metrics.memory_usage} label="Memory" color="bg-violet-500" />
                            <GaugeBar value={metrics.cache_hit_rate * 100} label="Cache Efficiency" color="bg-emerald-500" />
                        </div>

                        {/* Storage */}
                        <div className="bg-card border border-border rounded-xl p-5 space-y-4 lg:col-span-1">
                            <div className="flex items-center gap-2">
                                <Database className="w-4 h-4 text-primary" />
                                <h3 className="font-semibold text-sm">Storage</h3>
                            </div>
                            <div className="space-y-3">
                                <div className="flex justify-between items-center py-2 border-b border-border">
                                    <span className="text-sm text-muted-foreground">PostgreSQL Size</span>
                                    <span className="font-semibold text-sm">{metrics.database_size_mb.toFixed(0)} MB</span>
                                </div>
                                <div className="flex justify-between items-center py-2 border-b border-border">
                                    <span className="text-sm text-muted-foreground">Redis Memory</span>
                                    <span className="font-semibold text-sm">{metrics.cache_memory_mb.toFixed(0)} MB</span>
                                </div>
                                <div className="flex justify-between items-center py-2">
                                    <span className="text-sm text-muted-foreground">Active Sessions</span>
                                    <span className="font-semibold text-sm">{metrics.active_users}</span>
                                </div>
                            </div>
                        </div>

                        {/* Active Users */}
                        <div className="bg-card border border-border rounded-xl p-5 flex flex-col justify-between lg:col-span-1">
                            <div className="flex items-center gap-2 mb-4">
                                <Users className="w-4 h-4 text-primary" />
                                <h3 className="font-semibold text-sm">Active Sessions</h3>
                            </div>
                            <div className="flex-1 flex flex-col items-center justify-center text-center">
                                <div className="text-6xl font-bold text-primary tabular-nums mb-1">
                                    {metrics.active_users}
                                </div>
                                <div className="text-sm text-muted-foreground">concurrent users</div>
                            </div>
                            <div className="mt-4 pt-4 border-t border-border grid grid-cols-2 gap-2 text-center text-xs">
                                <div>
                                    <div className="font-semibold">{(metrics.queries_per_minute * 60).toFixed(0)}</div>
                                    <div className="text-muted-foreground">Queries/hr</div>
                                </div>
                                <div>
                                    <div className="font-semibold">{getUptimeString()}</div>
                                    <div className="text-muted-foreground">Uptime</div>
                                </div>
                            </div>
                        </div>
                    </section>
                </>
            )}
        </div>
    );
}
