import { useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { MessageSquare, Sparkles, LogOut, User as UserIcon } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ADMIN_URL } from "@/config";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  source?: string;  // Add source field
}

interface ChatInterfaceProps {
  messages: Message[];
  onSendMessage: (message: string, mode: string) => void;
  onStop?: () => void;
  isProcessing?: boolean;
  statusMessage?: string;
}

const ChatInterface = ({
  messages,
  onSendMessage,
  onStop,
  isProcessing = false,
  statusMessage = "Analyzing with expert rules...",
}: ChatInterfaceProps) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { user, logout } = useAuth();

  useEffect(() => {
    // Determine behavior: auto for streaming chunks, smooth for single messages
    const isStreaming = messages.length > 0 && messages[messages.length - 1].role === "assistant" && messages[messages.length - 1].content.length > 0;
    messagesEndRef.current?.scrollIntoView({ behavior: isStreaming ? "auto" : "smooth" });
  }, [messages]);

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'admin': return 'bg-primary/10 text-primary border-primary/20';
      case 'employee': return 'bg-indigo-500/10 text-indigo-600 border-indigo-500/20';
      case 'guest': return 'bg-slate-500/10 text-slate-600 border-slate-500/20';
      default: return 'bg-muted text-muted-foreground';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
      className="h-full flex flex-col"
    >
      {/* Header */}
      <div className="border-b border-border pb-6 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center">
              <MessageSquare className="w-5 h-5 text-primary-foreground" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-foreground">
                LxGuard.AI Diagnosis
              </h2>
              <p className="text-xs text-muted-foreground">
                LxGuard.AI Knowledge Agent
              </p>
            </div>
          </div>

          {/* User Info & Logout */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <UserIcon className="w-4 h-4 text-muted-foreground" />
              <span className="text-sm font-medium text-foreground">{user?.username}</span>
              <Badge variant="outline" className={`text-xs font-mono ${getRoleBadgeColor(user?.role || '')}`}>
                {user?.role}
              </Badge>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={logout}
              className="text-muted-foreground hover:text-foreground"
            >
              <LogOut className="w-4 h-4" />
            </Button>
            <div className="flex items-center gap-4 pointer-events-auto">
              {user?.role === "admin" && (
                <a
                  href={`${ADMIN_URL}/login`}
                  className="px-3 py-1.5 bg-indigo-600/20 hover:bg-indigo-600/40 border border-indigo-500/30 rounded-lg text-indigo-400 text-xs font-medium transition-all backdrop-blur-md flex items-center gap-2"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <span className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse" />
                  Admin Portal
                </a>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto custom-scrollbar pr-2">
        {messages.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="h-full flex flex-col items-center justify-center text-center p-8"
          >
            <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mb-6">
              <Sparkles className="w-8 h-8 text-primary" />
            </div>
            <h3 className="text-xl font-semibold text-foreground mb-2">
              Welcome to LxGuard.AI
            </h3>
            <p className="text-sm text-muted-foreground max-w-md leading-relaxed">
              Describe your Next.js issue below. Watch the Neuro-Console on the right
              to see exactly how the AI agent thinks, which rules it applies, and what
              documentation it references.
            </p>
            <div className="mt-6 flex flex-wrap justify-center gap-2">
              {[
                "Routing issues",
                "API routes",
                "Build errors",
                "SSR problems",
              ].map((tag) => (
                <span
                  key={tag}
                  className="px-3 py-1.5 text-xs font-mono bg-muted rounded-lg text-muted-foreground"
                >
                  {tag}
                </span>
              ))}
            </div>
          </motion.div>
        ) : (
          <div className="space-y-4 pb-4">
            {messages.map((message) => (
              <ChatMessage
                key={message.id}
                role={message.role}
                content={message.content}
                timestamp={message.timestamp}
                source={message.source}
              />
            ))}
            {isProcessing && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-center gap-2 text-sm text-muted-foreground p-4"
              >
                <div className="flex gap-1">
                  {[0, 1, 2].map((i) => (
                    <span
                      key={i}
                      className="w-2 h-2 bg-primary rounded-full animate-pulse"
                      style={{ animationDelay: `${i * 0.2}s` }}
                    />
                  ))}
                </div>
                <span>{statusMessage}</span>
              </motion.div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input area */}
      <div className="mt-4">
        <ChatInput onSubmit={onSendMessage} onStop={onStop} isProcessing={isProcessing} />
      </div>
    </motion.div>
  );
};

export default ChatInterface;
