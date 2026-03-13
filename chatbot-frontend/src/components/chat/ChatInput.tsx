import { useState } from "react";
import { motion } from "framer-motion";
import { Cpu, Sparkles, Loader2, Database, Globe, Square } from "lucide-react";
import { Textarea } from "@/components/ui/textarea";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";

interface ChatInputProps {
  onSubmit: (message: string, mode: string) => void;
  onStop?: () => void;
  isProcessing?: boolean;
}

const ChatInput = ({ onSubmit, onStop, isProcessing = false }: ChatInputProps) => {
  const [message, setMessage] = useState("");
  const [mode, setMode] = useState("full");

  const handleSubmit = () => {
    if (message.trim() && !isProcessing) {
      onSubmit(message.trim(), mode);
      setMessage("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const modeOptions = [
    { value: "full", label: "Project Knowledge", icon: Database, color: "text-blue-400" },
    { value: "external", label: "Linked Data (LOD)", icon: Globe, color: "text-amber-400" },
    { value: "llm", label: "Pure AI (LLM)", icon: Sparkles, color: "text-purple-400" },
  ];

  return (
    <div className="glass-card p-4">
      {/* Mode Selector */}
      <div className="mb-3 pb-3 border-b border-border/50">
        <Label className="text-xs text-muted-foreground mb-2 block">Knowledge Source</Label>
        <RadioGroup value={mode} onValueChange={setMode} className="flex gap-2">
          {modeOptions.map((option) => {
            const Icon = option.icon;
            return (
              <div key={option.value} className="flex items-center">
                <RadioGroupItem
                  value={option.value}
                  id={option.value}
                  className="peer sr-only"
                />
                <Label
                  htmlFor={option.value}
                  className={`
                    flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium
                    cursor-pointer transition-all duration-200
                    border border-border/50
                    peer-data-[state=checked]:border-primary/50
                    peer-data-[state=checked]:bg-primary/10
                    hover:bg-muted/50
                  `}
                >
                  <Icon className={`w-3.5 h-3.5 ${mode === option.value ? option.color : 'text-muted-foreground'}`} />
                  <span>{option.label}</span>
                </Label>
              </div>
            );
          })}
        </RadioGroup>
      </div>

      <div className="flex gap-3">
        <div className="flex-1 relative">
          <Textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Describe your issue or question..."
            className="min-h-[80px] bg-muted/50 border-border/50 focus:border-primary/50 focus:ring-primary/20 resize-none text-sm font-sans"
            disabled={isProcessing}
          />
          <div className="absolute bottom-2 left-3 text-xs text-muted-foreground">
            Press <kbd className="px-1.5 py-0.5 bg-muted rounded text-xs font-mono">Enter</kbd> to send
          </div>
        </div>

        {isProcessing ? (
          // Stop button — shown while streaming
          <motion.button
            onClick={onStop}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="
              flex items-center gap-2 px-6 py-3 rounded-xl font-medium text-sm
              transition-all duration-300 self-end
              bg-red-500/80 hover:bg-red-500 text-white cursor-pointer border border-red-400/50
            "
          >
            <Square className="w-4 h-4 fill-white" />
            <span>Stop</span>
          </motion.button>
        ) : (
          // Submit button — shown when idle
          <motion.button
            onClick={handleSubmit}
            disabled={!message.trim()}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className={`
              flex items-center gap-2 px-6 py-3 rounded-xl font-medium text-sm
              transition-all duration-300 self-end
              ${message.trim()
                ? "bg-primary text-primary-foreground glow-border-cyan cursor-pointer"
                : "bg-muted text-muted-foreground cursor-not-allowed"
              }
            `}
          >
            <Cpu className="w-4 h-4" />
            <span>Run Diagnosis</span>
          </motion.button>
        )}
      </div>

      <div className="flex items-center gap-2 mt-3 text-xs text-muted-foreground">
        <Sparkles className="w-3 h-3 text-primary" />
        <span>Hybrid Knowledge Agent • {mode === "full" ? "8-Layer Reasoning" : mode === "external" ? "DBpedia LOD Enrichment" : "Generative AI Mode"}</span>
      </div>
    </div>
  );
};

export default ChatInput;
