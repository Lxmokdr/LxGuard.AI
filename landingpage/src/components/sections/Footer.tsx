import { ArrowRight, Github, Mail } from "lucide-react";

export const Footer = () => (
  <footer id="cta" className="relative overflow-hidden border-t border-hairline bg-background">
    <div className="container relative z-10 py-16 sm:py-24">
      <div className="flex flex-col md:flex-row items-center justify-between gap-8 text-center md:text-left">
        <div className="max-w-md">
          <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-hairline glass px-3 py-1.5 font-mono text-[10px] uppercase tracking-[0.2em] text-primary">
            Ready when you are
          </div>
          <h2 className="font-display text-3xl sm:text-4xl font-semibold leading-tight">
            Govern your AI <span className="text-gradient block sm:inline">like critical infrastructure.</span>
          </h2>
        </div>
        
      </div>
    </div>

    <div className="container relative z-10 border-t border-hairline py-6">
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-[10px] sm:text-xs uppercase tracking-[0.18em] text-muted-foreground">
        <div>© 2026 LxGuard.AI. All rights reserved.</div>
        <div className="flex items-center gap-6">
          <a href="https://github.com/lxguard" target="_blank" rel="noopener noreferrer" className="hover:text-primary transition-colors flex items-center gap-2">
            <Github className="h-3.5 w-3.5" />
            <span>GitHub</span>
          </a>
        </div>
      </div>
    </div>
  </footer>
);