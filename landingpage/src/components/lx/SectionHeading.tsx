import { cn } from "@/lib/utils";
import { ReactNode } from "react";

interface Props {
  eyebrow?: string;
  title: ReactNode;
  description?: ReactNode;
  align?: "left" | "center";
  className?: string;
}

export const SectionHeading = ({ eyebrow, title, description, align = "center", className }: Props) => (
  <div
    className={cn(
      "mx-auto max-w-3xl",
      align === "center" ? "text-center" : "text-left",
      className,
    )}
  >
    {eyebrow && (
      <div
        className={cn(
          "mb-4 inline-flex items-center gap-2 rounded-full border border-hairline bg-surface/60 px-3 py-1 font-mono text-[11px] uppercase tracking-[0.2em] text-primary backdrop-blur",
        )}
      >
        <span className="h-1.5 w-1.5 rounded-full bg-primary shadow-neon" />
        {eyebrow}
      </div>
    )}
    <h2 className="font-display text-3xl sm:text-4xl md:text-5xl font-semibold leading-[1.05] tracking-tight">
      {title}
    </h2>
    {description && (
      <p className="mt-4 text-base sm:text-lg text-muted-foreground leading-relaxed">{description}</p>
    )}
  </div>
);