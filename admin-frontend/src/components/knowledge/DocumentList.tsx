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
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { FileText, Eye, Download, Trash2, Database, Loader2 } from "lucide-react"
import { api, API_URL } from "@/lib/api"

export interface Document {
    id: string
    name: string
    size: string
    type: string
    last_modified: string
}

export function DocumentList() {
    const [docs, setDocs] = useState<Document[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchDocs = async () => {
            try {
                const response = await api.documents.getAll()
                // Handle both Array (backend) and { data: [] } (mock) formats
                const docsData = Array.isArray(response) ? response : (response.data || [])
                setDocs(docsData)
            } catch (error) {
                console.error("Failed to fetch documents:", error)
            } finally {
                setLoading(false)
            }
        }

        fetchDocs()
    }, [])

    return (
        <div className="rounded-md border border-white/5 bg-black/20 overflow-hidden">
            <Table>
                <TableHeader>
                    <TableRow className="border-white/10 hover:bg-transparent">
                        <TableHead className="text-muted-foreground font-mono text-[10px] uppercase">Filename</TableHead>
                        <TableHead className="text-muted-foreground font-mono text-[10px] uppercase">Type</TableHead>
                        <TableHead className="text-muted-foreground font-mono text-[10px] uppercase">Size</TableHead>
                        <TableHead className="text-muted-foreground font-mono text-[10px] uppercase">Last Modified</TableHead>
                        <TableHead className="text-right text-muted-foreground font-mono text-[10px] uppercase">Actions</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {loading ? (
                        <TableRow>
                            <TableCell colSpan={5} className="text-center py-12">
                                <div className="flex flex-col items-center gap-3 text-muted-foreground">
                                    <Loader2 className="w-6 h-6 animate-spin text-primary" />
                                    <span className="font-mono text-xs uppercase tracking-widest">Indexing Documentation Layer...</span>
                                </div>
                            </TableCell>
                        </TableRow>
                    ) : docs.map((doc) => (
                        <TableRow key={doc.id} className="border-white/5 hover:bg-white/5 transition-colors">
                            <TableCell className="font-medium flex items-center gap-3 py-4">
                                <div className="p-2 rounded bg-primary/10">
                                    <FileText className="h-4 w-4 text-primary" />
                                </div>
                                <div>
                                    <p className="text-sm font-semibold">{doc.name}</p>
                                    <p className="text-[10px] text-muted-foreground font-mono uppercase">ID: {doc.id}</p>
                                </div>
                            </TableCell>
                            <TableCell>
                                <Badge variant="outline" className="text-[10px] uppercase border-white/20">
                                    {doc.type}
                                </Badge>
                            </TableCell>
                            <TableCell className="text-xs font-mono">{doc.size}</TableCell>
                            <TableCell className="text-xs text-muted-foreground">{doc.last_modified}</TableCell>
                            <TableCell className="text-right">
                                <div className="flex justify-end gap-1">
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        className="hover:bg-primary/20 hover:text-primary"
                                        onClick={() => window.open(`${API_URL}/docs/${doc.name}`, '_blank')}
                                    >
                                        <Eye className="h-4 w-4" />
                                    </Button>
                                    <Button variant="ghost" size="icon" className="hover:bg-primary/20 hover:text-primary">
                                        <Download className="h-4 w-4" />
                                    </Button>
                                    <Button variant="ghost" size="icon" className="hover:bg-destructive/20 hover:text-destructive">
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

