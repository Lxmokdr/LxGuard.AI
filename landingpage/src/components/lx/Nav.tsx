import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";

const links = [
  { href: "#architecture", label: "Architecture" },
  { href: "#pipeline", label: "Pipeline" },
  { href: "#modes", label: "Modes" },
  { href: "#security", label: "Security" },
  { href: "#stack", label: "Stack" },
  { href: "#ingestion", label: "Sync" },
];

export const Nav = () => {
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={cn(
        "fixed inset-x-0 top-0 z-50 transition-all duration-300",
        scrolled ? "py-2" : "py-4",
      )}
    >
      <div className="container">
        <div
          className={cn(
            "flex items-center justify-between rounded-full px-4 py-2 transition-all",
            scrolled ? "glass" : "bg-transparent",
          )}
        >
          <a href="#top" className="flex items-center gap-3 font-display text-sm font-semibold tracking-wide">
            <img src="/logo/LogoWhite-02.png" alt="LxGuard.AI logo" className="h-20 " />
          </a>
          <nav className="hidden md:flex items-center gap-1">
            {links.map((l) => (
              <a
                key={l.href}
                href={l.href}
                className="rounded-full px-3 py-1.5 text-xs font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
              >
                {l.label}
              </a>
            ))}
          </nav>
        </div>
      </div>
    </header>
  );
};