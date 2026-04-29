import { Suspense, useRef } from "react";
import { Canvas } from "@react-three/fiber";
import { motion, useScroll, useTransform } from "framer-motion";
import { Sparkles, ChevronDown } from "lucide-react";
import { EffectComposer, Bloom } from "@react-three/postprocessing";
import { NeuralCore } from "@/components/three/NeuralCore";

export const Hero = () => {
  const ref = useRef<HTMLElement>(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start start", "end start"] });
  const contentY = useTransform(scrollYProgress, [0, 1], [0, 180]);
  const contentOpacity = useTransform(scrollYProgress, [0, 0.6], [1, 0]);
  const canvasY = useTransform(scrollYProgress, [0, 1], [0, -80]);
  const canvasScale = useTransform(scrollYProgress, [0, 1], [1, 1.15]);
  return (
    <section ref={ref} id="top" className="relative min-h-[100svh] w-full overflow-hidden">
      {/* 3D canvas */}
      <motion.div style={{ y: canvasY, scale: canvasScale }} className="absolute inset-0 opacity-30">
        <Canvas
          dpr={[1, 1.6]}
          camera={{ position: [0, 0, 6.5], fov: 55 }}
          gl={{ antialias: true, alpha: true }}
        >
          <Suspense fallback={null}>
            <NeuralCore />
            <EffectComposer>
              <Bloom intensity={1.1} luminanceThreshold={0.2} luminanceSmoothing={0.5} mipmapBlur />
            </EffectComposer>
          </Suspense>
        </Canvas>
      </motion.div>

      {/* Decorative grid + vignette */}
      <div className="pointer-events-none absolute inset-0 grid-bg opacity-60" />
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(0,0,0,0.5)_0%,transparent_60%)]" />
      <div className="pointer-events-none absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-background via-background/70 to-transparent" />
      <div className="pointer-events-none absolute inset-x-0 top-0 h-32 bg-gradient-to-b from-background to-transparent" />

      {/* Content */}
      <motion.div
        style={{ y: contentY, opacity: contentOpacity }}
        className="relative z-10 mx-auto flex min-h-[100svh] max-w-6xl flex-col items-center justify-center px-6 py-32 text-center"
      >
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-6 inline-flex items-center gap-2 rounded-full border border-hairline glass px-3 py-1.5 font-mono text-[11px] uppercase tracking-[0.22em] text-primary"
        >
          <Sparkles className="h-3 w-3" />
          Neuro-Symbolic Governance · v1.0
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.05 }}
          className="font-display text-5xl sm:text-6xl md:text-7xl font-semibold leading-[1.02] tracking-tight"
        >
          <span className="block">LxGuard<span className="text-gradient">.AI</span></span>
          <span className="mt-3 block text-2xl sm:text-3xl md:text-4xl font-medium text-muted-foreground">
            The Neuro-Symbolic Governance System
          </span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.15 }}
          className="mt-6 max-w-2xl text-base sm:text-lg text-muted-foreground"
        >
          Where probabilistic intelligence meets deterministic truth — eight orchestrated layers
          that secure, parse, arbitrate, retrieve, plan, generate, and validate every decision.
        </motion.p>

        {/* stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.35 }}
          className="mt-12 grid w-full max-w-3xl grid-cols-3 gap-3"
        >
          {[
            { k: "8", v: "Reasoning layers" },
            { k: "100%", v: "Auditable trace" },
            { k: "<200ms", v: "Validation latency" },
          ].map((s) => (
            <div key={s.v} className="glass rounded-2xl px-4 py-4">
              <div className="font-display text-2xl sm:text-3xl text-gradient font-semibold">{s.k}</div>
              <div className="mt-1 text-[11px] sm:text-xs uppercase tracking-[0.18em] text-muted-foreground">
                {s.v}
              </div>
            </div>
          ))}
        </motion.div>
      </motion.div>

      {/* scroll cue */}
      <motion.div
        style={{ opacity: contentOpacity }}
        className="pointer-events-none absolute bottom-6 left-1/2 z-10 -translate-x-1/2 flex flex-col items-center gap-2 text-[10px] uppercase tracking-[0.3em] text-muted-foreground/80"
      >
        scroll to explore
        <ChevronDown className="h-4 w-4 animate-bounce text-primary" />
      </motion.div>
    </section>
  );
};