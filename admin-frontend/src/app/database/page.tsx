"use client";

import { useState, useEffect } from "react";
import {
    Database,
    Table as TableIcon,
    Search,
    RefreshCcw,
    ChevronRight,
    ChevronLeft,
    ListFilter,
    ArrowUpDown,
    Download,
    ArrowUp,
    ArrowDown,
    ExternalLink
} from "lucide-react";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { motion, AnimatePresence } from "framer-motion";

interface TableInfo {
    name: string;
    rows: number;
    columns: { name: string; type: string }[];
}

export default function DatabaseExplorerPage() {
    const [tables, setTables] = useState<TableInfo[]>([]);
    const [selectedTable, setSelectedTable] = useState<string | null>(null);
    const [tableData, setTableData] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [dataLoading, setDataLoading] = useState(false);
    const [searchTerm, setSearchTerm] = useState("");
    const [page, setPage] = useState(0);
    const [sortConfig, setSortConfig] = useState<{ key: string; direction: "ASC" | "DESC" } | null>(null);
    const limit = 20;

    useEffect(() => {
        loadTables();
    }, []);

    const loadTables = async () => {
        setLoading(true);
        try {
            const data = await api.database.getTables();
            setTables(data.tables || []);
        } catch (error) {
            console.error("Failed to load tables:", error);
        } finally {
            setLoading(false);
        }
    };

    const loadTableData = async (tableName: string, offset = 0, sortKey?: string, sortDir?: "ASC" | "DESC") => {
        setDataLoading(true);
        try {
            const data = await api.database.queryTable(tableName, {
                limit,
                offset,
                orderBy: sortKey || sortConfig?.key,
                orderDir: sortDir || sortConfig?.direction
            });
            setTableData(data.items || []);
            setSelectedTable(tableName);
        } catch (error) {
            console.error(`Failed to load data for ${tableName}:`, error);
        } finally {
            setDataLoading(false);
        }
    };

    const handleTableSelect = (tableName: string) => {
        setPage(0);
        setSortConfig(null);
        loadTableData(tableName, 0);
    };

    const handleSort = (columnName: string) => {
        if (!selectedTable) return;

        let direction: "ASC" | "DESC" = "ASC";
        if (sortConfig?.key === columnName && sortConfig.direction === "ASC") {
            direction = "DESC";
        }

        setSortConfig({ key: columnName, direction });
        setPage(0);
        loadTableData(selectedTable, 0, columnName, direction);
    };

    const handleNextPage = () => {
        if (!selectedTable) return;
        const nextOffset = (page + 1) * limit;
        setPage(page + 1);
        loadTableData(selectedTable, nextOffset);
    };

    const handlePrevPage = () => {
        if (!selectedTable || page === 0) return;
        const prevOffset = (page - 1) * limit;
        setPage(page - 1);
        loadTableData(selectedTable, prevOffset);
    };

    const exportToJSON = () => {
        if (!selectedTable || tableData.length === 0) return;
        const blob = new Blob([JSON.stringify(tableData, null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${selectedTable}_page_${page + 1}.json`;
        a.click();
        URL.revokeObjectURL(url);
    };

    const filteredTables = tables.filter(t =>
        t.name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const getColumns = () => {
        if (!selectedTable) return [];
        return tables.find(t => t.name === selectedTable)?.columns || [];
    };

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center h-96 gap-4">
                <div className="w-12 h-12 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
                <p className="text-muted-foreground font-medium animate-pulse">Introspecting Schema...</p>
            </div>
        );
    }

    return (
        <div className="h-full flex flex-col gap-6">
            <header className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-3">
                        <div className="p-2 rounded-xl bg-primary/10 text-primary">
                            <Database className="w-6 h-6" />
                        </div>
                        Database Explorer
                    </h1>
                    <p className="text-muted-foreground text-sm mt-1">
                        PostgreSQL introspection • <span className="font-semibold text-foreground">{tables.length} tables</span> discovered in cluster
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    <Button
                        variant="outline"
                        onClick={loadTables}
                        className="bg-background/50 hover:bg-secondary/80 gap-2 border-border/50"
                    >
                        <RefreshCcw className="w-4 h-4" />
                        Refresh Schema
                    </Button>
                </div>
            </header>

            <div className="grid grid-cols-12 gap-6 flex-1 min-h-0">
                {/* Tables Sidebar */}
                <div className="col-span-12 lg:col-span-3 flex flex-col gap-4 min-h-[300px] lg:min-h-0">
                    <div className="relative group">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
                        <input
                            type="text"
                            placeholder="Filter tables..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full bg-secondary/30 border border-border/50 rounded-xl pl-10 pr-4 py-2 text-sm focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all"
                        />
                    </div>

                    <div className="flex-1 overflow-y-auto glass-card border-border/40 p-2 custom-scrollbar">
                        <div className="space-y-1">
                            {filteredTables.map((table) => (
                                <button
                                    key={table.name}
                                    onClick={() => handleTableSelect(table.name)}
                                    className={`w-full text-left px-3 py-2.5 rounded-lg text-sm transition-all flex items-center justify-between group ${selectedTable === table.name
                                        ? "bg-primary text-primary-foreground shadow-lg shadow-primary/20"
                                        : "hover:bg-secondary/80 text-muted-foreground hover:text-foreground border border-transparent"
                                        }`}
                                >
                                    <div className="flex items-center gap-2">
                                        <TableIcon className={`w-4 h-4 ${selectedTable === table.name ? "opacity-100" : "opacity-50 group-hover:opacity-100"}`} />
                                        <span className="font-medium truncate">{table.name}</span>
                                    </div>
                                    <div className={`text-[10px] px-1.5 py-0.5 rounded-md font-bold ${selectedTable === table.name
                                        ? "bg-white/20 text-white"
                                        : "bg-secondary text-muted-foreground"
                                        }`}>
                                        {table.rows}
                                    </div>
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Data View */}
                <div className="col-span-12 lg:col-span-9 flex flex-col gap-4 min-h-0">
                    <AnimatePresence mode="wait">
                        {!selectedTable ? (
                            <motion.div
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className="flex-1 glass-card border-dashed flex flex-col items-center justify-center text-muted-foreground gap-4 bg-secondary/5"
                            >
                                <div className="p-6 rounded-3xl bg-secondary/20 border border-border/30">
                                    <ListFilter className="w-12 h-12 opacity-30" />
                                </div>
                                <div className="text-center">
                                    <p className="font-semibold text-foreground">Schema Synchronized</p>
                                    <p className="text-xs max-w-[250px] mt-1 opacity-70">Select a table from the sidebar to browse records and inspect relationships.</p>
                                </div>
                            </motion.div>
                        ) : (
                            <motion.div
                                key={selectedTable}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="flex-1 flex flex-col gap-4 min-h-0"
                            >
                                <div className="glass-card p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-border/40">
                                    <div className="flex items-center gap-4">
                                        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-primary text-xs font-bold">
                                            <TableIcon className="w-3.5 h-3.5" />
                                            {selectedTable}
                                        </div>
                                        <div className="text-[11px] text-muted-foreground font-medium flex items-center gap-2">
                                            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
                                            SHOWING {tableData.length > 0 ? page * limit + 1 : 0}-{page * limit + tableData.length} RECORDS
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-3">
                                        <Button
                                            size="sm"
                                            variant="outline"
                                            onClick={exportToJSON}
                                            disabled={tableData.length === 0}
                                            className="h-8 text-xs gap-2 px-3 border-border/50 bg-background/50 hover:bg-secondary/80"
                                        >
                                            <Download className="w-3.5 h-3.5" />
                                            Export
                                        </Button>
                                        <div className="h-4 w-px bg-border/50 mx-1"></div>
                                        <div className="flex items-center gap-1">
                                            <Button
                                                size="icon"
                                                variant="outline"
                                                className="h-8 w-8 rounded-lg"
                                                disabled={page === 0 || dataLoading}
                                                onClick={handlePrevPage}
                                            >
                                                <ChevronLeft className="w-4 h-4" />
                                            </Button>
                                            <div className="text-xs font-bold px-3 min-w-[70px] text-center">PAGE {page + 1}</div>
                                            <Button
                                                size="icon"
                                                variant="outline"
                                                className="h-8 w-8 rounded-lg"
                                                disabled={tableData.length < limit || dataLoading}
                                                onClick={handleNextPage}
                                            >
                                                <ChevronRight className="w-4 h-4" />
                                            </Button>
                                        </div>
                                    </div>
                                </div>

                                <div className="flex-1 glass-card overflow-hidden flex flex-col border-border/40">
                                    <div className="overflow-auto custom-scrollbar flex-1 relative">
                                        {dataLoading ? (
                                            <div className="absolute inset-0 bg-background/50 backdrop-blur-[2px] z-20 flex items-center justify-center">
                                                <RefreshCcw className="w-8 h-8 text-primary animate-spin opacity-80" />
                                            </div>
                                        ) : null}

                                        <table className="w-full text-left text-[11px] border-collapse relative">
                                            <thead className="sticky top-0 bg-secondary/95 backdrop-blur-md border-b border-border z-10">
                                                <tr>
                                                    {getColumns().map(col => (
                                                        <th
                                                            key={col.name}
                                                            className="px-4 py-3 text-foreground font-semibold border-r border-border/30 whitespace-nowrap cursor-pointer hover:bg-secondary transition-colors"
                                                            onClick={() => handleSort(col.name)}
                                                        >
                                                            <div className="flex items-center justify-between gap-4">
                                                                <div className="flex flex-col">
                                                                    <span>{col.name}</span>
                                                                    <span className="text-[9px] text-muted-foreground font-normal uppercase">{col.type}</span>
                                                                </div>
                                                                <div className="flex items-center">
                                                                    {sortConfig?.key === col.name ? (
                                                                        sortConfig.direction === "ASC" ? <ArrowUp className="w-4 h-4 text-primary" /> : <ArrowDown className="w-4 h-4 text-primary" />
                                                                    ) : (
                                                                        <ArrowUpDown className="w-3.5 h-3.5 opacity-20 group-hover:opacity-100 transition-opacity" />
                                                                    )}
                                                                </div>
                                                            </div>
                                                        </th>
                                                    ))}
                                                </tr>
                                            </thead>
                                            <tbody className="divide-y divide-border/30">
                                                {tableData.length === 0 && !dataLoading ? (
                                                    <tr>
                                                        <td colSpan={getColumns().length} className="px-4 py-20 text-center text-muted-foreground opacity-50 font-medium">
                                                            No records found in this table
                                                        </td>
                                                    </tr>
                                                ) : (
                                                    tableData.map((row, i) => (
                                                        <tr key={i} className="hover:bg-primary/[0.02] transition-colors group">
                                                            {getColumns().map(col => (
                                                                <td key={col.name} className="px-4 py-2.5 border-r border-border/20 max-w-[250px] truncate group-hover:border-primary/20 transition-all font-medium text-muted-foreground group-hover:text-foreground">
                                                                    {row[col.name] === null ? (
                                                                        <span className="text-destructive/50 italic opacity-60">NULL</span>
                                                                    ) : typeof row[col.name] === 'object' ? (
                                                                        <div className="flex items-center gap-1.5 text-primary/80">
                                                                            <pre className="text-[10px] bg-primary/5 p-2 rounded border border-primary/10 whitespace-pre-wrap font-mono min-w-[200px] max-w-[400px] max-h-32 overflow-y-auto custom-scrollbar shadow-inner shadow-black/20 text-left">
                                                                                {JSON.stringify(row[col.name], null, 2)}
                                                                            </pre>
                                                                        </div>
                                                                    ) : (
                                                                        <span>{String(row[col.name])}</span>
                                                                    )}
                                                                </td>
                                                            ))}
                                                        </tr>
                                                    ))
                                                )}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </div>

            {/* Status Footer */}
            <footer className="glass-card p-3 flex items-center justify-between border-border/40 bg-secondary/30">
                <div className="flex items-center gap-6 text-[10px] font-semibold text-muted-foreground uppercase tracking-widest px-2">
                    <div className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></div>
                        <span>Direct Introspection Active</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                        <div className="w-1 h-1 rounded-full bg-border"></div>
                        <span>PostgreSQL v15 (pgvector)</span>
                    </div>
                    <div className="hidden sm:flex items-center gap-1.5">
                        <div className="w-1 h-1 rounded-full bg-border"></div>
                        <span>Mode: Cluster-Admin</span>
                    </div>
                </div>
                <div className="text-[10px] font-bold text-primary flex items-center gap-2">
                    EXPERT-AGENT V2.0
                    <ExternalLink className="w-3 h-3" />
                </div>
            </footer>
        </div>
    );
}
