import { motion } from "framer-motion";
import { Brain, Terminal } from "lucide-react";
import LiveMetrics from "./LiveMetrics";
import RuleTrace, { Rule } from "./RuleTrace";
import KnowledgeRetrieval, { KnowledgeSource } from "./KnowledgeRetrieval";

interface NeuroConsoleProps {
  confidenceScore: number;
  processingTime: number;
  modelUsed: string;
  rules: Rule[];
  knowledgeSources: KnowledgeSource[];
  isProcessing?: boolean;
}

const NeuroConsole = ({
  confidenceScore,
  processingTime,
  modelUsed,
  rules,
  knowledgeSources,
  isProcessing = false,
}: NeuroConsoleProps) => {
  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
      className="h-full flex flex-col"
    >
      {/* Header */}
      <div className="glass-card p-4 mb-4 scan-line">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary/20 flex items-center justify-center glow-border-cyan">
              <Brain className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-foreground text-glow-cyan">
                LxGuard.AI Console
              </h2>
              <p className="text-xs text-muted-foreground font-mono">
                Real-time reasoning trace
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Terminal className="w-4 h-4 text-muted-foreground" />
            <span className="text-xs font-mono text-muted-foreground">v2.1.0</span>
          </div>
        </div>
      </div>

      {/* Scrollable content */}
      <div className="flex-1 overflow-y-auto custom-scrollbar space-y-6 pr-1">
        <LiveMetrics
          confidenceScore={confidenceScore}
          processingTime={processingTime}
          modelUsed={modelUsed}
          isProcessing={isProcessing}
        />

        <div className="border-t border-border/50" />

        <RuleTrace rules={rules} />

        <div className="border-t border-border/50" />

        <KnowledgeRetrieval sources={knowledgeSources} />
      </div>

      {/* Footer status */}
      <div className="mt-4 pt-4 border-t border-border/50">
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <span
              className={`w-2 h-2 rounded-full ${isProcessing ? "bg-primary animate-pulse" : "bg-secondary"
                }`}
            />
            <span className="text-muted-foreground">
              {isProcessing ? "Processing query..." : "System ready"}
            </span>
          </div>
          <span className="font-mono text-muted-foreground/60">
            {new Date().toLocaleTimeString()}
          </span>
        </div>
      </div>
    </motion.div>
  );
};

export default NeuroConsole;
