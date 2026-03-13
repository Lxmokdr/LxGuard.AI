"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { LucideIcon } from "lucide-react"
import { motion } from "framer-motion"
import { cn } from "@/lib/utils"

interface StatusCardProps {
  title: string
  value: string | number
  description?: string
  icon: LucideIcon
  status?: "default" | "success" | "warning" | "destructive"
  index?: number
}

export function StatusCard({ title, value, description, icon: Icon, status = "default", index = 0 }: StatusCardProps) {
  const statusConfig = {
    default: { color: "text-primary", bg: "bg-primary/10", border: "glow-border-cyan" },
    success: { color: "text-secondary", bg: "bg-secondary/10", border: "glow-border-emerald" },
    warning: { color: "text-destructive", bg: "bg-destructive/10", border: "glow-border-amber" },
    destructive: { color: "text-destructive", bg: "bg-destructive/10", border: "glow-border-amber" },
  }

  const config = statusConfig[status] || statusConfig.default

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.1 }}
    >
      <Card className="glass-card border-none overflow-hidden relative group">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground group-hover:text-foreground transition-colors">
            {title}
          </CardTitle>
          <div className={cn("p-2 rounded-lg transition-all duration-300", config.bg, config.border)}>
            <Icon className={cn("h-4 w-4", config.color)} />
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold tracking-tight mb-1">{value}</div>
          {description && (
            <p className="text-xs text-muted-foreground font-medium">
              {description}
            </p>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}

