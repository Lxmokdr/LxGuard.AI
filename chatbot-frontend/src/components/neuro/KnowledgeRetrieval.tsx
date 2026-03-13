import { motion, AnimatePresence } from "framer-motion";
import { BookOpen, FileText, ExternalLink, Hash } from "lucide-react";
import { API_URL } from "../../config";

export interface KnowledgeSource {
  id: string;
  filename: string;
  section: string;
  relevance: number;
  preview: string;
}

interface KnowledgeRetrievalProps {
  sources: KnowledgeSource[];
}

const KnowledgeRetrieval = ({ sources = [] }: KnowledgeRetrievalProps) => {
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <BookOpen className="w-4 h-4 text-primary" />
        <span className="text-sm font-medium text-foreground">Knowledge Retrieval</span>
        <span className="text-xs text-muted-foreground font-mono">
          ({sources.length} sources)
        </span>
      </div>

      <div className="space-y-2 max-h-[220px] overflow-y-auto custom-scrollbar pr-1">
        <AnimatePresence mode="popLayout">
          {sources.map((source, index) => (
            <motion.div
              key={source.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ delay: index * 0.1 }}
              layout
              onClick={() => window.open(`${API_URL}/docs/${source.filename}`, '_blank')}
              className="glass-card p-3 hover:glow-border-cyan transition-all duration-300 cursor-pointer group"
            >
              <div className="flex items-start justify-between gap-2 mb-2">
                <div className="flex items-center gap-2 min-w-0">
                  <FileText className="w-4 h-4 text-primary flex-shrink-0" />
                  <span className="font-mono text-xs text-foreground truncate">
                    {source.filename}
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  <div
                    className="h-1.5 rounded-full bg-muted overflow-hidden"
                    style={{ width: "40px" }}
                  >
                    <div
                      className="h-full bg-secondary rounded-full transition-all duration-500"
                      style={{ width: `${source.relevance}%` }}
                    />
                  </div>
                  <span className="text-xs font-mono text-muted-foreground">
                    {source.relevance}%
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-1 mb-2">
                <Hash className="w-3 h-3 text-muted-foreground" />
                <span className="text-xs text-accent-foreground">{source.section}</span>
              </div>

              <p className="text-xs text-muted-foreground line-clamp-2 leading-relaxed">
                {source.preview}
              </p>

              <div className="mt-2 flex items-center gap-1 text-xs text-primary opacity-0 group-hover:opacity-100 transition-opacity">
                <ExternalLink className="w-3 h-3" />
                <span>View source</span>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default KnowledgeRetrieval;
