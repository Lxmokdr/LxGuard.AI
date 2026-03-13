import { motion } from "framer-motion";
import { Activity, Clock, Cpu, TrendingUp } from "lucide-react";

interface LiveMetricsProps {
  confidenceScore: number;
  processingTime: number;
  modelUsed: string;
  isProcessing?: boolean;
}

const LiveMetrics = ({
  confidenceScore,
  processingTime,
  modelUsed,
  isProcessing = false,
}: LiveMetricsProps) => {
  const metrics = [
    {
      label: "Confidence",
      value: `${confidenceScore}%`,
      icon: TrendingUp,
      color: confidenceScore > 80 ? "text-secondary" : confidenceScore > 50 ? "text-destructive" : "text-muted-foreground",
      glowClass: confidenceScore > 80 ? "glow-border-emerald" : "",
    },
    {
      label: "Processing",
      value: `${processingTime}ms`,
      icon: Clock,
      color: "text-primary",
      glowClass: isProcessing ? "pulse-glow" : "",
    },
    {
      label: "Model",
      value: modelUsed,
      icon: Cpu,
      color: "text-accent-foreground",
      glowClass: "",
    },
  ];

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Activity className="w-4 h-4 text-primary" />
        <span className="text-sm font-medium text-foreground">Live Metrics</span>
        {isProcessing && (
          <span className="flex items-center gap-1 text-xs text-primary animate-pulse-subtle">
            <span className="w-2 h-2 bg-primary rounded-full animate-pulse" />
            Active
          </span>
        )}
      </div>

      <div className="grid grid-cols-1 gap-2">
        {metrics.map((metric, index) => (
          <motion.div
            key={metric.label}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`glass-card p-3 ${metric.glowClass}`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <metric.icon className={`w-4 h-4 ${metric.color}`} />
                <span className="text-xs text-muted-foreground">{metric.label}</span>
              </div>
              <span className={`text-sm font-mono font-medium ${metric.color}`}>
                {metric.value}
              </span>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default LiveMetrics;
