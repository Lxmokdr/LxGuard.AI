"use client"

import { useEffect, useState, useRef } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Loader2, Zap, Share2 } from "lucide-react"
import { api } from "@/lib/api"

interface Node {
    id: string
    label: string
    x?: number
    y?: number
    color?: string
}

interface Link {
    source: string
    target: string
    label: string
    verified: boolean
}

interface GraphData {
    nodes: Node[]
    links: Link[]
}

export function KnowledgeGraph() {
    const [data, setData] = useState<GraphData | null>(null)
    const [loading, setLoading] = useState(true)
    const [hoveredNode, setHoveredNode] = useState<string | null>(null)
    const containerRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        const fetchGraph = async () => {
            try {
                const response = await api.knowledge.getGraph()

                // Handle different response formats (data field or direct payload)
                const graphNodes = response.data?.nodes || response.nodes || []
                const graphLinks = response.data?.links || response.links || []

                // Add simple force-directed starting positions
                const nodes = graphNodes.map((n: Node, i: number) => ({
                    ...n,
                    x: 100 + Math.random() * 600,
                    y: 100 + Math.random() * 400
                }))

                setData({ nodes, links: graphLinks })
            } catch (err) {
                console.error("Failed to fetch KG:", err)
            } finally {
                setLoading(false)
            }
        }

        fetchGraph()
    }, [])

    if (loading) {
        return (
            <div className="h-[500px] flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-primary animate-spin" />
            </div>
        )
    }

    if (!data || data.nodes.length === 0) {
        return (
            <div className="h-[500px] flex flex-col items-center justify-center text-muted-foreground">
                <Share2 className="w-12 h-12 mb-4 opacity-20" />
                <p>No knowledge graph data available yet.</p>
                <p className="text-sm">Run an induction build to populate the graph.</p>
            </div>
        )
    }

    return (
        <div className="relative overflow-hidden rounded-xl border border-border/50 bg-black/40 backdrop-blur-sm" ref={containerRef}>
            <div className="absolute top-4 left-4 z-10">
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-xs text-primary font-mono glow-border-cyan">
                    <Zap className="w-3 h-3" />
                    LIVE INDUCED ONTOLOGY
                </div>
            </div>

            <svg viewBox="0 0 800 500" className="w-full h-[500px]">
                {/* Edges */}
                {data.links.map((link, i) => {
                    const sourceNode = data.nodes.find(n => n.id === link.source)
                    const targetNode = data.nodes.find(n => n.id === link.target)
                    if (!sourceNode || !targetNode) return null

                    return (
                        <g key={`link-${i}`}>
                            <motion.line
                                initial={{ pathLength: 0, opacity: 0 }}
                                animate={{
                                    pathLength: 1,
                                    opacity: link.verified ? 0.8 : 0.3,
                                    strokeDasharray: link.verified ? "0" : "5,5"
                                }}
                                x1={sourceNode.x}
                                y1={sourceNode.y}
                                x2={targetNode.x}
                                y2={targetNode.y}
                                className={link.verified ? "text-secondary" : "text-primary/50"}
                                stroke="currentColor"
                                strokeWidth={link.verified ? "2" : "1"}
                            />
                            {/* Predicate Label */}
                            <text
                                x={(sourceNode.x! + targetNode.x!) / 2}
                                y={(sourceNode.y! + targetNode.y!) / 2}
                                className={`${link.verified ? 'fill-secondary font-bold' : 'fill-muted-foreground'} text-[8px] font-mono pointer-events-none`}
                                textAnchor="middle"
                                dy="-4"
                            >
                                {link.label}
                                {link.verified && " ✓"}
                            </text>
                        </g>
                    )
                })}

                {/* Nodes */}
                {data.nodes.map((node, i) => (
                    <motion.g
                        key={node.id}
                        initial={{ scale: 0, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        transition={{ delay: i * 0.05 }}
                        onMouseEnter={() => setHoveredNode(node.id)}
                        onMouseLeave={() => setHoveredNode(null)}
                        className="cursor-pointer"
                    >
                        <circle
                            cx={node.x}
                            cy={node.y}
                            r="6"
                            className={`fill-black stroke-2 transition-colors duration-300 ${hoveredNode === node.id ? 'stroke-primary' : 'stroke-primary/40'
                                }`}
                            style={{ stroke: hoveredNode === node.id ? (node.color || 'var(--primary)') : undefined }}
                        />
                        <circle
                            cx={node.x}
                            cy={node.y}
                            r="3"
                            className="fill-primary"
                            style={{ fill: node.color || 'var(--primary)' }}
                        />
                        {/* Shadow/Glow circle */}
                        <circle
                            cx={node.x}
                            cy={node.y}
                            r="10"
                            className={`opacity-0 transition-opacity duration-300 ${hoveredNode === node.id ? 'opacity-100' : ''
                                }`}
                            style={{ fill: node.color ? `${node.color}33` : 'rgba(var(--primary), 0.1)' }}
                        />
                        {/* Label */}
                        <text
                            x={node.x! + 10}
                            y={node.y! + 4}
                            className={`text-[10px] font-mono transition-all duration-300 ${hoveredNode === node.id ? 'font-bold' : 'fill-muted-foreground'
                                }`}
                            style={{ fill: hoveredNode === node.id ? (node.color || 'var(--primary)') : undefined }}
                        >
                            {node.label}
                        </text>
                    </motion.g>
                ))}
            </svg>
        </div>
    )
}
