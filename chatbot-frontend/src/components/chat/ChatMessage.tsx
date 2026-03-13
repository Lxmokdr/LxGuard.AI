import { motion } from "framer-motion";
import { Bot, User, Database, Globe, Layers } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
  source?: string;
}

const ChatMessage = ({ role, content, timestamp, source }: ChatMessageProps) => {
  const isUser = role === "user";

  const getSourceBadge = () => {
    if (!source || isUser) return null;

    const sourceConfig = {
      "Local Ontology": { icon: Database, color: "bg-indigo-500/10 text-indigo-600 border-indigo-500/20" },
      "LOD (DBpedia)": { icon: Globe, color: "bg-indigo-500/10 text-indigo-600 border-indigo-500/20" },
      "Hybrid (Local + LOD)": { icon: Layers, color: "bg-indigo-500/10 text-indigo-600 border-indigo-500/20" },
      "Full Pipeline": { icon: Layers, color: "bg-indigo-500/10 text-indigo-600 border-indigo-500/20" },
      "Local LLM": { icon: Bot, color: "bg-indigo-500/10 text-indigo-600 border-indigo-500/20" },
      "Dual-System": { icon: Layers, color: "bg-indigo-500/10 text-indigo-600 border-indigo-500/20" },
    };

    const config = sourceConfig[source as keyof typeof sourceConfig] || sourceConfig["Full Pipeline"];
    const Icon = config.icon;

    return (
      <Badge variant="outline" className={`${config.color} border-none text-[10px] font-medium mt-2 px-2 py-0 h-5`}>
        <Icon className="w-3 h-3 mr-1" />
        {source}
      </Badge>
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className={`flex gap-3 ${isUser ? "flex-row-reverse" : "flex-row"}`}
    >
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center ${isUser
          ? "bg-secondary"
          : "bg-primary text-primary-foreground"
          }`}
      >
        {isUser ? (
          <User className="w-4 h-4 text-secondary-foreground" />
        ) : (
          <Bot className="w-4 h-4" />
        )}
      </div>

      <div
        className={`flex-1 max-w-[85%] ${isUser ? "text-right" : "text-left"}`}
      >
        <div
          className={`inline-block p-3 px-4 rounded-2xl ${isUser
            ? "bg-primary text-primary-foreground rounded-tr-none"
            : "bg-muted text-foreground rounded-tl-none"
            }`}
        >
          <div className="text-sm leading-relaxed whitespace-pre-wrap">
            {content}
          </div>
          {getSourceBadge()}
        </div>
        {timestamp && (
          <div className="mt-1 text-xs text-muted-foreground font-mono">
            {timestamp}
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default ChatMessage;
