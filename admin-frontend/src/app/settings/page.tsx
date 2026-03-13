"use client"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Settings, ShieldCheck, Cpu, CheckCircle2, AlertCircle, Loader2, FolderOpen, Upload } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import { api } from "@/lib/api"

type Toast = { type: "success" | "error" | "info"; message: string }

const SUPPORTED_EXTS = [".pdf", ".docx", ".md", ".txt"]

export default function SettingsPage() {
    const [loading, setLoading] = useState(true)
    const [saving, setSaving] = useState(false)
    const [toast, setToast] = useState<Toast | null>(null)

    // System tab state
    const [maintenanceMode, setMaintenanceMode] = useState(false)
    const [enhancedLogging, setEnhancedLogging] = useState(true)
    const [sourceDirectory, setSourceDirectory] = useState("docs")
    const [maxChunkSize, setMaxChunkSize] = useState(600)
    const [chunkOverlap, setChunkOverlap] = useState(100)

    // Directory picker state
    const dirInputRef = useRef<HTMLInputElement>(null)
    const [pickedFiles, setPickedFiles] = useState<File[]>([])
    const [uploading, setUploading] = useState(false)
    const [uploadProgress, setUploadProgress] = useState<{ done: number; total: number } | null>(null)

    useEffect(() => {
        const loadSettings = async () => {
            try {
                const res = await api.settings.get()
                const s = res.data || {}
                setMaintenanceMode(s.maintenance_mode ?? false)
                setEnhancedLogging(s.enhanced_audit_logging ?? true)
                setSourceDirectory(s.source_directory ?? "docs")
                setMaxChunkSize(s.max_chunk_size ?? 600)
                setChunkOverlap(s.chunk_overlap ?? 100)
            } catch (err: any) {
                showToast("error", "Failed to load settings: " + (err.message || "Unknown error"))
            } finally {
                setLoading(false)
            }
        }
        loadSettings()
    }, [])

    const showToast = (type: "success" | "error" | "info", message: string) => {
        setToast({ type, message })
        setTimeout(() => setToast(null), 5000)
    }

    const handleSave = async () => {
        setSaving(true)
        try {
            await api.settings.update({
                maintenance_mode: maintenanceMode,
                enhanced_audit_logging: enhancedLogging,
                source_directory: sourceDirectory,
                max_chunk_size: maxChunkSize,
                chunk_overlap: chunkOverlap,
            })
            showToast("success", "Settings saved and applied successfully.")
        } catch (err: any) {
            showToast("error", "Failed to save: " + (err.message || "Unknown error"))
        } finally {
            setSaving(false)
        }
    }

    /** Handle directory selection from <input type="file" webkitdirectory> */
    const handleDirPick = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = Array.from(e.target.files || [])
        const supported = files.filter(f =>
            SUPPORTED_EXTS.some(ext => f.name.toLowerCase().endsWith(ext))
        )

        if (supported.length === 0) {
            showToast("error", "No supported documents found (PDF, DOCX, MD, TXT).")
            return
        }

        // Derive folder name from the first file's relative path: "FolderName/file.pdf"
        const firstRelative = (supported[0] as any).webkitRelativePath as string | undefined
        const folderName = firstRelative ? firstRelative.split("/")[0] : "docs"

        setPickedFiles(supported)
        setSourceDirectory(folderName)
        showToast("info", `Selected "${folderName}" — ${supported.length} document(s) ready to upload.`)
    }

    /** Upload every picked file via the existing /admin/documents/upload endpoint */
    const handleUploadAll = async () => {
        if (pickedFiles.length === 0) return
        setUploading(true)
        setUploadProgress({ done: 0, total: pickedFiles.length })

        let successCount = 0
        let failCount = 0

        for (let i = 0; i < pickedFiles.length; i++) {
            const file = pickedFiles[i]
            const form = new FormData()
            form.append("file", file)
            form.append("title", file.name)
            form.append("scope", "internal")
            form.append("access_level", "employee")

            try {
                await api.documents.upload(form)
                successCount++
            } catch {
                failCount++
            }

            setUploadProgress({ done: i + 1, total: pickedFiles.length })
        }

        setUploading(false)
        setPickedFiles([])
        setUploadProgress(null)
        if (dirInputRef.current) dirInputRef.current.value = ""

        if (failCount === 0) {
            showToast("success", `✅ Uploaded ${successCount} document(s) to "${sourceDirectory}".`)
        } else {
            showToast("error", `⚠️ ${successCount} uploaded, ${failCount} failed.`)
        }
    }

    const toastColors: Record<string, string> = {
        success: "bg-emerald-500/10 border-emerald-500/30 text-emerald-400",
        error: "bg-destructive/10 border-destructive/30 text-destructive",
        info: "bg-blue-500/10 border-blue-500/30 text-blue-400",
    }

    return (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-8">
            {/* Header */}
            <div>
                <h2 className="text-3xl font-bold tracking-tight text-white flex items-center gap-3">
                    <Settings className="w-8 h-8 text-primary" />
                    System Settings
                </h2>
                <p className="text-muted-foreground font-mono text-sm mt-1">
                    GOVERNANCE, SECURITY &amp; INFRASTRUCTURE CONFIG
                </p>
            </div>

            {/* Toast */}
            <AnimatePresence>
                {toast && (
                    <motion.div
                        key="toast"
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className={`flex items-center gap-3 px-4 py-3 rounded-lg border text-sm font-medium ${toastColors[toast.type]}`}
                    >
                        {toast.type === "success" && <CheckCircle2 className="w-4 h-4 shrink-0" />}
                        {toast.type === "error" && <AlertCircle className="w-4 h-4 shrink-0" />}
                        {toast.type === "info" && <FolderOpen className="w-4 h-4 shrink-0" />}
                        {toast.message}
                    </motion.div>
                )}
            </AnimatePresence>

            {loading ? (
                <div className="flex items-center justify-center h-48 text-muted-foreground gap-3">
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Loading settings...
                </div>
            ) : (
                <Tabs defaultValue="system" className="w-full">
                    <TabsList className="bg-black/20 border border-white/10 p-1 rounded-xl mb-6">
                        <TabsTrigger value="system" className="rounded-lg data-[state=active]:bg-primary/20 data-[state=active]:text-primary transition-all">
                            <Cpu className="w-4 h-4 mr-2" /> System Configuration
                        </TabsTrigger>
                        <TabsTrigger value="chunking" className="rounded-lg data-[state=active]:bg-primary/20 data-[state=active]:text-primary transition-all">
                            <Settings className="w-4 h-4 mr-2" /> Chunking &amp; Indexing
                        </TabsTrigger>
                        <TabsTrigger value="access" className="rounded-lg data-[state=active]:bg-secondary/20 data-[state=active]:text-secondary transition-all">
                            <ShieldCheck className="w-4 h-4 mr-2" /> Access Control
                        </TabsTrigger>
                    </TabsList>

                    {/* ── System Configuration ── */}
                    <TabsContent value="system">
                        <Card className="glass-card border-none">
                            <CardHeader>
                                <CardTitle className="text-xl font-bold">Core System Settings</CardTitle>
                                <CardDescription className="text-muted-foreground">
                                    Configure global parameters for the LxGuard.AI Architecture.
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">

                                {/* Maintenance Mode */}
                                <div className="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/5">
                                    <Label htmlFor="maintenance" className="flex flex-col space-y-1 cursor-pointer">
                                        <span className="font-bold">Maintenance Mode</span>
                                        <span className="text-xs font-normal text-muted-foreground">
                                            Route all non-admin traffic to the system status page.
                                        </span>
                                    </Label>
                                    <Switch id="maintenance" checked={maintenanceMode} onCheckedChange={setMaintenanceMode}
                                        className="data-[state=checked]:bg-orange-500" />
                                </div>

                                {/* Enhanced Audit Logging */}
                                <div className="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/5">
                                    <Label htmlFor="audit" className="flex flex-col space-y-1 cursor-pointer">
                                        <span className="font-bold">Enhanced Neural Logging</span>
                                        <span className="text-xs font-normal text-muted-foreground">
                                            Persist full reasoning chains and vector attention maps.
                                        </span>
                                    </Label>
                                    <Switch id="audit" checked={enhancedLogging} onCheckedChange={setEnhancedLogging}
                                        className="data-[state=checked]:bg-primary" />
                                </div>

                                {/* Document Source Directory */}
                                <div className="p-4 rounded-xl bg-white/5 border border-white/5 space-y-3">
                                    <div>
                                        <Label className="font-bold">Document Source Directory</Label>
                                        <p className="text-xs text-muted-foreground mt-0.5">
                                            Path on the server scanned by the watchdog for automatic indexing.
                                            Use the picker to select a local folder and bulk-upload its documents.
                                        </p>
                                    </div>

                                    {/* Path input + Browse button */}
                                    <div className="flex gap-2">
                                        <Input
                                            value={sourceDirectory}
                                            onChange={(e) => setSourceDirectory(e.target.value)}
                                            className="bg-background border-border font-mono text-sm flex-1"
                                            placeholder="docs"
                                        />
                                        <Button
                                            type="button"
                                            variant="outline"
                                            onClick={() => dirInputRef.current?.click()}
                                            className="shrink-0 gap-2 border-border"
                                        >
                                            <FolderOpen className="w-4 h-4" />
                                            Browse…
                                        </Button>
                                        {/* Hidden directory input */}
                                        <input
                                            ref={dirInputRef}
                                            type="file"
                                            className="hidden"
                                            // @ts-ignore – non-standard but widely supported
                                            webkitdirectory=""
                                            multiple
                                            onChange={handleDirPick}
                                        />
                                    </div>

                                    {/* File preview + upload */}
                                    <AnimatePresence>
                                        {pickedFiles.length > 0 && (
                                            <motion.div
                                                initial={{ opacity: 0, height: 0 }}
                                                animate={{ opacity: 1, height: "auto" }}
                                                exit={{ opacity: 0, height: 0 }}
                                                className="space-y-2"
                                            >
                                                <div className="max-h-36 overflow-y-auto rounded-lg bg-black/30 border border-white/5 divide-y divide-white/5 text-xs font-mono">
                                                    {pickedFiles.map((f, i) => (
                                                        <div key={i} className="px-3 py-1.5 flex items-center gap-2 text-muted-foreground">
                                                            <span className="uppercase text-primary/70 w-8 shrink-0">
                                                                {f.name.split(".").pop()}
                                                            </span>
                                                            {f.name}
                                                            <span className="ml-auto opacity-50">
                                                                {(f.size / 1024).toFixed(1)} KB
                                                            </span>
                                                        </div>
                                                    ))}
                                                </div>

                                                {/* Progress bar */}
                                                {uploadProgress && (
                                                    <div className="space-y-1">
                                                        <div className="h-1.5 rounded-full bg-white/10 overflow-hidden">
                                                            <motion.div
                                                                className="h-full bg-primary rounded-full"
                                                                initial={{ width: 0 }}
                                                                animate={{ width: `${(uploadProgress.done / uploadProgress.total) * 100}%` }}
                                                            />
                                                        </div>
                                                        <p className="text-xs text-muted-foreground text-right">
                                                            {uploadProgress.done} / {uploadProgress.total} uploaded
                                                        </p>
                                                    </div>
                                                )}

                                                <Button
                                                    type="button"
                                                    onClick={handleUploadAll}
                                                    disabled={uploading}
                                                    className="w-full gap-2 bg-primary/20 text-primary border border-primary/30 hover:bg-primary/30"
                                                >
                                                    {uploading
                                                        ? <><Loader2 className="w-4 h-4 animate-spin" /> Uploading…</>
                                                        : <><Upload className="w-4 h-4" /> Upload {pickedFiles.length} file{pickedFiles.length !== 1 ? "s" : ""} to server</>
                                                    }
                                                </Button>
                                            </motion.div>
                                        )}
                                    </AnimatePresence>
                                </div>
                            </CardContent>
                            <CardFooter className="pt-2">
                                <Button onClick={handleSave} disabled={saving}
                                    className="bg-primary/20 text-primary border border-primary/30 hover:bg-primary/30">
                                    {saving ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Saving…</> : "Commit Changes"}
                                </Button>
                            </CardFooter>
                        </Card>
                    </TabsContent>

                    {/* ── Chunking & Indexing ── */}
                    <TabsContent value="chunking">
                        <Card className="glass-card border-none">
                            <CardHeader>
                                <CardTitle className="text-xl font-bold">Chunking &amp; Indexing</CardTitle>
                                <CardDescription className="text-muted-foreground">
                                    Controls how documents are split and embedded into the vector store.
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="p-4 rounded-xl bg-white/5 border border-white/5 space-y-2">
                                    <Label htmlFor="chunk-size" className="font-bold">Max Chunk Size (characters)</Label>
                                    <p className="text-xs text-muted-foreground">Paragraphs longer than this are further split by sentence boundaries.</p>
                                    <Input id="chunk-size" type="number" min={100} max={4000} value={maxChunkSize}
                                        onChange={(e) => setMaxChunkSize(Number(e.target.value))}
                                        className="bg-background border-border font-mono text-sm w-40" />
                                </div>
                                <div className="p-4 rounded-xl bg-white/5 border border-white/5 space-y-2">
                                    <Label htmlFor="overlap" className="font-bold">Chunk Overlap (characters)</Label>
                                    <p className="text-xs text-muted-foreground">Trailing characters carried forward into the next chunk for context continuity.</p>
                                    <Input id="overlap" type="number" min={0} max={500} value={chunkOverlap}
                                        onChange={(e) => setChunkOverlap(Number(e.target.value))}
                                        className="bg-background border-border font-mono text-sm w-40" />
                                </div>
                                <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs">
                                    ⚠️ Changes take effect on the <strong>next re-index</strong> of each document.
                                </div>
                            </CardContent>
                            <CardFooter className="pt-2">
                                <Button onClick={handleSave} disabled={saving}
                                    className="bg-primary/20 text-primary border border-primary/30 hover:bg-primary/30">
                                    {saving ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Saving…</> : "Commit Changes"}
                                </Button>
                            </CardFooter>
                        </Card>
                    </TabsContent>

                    {/* ── Access Control ── */}
                    <TabsContent value="access">
                        <Card className="glass-card border-none">
                            <CardHeader>
                                <CardTitle className="text-xl font-bold flex items-center gap-2">
                                    <ShieldCheck className="w-5 h-5 text-secondary" />
                                    Role-Based Access Control
                                </CardTitle>
                                <CardDescription>Identity management and permission propagation.</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="p-6 rounded-xl border border-dashed border-white/10 text-center">
                                    <p className="text-sm text-muted-foreground font-mono uppercase tracking-tight">
                                        External Identity Provider (LDAP/LDAPS)
                                    </p>
                                    <p className="text-xs text-muted-foreground/60 mt-1">
                                        Permissions are managed via institutional group mappings.
                                    </p>
                                </div>
                                <div className="grid grid-cols-3 gap-3 text-center text-sm">
                                    {[
                                        { role: "admin", desc: "Full access" },
                                        { role: "employee", desc: "Standard access" },
                                        { role: "guest", desc: "Read-only" },
                                    ].map(({ role, desc }) => (
                                        <div key={role} className="p-3 rounded-lg bg-white/5 border border-white/5">
                                            <div className="font-bold capitalize">{role}</div>
                                            <div className="text-xs text-muted-foreground mt-1">{desc}</div>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    </TabsContent>
                </Tabs>
            )}
        </motion.div>
    )
}
