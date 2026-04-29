import { useRef, ReactNode } from "react";
import { motion, useScroll, useTransform, MotionValue } from "framer-motion";

interface ParallaxProps {
  children: ReactNode;
  /** pixels to translate at the extremes of the element's scroll range */
  offset?: number;
  className?: string;
  /** scale change at extremes (e.g. 0.05 means 0.95 → 1.05) */
  scale?: number;
  /** opacity at top + bottom (1 = no fade) */
  fade?: boolean;
}

/**
 * Wrap any block in a scroll-driven parallax. Translates on Y as the element
 * passes through the viewport. Optional gentle scale + fade for cinematic feel.
 */
export const Parallax = ({ children, offset = 60, scale = 0, fade = false, className }: ParallaxProps) => {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"],
  });
  const y = useTransform(scrollYProgress, [0, 1], [offset, -offset]);
  const s = useTransform(scrollYProgress, [0, 0.5, 1], [1 - scale, 1, 1 + scale]);
  const o = useTransform(scrollYProgress, [0, 0.2, 0.8, 1], fade ? [0, 1, 1, 0] : [1, 1, 1, 1]);

  return (
    <motion.div ref={ref} style={{ y, scale: s, opacity: o }} className={className}>
      {children}
    </motion.div>
  );
};

/** Smaller helper: returns a parallax Y motion value for a target ref. */
export const useParallaxY = (ref: React.RefObject<HTMLElement>, range = 80): MotionValue<number> => {
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start end", "end start"] });
  return useTransform(scrollYProgress, [0, 1], [range, -range]);
};