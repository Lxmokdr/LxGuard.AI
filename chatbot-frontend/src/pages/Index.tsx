import { useState, useCallback, useRef } from "react";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/contexts/AuthContext";
import ChatInterface from "@/components/chat/ChatInterface";
import NeuroConsole from "@/components/neuro/NeuroConsole";
import { Rule } from "@/components/neuro/RuleTrace";
import { KnowledgeSource } from "@/components/neuro/KnowledgeRetrieval";
import { API_URL } from "../config";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  source?: string;  // Add source field
}

// Hybrid API Response Types
interface HybridAPIResponse {
  answer: string;
  reasoning: {
    nlp_analysis: {
      intent_hypotheses: Array<{
        intent: string;
        confidence: number;
        evidence: string[];
      }>;
      entities: Record<string, string>;
      semantic_roles: Record<string, string>;
      keywords: string[];
      question_type: string;
    };
    intent_arbitration: {
      final_intent: string;
      confidence: number;
      reason: string;
      rejected_intents: string[];
    };
    retrieval_path: {
      tier1_symbolic: {
        topic_filter: string;
        forbidden_docs: string[];
        eligible_count: number;
      };
      tier2_semantic: {
        top_scores: Array<[string, number]>;
      };
      final_documents: string[];
    };
    answer_plan: {
      goal: string;
      structure: string;
      steps: string[];
      excluded_topics: string[];
      max_length: number;
    };
    documents: Array<{
      name: string;
      score: number;
      sections: string[];
    }>;
  };
  validation: {
    valid: boolean;
    score: number;
    checks: Record<string, boolean>;
    issues: string[];
  };
  confidence: number;
  architecture_info: {
    type: string;
    design: string;
    layers: string;
  };
  source?: string;  // Add source field
}

const Index = () => {
  const { toast } = useToast();
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [confidenceScore, setConfidenceScore] = useState(0);
  const [processingTime, setProcessingTime] = useState(0);
  const [rules, setRules] = useState<Rule[]>([]);
  const [knowledgeSources, setKnowledgeSources] = useState<KnowledgeSource[]>([]);
  const [streamingMessage, setStreamingMessage] = useState<Message | null>(null);
  const [modelUsed, setModelUsed] = useState("LxGuard.AI");
  const [currentStatus, setCurrentStatus] = useState("Analyzing...");
  const abortControllerRef = useRef<AbortController | null>(null);
  const readerRef = useRef<ReadableStreamDefaultReader<Uint8Array> | null>(null);

  const handleStop = useCallback(() => {
    if (readerRef.current) {
      readerRef.current.cancel();
      readerRef.current = null;
    }
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsProcessing(false);
    setStreamingMessage(null);
    setCurrentStatus("Stopped by user.");
  }, []);

  const handleSendMessage = useCallback(
    async (content: string, mode: string) => {
      const userMessage: Message = {
        id: `msg-${Date.now()}`,
        role: "user",
        content,
        timestamp: new Date().toLocaleTimeString(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsProcessing(true);
      setStreamingMessage(null); // Clear any previous streaming
      setConfidenceScore(0);
      setProcessingTime(0);
      setRules([]);
      setKnowledgeSources([]);

      const startTime = Date.now();

      // Create a new abort controller for this request
      const controller = new AbortController();
      abortControllerRef.current = controller;

      try {
        const headers: HeadersInit = {
          "Content-Type": "application/json",
        };

        const token = localStorage.getItem("access_token");
        if (token) {
          headers["Authorization"] = `Bearer ${token}`;
        }

        const response = await fetch(`${API_URL}/api/chat/stream`, {
          method: "POST",
          headers,
          body: JSON.stringify({ question: content, mode }),
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error("Network response was not ok");
        }

        if (!response.body) {
          throw new Error("Streaming response body is empty");
        }

        const reader = response.body.getReader();
        readerRef.current = reader ?? null;
        const decoder = new TextDecoder();

        let assistantContent = "";
        let finalSource = "";

        if (reader) {
          let buffer = "";
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split("\n\n");
            buffer = lines.pop() || "";

            for (const line of lines) {
              if (line.startsWith("data: ")) {
                try {
                  const data = JSON.parse(line.slice(6));

                  if (data.type === "chunk") {
                    assistantContent += data.content;
                    // Highly efficient: only update the streaming message state
                    setStreamingMessage({
                      id: "streaming-msg",
                      role: "assistant",
                      content: assistantContent,
                      timestamp: new Date().toLocaleTimeString(),
                    });
                  } else if (data.type === "status") {
                    setCurrentStatus(data.message);
                    setRules((prev) => [
                      ...prev,
                      {
                        id: `layer-${data.layer || Date.now()}`,
                        name: data.message,
                        type: "analysis",
                        status: "triggered",
                        timestamp: new Date().toLocaleTimeString().split(" ")[0],
                      }
                    ]);
                  } else if (data.type === "layer_result") {
                    // Attach the result to the matching layer card
                    setRules((prev) =>
                      prev.map((r) =>
                        r.id === `layer-${data.layer}`
                          ? { ...r, result: data.result }
                          : r
                      )
                    );
                  } else if (data.type === "error") {
                    toast({
                      title: "Stream Error",
                      description: data.message,
                      variant: "destructive",
                    });
                    setIsProcessing(false);
                  } else if (data.type === "final") {
                    setConfidenceScore(Math.round((data.confidence ?? 0) * 100));

                    // Update source and model info
                    if (data.source) {
                      finalSource = data.source;
                    }

                    // Handle architecture/model info
                    const archInfo = data.architecture_info;
                    if (archInfo?.type || archInfo?.orchestrator) {
                      setModelUsed(archInfo.type || archInfo.orchestrator);
                    }

                    // Final reasoning trace - ROBUST MAPPING
                    const reasoning = data.reasoning;
                    console.log("🔍 [Stream Final] Full reasoning trace arrived:", reasoning);

                    if (reasoning && reasoning.documents) {
                      const mappedSources: KnowledgeSource[] = reasoning.documents.map((doc: any, idx: number) => ({
                        id: `src-${idx}-${Date.now()}`,
                        filename: doc.name || "Unknown Document",
                        section: (doc.sections && doc.sections.length > 0) ? doc.sections[0] : "General",
                        relevance: Math.round((doc.score || 0) * 100),
                        preview: doc.best_chunk
                          ? (doc.best_chunk.substring(0, 150) + "...")
                          : `Retrieved for ${reasoning.intent_arbitration?.final_intent || "General"} intent.`,
                      }));

                      console.log("✅ [Frontend] Mapped sources for display:", mappedSources);
                      setKnowledgeSources(mappedSources);
                    }
                  }
                } catch (e) {
                  console.error("Error parsing stream chunk", e);
                }
              }
            }
          }
        }

        // Finish up: Merge streaming message into main messsages history
        if (assistantContent) {
          const finalAssistantMsg: Message = {
            id: `msg-${Date.now()}`,
            role: "assistant",
            content: assistantContent,
            timestamp: new Date().toLocaleTimeString(),
            source: finalSource
          };
          setMessages(prev => [...prev, finalAssistantMsg]);
          setStreamingMessage(null);
        }

        const endTime = Date.now();
        setProcessingTime(endTime - startTime);

      } catch (error: any) {
        if (error.name === 'AbortError') {
          // User clicked stop — this is expected, don't show an error.
          console.log("Stream aborted by user.");
        } else {
          console.error("Error communicating with hybrid agent:", error);
          const errorMessage: Message = {
            id: `msg-${Date.now() + 1}`,
            role: "assistant",
            content: "⚠️ Error processing response from LxGuard.AI. Check console for details.",
            timestamp: new Date().toLocaleTimeString(),
          };
          setMessages((prev) => [...prev, errorMessage]);
        }
      } finally {
        readerRef.current = null;
        abortControllerRef.current = null;
        setIsProcessing(false);
      }
    },
    []
  );

  return (
    <div className="min-h-screen bg-background neural-bg">
      {/* Ambient glow effects */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-glow-cyan/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-glow-emerald/5 rounded-full blur-3xl" />
      </div>

      {/* Main layout */}
      <div className="relative z-10 h-screen flex">
        {/* Left: Conversation (60%) */}
        <div className="w-[60%] h-full p-6 border-r border-border/50">
          <ChatInterface
            messages={streamingMessage ? [...messages, streamingMessage] : messages}
            onSendMessage={handleSendMessage}
            onStop={handleStop}
            isProcessing={isProcessing}
            statusMessage={currentStatus}
          />
        </div>

        {/* Right: Neuro-Console (40%) */}
        <div className="w-[40%] h-full p-6 bg-sidebar/50">
          <NeuroConsole
            confidenceScore={confidenceScore}
            processingTime={processingTime}
            modelUsed={modelUsed}
            rules={rules}
            knowledgeSources={knowledgeSources}
            isProcessing={isProcessing}
          />
        </div>
      </div>
    </div>
  );
};

export default Index;
