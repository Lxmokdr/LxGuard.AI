import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { GitBranch, Zap, ChevronDown, ChevronRight } from "lucide-react";

export interface Rule {
  id: string;
  name: string;
  type: "creation" | "debug" | "analysis";
  status: "active" | "triggered" | "pending";
  timestamp: string;
  result?: Record<string, any>; // layer output data
}

interface RuleTraceProps {
  rules: Rule[];
}

/** Render a value from the layer result as a readable string */
function renderValue(value: any): string {
  if (Array.isArray(value)) {
    if (value.length === 0) return "—";
    return value
      .map((v) => (typeof v === "object" ? JSON.stringify(v) : String(v)))
      .join(", ");
  }
  if (typeof value === "object" && value !== null) {
    return Object.entries(value)
      .map(([k, v]) => `${k}: ${v}`)
      .join(" · ");
  }
  if (typeof value === "boolean") return value ? "✓ Yes" : "✗ No";
  if (typeof value === "number") return String(value);
  return value ?? "—";
}

/** 
 * Maps layer result keys to human-readable labels 
 */
const LABEL_MAP: Record<string, string> = {
  allowed: "Allowed",
  reason: "Reason",
  keywords: "Keywords",
  question_type: "Q-Type",
  entities: "Entities",
  final_intent: "Intent",
  confidence: "Confidence",
  docs_found: "Docs found",
  top_docs: "Top docs",
  goal: "Goal",
  structure: "Structure",
  steps: "Steps",
  valid: "Valid",
  score: "Score",
  checks: "Checks",
  issues: "Issues",
};

const LayerResultPanel = ({ result }: { result: Record<string, any> }) => {
  const entries = Object.entries(result).filter(
    ([, v]) =>
      v !== null &&
      v !== undefined &&
      !(Array.isArray(v) && v.length === 0) &&
      !(typeof v === "object" && !Array.isArray(v) && Object.keys(v).length === 0)
  );

  if (entries.length === 0) return null;

  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: "auto" }}
      exit={{ opacity: 0, height: 0 }}
      transition={{ duration: 0.2 }}
      className="mt-2 rounded border border-border/40 bg-background/40 px-2 py-1.5 space-y-1"
    >
      {entries.map(([key, value]) => (
        <div key={key} className="flex items-start gap-1.5 text-xs">
          <span className="font-mono text-primary/70 shrink-0 min-w-[70px]">
            {LABEL_MAP[key] ?? key}
          </span>
          <span className="text-muted-foreground break-words">
            {renderValue(value)}
          </span>
        </div>
      ))}
    </motion.div>
  );
};

const RuleTrace = ({ rules }: RuleTraceProps) => {
  const [expanded, setExpanded] = useState<Set<string>>(new Set());

  // Auto-expand when a layer result arrives
  useEffect(() => {
    rules.forEach((rule) => {
      if (rule.result && Object.keys(rule.result).length > 0) {
        setExpanded((prev) => {
          if (prev.has(rule.id)) return prev;
          const next = new Set(prev);
          next.add(rule.id);
          return next;
        });
      }
    });
  }, [rules]);

  const toggle = (id: string) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };  

  const getTypeStyles = (type: Rule["type"]) => {
    switch (type) {
      case "creation":
        return "rule-tag-creation";
      case "debug":
        return "rule-tag-debug";
      case "analysis":
        return "rule-tag-analysis";
    }
  };

  const getStatusIcon = (status: Rule["status"]) => {
    switch (status) {
      case "active":
        return <span className="w-2 h-2 bg-secondary rounded-full animate-pulse" />;
      case "triggered":
        return <Zap className="w-3 h-3 text-destructive" />;
      case "pending":
        return <span className="w-2 h-2 bg-muted-foreground rounded-full" />;
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <GitBranch className="w-4 h-4 text-primary" />
        <span className="text-sm font-medium text-foreground">Engine Trace</span>
        <span className="text-xs text-muted-foreground font-mono">
          ({rules.filter((r) => r.status === "triggered").length} layers)
        </span>
      </div>

      <div className="space-y-2 max-h-[400px] overflow-y-auto custom-scrollbar pr-1">
        <AnimatePresence mode="popLayout">
          {rules.map((rule, index) => {
            const hasResult = rule.result && Object.keys(rule.result).length > 0;
            const isExpanded = expanded.has(rule.id);

            return (
              <motion.div
                key={rule.id}
                initial={{ opacity: 0, scale: 0.9, x: 20 }}
                animate={{ opacity: 1, scale: 1, x: 0 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{
                  type: "spring",
                  stiffness: 500,
                  damping: 30,
                  delay: index * 0.05,
                }}
                layout
                className={`
                  glass-card p-3 transition-all duration-300
                  ${rule.status === "active" ? "glow-border-cyan" : ""}
                  ${rule.status === "triggered" ? "glow-border-emerald" : ""}
                `}
              >
                {/* Header row */}
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      {getStatusIcon(rule.status)}
                      <span className="font-mono text-xs text-foreground truncate">
                        {rule.name}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-1.5">
                    <span
                      className={`px-2 py-0.5 text-xs font-mono rounded ${getTypeStyles(rule.type)}`}
                    >
                      {rule.type}
                    </span>

                    {/* Toggle button — only if there's a result */}
                    {hasResult && (
                      <button
                        onClick={() => toggle(rule.id)}
                        className="text-muted-foreground hover:text-foreground transition-colors"
                        title={isExpanded ? "Hide result" : "Show result"}
                      >
                        {isExpanded ? (
                          <ChevronDown className="w-3.5 h-3.5" />
                        ) : (
                          <ChevronRight className="w-3.5 h-3.5" />
                        )}
                      </button>
                    )}
                  </div>
                </div>

                {/* Timestamp */}
                <div className="text-xs text-muted-foreground/60 font-mono mb-0.5">
                  {rule.timestamp}
                </div>

                {/* Layer result — auto-expand when result arrives */}
                <AnimatePresence>
                  {hasResult && isExpanded && (
                    <LayerResultPanel result={rule.result!} />
                  )}
                </AnimatePresence>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default RuleTrace;
