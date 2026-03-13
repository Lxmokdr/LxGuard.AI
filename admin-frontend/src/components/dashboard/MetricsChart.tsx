"use client"

import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts"

const data = [
    { name: "00:00", total: 12, blocked: 2 },
    { name: "04:00", total: 8, blocked: 0 },
    { name: "08:00", total: 45, blocked: 5 },
    { name: "12:00", total: 120, blocked: 12 },
    { name: "16:00", total: 98, blocked: 8 },
    { name: "20:00", total: 56, blocked: 3 },
]

export function MetricsChart() {
    return (
        <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data}>
                <defs>
                    <linearGradient id="totalGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0} />
                    </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                <XAxis
                    dataKey="name"
                    stroke="rgba(255,255,255,0.4)"
                    fontSize={10}
                    tickLine={false}
                    axisLine={false}
                    dy={10}
                />
                <YAxis
                    stroke="rgba(255,255,255,0.4)"
                    fontSize={10}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(value) => `${value}`}
                />
                <Tooltip
                    cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                    contentStyle={{
                        backgroundColor: 'rgba(10, 15, 25, 0.95)',
                        backdropFilter: 'blur(10px)',
                        borderRadius: '12px',
                        border: '1px solid rgba(255,255,255,0.1)',
                        boxShadow: '0 8px 32px rgba(0,0,0,0.4)'
                    }}
                    labelStyle={{ color: 'rgba(255,255,255,0.8)', fontWeight: 'bold', marginBottom: '4px' }}
                />
                <Bar
                    dataKey="total"
                    fill="hsl(var(--primary))"
                    radius={[4, 4, 0, 0]}
                    name="Total Queries"
                    barSize={24}
                />
                <Bar
                    dataKey="blocked"
                    fill="hsl(var(--destructive))"
                    radius={[4, 4, 0, 0]}
                    name="Blocked"
                    barSize={24}
                />
            </BarChart>
        </ResponsiveContainer>
    )
}

