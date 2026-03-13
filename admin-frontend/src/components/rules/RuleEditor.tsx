"use client"

import { useState } from "react"
import { Rule } from "./RuleList"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription, SheetFooter } from "@/components/ui/sheet"
import { Badge } from "@/components/ui/badge"
import { Shield, Save, Code, Play, AlertTriangle, CheckCircle } from "lucide-react"
import { api } from "@/lib/api"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

interface RuleEditorProps {
    rule: Rule | null
    open: boolean
    onOpenChange: (open: boolean) => void
}

export function RuleEditor({ rule, open, onOpenChange }: RuleEditorProps) {
    const [saving, setSaving] = useState(false)
    const [simulating, setSimulating] = useState(false)
    const [simulationResult, setSimulationResult] = useState<any>(null)

    // Form State
    const [formData, setFormData] = useState<Partial<Rule>>(rule || {})

    // Simulation State
    const [simRole, setSimRole] = useState("guest")
    const [simIntent, setSimIntent] = useState("General")

    if (!rule) return null

    const handleSave = async () => {
        setSaving(true)
        try {
            await api.createRule({
                id: rule.id, // ID is fixed for edits, new for create
                description: formData.description || rule.description,
                priority: parseInt(formData.priority?.toString() || rule.priority.toString()),
                intent: simIntent, // Using sim intent as the rule intent for MVP editing
                enabled: true
            })
            onOpenChange(false)
            // Trigger refresh (in real app, use query client)
            window.location.reload()
        } catch (e) {
            console.error(e)
            alert("Failed to save rule")
        } finally {
            setSaving(false)
        }
    }

    const handleSimulate = async () => {
        setSimulating(true)
        setSimulationResult(null)
        try {
            const result = await api.simulateQuery(
                "Test query",
                simRole,
                simIntent
            )
            setSimulationResult(result)
        } catch (e) {
            console.error(e)
        } finally {
            setSimulating(false)
        }
    }

    return (
        <Sheet open={open} onOpenChange={onOpenChange}>
            <SheetContent className="w-[400px] sm:w-[540px] bg-black/90 backdrop-blur-2xl border-white/5 text-white overflow-y-auto">
                <SheetHeader className="mb-8">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="p-2 rounded-lg bg-primary/20 glow-border-cyan">
                            <Shield className="w-5 h-5 text-primary" />
                        </div>
                        <div>
                            <SheetTitle className="text-xl font-bold tracking-tight text-white">Edit Expert Rule</SheetTitle>
                            <SheetDescription className="text-muted-foreground font-mono text-xs uppercase">
                                Configure deterministic logic & priority.
                            </SheetDescription>
                        </div>
                    </div>
                </SheetHeader>

                <div className="grid gap-6 py-4">
                    <div className="grid gap-2">
                        <Label htmlFor="id" className="text-[10px] uppercase font-mono text-muted-foreground">Rule ID (Immutable)</Label>
                        <Input id="id" value={rule.id} disabled className="bg-white/5 border-white/10 font-mono text-primary" />
                    </div>

                    <div className="grid gap-2">
                        <Label htmlFor="description" className="text-[10px] uppercase font-mono text-muted-foreground">Logic Description</Label>
                        <Textarea
                            id="description"
                            defaultValue={rule.description}
                            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                            className="bg-white/5 border-white/10 focus:border-primary/50 min-h-[100px] text-sm leading-relaxed"
                        />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="grid gap-2">
                            <Label htmlFor="priority" className="text-[10px] uppercase font-mono text-muted-foreground">Priority (1-10)</Label>
                            <Input
                                id="priority"
                                type="number"
                                defaultValue={rule.priority}
                                onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) })}
                                className="bg-white/5 border-white/10 focus:border-primary/50 font-mono"
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="intent" className="text-[10px] uppercase font-mono text-muted-foreground">Target Intent</Label>
                            <Select value={simIntent} onValueChange={setSimIntent}>
                                <SelectTrigger className="bg-white/5 border-white/10">
                                    <SelectValue />
                                </SelectTrigger>
                                <SelectContent className="bg-black/90 border-white/10 text-white">
                                    <SelectItem value="General">General</SelectItem>
                                    <SelectItem value="Deployment">Deployment</SelectItem>
                                    <SelectItem value="SecurityConfig">SecurityConfig</SelectItem>
                                    <SelectItem value="Help">Help</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                    </div>

                    {/* Blast Radius Simulation Section */}
                    <div className="rounded-lg border border-white/10 bg-white/5 p-4 mt-4">
                        <div className="flex items-center justify-between mb-4">
                            <Label className="text-[10px] uppercase font-mono text-primary flex items-center gap-2">
                                <AlertTriangle className="w-3 h-3" />
                                Blast Radius Simulation
                            </Label>
                        </div>

                        <div className="grid grid-cols-2 gap-2 mb-4">
                            <Select value={simRole} onValueChange={setSimRole}>
                                <SelectTrigger className="h-8 text-xs bg-black/40 border-white/10">
                                    <SelectValue placeholder="Select Role" />
                                </SelectTrigger>
                                <SelectContent className="bg-black/90 border-white/10 text-white">
                                    <SelectItem value="admin">Admin</SelectItem>
                                    <SelectItem value="employee">Employee</SelectItem>
                                    <SelectItem value="guest">Guest</SelectItem>
                                </SelectContent>
                            </Select>
                            <Button
                                size="sm"
                                variant="outline"
                                onClick={handleSimulate}
                                disabled={simulating}
                                className="h-8 text-xs border-primary/30 text-primary hover:bg-primary/20"
                            >
                                {simulating ? "Running..." : "Test Rule Impact"}
                                <Play className="w-3 h-3 ml-2" />
                            </Button>
                        </div>

                        {simulationResult && (
                            <div className={`p-3 rounded border text-xs font-mono ${simulationResult.decision === "BLOCKED"
                                ? "bg-red-500/10 border-red-500/30 text-red-400"
                                : "bg-green-500/10 border-green-500/30 text-green-400"
                                }`}>
                                <div className="flex items-center gap-2 mb-1 font-bold">
                                    {simulationResult.decision === "BLOCKED"
                                        ? <Shield className="w-3 h-3" />
                                        : <CheckCircle className="w-3 h-3" />
                                    }
                                    DECISION: {simulationResult.decision}
                                </div>
                                <div className="opacity-80">{simulationResult.reason}</div>
                            </div>
                        )}
                    </div>
                </div>

                <SheetFooter className="mt-8">
                    <Button
                        onClick={handleSave}
                        disabled={saving}
                        className="w-full bg-primary/20 text-primary border border-primary/30 hover:bg-primary/30 glow-border-cyan gap-2"
                    >
                        {saving ? "Compiling Logic..." : "Deploy Rule Changes"}
                        {!saving && <Save className="w-4 h-4" />}
                    </Button>
                </SheetFooter>
            </SheetContent>
        </Sheet>
    )
}


