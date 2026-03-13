"use client";

import { useState, useEffect } from "react";
import { Upload, FileText, Trash2, RefreshCw, Eye, Filter, Pencil } from "lucide-react";
import { api, API_URL } from "@/lib/api";
import type { Document, DocumentScope, DocumentAccessLevel } from "@/lib/types";

export default function DocumentsPage() {
    const [documents, setDocuments] = useState<Document[]>([]);
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(false);
    const [filterScope, setFilterScope] = useState<"all" | DocumentScope>("all");

    // Upload form state
    const [showUploadForm, setShowUploadForm] = useState(false);
    const [uploadFile, setUploadFile] = useState<File | null>(null);
    const [uploadTitle, setUploadTitle] = useState("");
    const [uploadScope, setUploadScope] = useState<DocumentScope>("internal");
    const [uploadAccessLevel, setUploadAccessLevel] = useState<DocumentAccessLevel>("employee");

    // Edit form state
    const [showEditModal, setShowEditModal] = useState(false);
    const [editingDoc, setEditingDoc] = useState<Document | null>(null);
    const [editTitle, setEditTitle] = useState("");
    const [editScope, setEditScope] = useState<DocumentScope>("internal");
    const [editAccessLevel, setEditAccessLevel] = useState<DocumentAccessLevel>("employee");

    useEffect(() => {
        loadDocuments();
    }, []);

    const loadDocuments = async () => {
        try {
            const data = await api.documents.getAll();
            setDocuments(data.data || []);
        } catch (error) {
            console.error("Failed to load documents:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleUpload = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!uploadFile) return;

        setUploading(true);
        try {
            const formData = new FormData();
            formData.append("file", uploadFile);
            formData.append("title", uploadTitle);
            formData.append("scope", uploadScope);
            formData.append("access_level", uploadAccessLevel);

            await api.documents.upload(formData);
            await loadDocuments();

            // Reset form
            setShowUploadForm(false);
            setUploadFile(null);
            setUploadTitle("");
        } catch (error) {
            console.error("Failed to upload document:", error);
            alert("Upload failed. Please try again.");
        } finally {
            setUploading(false);
        }
    };

    const handleDelete = async (id: number) => {
        if (!confirm("Are you sure you want to delete this document?")) return;
        try {
            await api.documents.delete(id);
            await loadDocuments();
        } catch (error) {
            console.error("Failed to delete document:", error);
        }
    };

    const handleReindex = async (id: number) => {
        try {
            await api.documents.reindex(id);
            alert("Document re-indexing started");
        } catch (error) {
            console.error("Failed to reindex document:", error);
        }
    };

    const handleEdit = (doc: Document) => {
        setEditingDoc(doc);
        setEditTitle(doc.title);
        setEditScope(doc.scope || "internal");
        setEditAccessLevel(doc.access_level || "employee");
        setShowEditModal(true);
    };

    const handleUpdate = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!editingDoc) return;

        try {
            await api.documents.update(editingDoc.id, {
                title: editTitle,
                scope: editScope,
                access_level: editAccessLevel,
            });
            await loadDocuments();
            setShowEditModal(false);
        } catch (error) {
            console.error("Failed to update document:", error);
            alert("Update failed. Please try again.");
        }
    };

    const filteredDocuments = documents.filter((doc) => {
        if (filterScope === "all") return true;
        return doc.scope === filterScope;
    });

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-muted-foreground">Loading documents...</div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Document Library</h1>
                    <p className="text-muted-foreground mt-1">
                        Manage knowledge base documents and embeddings
                    </p>
                </div>
                <button
                    onClick={() => setShowUploadForm(true)}
                    className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
                >
                    <Upload className="w-4 h-4" />
                    Upload Document
                </button>
            </div>

            {/* Upload Form Modal */}
            {showUploadForm && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-card border border-border rounded-lg p-6 w-full max-w-md">
                        <h2 className="text-xl font-bold mb-4">Upload Document</h2>
                        <form onSubmit={handleUpload} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-2">Title</label>
                                <input
                                    type="text"
                                    value={uploadTitle}
                                    onChange={(e) => setUploadTitle(e.target.value)}
                                    required
                                    className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                                    placeholder="e.g., deployment.md"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-2">File</label>
                                <input
                                    type="file"
                                    accept=".md,.txt,.pdf"
                                    onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                                    required
                                    className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-2">Scope</label>
                                <select
                                    value={uploadScope}
                                    onChange={(e) => setUploadScope(e.target.value as DocumentScope)}
                                    className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                                >
                                    <option value="internal">Internal</option>
                                    <option value="public">Public</option>
                                    <option value="restricted">Restricted</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-2">Access Level</label>
                                <select
                                    value={uploadAccessLevel}
                                    onChange={(e) => setUploadAccessLevel(e.target.value as DocumentAccessLevel)}
                                    className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                                >
                                    <option value="all">All Users</option>
                                    <option value="employee">Employees Only</option>
                                    <option value="admin">Admin Only</option>
                                </select>
                            </div>
                            <div className="flex gap-3 pt-4">
                                <button
                                    type="button"
                                    onClick={() => setShowUploadForm(false)}
                                    className="flex-1 px-4 py-2 bg-accent rounded-lg hover:bg-accent/80 transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    disabled={uploading}
                                    className="flex-1 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50"
                                >
                                    {uploading ? "Uploading..." : "Upload"}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Edit Document Modal */}
            {showEditModal && editingDoc && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-card border border-border rounded-lg p-6 w-full max-w-md">
                        <h2 className="text-xl font-bold mb-4">Edit Document Metadata</h2>
                        <form onSubmit={handleUpdate} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-2">Title</label>
                                <input
                                    type="text"
                                    value={editTitle}
                                    onChange={(e) => setEditTitle(e.target.value)}
                                    required
                                    className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-2">Scope</label>
                                <select
                                    value={editScope}
                                    onChange={(e) => setEditScope(e.target.value as DocumentScope)}
                                    className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                                >
                                    <option value="internal">Internal</option>
                                    <option value="public">Public</option>
                                    <option value="restricted">Restricted</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-2">Access Level</label>
                                <select
                                    value={editAccessLevel}
                                    onChange={(e) => setEditAccessLevel(e.target.value as DocumentAccessLevel)}
                                    className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                                >
                                    <option value="all">All Users</option>
                                    <option value="employee">Employees Only</option>
                                    <option value="admin">Admin Only</option>
                                </select>
                            </div>
                            <div className="flex gap-3 pt-4">
                                <button
                                    type="button"
                                    onClick={() => setShowEditModal(false)}
                                    className="flex-1 px-4 py-2 bg-accent rounded-lg hover:bg-accent/80 transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="flex-1 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
                                >
                                    Save Changes
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Filter */}
            <div className="flex gap-4">
                <select
                    value={filterScope}
                    onChange={(e) => setFilterScope(e.target.value as any)}
                    className="px-4 py-2 bg-card border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                >
                    <option value="all">All Scopes</option>
                    <option value="internal">Internal</option>
                    <option value="public">Public</option>
                    <option value="restricted">Restricted</option>
                </select>
            </div>

            {/* Documents Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredDocuments.length === 0 ? (
                    <div className="col-span-full text-center py-12 bg-card rounded-lg border border-border">
                        <p className="text-muted-foreground">No documents found</p>
                    </div>
                ) : (
                    filteredDocuments.map((doc) => (
                        <div
                            key={doc.id}
                            className="bg-card border border-border rounded-lg p-4 hover:border-primary/50 transition-colors"
                        >
                            <div className="flex items-start justify-between mb-3 gap-3">
                                <div className="flex items-center gap-2 overflow-hidden flex-1">
                                    <FileText className="w-5 h-5 text-primary shrink-0" />
                                    <h3 className="font-semibold truncate" title={doc.title}>{doc.title}</h3>
                                </div>
                                <span
                                    className={`shrink-0 px-2 py-1 rounded text-xs font-medium ${doc.scope === "public"
                                        ? "bg-green-500/20 text-green-400"
                                        : doc.scope === "internal"
                                            ? "bg-blue-500/20 text-blue-400"
                                            : "bg-orange-500/20 text-orange-400"
                                        }`}
                                >
                                    {doc.scope}
                                </span>
                            </div>
                            <div className="space-y-2 text-sm text-muted-foreground">
                                <div>Version: {doc.version || "1.0"}</div>
                                <div>Chunks: {doc.chunk_count || 0}</div>
                                <div>Vectors: {doc.vector_count || 0}</div>
                                <div>Access: {doc.access_level || "all"}</div>
                            </div>
                            <div className="flex gap-2 mt-4">
                                <button
                                    onClick={() => window.open(`${API_URL}/docs/${doc.source}`, '_blank')}
                                    className="px-3 py-2 bg-accent rounded-lg hover:bg-accent/80 transition-colors"
                                    title="View"
                                >
                                    <Eye className="w-3 h-3" />
                                </button>
                                <button
                                    onClick={() => handleReindex(doc.id)}
                                    className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-accent rounded-lg hover:bg-accent/80 transition-colors text-sm"
                                    title="Re-index"
                                >
                                    <RefreshCw className="w-3 h-3" />
                                    Re-index
                                </button>
                                <button
                                    onClick={() => handleEdit(doc)}
                                    className="px-3 py-2 bg-accent rounded-lg hover:bg-accent/80 transition-colors"
                                    title="Edit"
                                >
                                    <Pencil className="w-3 h-3" />
                                </button>
                                <button
                                    onClick={() => handleDelete(doc.id)}
                                    className="px-3 py-2 bg-destructive/20 rounded-lg hover:bg-destructive/30 transition-colors"
                                    title="Delete"
                                >
                                    <Trash2 className="w-3 h-3 text-destructive" />
                                </button>
                            </div>
                        </div>
                    ))
                )}
            </div>

            {/* Stats */}
            <div className="grid grid-cols-4 gap-4">
                <div className="bg-card border border-border rounded-lg p-4">
                    <div className="text-2xl font-bold">{documents.length}</div>
                    <div className="text-sm text-muted-foreground">Total Documents</div>
                </div>
                <div className="bg-card border border-border rounded-lg p-4">
                    <div className="text-2xl font-bold text-green-400">
                        {documents.filter((d) => d.scope === "public").length}
                    </div>
                    <div className="text-sm text-muted-foreground">Public</div>
                </div>
                <div className="bg-card border border-border rounded-lg p-4">
                    <div className="text-2xl font-bold text-blue-400">
                        {documents.filter((d) => d.scope === "internal").length}
                    </div>
                    <div className="text-sm text-muted-foreground">Internal</div>
                </div>
                <div className="bg-card border border-border rounded-lg p-4">
                    <div className="text-2xl font-bold text-orange-400">
                        {documents.filter((d) => d.scope === "restricted").length}
                    </div>
                    <div className="text-sm text-muted-foreground">Restricted</div>
                </div>
            </div>
        </div>
    );
}
