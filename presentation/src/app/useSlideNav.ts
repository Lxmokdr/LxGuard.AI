import { useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";

/**
 * Shared keyboard + click navigation hook.
 * Returns { handleNext, handlePrev } for arrow buttons.
 *
 * handleNext: advance phase by 1, or navigate to nextRoute when at max.
 * handlePrev: go back phase by 1, or navigate to prevRoute when at 0.
 */
export function useSlideNav(
    phase: number,
    setPhase: React.Dispatch<React.SetStateAction<number>>,
    maxPhase: number,
    nextRoute: string,
    prevRoute: string,
) {
    const router = useRouter();

    // IMPORTANT: use plain state value, never call router.push inside setPhase
    const handleNext = useCallback(() => {
        if (phase < maxPhase) {
            setPhase(phase + 1);
        } else {
            router.push(nextRoute);
        }
    }, [phase, maxPhase, nextRoute, router, setPhase]);

    const handlePrev = useCallback(() => {
        if (phase > 0) {
            setPhase(phase - 1);
        } else {
            router.push(prevRoute);
        }
    }, [phase, prevRoute, router, setPhase]);

    // Keyboard arrow listener — re-registers whenever phase (and thus the
    // callbacks) change, so there are no stale closures.
    useEffect(() => {
        const onKey = (e: KeyboardEvent) => {
            const tag = (e.target as HTMLElement)?.tagName;
            if (tag === "INPUT" || tag === "TEXTAREA") return;
            if (e.key === "ArrowRight") handleNext();
            if (e.key === "ArrowLeft") handlePrev();
        };
        window.addEventListener("keydown", onKey);
        return () => window.removeEventListener("keydown", onKey);
    }, [handleNext, handlePrev]); // callbacks are stable as long as phase doesn't change

    return { handleNext, handlePrev };
}
