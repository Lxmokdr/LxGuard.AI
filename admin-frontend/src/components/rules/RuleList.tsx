"use client"

import { useEffect, useState } from "react"
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"
import { Switch } from "@/components/ui/switch"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Edit2, Trash2, Play, Search, Loader2 } from "lucide-react"
import { api } from "@/lib/api"

export interface Rule {
    id: string
    description: string
    priority: number
    enabled?: boolean
}

interface RuleListProps {
    onEdit: (rule: Rule) => void
}

export function RuleList({ onEdit }: RuleListProps) {
    const [rules, setRules] = useState<Rule[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchRules = async () => {
            try {
                const data = await api.getRules()
                setRules(data)
            } catch (error) {
                console.error("Failed to fetch rules:", error)
            } finally {
                setLoading(false)
            }
        }

        fetchRules()
    }, [])

    const handleDelete = async (id: string) => {
        if (!confirm("Are you sure you want to delete this rule? logic will be removed from DSL.")) return
        try {
            await api.deleteRule(id)
            setRules(rules.filter(r => r.id !== id))
        } catch (e) {
            console.error(e)
            alert("Failed to delete rule")
        }
    }

    return (
        <div className="rounded-md border border-white/5 bg-black/20 overflow-hidden">
            <Table>
                <TableHeader>
                    <TableRow className="border-white/10 hover:bg-transparent">
                        <TableHead className="text-muted-foreground font-mono text-[10px] uppercase">Rule ID</TableHead>
                        <TableHead className="text-muted-foreground font-mono text-[10px] uppercase">Logic Description</TableHead>
                        <TableHead className="text-muted-foreground font-mono text-[10px] uppercase">Priority</TableHead>
                        <TableHead className="text-muted-foreground font-mono text-[10px] uppercase">Status</TableHead>
                        <TableHead className="text-right text-muted-foreground font-mono text-[10px] uppercase">Actions</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {loading ? (
                        <TableRow>
                            <TableCell colSpan={5} className="text-center py-12">
                                <div className="flex flex-col items-center gap-3 text-muted-foreground">
                                    <Loader2 className="w-6 h-6 animate-spin text-primary" />
                                    <span className="font-mono text-xs uppercase tracking-widest">Compiling Rule Database...</span>
                                </div>
                            </TableCell>
                        </TableRow>
                    ) : rules.map((rule) => (
                        <TableRow key={rule.id} className="border-white/5 hover:bg-white/5 transition-colors">
                            <TableCell className="font-mono font-medium text-xs text-primary">{rule.id}</TableCell>
                            <TableCell className="max-w-md">
                                <p className="text-sm line-clamp-2">{rule.description}</p>
                            </TableCell>
                            <TableCell>
                                <Badge variant="outline" className="font-mono text-[10px] border-primary/30 text-primary">
                                    P{rule.priority}
                                </Badge>
                            </TableCell>
                            <TableCell>
                                <Switch checked={rule.enabled ?? true} />
                            </TableCell>
                            <TableCell className="text-right">
                                <div className="flex justify-end gap-2">
                                    <Button variant="ghost" size="icon" onClick={() => onEdit(rule)} className="hover:bg-primary/20 hover:text-primary">
                                        <Edit2 className="h-4 w-4" />
                                    </Button>
                                    <Button variant="ghost" size="icon" onClick={() => handleDelete(rule.id)} className="hover:bg-destructive/20 hover:text-destructive">
                                        <Trash2 className="h-4 w-4" />
                                    </Button>
                                </div>
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </div>
    )
}

